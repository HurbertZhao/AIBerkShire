"""2026-10-20 Moutai research. RMB 100m unless specified. No network.
Scenarios are analyst assumptions; no probability or empirical guarantee.
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json, subprocess, sys
getcontext().prec=40
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
S=D('12.50081601'); P=D('1324.97')
H={
'2021':['1061.9015484376','524.6014437816','89.8337780996','747.5088077752','640.2867614737','34.0878453201','1786.41'],
'2022':['1240.9984377199','627.1644373827','100.9346861663','878.7952178239','366.9859583003','53.0654641654','1523.79'],
'2023':['1476.9360499414','747.3407155075','118.6727385178','1037.0865520838','665.9324772109','26.1975588879','1503.6018895247'],
'2024':['1708.9915227634','862.2814642162','137.8948236798','1196.8857945323','924.6369216843','46.7871205356','1699.7008925783'],
'2025':['1688.3810251479','823.2006710168','148.9227757091','1148.0895016424','615.2220498935','31.2759491641','1264.2560944772'],
'2026H1':['907.0326096448','445.1688042186','94.7376256588','614.1129168627','706.9075011906','8.3214275228','1848.1109548262']}
hist={}
for k,a in H.items():
 r,n,c,o,cf,cap,cash=map(D,a)
 hist[k]=dict(revenue=r,net_income=n,gross_margin=(1-c/r)*100,operating_margin=o/r*100,cfo=cf,capex=cap,simple_fcf=cf-cap,cash_equivalents=cash,net_margin=n/r*100)
TTMN=D(H['2025'][1])+D(H['2026H1'][1])-D('454.0296229810')
TTMR=D(H['2025'][0])+D(H['2026H1'][0])-D('893.8935441684')
TTMCF=D(H['2025'][4])+D(H['2026H1'][4])-D('131.1906103133')
TTMCAP=D(H['2025'][5])+D(H['2026H1'][5])-D('15.9599580923')
# Remove financial-company principal movements only, NOT full segment carve-out.
bridge={}
for name,cf,dep,loan,interbank,lend,cap in [
 ('2025','615.2220498935','-50.9927196687','-8.4811354525','128.4726586672','-9','31.2759491641'),
 ('2025H1','131.1906103133','-25.1665358450','-2.5473430526','254.1078816925','-21','15.9599580923'),
 ('2026H1','706.9075011906','73.8300456378','-11.7042484320','-218.9545228418','-9','8.3214275228')]:
 vals=list(map(D,[cf,dep,loan,interbank,lend,cap])); cf,dep,loan,interbank,lend,cap=vals
 adjusted=cf-dep+loan+interbank+lend
 bridge[name]=dict(cfo=cf,deposits=dep,loans=loan,interbank=interbank,lending=lend,adjusted_cfo=adjusted,adjusted_simple_fcf=adjusted-cap)
metrics=dict(price=P,shares_yi=S,market_cap=P*S,ttm_net=TTMN,ttm_revenue=TTMR,ttm_pe=P*S/TTMN,fy25_pe=P*S/D(H['2025'][1]),ttm_ps=P*S/TTMR,ttm_cfo=TTMCF,ttm_capex=TTMCAP,ttm_simple_fcf=TTMCF-TTMCAP,pb=P*S/D('2512.535944195'),eps_ttm=TTMN/S,bvps=D('2512.535944195')/S,dividend_yield_75pct=D('820')*D('.75')/(P*S)*100,imoutai_share=D('402.635642')/D(H['2026H1'][0])*100,net_profit_h1_yoy=(D(H['2026H1'][1])/D('454.029622981')-1)*100,cash_less_deposits=D('1848.1109548262')-D('254.2631666817'),gross_cash_plus_interbank=D('535.1879897908')+D('1410.8415812401'),controller_pct=D('681282935')/D('1250081601')*100)
# Equity cash flow with net income incl. recurring financial earnings; no starting cash add-on.
def dcf(cash0,g,r,tg):
 flows=[cash0*(1+g)**t for t in range(1,11)]
 explicit=sum(f/(1+r)**t for t,f in enumerate(flows,1))
 terminal=flows[-1]*(1+tg)/(r-tg)/(1+r)**10
 return dict(equity_value=explicit+terminal,price=(explicit+terminal)/S,terminal_share=terminal/(explicit+terminal)*100,annual_cash_flows=flows)
scenarios={}
for name,ng,cash0,g,r,tg,pe,payout in [('悲观','-.02','650','-.01','.08','0','14','.65'),('基准','.04','760','.04','.08','.02','20','.75'),('乐观','.07','810','.07','.08','.03','25','.80')]:
 ng,cash0,g,r,tg,pe,payout=map(D,[ng,cash0,g,r,tg,pe,payout]); vals=dcf(cash0,g,r,tg)
 profits=[D('820')*(1+ng)**t for t in range(1,11)]
 divs=sum(n*payout for n in profits[:5])/S
 exitprice=profits[4]*pe/S
 wealth=(exitprice+divs)/P
 vals.update(dict(net_growth=ng,fcfe0=cash0,fcfe_growth=g,discount=r,terminal_growth=tg,pe5=pe,payout=payout,profit3=profits[2],profit5=profits[4],profit10=profits[9],dividend5=divs,exit_price5=exitprice,wealth5=wealth,cagr5=wealth**D('.2')-1))
 scenarios[name]=vals
sensitivity={f'{r}/{g}':dcf(D('760'),D('.04'),D(r),D(g))['price'] for r in ['.07','.08','.09'] for g in ['.01','.02','.03']}
lo,hi=D('-.1'),D('.2')
for _ in range(150):
 mid=(lo+hi)/2
 if dcf(D('760'),mid,D('.08'),D('.02'))['price']>P: hi=mid
 else:lo=mid
reverse=(lo+hi)/2
cross=[
 ('2025营业收入','1688.3810251479','1688.38','亿元','2025年报','中新网/东方财富'),
 ('2025归母净利','823.2006710168','823.20','亿元','2025年报','中新网/东方财富'),
 ('2026H1营业收入','907.0326096448','907.03','亿元','2026中报','澎湃新闻'),
 ('2026H1归母净利','445.1688042186','445.17','亿元','2026中报','澎湃新闻'),
 ('2026H1经营现金流','706.9075011906','706.91','亿元','2026中报','深圳商报/东方财富'),
 ('2026H1现金等价物','1848.1109548262','1848.11','亿元','2026中报','上证报/东方财富'),
 ('总股本','1250081601','1250081601','股','2026中报','北京商报/东方财富'),
 ('20261019收盘','1324.97','1324.97','元','Investing历史','金融界行情')]
logs=[]
def run(args):
 result=subprocess.run([sys.executable,str(ROOT/'tools/financial_rigor.py')]+args,capture_output=True,text=True,check=True); logs.append(result.stdout)
run(['verify-market-cap','--price',str(P),'--shares',str(S*10**8),'--reported','1656321000000','--currency','CNY'])
for field,a,b,u,sa,sb in cross: run(['cross-validate','--field',field,'--values',json.dumps({sa:float(a),sb:float(b)},ensure_ascii=False),'--unit',u,'--tolerance','1'])
run(['verify-valuation','--price',str(P),'--eps',str(metrics['eps_ttm']),'--bvps',str(metrics['bvps']),'--fcf-per-share',str((TTMCF-TTMCAP)/S),'--dividend',str(D('820')*D('.75')/S)])
run(['three-scenario','--price',str(P),'--eps',str(D('820')/S),'--shares',str(S),'--growth','.07','.04','-.02','--pe','25','20','14','--years','5','--currency','CNY'])
output=dict(as_of='2026-10-20 01:25 CST',units='RMB 100m unless per-share/percent',history=hist,metrics=metrics,financial_principal_bridge=bridge,scenarios=scenarios,dcf_sensitivity=sensitivity,reverse_fcfe_growth=reverse,cross_checks=cross,limitations=['All valuation assumptions conditional. No cash add-on in equity cashflow valuation.','Adjusted CFO removes selected principal movements only; not audited standalone liquor FCFE.','No new buyback assumed; payouts not double counted in DCF.','2021/2022 cash balances are rounded disclosures.'])
(OUT/'model-results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2,default=str)+'\n')
(OUT/'financial-rigor-output.txt').write_text('\n'.join(logs))
for key in ['history','metrics','financial_principal_bridge','scenarios','dcf_sensitivity','reverse_fcfe_growth']:print(key,json.dumps(output[key],ensure_ascii=False,default=lambda v:str(round(v,4)) if isinstance(v,D) else str(v)))
