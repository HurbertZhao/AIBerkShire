#!/usr/bin/env python3
"""Reproducible Meta snapshot/model. Run from any directory. All dollars in USD millions unless noted."""
from pathlib import Path
from decimal import Decimal as D
import json, subprocess, math
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
data={
 'as_of':'2026-10-19 Asia/Shanghai','quote_date':'2026-10-16','price':709.33,
 'class_a':2205128509,'class_b':342377716,'shares_date':'2026-07-24',
 'revenue':[117929,116609,134902,164501,200966],
 'net_income':[39370,23200,39098,62360,60458],
 'cor':[22649,25249,25959,30161,36175],
 'operating_income':[46753,28944,46751,69380,83276],
 'ocf':[57683,50475,71113,91328,115800],
 'fcf_company':[38439,18439,43010,52103,43585],
 'fcf_third_party':[38993,19289,44068,54072,46109],
 'cash_marketable':[47998,40738,65403,77815,81592],
 'ttm_revenue':228247,'ttm_net_income':68098,'ttm_eps':26.54,
 'ttm_fcf_company':43585+13170-18883,
 'cash':90260,'bonds':83664,'debt_including_leases':112318,'equity':261221,
 'normalization':{'q3_2025_tax_eps_addback':6.20,'q1_2026_tax_eps_remove':3.13},
 'q':{'2025Q3':[51242,50772,470,24967,-4432,40319,270],
      '2025Q4':[59893,58938,955,30766,-6021,47302,1083],
      '2026Q1':[56311,55909,402,26900,-4028,41902,412],
      '2026Q2':[60801,60370,431,23394,-4619,47146,370]},
 'model_assumptions':{'eps_growth_bear_base_bull':[-.03,.12,.20],'pe3':[18,24,28],
 'revenue2036':[320000,650000,1000000],'net_margin2036':[.20,.32,.36],
 'r':.10,'rf_assumption':.045,'beta':1,'erp_assumption':.055,'roic':.20,'g':[.015,.03,.04],'p':[.25,.5,.25],'k':.003}
}
(HERE/'data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
p=D(str(data['price'])); shares=D(data['class_a']+data['class_b']); mc=p*shares/D(1000000)
eps=D(str(data['ttm_eps']))+D('6.20')-D('3.13')
out={'shares':str(shares),'mcap_m':str(mc),'normal_eps':str(eps),
 'PS':float(mc/D(data['ttm_revenue'])),'PE_gaap':float(p/D('26.54')),'PE_normal':float(p/eps),
 'net_cash_bonds_m':data['cash']-data['bonds'],'net_cash_all_m':data['cash']-data['debt_including_leases'],
 'EV_sales_all':float((mc+D(data['debt_including_leases']-data['cash']))/D(data['ttm_revenue'])),
 'fcf_yield_company':float(D(data['ttm_fcf_company'])/mc*100),'quarters':{},'annual':[]}
for i,y in enumerate(range(2021,2026)):
 out['annual'].append({'year':y,'gross_margin':100*(1-data['cor'][i]/data['revenue'][i]),'operating_margin':data['operating_income'][i]/data['revenue'][i]*100})
for q,v in data['q'].items():
 out['quarters'][q]={'foa_growth':(v[1]/v[5]-1)*100,'rl_growth':(v[2]/v[6]-1)*100,'foa_margin':v[3]/v[1]*100,'rl_margin':v[4]/v[2]*100}
a=data['model_assumptions']; out['three_year']=[]; irr=[]
for j,(growth,pe) in enumerate(zip(a['eps_growth_bear_base_bull'],a['pe3'])):
 eps3=float(eps)*(1+growth)**3; price3=eps3*pe
 out['three_year'].append({'eps':eps3,'profit_m':eps3*float(shares)/1e6,'price':price3,'pv10':price3/1.1**3,'cagr':(price3/float(p))**(1/3)-1})
out['ten_year']=[]
for rev,margin,g in zip(a['revenue2036'],a['net_margin2036'],a['g']):
 profit=rev*margin; pe=(1-g/a['roic'])/(a['r']-g); ir=(profit*pe/float(mc))**.1-1+a['k']; irr.append(ir*100)
 out['ten_year'].append({'profit_m':profit,'pe':pe,'irr_pct':ir*100})
# Reverse DCF: equity owner earnings; no debt added twice; equity value target mc.
def pv(fc,growth):
 return sum(fc*(1+growth)**t/1.1**t for t in range(1,11))+fc*(1+growth)**10*1.03/(.1-.03)/1.1**10
out['reverse_dcf']=[]
for fc in [data['ttm_fcf_company'],60000,80000]:
 lo,hi=-.3,.5
 for _ in range(150):
  mid=(lo+hi)/2
  if pv(fc,mid)>float(mc):hi=mid
  else:lo=mid
 out['reverse_dcf'].append({'initial_fcf_m':fc,'required_growth_pct':(lo+hi)/2*100,'pv_m':pv(fc,(lo+hi)/2)})
(HERE/'model-output.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
config={'Meta':{'roic':a['roic'],'g':a['g'],'p':a['p'],'irr10':irr,'k':a['k']}}
(HERE/'terminal-config.json').write_text(json.dumps(config,indent=2))
logs=[]
def run(tool,args):
 cmd=['python3',str(ROOT/'tools'/tool)]+[str(x) for x in args]
 r=subprocess.run(cmd,text=True,capture_output=True)
 logs.append('$ '+' '.join(cmd)+'\n'+r.stdout+r.stderr+'\nEXIT='+str(r.returncode)+'\n')
run('financial_rigor.py',['verify-market-cap','--price',p,'--shares',shares,'--reported',1807000000000,'--currency','USD'])
for field,v1,v2,unit in [('FY2025_Revenue',200966,200966,'USD_m'),('FY2025_NetIncome',60458,60458,'USD_m'),('Q2_Cash',90260,90260,'USD_m'),('TotalShares',int(shares),2550000000,'shares'),('2022_OpIncome_RAW_DIFFERENCE',28944,33555,'USD_m'),('FY2025_FCF_RAW_DIFFERENCE',43585,46109,'USD_m')]:
 run('financial_rigor.py',['cross-validate','--field',field,'--values',json.dumps({'SEC':v1,'StockAnalysis':v2}),'--unit',unit])
run('financial_rigor.py',['verify-valuation','--price',p,'--eps',26.54,'--bvps',D(data['equity'])*D(1000000)/shares,'--fcf-per-share',D(data['ttm_fcf_company'])*D(1000000)/shares,'--dividend',2.10])
run('financial_rigor.py',['three-scenario','--price',p,'--eps',eps,'--shares',shares/D(100000000),'--growth',.20,.12,-.03,'--pe',28,24,18,'--years',3,'--currency','USD'])
audit=['audit','--currency','USD','--r',.10,'--roic',.20,'--g','.015,.03,.04','--rf',.045,'--beta',1,'--discrete-risks','AI资本配置失败:情景,广告份额流失:情景,监管重罚与强制拆分:未建模,数据中心断供:未建模']
run('terminal_value.py',audit)
for row,g in zip(out['ten_year'],a['g']):
 run('terminal_value.py',['pe','--roic',.20,'--g',g,'--r',.10])
 run('terminal_value.py',['irr','--profit',row['profit_m'],'--mcap',mc,'--pe',row['pe'],'--years',10,'--payout',.003])
for delta in [.02,.01]:
 run('terminal_value.py',['flip','--config',HERE/'terminal-config.json','--name','Meta','--r',.10,'--delta',delta,'--currency','USD','--g-shift',0,'--rf',.045])
run('terminal_value.py',audit)
(HERE/'tool-audit.log').write_text('\n'.join(logs))
print(json.dumps(out,ensure_ascii=False,indent=2))
