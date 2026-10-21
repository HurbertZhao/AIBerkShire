# -*- coding: utf-8 -*-
from decimal import Decimal as D, getcontext
from pathlib import Path
import json,sys,subprocess
getcontext().prec=40
P=Path(__file__).resolve().parent
R=P.parents[2]
S=D('1250081601'); price=D('1258.62'); U=D('100000000')
# CNY historical original filings; FY2022 profit uses 2024 comparative restatement.
rows={
 '2021':['106190154843.76','52460144378.16','8983377809.96','74750880777.52','64028676147.37','3408784532.01','178640587379.52'],
 '2022':['124099843771.99','62717467870.12','10093468616.63','87879521782.39','36698595830.03','5306546416.54','152378738982.83'],
 '2023':['147693604994.14','74734071550.75','11867273851.78','103708655208.38','66593247721.09','2619755888.79','150360188952.47'],
 '2024':['170899152276.34','86228146421.62','13789482367.98','119688579453.23','92463692168.43','4678712053.56','169970089257.83'],
 '2025':['168838102514.79','82320067101.68','14892277570.91','114808950164.24','61522204989.35','3127594916.41','126425609447.72'],
 '2026H1':['90703260964.48','44516880421.86','9473762565.88','61411291686.27','70690750119.06','832142752.28','184811095482.62']}
annual={}
for y,v in rows.items():
 rev,np,cost,op,cfo,capex,cash=map(D,v)
 annual[y]=dict(zip(['revenue','parent_profit','cost','operating_profit','cfo','capex','cash_equivalents'],map(D,v)))
 annual[y].update(gross_margin=(rev-cost)/rev*100,operating_margin=op/rev*100,fcf=cfo-capex,cfo_parent=cfo/np,fcf_parent=(cfo-capex)/np)
TTM=D(rows['2025'][1])+D(rows['2026H1'][1])-D('45402962298.10')
q={
 '2025Q3':{'revenue':D('39064353239.02'),'parent_profit':D('19223784414.08'),'moutai':D('110513502600')-D('75589948900'),'series':D('17884354800')-D('13762529400')},
 '2025Q4':{'revenue':D('40384394858.93'),'parent_profit':D('17693320389.50'),'moutai':D('146499906480.49')-D('110513502600'),'series':D('22274678707.16')-D('17884354800')},
 '2026Q1':{'revenue':D('53909252220.51'),'parent_profit':D('27242512886.45'),'moutai':D('46004868600'),'series':D('7880878300')},
 '2026Q2':{'revenue':D('90703260964.48')-D('53909252220.51'),'parent_profit':D('44516880421.86')-D('27242512886.45'),'moutai':D('77724437900')-D('46004868600'),'series':D('12934186500')-D('7880878300')}}
for name,prior,cost in [('2025Q3','38845154206.94',D('11183972073.77')-D('7777491083.93')),('2025Q4','50123020401.65',D('14892277570.91')-D('11183972073.77')),('2026Q1','50600957885.78',D('5520729200.32')),('2026Q2','38788396531.06',D('9473762565.88')-D('5520729200.32'))]:
 q[name]['growth']=q[name]['revenue']/D(prior)-1
 q[name]['gross_margin']=(1-cost/q[name]['revenue'])*100
def dcf(o,g,r,t,extra):
 o,g,r,t,extra=map(D,[o,g,r,t,extra]); flows=[o*(1+g)**i for i in range(1,11)]; pv=sum((f/(1+r)**i for i,f in enumerate(flows,1)),D(0)); tv=flows[-1]*(1+t)/(r-t)/(1+r)**10
 return {'oe0_100m':o,'growth':g,'discount':r,'terminal_g':t,'excess_cash_100m':extra,'equity_100m':pv+tv+extra,'price':(pv+tv+extra)*U/S,'terminal_share':tv/(pv+tv+extra),'cashflows_100m':flows}
cases={'悲观':dcf('650','-.01','.11','0','800'),'中性':dcf('760','.04','.10','.02','1000'),'乐观':dcf('800','.07','.09','.03','1200')}
lo,hi=D('-.2'),D('.3')
for _ in range(150):
 mid=(lo+hi)/2
 if dcf('760',mid,'.10','.02','1000')['price']>price:hi=mid
 else:lo=mid
reverse=(lo+hi)/2
sensitivity={str(r):{str(g):dcf('760',str(g),str(r),'.02','1000')['price'] for g in [D('.02'),D('.04'),D('.06')]} for r in [D('.09'),D('.10'),D('.11')]}
three={}
for name,g,pe in [('悲观',D('-.02'),D(14)),('中性',D('.04'),D(18)),('乐观',D('.08'),D(23))]:
 eps=TTM/S; div=sum((eps*(1+g)**i*D('.75') for i in range(1,4)),D(0)); end=eps*(1+g)**3*pe
 # distributions included as cash at horizon; ignores reinvestment and taxes
 three[name]={'eps0':eps,'growth':g,'pe':pe,'year3_price':end,'dividends':div,'present_value':end/(D('1.10')**3)+sum((eps*(1+g)**i*D('.75')/D('1.10')**i for i in range(1,4)),D(0)),'cagr':((end+div)/price)**(D(1)/3)-1}
cf_adj={}
for name,cfo,dep,loans,placement,interbank,cap in [
 ('2025','61522204989.35','-5099271966.87','-848113545.25','12847265866.72','-900000000','3127594916.41'),
 ('2025H1','13119061031.33','-2516653584.50','-254734305.26','25410788169.25','-2100000000','1595995809.23'),
 ('2026H1','70690750119.06','7383004563.78','-1170424843.20','-21895452284.18','-900000000','832142752.28')]:
 cfo,dep,loans,placement,interbank,cap=map(D,[cfo,dep,loans,placement,interbank,cap]); residual=cfo-dep+loans+placement+interbank
 cf_adj[name]={'residual_cfo':residual,'after_capex':residual-cap}
out={'annual':annual,'quarterly':q,'price':price,'shares':S,'cap':price*S,'TTM_profit':TTM,'PE_TTM':price*S/TTM,'PE_2025':price*S/D(rows['2025'][1]),'PB':price*S/D('251253594419.50'),'dividend_yield':D('51.98123')/price,'DCF':cases,'sensitivity':sensitivity,'reverse_growth':reverse,'three_year':three,'cashflow_adjustments':cf_adj,'safety_price':cases['中性']['price']*D('.8')}
(P/'model-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str))
# shared-tool reproducibility; normalized operating margins intentionally excluded from cross-source PASS
cmds=[['verify-market-cap','--price',str(price),'--shares',str(S),'--reported','1570000000000','--currency','CNY'],['verify-valuation','--price',str(price),'--eps',str(TTM/S),'--bvps',str(D('251253594419.50')/S),'--fcf-per-share',str((D(rows['2025'][4])-D(rows['2025'][5]))/S),'--dividend','51.98123'],['three-scenario','--price',str(price),'--eps',str(TTM/S),'--shares',str(S/U),'--growth','.08','.04','-.02','--pe','23','18','14','--years','3','--currency','CNY']]
sa={'2021':['106190','52460','64029','3409'],'2022':['124100','62717','36699','5307'],'2023':['147694','74734','66593','2620'],'2024':['170899','86228','92464','4679'],'2025':['168838','82320','61522','3128']}
for y,x in sa.items():
 for key,secondary in zip(['revenue','parent_profit','cfo','capex'],x):
  cmds.append(['cross-validate','--field',y+' '+key,'--values',json.dumps({'公司年报':str(annual[y][key]),'StockAnalysis':str(D(secondary)*1000000)},ensure_ascii=False),'--unit','CNY'])
for name,a,b in [('shares','1250081601','1250081601'),('2026H1现金等价物','184811095482.62','184811000000'),('控股股东经济权益百分比','54.50','54.499'),('收盘价','1258.62','1258.62')]:
 cmds.append(['cross-validate','--field',name,'--values',json.dumps({'公司公告或StockAnalysis':a,'新浪或新华或Investing':b},ensure_ascii=False),'--unit','同口径'])
for name,c in cases.items():
 oe,g,r,t,ex=[str(c[k]) for k in ['oe0_100m','growth','discount','terminal_g','excess_cash_100m']]
 expr='+'.join(f'({oe}*(1+({g}))**{i}/(1+{r})**{i})' for i in range(1,11))
 expr=f'(({expr})+{oe}*(1+({g}))**10*(1+{t})/({r}-{t})/(1+{r})**10+{ex})*100000000/{S}'
 cmds.append(['calc','--expr',expr])
with (P/'financial-rigor.txt').open('w') as f:
 for cmd in cmds:
  if cmd[0]=='cross-validate':
   vals=[D(v) for v in json.loads(cmd[cmd.index('--values')+1]).values()]
   assert abs(vals[0]-vals[1])/abs(vals[0]) <= D('.01')
  z=subprocess.run([sys.executable,str(R/'tools/financial_rigor.py'),*cmd],capture_output=True,text=True);f.write(' '.join(cmd)+'\n'+z.stdout+z.stderr+'\n');assert z.returncode==0,(cmd,z.stderr)
print(json.dumps({k:out[k] for k in ['cap','PE_TTM','PE_2025','PB','dividend_yield','DCF','reverse_growth','safety_price','three_year','cashflow_adjustments']},ensure_ascii=False,indent=2,default=str))
