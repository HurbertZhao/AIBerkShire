#!/usr/bin/env python3
"""Tesla research calculations. USD million unless explicitly noted; no network."""
from pathlib import Path
from decimal import Decimal as D, getcontext
import json, subprocess, sys, re
getcontext().prec=36
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
price=D('354.72'); shares=D('3949547394'); sm=shares/D(1000000)
mcap=price*sm
annual={
 '2021':[53823,13606,6523,5519,11497,6514,17707],
 '2022':[81462,20853,13656,12556,14724,7163,22185],
 '2023':[96773,17660,8891,14997,13256,8899,29094],
 '2024':[97690,17450,7076,7091,14923,11342,36563],
 '2025':[94827,17094,4355,3794,14747,8527,44059]}
# Quarter arrays: auto, energy, services, total, gross profit, EBIT, NI, CFO, capex,
# auto cost, energy cost, service cost.
quarters={
 '2025Q3':[21205,3415,3475,28095,5054,1624,1373,6238,2248,17590,2342,3109],
 '2025Q4':[17693,3837,3371,24901,5009,1409,840,3813,2393,14080,2739,3073],
 '2026Q1':[16234,2408,3745,22387,4720,941,477,3937,2493,12812,1456,3399],
 '2026Q2':[20516,3139,4581,28236,4751,398,1114,4697,5789,17053,2499,3933]}
metrics={'price':price,'shares':shares,'market_cap_m':mcap,
 'net_cash_ex_operating_leases_m':D(43524)-D(9342),
 'net_cash_including_leases_m':D(43524)-D(16080),
 'pe_current_shares':mcap/D(3804),'pe_diluted_eps':price/D('1.08'),
 'ps':mcap/D(103619),'ev_sales':(mcap-D(27444))/D(103619),
 'fcf_yield_percent':D(5762)/mcap*100,'pb':mcap/D(86858),
 'musk_voting_total_percent':D(699580882)/shares*100,
 'musk_award_inclusive_percent':D(1123324786)/shares*100,
 'q3_delivery_yoy_percent':(D(486532)/D(497099)-1)*100,
 'q2_auto_yoy_percent':(D(20516)/D(16661)-1)*100,
 'q2_energy_yoy_percent':(D(3139)/D(2789)-1)*100,
 'q2_services_yoy_percent':(D(4581)/D(3046)-1)*100}
scenarios=[]
for label,profit,pe,g,p in [('悲观',5000,25,D('.01'),D('.35')),('基准',15000,45,D('.025'),D('.45')),('乐观',35000,70,D('.04'),D('.20'))]:
 growth=(D(profit)/D(3804))**(D(1)/3)-1
 target=D(profit)*pe/sm
 scenarios.append(dict(label=label,profit2029_m=D(profit),pe3=D(pe),growth=growth,target2029=target,pv3=target/D('1.1')**3,prob=p,g=g))
long=[]
profit_components=[[(100,'.03'),(40,'.10'),(3,'.30'),(0,'.20'),(-1.9,'1')],[(180,'.06'),(100,'.12'),(40,'.35'),(10,'.20'),(-3.8,'1')],[(300,'.08'),(180,'.15'),(150,'.40'),(80,'.20'),(-7,'1')]]
profit2036=[sum(D(str(a))*D(b) for a,b in row)*1000 for row in profit_components]
for row,profit in zip(scenarios,profit2036):
 g=row['g']; pe=(1-g/D('.20'))/(D('.10')-g)
 irr=((D(profit)*pe/mcap)**(D(1)/10)-1-D('.01'))*100
 long.append(dict(label=row['label'],profit2036_m=D(profit),g=g,pe=pe,irr_percent=irr,prob=row['prob']))
# Equity reverse DCF: E0 4bn, 50% cash distribution, Gordon PE, no surplus cash added.
pebase=(1-D('.025')/D('.20'))/(D('.1')-D('.025'))
def reverse_pv(h):
 return sum(D(4000)*(1+h)**t*D('.5')/D('1.1')**t for t in range(1,11))+D(4000)*(1+h)**10*pebase/D('1.1')**10
lo,hi=D(0),D(1)
for _ in range(180):
 mid=(lo+hi)/2
 if reverse_pv(mid)>mcap:hi=mid
 else:lo=mid
metrics['reverse_growth_percent']=(lo+hi)/2*100
metrics['reverse_terminal_profit_m']=D(4000)*(1+(lo+hi)/2)**10
metrics['required_terminal_profit_no_distribution_m']=mcap*(D('1.11')**10)/pebase
metrics['prob_weighted_pv3']=sum(x['pv3']*x['prob'] for x in scenarios)
metrics['prob_weighted_irr']=sum(x['irr_percent']*x['prob'] for x in long)
metrics['buy_threshold_25pct_safety']=scenarios[1]['pv3']*D('.75')
metrics['q2_energy_margin']=D(3139-2499)/3139*100
metrics['q2_services_margin']=D(4581-3933)/4581*100
metrics['q2_auto_margin']=D(20516-17053)/20516*100
metrics['sbc_adjusted_ttm_cash_m']=D(5762)-D(3798)
metrics['pe_standardized_eps_numerator']=mcap/D(3806)
def serial(x):
 if isinstance(x,D):return str(x)
 raise TypeError()
quarter_margins={q:[(D(row[i])-D(row[9+i]))/D(row[i])*100 for i in range(3)] for q,row in quarters.items()}
annual_margins={y:[D(row[i])/D(row[0])*100 for i in [1,2]] for y,row in annual.items()}
out=dict(units='USD million except per share, shares and percentages',annual_columns=['revenue','gross_profit','ebit','net_income_common','cfo','capex','cash_and_short_term_investments'],annual=annual,annual_margins=annual_margins,quarters=quarters,quarter_margins=quarter_margins,profit2036_components_billions=profit_components,metrics=metrics,scenarios3=scenarios,scenarios10=long)
(HERE/'calculations.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=serial)+'\n')
config={'Tesla':dict(roic=.20,g=[.01,.025,.04],p=[.35,.45,.20],irr10=[float(x['irr_percent']) for x in long],k=-.01)}
(HERE/'terminal-config.json').write_text(json.dumps(config,indent=2)+'\n')
logs=[]
def run(tool,*args):
 cmd=[sys.executable,str(ROOT/'tools'/tool),*map(str,args)]
 r=subprocess.run(cmd,capture_output=True,text=True)
 logs.append('$ '+' '.join(cmd[1:])+'\n'+re.sub(r'\x1b\[[0-9;]*m','',r.stdout+r.stderr)+'\nexit='+str(r.returncode))
 return r
run('financial_rigor.py','verify-market-cap','--price',price,'--shares',shares,'--reported',1400983000000,'--currency','USD')
for field,a,b in [('FY2025 revenue',94827,94827),('FY2025 NI common',3794,3794),('FY2025 cash+ST',44059,44059),('Q2 cash+ST',43524,43524),('TTM NI common vs EPS numerator',3804,3806),('shares SEC vs SA rounded',3949547394,3950000000),('debt including leases reconciled',16080,16080)]:
 run('financial_rigor.py','cross-validate','--field',field,'--values',json.dumps({'SEC/Tesla':a,'StockAnalysis':b}),'--unit','USD_m_or_shares')
# Material differences are intentionally retained, not silently relabeled as agreement.
run('financial_rigor.py','cross-validate','--field','FY2024 EBIT official vs standardized','--values',json.dumps({'SEC':7076,'StockAnalysis':7659}),'--unit','USD_m')
run('financial_rigor.py','cross-validate','--field','2025Q3 EBIT official vs standardized','--values',json.dumps({'Tesla':1624,'StockAnalysis':1862}),'--unit','USD_m')
run('financial_rigor.py','verify-valuation','--price',price,'--eps',D(3804)/sm,'--bvps',D(86858)/sm,'--fcf-per-share',D(5762)/sm,'--dividend',0)
run('financial_rigor.py','three-scenario','--price',price,'--eps',D(3804)/sm,'--shares',shares/D(100000000),'--growth',*[x['growth'] for x in scenarios[::-1]],'--pe',70,45,25,'--years',3,'--currency','USD')
audit=['audit','--currency','USD','--r','.10','--roic','.20','--g','.01,.025,.04','--rf','.051','--beta','1','--discrete-risks','自动驾驶禁运或停运:情景,严重事故赔偿:未建模,关联交易价值转移:未建模']
assert run('terminal_value.py',*audit).returncode==0
for x in long:
 run('terminal_value.py','pe','--roic','.20','--g',x['g'],'--r','.10')
 run('terminal_value.py','irr','--profit',x['profit2036_m'],'--mcap',mcap,'--pe',x['pe'],'--years',10,'--payout','-.01')
for delta in ['.02','.01']:
 run('terminal_value.py','flip','--config',HERE/'terminal-config.json','--name','Tesla','--r','.10','--delta',delta,'--currency','USD','--g-shift',0,'--rf','.051')
run('terminal_value.py',*audit)
(HERE/'validation-log.txt').write_text('\n\n'.join(logs)+'\n')
print(json.dumps(metrics,ensure_ascii=False,indent=2,default=serial))
print(json.dumps(scenarios,ensure_ascii=False,indent=2,default=serial))
print(json.dumps(long,ensure_ascii=False,indent=2,default=serial))
