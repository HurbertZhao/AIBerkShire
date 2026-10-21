#!/usr/bin/env python3
"""Run from any directory. USD million unless explicitly stated; no network required."""
import json, subprocess, sys
from pathlib import Path
from decimal import Decimal as D
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
logs=[]
def run(tool,*args):
    cmd=[sys.executable,str(ROOT/'tools'/tool),*map(str,args)]
    p=subprocess.run(cmd,capture_output=True,text=True)
    logs.append('$ '+' '.join(cmd)+'\n'+p.stdout+p.stderr+'\nexit='+str(p.returncode))
    return p
def calc(expr):
    run('financial_rigor.py','calc','--expr',expr)
price=D('529.05'); shares=D('7425545491'); mcap=price*shares/D(1000000)
annual={
'2022':dict(revenue=198270,net=72738,gross=135620,op=83383,ocf=89035,capex=23886,cash=104757),
'2023':dict(revenue=211915,net=72361,gross=146052,op=88523,ocf=87582,capex=28107,cash=111262),
'2024':dict(revenue=245122,net=88136,gross=171008,op=109433,ocf=118548,capex=44477,cash=75543),
'2025':dict(revenue=281724,net=101832,gross=193893,op=128528,ocf=136162,capex=64551,cash=94565),
'2026':dict(revenue=331839,net=133749,gross=225465,op=155237,ocf=182935,capex=115948,cash=76843)}
quarters={
'FY26Q1':[[33020,5721,20407,28317],[30897,12314,13391,24092],[13756,6008,4163,13176]],
'FY26Q2':[[34116,6110,20599,29437],[32907,13566,13873,25544],[14250,6302,3803,14651]],
'FY26Q3':[[35013,6197,20973,29944],[34681,15120,13753,26751],[13192,5511,3672,13371]],
'FY26Q4':[[37847,6989,21900,33112],[39306,16876,15955,29878],[12854,5660,2748,13451]]}
for row in annual.values():
    row.update(fcf=row['ocf']-row['capex'],gm=round(100*row['gross']/row['revenue'],2),om=round(100*row['op']/row['revenue'],2))
for row in quarters.values():
    for a in row:
        a.extend([round(100*(a[0]/a[3]-1),2),round(100*(1-a[1]/a[0]),2),round(100*a[2]/a[0],2)])
run('financial_rigor.py','verify-market-cap','--price',price,'--shares',shares,'--reported','3930000000000','--currency','USD')
for field,v in [('revenue',331839),('net_income',133749),('cash_and_short_investments',76843),('ocf',182935),('capex',115948)]:
    run('financial_rigor.py','cross-validate','--field',field,'--values',json.dumps({'Microsoft FY26 Q4':v,'StockAnalysis S&P Global':v}),'--unit','USD million')
for year,v1,v2 in [(2022,104757,104749),(2023,111262,111256),(2024,75543,75531)]:
    run('financial_rigor.py','cross-validate','--field',f'FY{year} cash','--values',json.dumps({'Microsoft annual report':v1,'StockAnalysis standardized':v2}),'--unit','USD million')
run('financial_rigor.py','cross-validate','--field','shares','--values',json.dumps({'SEC 10K cover 2026-07-23':7425545491,'StockAnalysis filing date rounded':7426000000}),'--unit','shares')
run('financial_rigor.py','cross-validate','--field','close 2026-10-16','--values',json.dumps({'StockAnalysis':529.05,'Yahoo historical':529.05}),'--unit','USD')
run('financial_rigor.py','verify-valuation','--price',price,'--eps','17.95','--bvps',D(442387000000)/shares,'--fcf-per-share',D(66987000000)/shares,'--dividend','3.92')
run('financial_rigor.py','three-scenario','--price',price,'--eps','17','--shares',shares/D(100000000),'--growth','.20','.14','.06','--pe','36','30','24','--years','3','--currency','USD')
calc('76843-9227-31067');calc('76843-128813');calc('(486762.534+51450+103985+116300+58270+101459)/7425545491*100')
calc('155237*(1-0.2)/7453')
r=.10;roic=.21;gs=[.02,.03,.04];profits=[180000,400000,700000];prob=[.25,.50,.25];k=.006
audit=['--currency','USD','--r',r,'--roic',roic,'--g',','.join(map(str,gs)),'--rf','.051','--beta','1','--discrete-risks','AI overcapacity:情景,agent displacement:情景,forced breakup:未建模,export shutdown:未建模']
run('terminal_value.py','audit',*audit)
pes=[];irrs=[]
for g,profit in zip(gs,profits):
    pe=(1-g/roic)/(r-g);irr=((profit*pe/float(mcap))**.1-1+k)*100
    pes.append(pe);irrs.append(irr)
    run('terminal_value.py','pe','--roic',roic,'--g',g,'--r',r)
    run('terminal_value.py','irr','--profit',profit,'--mcap',mcap,'--pe',pe,'--years','10','--payout',k)
config={'微软':dict(roic=roic,g=gs,p=prob,irr10=irrs,k=k)}
(HERE/'terminal_config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2))
for delta in ['.02','.01']:
    run('terminal_value.py','flip','--config',HERE/'terminal_config.json','--name','微软','--r',r,'--delta',delta,'--currency','USD','--g-shift','0','--rf','.051')
def reverse_dcf(fcf):
    # Equity cash flow proxy; no separate net cash add-back to avoid double counting.
    def pv(x):
        return sum(fcf*(1+x)**t/(1+r)**t for t in range(1,11))+fcf*(1+x)**10*1.03/(r-.03)/(1+r)**10
    lo,hi=-.5,1.
    for _ in range(150):
        mid=(lo+hi)/2
        if pv(mid)<float(mcap):lo=mid
        else:hi=mid
    return dict(growth=(lo+hi)/2,pv=pv((lo+hi)/2))
scenario=[]
for growth,pe,p in zip([.06,.14,.20],[24,30,36],prob):
    eps=17*(1+growth)**3;target=eps*pe;pv=target/1.1**3
    scenario.append(dict(growth=growth,pe=pe,prob=p,eps=eps,target=target,pv=pv,price_cagr=(target/float(price))**(1/3)-1))
metrics=dict(mcap_million=str(mcap),pe_gaap=float(price)/17.95,pe_normalized=float(price)/17,ps=float(mcap)/331839,ev_sales_exlease=(float(mcap)-36549)/331839,ev_sales_incllease=(float(mcap)+51970)/331839,fcf_yield=66987/float(mcap)*100,capex_revenue=115948/331839*100,fcf_net=66987/133749*100,normalized_ebit_eps=155237*.8/7453,management_common_pct=918226.534/float(shares)*100)
out=dict(units='USD million; per share USD; percent fields documented in report',annual=annual,quarters=quarters,quarter_row_schema=['revenue','cost','op','prior_year_revenue','yoy_pct','gross_margin_pct','op_margin_pct'],metrics=metrics,scenario3=scenario,fair_probability_weighted=sum(x['pv']*x['prob'] for x in scenario),terminal=dict(profits=profits,pe=pes,irr_pct=irrs,expected_irr_pct=sum(a*b for a,b in zip(irrs,prob))),reverse_dcf_reported=reverse_dcf(66987),reverse_dcf_normalized=reverse_dcf(100000))
(HERE/'model_results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
(HERE/'financial_and_terminal_audit.log').write_text('\n\n'.join(logs))
print(json.dumps(out,ensure_ascii=False,indent=2))
