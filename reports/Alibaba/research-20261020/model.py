"""Alibaba, cutoff 2026-10-20. All amount units RMB 100m; price HKD.
Conditional analyst model, not reported FCFF or a prediction. No network.
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json, subprocess, sys
getcontext().prec=40
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
P=D('108.80'); S=D('199.01959514'); FX=D('.8525')
# Revenue, attributable ordinary net income, reported operating income,
# cost of revenue, CFO, purchases of PPE. All source RMB millions / 100.
raw={
'FY2022':[853062,61959,69638,539450,142759,53309],
'FY2023':[868687,72509,100351,549695,199752,34330],
'FY2024':[941168,79741,113350,586323,182593,32087],
'FY2025':[996347,129470,140905,598285,163509,85972],
'FY2026':[1023670,105904,50150,616136,76213,126063],
'2026June':[268953,10537,15161,166096,22945,67678]}
history={}
for k,v in raw.items():
 r,n,o,c,cf,cap=[D(x)/100 for x in v]
 history[k]=dict(revenue=r,ordinary_net=n,operating_income=o,gross_margin=(1-c/r)*100,operating_margin=o/r*100,net_margin=n/r*100,cfo=cf,capex=cap,simple_fcf=cf-cap)
metrics=dict(price=P,shares_100m=S,hkd_cny=FX,cap_hkd=P*S,cap_cny=P*S*FX,
 ttm_revenue=D(1023670+268953-247652)/100,ttm_net=D(105904+10537-43116)/100,
 ttm_op=D(50150+15161-34988)/100,ttm_cfo=D(76213+22945-20672)/100,
 ttm_capex=D(126063+67678-38676)/100,ttm_company_fcf=D(-46609-44670+18815)/100)
metrics['ttm_simple_fcf']=metrics['ttm_cfo']-metrics['ttm_capex']
metrics['pe']=metrics['cap_cny']/metrics['ttm_net'];metrics['ps']=metrics['cap_cny']/metrics['ttm_revenue']
metrics['pb_june']=metrics['cap_cny']/D('10490.38')
metrics['ttm_op_margin']=metrics['ttm_op']/metrics['ttm_revenue']*100
metrics['new_shares_pct']=D('710000000')/D('19174988918')*100
metrics['fcf_june_margin']=D('-446.70')/D('2689.53')*100
metrics['cloud_margin']=D('56.28')/D('484.37')*100
# Consolidated FCFF excludes investment income. Leases remain operating expense.
# Bridge includes minority/mezzanine claims; convertible debt remains debt, not also shares.
bridge=dict(june_liquid=D('4745.05'),placing_net_hkd=D('797'),placing_cny=D('797')*FX,
 july_to_cutoff_cash_change_assumption=D('-400'),operating_cash_reserve_assumption=D('-1000'),
 debt=-D(30614+56007+115716+54905+9288)/100,
 nonliquid_strategic_value_assumption=D('2000'),minority=-D('572.72'),mezzanine=-D('75.84'))
bridge['total']=sum(bridge[k] for k in ['june_liquid','placing_cny','july_to_cutoff_cash_change_assumption','operating_cash_reserve_assumption','debt','nonliquid_strategic_value_assumption','minority','mezzanine'])
# Nonliquid investment book pool: remove treasury instruments already in liquid total.
metrics['treasury_investments']=D('4745.05')-D('1429.14')-D('1546.53')
metrics['nonliquid_investment_book_pool']=D('881.30')+D('3430.18')+D('2032.07')-metrics['treasury_investments']
def value(flows,r,tg,b=bridge['total']):
 explicit=sum(f/(1+r)**t for t,f in enumerate(flows,1))
 terminal=flows[-1]*(1+tg)/(r-tg)/(1+r)**len(flows)
 ev=explicit+terminal
 return dict(explicit_pv=explicit,terminal_pv=terminal,enterprise_value=ev,equity_value=ev+b,price=(ev+b)/S/FX,terminal_share=terminal/ev*100)
scenarios={}
for name,flow,tg,profits,pe,div in [
('悲观',[-900,-700,-300,0,300,450,550,650,750,850],'.01',[300,600,1000],14,600),
('基准',[-500,-100,500,900,1300,1500,1650,1800,1950,2100],'.025',[750,1400,2400],22,1000),
('乐观',[-300,300,1000,1600,2200,2600,3000,3400,3800,4200],'.03',[1300,2300,4500],28,1500)]:
 flows=list(map(D,flow));a=value(flows,D('.095'),D(tg));p3,p5,p10=map(D,profits)
 exitprice=p5*D(pe)/S/FX;divprice=D(div)/S/FX
 a.update(dict(flows=flows,wacc=D('.095'),terminal_growth=D(tg),profit3=p3,profit5=p5,profit10=p10,pe5=pe,dividend_total5=D(div),exit_price5=exitprice,dividend_per_share5=divprice,wealth5=(exitprice+divprice)/P,cagr5=((exitprice+divprice)/P)**D('.2')-1))
 scenarios[name]=a
base=scenarios['基准']['flows'];sensitivity={f'{r}/{tg}':value(base,D(r),D(tg))['price'] for r in ['.085','.095','.105'] for tg in ['.015','.025','.035']}
# Solve uniform scale of positive base flows, keeping first two negative cash flows fixed.
lo,hi=D(0),D(5)
for _ in range(150):
 mid=(lo+hi)/2;f=[x*mid if x>0 else x for x in base]
 if value(f,D('.095'),D('.025'))['price']>P:hi=mid
 else:lo=mid
scale=(hi+lo)/2
checks=[('股价','108.80','108.80','HKD','StockAnalysis','Webull'),('股本','19901959514','19900000000','shares','HKEX September monthly','Webull rounded'),('FY2026收入','1023670','1023670','RMBm','FY2026 annual','S&P StockAnalysis'),('FY2026归普净利','105904','105904','RMBm','FY2026 annual','S&P StockAnalysis'),('FY2026经营现金流','76213','76213','RMBm','FY2026 annual','S&P StockAnalysis'),('FY2026资本开支','126063','126063','RMBm','FY2026 annual','S&P StockAnalysis'),('六月季度收入','268953','269000','RMBm','June results','AP rounded'),('六月季度净利','10537','10500','RMBm','June results','AP rounded'),('六月云收入','48437','48400','RMBm','June results','AP rounded'),('六月资本开支','67678','67700','RMBm','June results','AP rounded'),('TTM简单FCF','-76579','-76579','RMBm','filing bridge','S&P StockAnalysis'),('六月现金等价物','142914','142914','RMBm','June results','S&P balance sheet'),('六月有息债务','266530','266530','RMBm','June results five lines','S&P balance sheet'),('六月普通股权益','1049038','1049038','RMBm','June results','S&P balance sheet'),('HKD/CNY','.8525','.8520','CNY/HKD','exchangerates','Investing')]
logs=[]
def run(a):
 p=subprocess.run([sys.executable,str(ROOT/'tools/financial_rigor.py')]+a,capture_output=True,text=True,check=True);logs.append(p.stdout)
run(['verify-market-cap','--price',str(P),'--shares',str(S*10**8),'--reported','2165333000000','--currency','HKD'])
for field,a,b,u,sa,sb in checks:run(['cross-validate','--field',field,'--values',json.dumps({sa:float(a),sb:float(b)}),'--unit',u,'--tolerance','1'])
run(['verify-valuation','--price',str(P),'--eps',str(metrics['ttm_net']/S/FX),'--bvps',str(D('10490.38')/S/FX),'--fcf-per-share',str(metrics['ttm_simple_fcf']/S/FX)])
# Generic CLI scenario excludes dividends and is a crosscheck of our exit-price arithmetic only.
growth=[(D(n)/D('733.25'))**D('.2')-1 for n in [2300,1400,600]]
run(['three-scenario','--price',str(P),'--eps',str(D('733.25')/S/FX),'--shares',str(S),'--growth',*[str(x) for x in growth],'--pe','28','22','14','--years','5','--currency','HKD'])
fcff_bridges={k:dict(ebit=D(e),tax=D('.25'),da=D(da),capex=D(cap),delta_nwc=D(wc),fcff=D(e)*D('.75')+D(da)-D(cap)-D(wc)) for k,e,da,cap,wc in [('bear5',1000,800,1200,50),('base5',2000,1000,1100,100),('bull5',3600,1400,1700,200),('base10',3200,1600,1700,200)]}
assert [fcff_bridges[k]['fcff'] for k in ['bear5','base5','bull5','base10']]==[D(300),D(1300),D(2200),D(2100)]
out=dict(fcff_operating_bridges=fcff_bridges,cutoff='2026-10-20',units='RMB 100m; prices HKD; share count 100m',history=history,metrics=metrics,bridge=bridge,scenarios=scenarios,sensitivity=sensitivity,reverse_positive_cashflow_scale=scale,reverse_year5_fcff=D(1300)*scale,reverse_year10_fcff=D(2100)*scale,crosschecks=checks)
(OUT/'model-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str)+'\n')
(OUT/'financial-rigor-output.txt').write_text('\n'.join(logs))
for k in ['history','metrics','bridge','scenarios','sensitivity','reverse_year5_fcff','reverse_year10_fcff']:print(k,json.dumps(out[k],ensure_ascii=False,default=lambda x:str(round(x,4)) if isinstance(x,D) else str(x)))
