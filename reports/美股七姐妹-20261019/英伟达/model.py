#!/usr/bin/env python3
"""Reproduce NVDA research valuation and repository audit CLI calls. USD millions except per-share."""
import json, subprocess, pathlib, sys, math
from decimal import Decimal as D
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from terminal_value import irr_from_terminal
price=D('214.13'); shares=D('24147'); mcap=price*shares
annual={
'FY2022':dict(revenue=26914,net=9752,gross=17475,op=10041,ocf=9108,capex=976,cash=1990,liquid=21208),
'FY2023':dict(revenue=26974,net=4368,gross=15356,op=4224,ocf=5641,capex=1833,cash=3389,liquid=13296),
'FY2024':dict(revenue=60922,net=29760,gross=44301,op=32972,ocf=28090,capex=1069,cash=7280,liquid=25984),
'FY2025':dict(revenue=130497,net=72880,gross=97858,op=81453,ocf=64089,capex=3236,cash=8589,liquid=43210),
'FY2026':dict(revenue=215938,net=120067,gross=153463,op=130387,ocf=102718,capex=6042,cash=10605,liquid=62556)}
for v in annual.values():
 v.update(gm=v['gross']/v['revenue']*100,om=v['op']/v['revenue']*100,fcf=v['ocf']-v['capex'])
quarter={
'FY26Q3':dict(revenue=57006,compute=50908,graphics=6098,compute_yoy_base=31036,graphics_yoy_base=4046,gm=73.4,net=31910),
'FY26Q4':dict(revenue=68127,compute=193479-131828,graphics=22459-15983,compute_yoy_base=116193-80157,graphics_yoy_base=14304-11009,gm=75,net=42960),
'FY27Q1':dict(revenue=81615,compute=74550,graphics=7065,compute_yoy_base=39589,graphics_yoy_base=4473,gm=74.9,net=58321),
'FY27Q2':dict(revenue=96221,compute=88299,graphics=7922,compute_yoy_base=41331,graphics_yoy_base=5412,gm=75,net=59688)}
for v in quarter.values():
 for k in ['compute','graphics']:v[k+'_yoy']=(v[k]/v[k+'_yoy_base']-1)*100
baseeps=D('8.18'); r=D('.10'); roic=D('.40'); gs=[D('.01'),D('.03'),D('.04')]; probs=[.25,.5,.25]; profits=[150000,600000,1200000]; k=.005
pes=[(1-g/roic)/(r-g) for g in gs]
irrs=[irr_from_terminal(n,float(mcap),float(pe),10,k)*100 for n,pe in zip(profits,pes)]
conf={'英伟达':dict(roic=float(roic),g=list(map(float,gs)),p=probs,irr10=irrs,k=k)}
(HERE/'terminal-config.json').write_text(json.dumps(conf,ensure_ascii=False,indent=2))
three=[]
for name,g,pe,p,rev in [('悲观',D('-.05'),18,.25,400000),('基准',D('.20'),25,.50,700000),('乐观',D('.30'),30,.25,1000000)]:
 eps=baseeps*(1+g)**3; target=eps*pe
 three.append(dict(name=name,growth=float(g),pe=pe,probability=p,eps=float(eps),profit=float(eps*shares),revenue=rev,net_margin=float(eps*shares/D(rev)),price=float(target),pv=float(target/(1+r)**3),cagr=float((target/price)**(D(1)/3)-1)))
# Reverse DCF: OCF-capex equity cash-flow proxy, no debt/cash adjustment.
# No additional SBC addback; OCF already adds back SBC and this proxy does not deduct its economic dilution cost.
f0=127006; discount=.10; terminalg=.03
def dcf(g):
 return sum(f0*(1+g)**t/(1+discount)**t for t in range(1,11))+f0*(1+g)**10*(1+terminalg)/(discount-terminalg)/(1+discount)**10
lo,hi=-.5,1
for _ in range(120):
 mid=(lo+hi)/2
 if dcf(mid)<float(mcap):lo=mid
 else:hi=mid
out=dict(price=float(price),shares_million=float(shares),mcap_million=float(mcap),annual=annual,quarters=quarter,eps_normalized_calculation=(53954+45548)*2/24338,eps_used=float(baseeps),three_year=three,three_year_weighted_pv=sum(v['pv']*v['probability'] for v in three),terminal_pes=list(map(float,pes)),terminal_profit_million=profits,terminal_irr=irrs,expected_irr=sum(p*i for p,i in zip(probs,irrs)),reverse_dcf_growth=mid,reverse_dcf_terminal_fcf=f0*(1+mid)**10,reverse_dcf_terminal_weight=(f0*(1+mid)**10*(1+terminalg)/(discount-terminalg)/(1+discount)**10)/float(mcap),net_cash_narrow=22443+34143-1000-32366,net_cash_including_leases=22443+34143-38860,liquid_broad=22443+34143+42783,cash_conflict_pct=(62469-56586)/56586*100,fy23_op_conflict_pct=(5577-4224)/4224*100,ttm_revenue=sum(v['revenue'] for v in quarter.values()),ttm_net=sum(v['net'] for v in quarter.values()),pb=float(mcap)/228984,ps=float(mcap)/302970,ev_sales=(float(mcap)-23220)/302970,fcf_yield=127006/float(mcap)*100,pe_eps=float(price)/7.91,pe_profit=float(mcap)/192880,normalized_pe=float(price/baseeps),h1_investment_gain_share=23707/141410*100,huang_vote_pct=870604104/24312141810*100,huang_ex_foundation_pct=(870604104-58683830)/24312141810*100)
(HERE/'model-output.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
commands=[]
def run(tool,*args):
 cmd=[sys.executable,str(ROOT/'tools'/tool),*map(str,args)]
 cp=subprocess.run(cmd,capture_output=True,text=True)
 commands.append('$ '+' '.join(cmd)+'\n'+cp.stdout+cp.stderr+f'\n[exit={cp.returncode}]\n')
 return cp.returncode
run('financial_rigor.py','verify-market-cap','--price',price,'--shares',int(shares*1000000),'--reported',5170000000000,'--currency','USD')
for field,a,b,unit in [('FY26收入',215938,215938,'USD_million'),('FY26净利',120067,120067,'USD_million'),('FY26现金广义',62556,62556,'USD_million'),('Q2现金等价物',22443,22443,'USD_million'),('期末股数',24147,24147,'million'),('FY23营业利润差异',4224,5577,'USD_million'),('Q2流动现金口径冲突',56586,62469,'USD_million')]:
 run('financial_rigor.py','cross-validate','--field',field,'--values',json.dumps({'SEC':a,'StockAnalysis':b}),'--unit',unit)
run('financial_rigor.py','verify-valuation','--price',price,'--eps',7.91,'--bvps',D(228984)/shares,'--fcf-per-share',D(127006)/shares,'--dividend',1,'--revenue-per-share',D(302970)/shares)
run('financial_rigor.py','three-scenario','--price',price,'--eps',baseeps,'--shares',D('241.47'),'--growth','.30','.20','-.05','--pe',30,25,18,'--years',3,'--currency','USD')
audit=['audit','--currency','USD','--r','.10','--roic','.40','--g','.01,.03,.04','--rf','.051','--beta','1','--discrete-risks','ASIC替代:情景,需求收缩:情景,台海中断:未建模,反垄断拆分:未建模']
run('terminal_value.py',*audit)
for g,pe,profit in zip(gs,pes,profits):
 run('terminal_value.py','pe','--roic',roic,'--g',g,'--r',r)
 run('terminal_value.py','irr','--profit',profit,'--mcap',mcap,'--pe',pe,'--years',10,'--payout',k)
for delta in ['.02','.01']:
 run('terminal_value.py','flip','--config',HERE/'terminal-config.json','--name','英伟达','--r','.10','--delta',delta,'--currency','USD','--rf','.051')
run('terminal_value.py',*audit)
(HERE/'calculation-audit.log').write_text('\n'.join(commands))
print(json.dumps(out,ensure_ascii=False,indent=2))
