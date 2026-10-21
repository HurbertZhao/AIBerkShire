from decimal import Decimal as D, getcontext
from pathlib import Path
import subprocess, sys, json
getcontext().prec=40
root=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent
p=D('393.8'); shares=D('9092644829'); fx=D('0.8525'); profit=D('200000000000')
mcap=p*shares; mcny=mcap*fx; eps=profit/shares/fx; k=D('5.3')/p
log=[]
def run(tool,*args):
    cmd=[sys.executable,str(root/'tools'/tool),*map(str,args)]
    res=subprocess.run(cmd,capture_output=True,encoding='utf-8')
    log.append('$ '+' '.join(cmd)+'\n'+res.stdout+res.stderr+'\nExit: '+str(res.returncode))
    if res.returncode: raise RuntimeError(log[-1])
run('financial_rigor.py','verify-market-cap','--price',p,'--shares',shares,'--reported','3580684000000','--currency','HKD')
run('financial_rigor.py','verify-valuation','--price',p,'--eps',eps,'--dividend','5.3')
run('financial_rigor.py','three-scenario','--price',p,'--eps',eps,'--shares',shares/D('1e8'),'--growth','.12','.07','0','--pe','20','16','10','--years','3','--currency','HKD')
audit=['audit','--currency','CNY','--r','.08','--roic','.2','--g','0,.02,.03','--rf','.02','--beta','1','--discrete-risks','VIE失效:未建模,全面断供:未建模,游戏监管重击:情景,AI回报不足:情景']
run('terminal_value.py',*audit)
data={'inputs':{'price_HKD':str(p),'shares':str(shares),'CNY_per_HKD_assumed':str(fx),'normalized_profit_CNY_assumed':str(profit),'dividend_HKD_assumed': '5.3'},'market_cap_HKD':str(mcap),'market_cap_CNY':str(mcny),'normalized_EPS_HKD':str(eps),'normalized_PE':str(p/eps),'IFRS_TTM_PE':str(mcny/D('235508000000')),'FY25_IFRS_PE':str(mcny/D('224842000000')),'yield':str(k),'three_year':[],'ten_year':[]}
for growth,pe in [('0','10'),('.07','16'),('.12','20')]:
    target=eps*(1+D(growth))**3*D(pe)
    data['three_year'].append({'EPS_growth':growth,'exit_PE':pe,'target_HKD':str(target),'capital_return':str(target/p-1),'capital_CAGR':str((target/p)**(D(1)/3)-1),'discounted_at_10pct':str(target/(D('1.1')**3))})
anchors=[]
def actual_irr(terminal,market,dividend,years=10):
    lo,hi=-.99,2.
    for _ in range(200):
        mid=(lo+hi)/2
        pv=sum(dividend/(1+mid)**t for t in range(1,years+1))+terminal/(1+mid)**years
        if pv>market: lo=mid
        else: hi=mid
    return (lo+hi)/2
for row in data['three_year']:
    row['fixed_dividend_exact_IRR']=actual_irr(float(row['target_HKD']),float(p),5.3,3)
    row['discounted_at_8pct_including_fixed_dividend']=str(D(row['target_HKD'])/D('1.08')**3+sum(D('5.3')/D('1.08')**t for t in range(1,4)))
for growth,g in [(D('0'),D('0')),(D('.06'),D('.02')),(D('.1'),D('.03'))]:
    terminal_profit=profit*(1+growth)**10
    row={'growth':str(growth),'perpetual_g':str(g),'terminal_profit_CNY':str(terminal_profit),'rates':{}}
    for r in [D('.06'),D('.07'),D('.08'),D('.09'),D('.10')]:
        pe=(1-g/D('.2'))/(r-g)
        approx=(terminal_profit*pe/mcny)**(D(1)/10)-1+k
        row['rates'][str(r)]={'PE':str(pe),'spread':str(r-g),'approx_return':str(approx),'fixed_dividend_exact_IRR':actual_irr(float(terminal_profit*pe),float(mcny),float(D('5.3')*shares*fx))}
        if r in [D('.08'),D('.10')]:
            run('terminal_value.py','pe','--roic','.2','--g',g,'--r',r)
            run('terminal_value.py','irr','--profit',terminal_profit/D('1e8'),'--mcap',mcny/D('1e8'),'--pe',pe,'--years','10','--payout',k)
        if r==D('.10'): anchors.append(float(approx*100))
    data['ten_year'].append(row)
config={'腾讯本次模型':{'roic':.2,'g':[0,.02,.03],'p':[.3,.5,.2],'irr10':anchors,'k':float(k)}}
cfg=out/'valuation-config.json'; cfg.write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
for delta in ['.02','.01']:
    run('terminal_value.py','flip','--config',cfg,'--name','腾讯本次模型','--r','.08','--delta',delta,'--currency','CNY','--g-shift','0','--rf','.02')
data['weighted_returns']={r:sum(float(row['rates'][r]['approx_return'])*w for row,w in zip(data['ten_year'],[.3,.5,.2])) for r in ['0.06','0.07','0.08','0.09','0.10']}
data['required_growth_3y_10pct_return_exit_PE16_ex_dividend']=str((p*D('1.1')**3/(eps*16))**(D(1)/3)-1)
data['required_growth_3y_10pct_return_exit_PE16_fixed_dividend']=str(((p*D('1.1')**3-D('5.3')*(D('1.1')**2+D('1.1')+1))/(eps*16))**(D(1)/3)-1)
data['current_normalized_value_HKD']={str(pe):str(eps*pe) for pe in [14,16,18]}
data['base_3y_discounted_at_8pct_HKD']=str(eps*D('1.07')**3*16/D('1.08')**3)
data['base_3y_discounted_at_8pct_plus_fixed_dividend_HKD']=str(eps*D('1.07')**3*16/D('1.08')**3+sum(D('5.3')/D('1.08')**t for t in range(1,4)))
data['reverse_DCF']={}
for cash in [D('120e9'),D('160e9'),D('200e9')]:
    lo,hi=D('-.5'),D('.5')
    for _ in range(180):
        h=(lo+hi)/2
        pv=sum(cash*(1+h)**t/D('1.08')**t for t in range(1,11))+cash*(1+h)**10*D('1.02')/D('.06')/D('1.08')**10
        if pv>mcny: hi=h
        else: lo=h
    data['reverse_DCF'][str(cash)]={'required_10y_growth':str((lo+hi)/2),'PV_CNY':str(pv)}
run('terminal_value.py',*audit)
(out/'valuation-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'valuation-tool-output.txt').write_text('\n\n'.join(log),encoding='utf-8')
print(json.dumps(data,ensure_ascii=False,indent=2))
