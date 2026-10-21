#!/usr/bin/env python3
"""AMZN research reproducibility. USD billions except prices/shares explicitly labelled.
Run from any directory; no network, no undocumented data fetch. Source values were
read on 2026-10-19 from the URLs in source-data.json and the report.
"""
from pathlib import Path
from decimal import Decimal as D, getcontext
import json, subprocess, sys
getcontext().prec=32
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
data={
 'retrieval_date':'2026-10-19 Asia/Shanghai',
 'price_date':'2026-10-16 US close','price':250,
 'shares_asof':'2026-07-22','shares':10786313572,
 'annual':{
 '2021':{'revenue':469822,'net_income':33364,'gross_profit':197478,'operating_income':24879,'ocf':46327,'capex_gross':61053,'asset_sales':5657,'cash_and_securities':96049},
 '2022':{'revenue':513983,'net_income':-2722,'gross_profit':225152,'operating_income':13348,'ocf':46752,'capex_gross':63645,'asset_sales':5324,'cash_and_securities':70026},
 '2023':{'revenue':574785,'net_income':30425,'gross_profit':270046,'operating_income':36852,'ocf':84946,'capex_gross':52729,'asset_sales':4596,'cash_and_securities':86780},
 '2024':{'revenue':637959,'net_income':59248,'gross_profit':311671,'operating_income':68593,'ocf':115877,'capex_gross':82999,'asset_sales':5341,'cash_and_securities':101202},
 '2025':{'revenue':716924,'net_income':77670,'gross_profit':360510,'operating_income':79975,'ocf':139514,'capex_gross':131819,'asset_sales':3499,'cash_and_securities':123029}},
 'annual_unit':'USD million',
 'quarters':{
 '2025Q3':{'NA':[106267,4789,11],'International':[40896,1199,10],'AWS':[33006,11434,20]},
 '2025Q4':{'NA':[127083,11472,10],'International':[50724,1040,11],'AWS':[35579,12465,24]},
 '2026Q1':{'NA':[104143,8267,12],'International':[39789,1424,11],'AWS':[37587,14161,28]},
 '2026Q2':{'NA':[116177,9123,16],'International':[42197,1717,15],'AWS':[42232,16621,37]}},
 'quarter_units':['revenue USD million','operating_income USD million','FX-neutral YoY % rounded by issuer'],
 'ttm':{'revenue':775680,'net_income':135281,'operating_income':93712,'ocf':161403,'capex_net':169007,'fcf':-7604,'eps':12.44},
 'balance_20260630':{'cash':78213,'marketable_securities':44775,'long_term_debt':128894,'current_long_term_debt':3330,'short_term_debt':325,'third_party_debt_including_leases_and_financing':251635,'equity':551620},
 'sources':{
 'annual_primary':'https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm',
 'older_primary':'https://www.sec.gov/Archives/edgar/data/1018724/000101872424000008/amzn-20231231.htm',
 'fy2021_balance_primary':'https://www.sec.gov/Archives/edgar/data/1018724/000101872422000005/R7.htm',
 'quarter_primary':'https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Second-Quarter-Results/default.aspx',
 'quarter_filing':'https://www.sec.gov/Archives/edgar/data/1018724/000101872426000026/amzn-20260630.htm',
 'income_secondary':'https://stockanalysis.com/stocks/amzn/financials/',
 'cashflow_secondary':'https://stockanalysis.com/stocks/amzn/financials/cash-flow-statement/',
 'balance_secondary':'https://stockanalysis.com/stocks/amzn/financials/balance-sheet/',
 'quote_secondary':'https://stockanalysis.com/stocks/amzn/statistics/',
 'price_second_source':'https://finance.yahoo.co.jp/quote/AMZN/history',
 'macrotrends_revenue':'https://www.macrotrends.net/stocks/charts/AMZN/amazon/revenue/Amazon',
 'macrotrends_income':'https://www.macrotrends.net/stocks/charts/AMZN/amazon/net-income/'},
 'gaps':['Macrotrends body HTTP403: only FY2025 revenue and profit search extracts corroborated; not a complete independent five-year read.', 'Quarter segment values issuer source only; no claim of independent quarterly double verification.', 'Current exact shares unknown: latest 10-Q cover as of July22 used; third-party rounded 10.79bn agrees.', 'Management ownership SEC proxy snapshot; no second independent full voting/economic reconciliation.']
}
(HERE/'source-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
price=D('250'); shares=D(str(data['shares'])); sb=shares/D(10**9); mcap=price*sb
normal=D('93.712')*D('.8'); eps=normal/sb
res={'mcap_bn':float(mcap),'normal_profit_bn':float(normal),'normal_eps':float(eps),
 'gaap_pe':float(price/D('12.44')),'normal_pe':float(mcap/normal),'ps':float(mcap/D('775.680')),
 'net_cash_no_leases_bn':float(D('122.988')-D('128.894')-D('3.330')-D('.325')),
 'net_cash_with_leases_bn':float(D('122.988')-D('251.635')),
 'ev_sales_no_leases':float((mcap+D('9.561'))/D('775.680')),
 'ev_sales_with_leases':float((mcap+D('128.647'))/D('775.680')),
 'annual_derived':{y:{'gross_margin':v['gross_profit']/v['revenue']*100,'op_margin':v['operating_income']/v['revenue']*100,'fcf_company':v['ocf']-v['capex_gross']+v['asset_sales'],'fcf_gross':v['ocf']-v['capex_gross']} for y,v in data['annual'].items()},
 'bezos_beneficial_pct':950434581/10751236247*100,'bezos_economic_proxy_pct':(950434581-68232131)/10751236247*100,'jassy_pct':2313536/10751236247*100}
scenarios=[]
for name,growth,pe,p in [('悲观','.08','22','.25'),('基准','.20','30','.50'),('乐观','.28','36','.25')]:
 profit=normal*(1+D(growth))**3; future_shares=sb*D('1.008')**3; target=profit/future_shares*D(pe); pv=target/D('1.1')**3
 scenarios.append({'name':name,'growth':float(growth),'eps_growth':float((1+D(growth))/D('1.008')-1),'pe':float(pe),'probability':float(p),'profit_bn':float(profit),'eps':float(profit/future_shares),'target':float(target),'pv':float(pv),'annual_return':float((target/price)**(D(1)/D(3))-1)})
res['three_year']=scenarios
res['three_year_weighted_pv']=sum(v['pv']*v['probability'] for v in scenarios)
res['three_year_margin20_price']=res['three_year_weighted_pv']*.8
roic=.18; gs=[.015,.03,.04]; profits=[125,300,550]; probs=[.25,.50,.25]; k=-.008
pes=[(1-g/roic)/(.1-g) for g in gs]
irrs=[((p*pe/float(mcap))**.1-1+k)*100 for p,pe in zip(profits,pes)]
res['ten_year']=[dict(name=n,profit_bn=p,g=g,pe=pe,irr=ir,profit_cagr=(p/float(normal))**.1-1) for n,p,g,pe,ir in zip(['悲观','基准','乐观'],profits,gs,pes,irrs)]
res['sensitivity']={str(r):{'irrs':[((p*((1-g/roic)/(r-g))/float(mcap))**.1-1+k)*100 for p,g in zip(profits,gs)]} for r in [.08,.09,.10,.11,.12]}
for r,v in res['sensitivity'].items():v['weighted_irr']=sum(p*x for p,x in zip(probs,v['irrs']));v['covers_r']=v['weighted_irr']>=float(r)*100
# Reverse DCF: normalized profit growth h; explicit cash conversion path,
# terminal PE from Gordon formula. This is a conditional requirement, not fact.
conversion=[-.10,.10,.25,.40,.50,.60,.70,.75,.80,.8333333333333333]
def dcf(h):
 earnings=[float(normal)*(1+h)**t for t in range(1,11)]
 cfs=[e*c/(1.008**t) for t,(e,c) in enumerate(zip(earnings,conversion),1)]
 tv=earnings[-1]*pes[1]/1.008**10
 return sum(cf/1.1**t for t,cf in enumerate(cfs,1))+tv/1.1**10
lo,hi=0.,.5
for _ in range(100):
 mid=(lo+hi)/2
 if dcf(mid)<float(mcap):lo=mid
 else:hi=mid
h=(lo+hi)/2
res['reverse_dcf']={'h':h,'terminal_profit':float(normal)*(1+h)**10,'equity_value':dcf(h),'cash_conversion_path':conversion,'r':.10,'g':.03,'roic':.18,'annual_dilution':.008,'valuation_at_15pct_growth':dcf(.15)}
(HERE/'model-results.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
config={'亚马逊':{'roic':roic,'g':gs,'p':probs,'irr10':irrs,'k':k}}
(HERE/'terminal-config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
commands=[]
def cmd(script,*args): commands.append([sys.executable,str(ROOT/'tools'/script),*map(str,args)])
cmd('financial_rigor.py','verify-market-cap','--price',250,'--shares',shares,'--reported',2700000000000,'--currency','USD')
for f,values,u in [('FY2025 revenue',{'SEC':716924,'StockAnalysis':716924,'Macrotrends_search_extract':716924},'USD million'),('FY2025 net income',{'SEC':77670,'StockAnalysis':77670,'Macrotrends_search_extract':77670},'USD million'),('June2026 cash and securities',{'SEC':122988,'StockAnalysis':122988},'USD million'),('Shares',{'SEC_20260722':10786313572,'StockAnalysis_rounded':10790000000},'shares')]:cmd('financial_rigor.py','cross-validate','--field',f,'--values',json.dumps(values),'--unit',u)
cmd('financial_rigor.py','verify-valuation','--price',250,'--eps',12.44,'--bvps',D('551.620')/sb,'--fcf-per-share',D('-7.604')/sb,'--dividend',0,'--revenue-per-share',D('775.680')/sb)
cmd('financial_rigor.py','verify-valuation','--price',250,'--eps',eps)
cmd('financial_rigor.py','three-scenario','--price',250,'--eps',eps,'--shares',shares/D(10**8),'--growth',D('1.28')/D('1.008')-1,D('1.20')/D('1.008')-1,D('1.08')/D('1.008')-1,'--pe',36,30,22,'--years',3,'--currency','USD')
audit=['audit','--currency','USD','--r',.10,'--roic',.18,'--g','.015,.03,.04','--rf',.0509,'--beta',1.0,'--discrete-risks','AI过剩:情景,广告监管:情景,系统性网络攻击:未建模,战争供应链:未建模']
cmd('terminal_value.py',*audit)
for p,g,pe in zip(profits,gs,pes):
 cmd('terminal_value.py','pe','--roic',roic,'--g',g,'--r',.10)
 cmd('terminal_value.py','irr','--profit',p,'--mcap',mcap,'--pe',pe,'--years',10,'--payout',k)
for delta in [.02,.01]:cmd('terminal_value.py','flip','--config',HERE/'terminal-config.json','--name','亚马逊','--r',.10,'--delta',delta,'--currency','USD','--g-shift',0,'--rf',.0509)
cmd('terminal_value.py',*audit)
log=[]
for c in commands:
 p=subprocess.run(c,capture_output=True,text=True)
 log.extend(['$ '+' '.join(c),p.stdout,p.stderr,f'EXIT={p.returncode}\n'])
 if p.returncode: print('Command nonzero:',c,p.returncode)
(HERE/'financial-audit.log').write_text('\n'.join(log))
print(json.dumps(res,ensure_ascii=False,indent=2))
