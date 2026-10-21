from pathlib import Path
import json, subprocess, math, sys
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
annual={
'2021':[365817,94680,152836,108949,104038,11085,190516],
'2022':[394328,99803,170782,119437,122151,10708,169109],
'2023':[383285,96995,169148,114301,110543,10959,162099],
'2024':[391035,93736,180683,123216,118254,9447,156650],
'2025':[416161,112010,195201,133050,111482,12715,132420]}
quarters={
'FY25Q4':{'sales':[49025,8726,6952,9013,28750],'prior':[46222,7744,6950,9042,24972],'cost':[47019,7106],'regions':[44192,28703,14493,6636,8442]},
'FY26Q1':{'sales':[85269,8386,8595,11493,30013],'prior':[69138,8987,8088,11747,26340],'cost':[67478,7047],'regions':[58529,38146,25526,9413,12142]},
'FY26Q2':{'sales':[56994,8399,6914,7901,30976],'prior':[46841,7949,6402,7522,26645],'cost':[49179,7224],'regions':[45093,28055,20497,8401,9138]},
'FY26Q3':{'sales':[54252,10352,6191,7883,30739],'prior':[44582,8046,6581,7404,27423],'cost':[47153,7494],'regions':[45781,29395,18816,6554,8871]}}
price=D('343.46'); shares=D('14.59418'); mcap=price*shares
ni=D('128.930'); normalized=ni-D('.11')*D('14.714676'); eps=D('8.61')
cash=D('39.544')+D('22.855')+D('84.118'); debt=D('1.997')+D('11.007')+D('71.340'); net=cash-debt
fcf=D('136.683'); revenue=D('466.823')
data={'unit':'USD million except share/market-cap variables explicitly USD billion','price':str(price),'shares_billion':str(shares),'marketcap_billion':str(mcap),'annual':annual,'annual_columns':['revenue','net_income','gross_profit','operating_profit','cfo','capex','cash_all_marketable'],'quarters':quarters,'quarter_categories':['iPhone','Mac','iPad','Wearables','Services'],'quarter_regions':['Americas','Europe','Greater China','Japan','Rest APAC'],'cash_billion':str(cash),'debt_billion':str(debt),'netcash_billion':str(net),'normalized_profit_billion':str(normalized),'normalized_eps':str(eps)}
# TTM bridge in USD million: prior full fiscal year + current first nine months - prior first nine months.
bridge={'unit':'USD million','formula':'FY2025 full year + FY2026 first 9 months - FY2025 first 9 months','periods':{'FY2025_full_year_end':'2025-09-27','FY2026_9m_end':'2026-06-27','FY2025_9m_end':'2025-06-28'},'inputs':{'revenue':[416161,364357,313695],'net_income':[112010,101464,84544],'operating_cash_flow':[111482,116996,81754],'cash_capex':[12715,6799,9473]},'sources':{'full_year':'https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm','nine_month_comparison':'https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/aapl-20260627.htm','third_party_ttm':'https://stockanalysis.com/stocks/aapl/financials/','retrieved':'2026-10-19 Asia/Shanghai'}}
bridge['ttm_result']={key:v[0]+v[1]-v[2] for key,v in bridge['inputs'].items()}
bridge['ttm_result']['free_cash_flow']=bridge['ttm_result']['operating_cash_flow']-bridge['ttm_result']['cash_capex']
bridge['third_party_ttm_values']={'revenue':466823,'net_income':128930,'operating_cash_flow':146724,'cash_capex':10041,'free_cash_flow':136683}
assert bridge['ttm_result']==bridge['third_party_ttm_values']
data['ttm_bridge']=bridge
(OUT/'ttm_bridge.json').write_text(json.dumps(bridge,ensure_ascii=False,indent=2))
(OUT/'source_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
logs=[]
def run(tool,*args):
 p=subprocess.run([sys.executable,str(ROOT/'tools'/tool),*map(str,args)],capture_output=True,text=True);logs.append('$ '+tool+' '+' '.join(map(str,args))+'\n'+p.stdout+p.stderr+'\nexit='+str(p.returncode)); return p.stdout
run('financial_rigor.py','verify-market-cap','--price',price,'--shares',shares*D(10)**9,'--reported','5010000000000','--currency','USD')
for field,vals,unit in [('FY25 revenue',{'Apple10K':416161,'StockAnalysis':416161,'Macrotrends_search':416161},'USD_million'),('FY25 net income',{'Apple10K':112010,'StockAnalysis':112010,'Macrotrends_search':112010},'USD_million'),('FY25 cash short term',{'Apple10K':54697,'Macrotrends':54697},'USD_million'),('FY26Q3 cash all securities',{'ApplePDF':146517,'StockAnalysis':146517},'USD_million'),('shares',{'SEC_July17':14594180000,'StockAnalysis_rounded':14590000000},'shares'),('FY26Q3 debt',{'ApplePDF':84344,'StockAnalysis':84344},'USD_million')]:
 run('financial_rigor.py','cross-validate','--field',field,'--values',json.dumps(vals),'--unit',unit)
run('financial_rigor.py','verify-valuation','--price',price,'--eps','8.72','--bvps',D('107.520')/shares,'--fcf-per-share',fcf/shares,'--dividend','1.08','--revenue-per-share',revenue/shares)
run('financial_rigor.py','three-scenario','--price',price,'--eps',eps,'--shares',shares*10,'--growth','.14','.08','-.02','--pe','34','28','22','--years','3','--currency','USD')
risks='台海供应中断:尾部档,佣金监管:情景,AI入口替代:情景,网络安全:未建模'
run('terminal_value.py','audit','--currency','USD','--r','.10','--roic','.25','--g','.01,.025,.04','--rf','.051','--beta','1.0','--discrete-risks',risks)
scenarios=[]
for name,gr,g,p in [('悲观',0,.01,.3),('基准',.07,.025,.5),('乐观',.11,.04,.2)]:
 profit=float(normalized)*(1+gr)**10; pe=(1-g/.25)/(.10-g); irr=(profit*pe/float(mcap))**.1-1+.02
 run('terminal_value.py','pe','--roic','.25','--g',g,'--r','.10')
 run('terminal_value.py','irr','--profit',profit,'--mcap',mcap,'--pe',pe,'--years','10','--payout','.02')
 scenarios.append(dict(name=name,growth=gr,g=g,p=p,profit=profit,pe=pe,irr=irr*100))
config={'苹果':{'roic':.25,'g':[s['g'] for s in scenarios],'p':[s['p'] for s in scenarios],'irr10':[s['irr'] for s in scenarios],'k':.02}}
(OUT/'terminal_config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2))
for delta in [.02,.01]:run('terminal_value.py','flip','--config',OUT/'terminal_config.json','--name','苹果','--r','.10','--delta',delta,'--currency','USD','--g-shift','0','--rf','.051')
# reverse equity DCF: normalized owner cash flow CFO-capex-SBC proxy, no extra net cash added
# net income starting point 127.31b conservative vs 136.683b FCF; no repurchase double counting.
def dcf(gr,base=120.,r=.1,g=.03):
 return sum(base*(1+gr)**t/(1+r)**t for t in range(1,11))+base*(1+gr)**10*(1+g)/(r-g)/(1+r)**10
lo,hi=-.1,.4
for _ in range(150):
 mid=(lo+hi)/2
 if dcf(mid)<float(mcap):lo=mid
 else:hi=mid
results={'mcap':float(mcap),'pe_price_eps':float(price/D('8.72')),'pe_mcap_netincome':float(mcap/ni),'ps':float(mcap/revenue),'ev_sales':float((mcap-net)/revenue),'fcf_yield':float(fcf/mcap*100),'normalized_profit':float(normalized),'scenarios10':scenarios,'reverse_dcf_growth':mid,'reverse_dcf_base_fcf':120,'reverse_dcf_r':.1,'reverse_dcf_g':.03,'reverse_dcf_no_extra_netcash':True,'three_year':[{'name':n,'eps3':float(eps)*(1+gr)**3,'pe':pe,'future_price':float(eps)*(1+gr)**3*pe,'present_value':float(eps)*(1+gr)**3*pe/1.1**3,'cagr':(float(eps)*(1+gr)**3*pe/float(price))**(1/3)-1} for n,gr,pe in [('悲观',-.02,22),('基准',.08,28),('乐观',.14,34)]]}
results['strict_shortterm_netcash_billion']=float(D('39.544')+D('22.855')-debt)
results['ai_profit_bridge_billion']={'gross_low':20*.25,'gross_high':40*.35,'net_low':20*.25-10,'net_high':40*.35-5}
results['cashflow_dcf_sensitivity']={str(b):None for b in [110,120,130]}
for b in [110,120,130]:
 l,h=-.1,.4
 for _ in range(150):
  m=(l+h)/2
  if dcf(m,b)<float(mcap):l=m
  else:h=m
 results['cashflow_dcf_sensitivity'][str(b)]=m
(OUT/'calculations.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
(OUT/'financial_audit.log').write_text('\n\n'.join(logs))
print(json.dumps(results,ensure_ascii=False,indent=2))
