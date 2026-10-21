from decimal import Decimal as D, getcontext
from pathlib import Path
import json,subprocess
getcontext().prec=40
ROOT=Path(__file__).resolve().parent
FX=D('0.85842'); SH=D('1331779203'); PRICE=D('149.2')
def dcf(f0,g1,g2,r,g,excess):
 f=D(f0); flows=[]; pv=D(0)
 for y in range(1,11):
  f*=1+D(g1 if y<=5 else g2); flows.append(f);pv+=f/(1+D(r))**y
 tv=f*(1+D(g))/(D(r)-D(g))/(1+D(r))**10
 return {'flows':flows,'pv_flows':pv,'pv_terminal':tv,'equity_cny_bn':pv+tv+D(excess),'price':(pv+tv+D(excess))*D(10)**9/SH/FX,'terminal_weight':tv/(pv+tv)}
annual={
'2021':{'revenue':'4.490651','net':'0.854339','gp':'2.758624','op':'1.149812','cfo':'0.779097','ppe':'0.287502','cash':'5.264710'},
'2022':{'revenue':'4.617324','net':'0.475660','gp':'2.654543','op':'0.583380','cfo':'0.891022','ppe':'0.266132','cash':'0.685314'},
'2023':{'revenue':'6.301002','net':'1.082344','gp':'3.864071','op':'1.230646','cfo':'1.990596','ppe':'0.324179','cash':'2.077927'},
'2024':{'revenue':'13.037749','net':'3.125473','gp':'8.707765','op':'4.154272','cfo':'4.954220','ppe':'0.372670','cash':'6.109'},
'2025':{'revenue':'37.120052','net':'12.775689','gp':'26.764916','op':'16.890474','cfo':'10.865152','ppe':'0.985250','cash':'13.775087'},
'2026H1':{'revenue':'17.172921','net':'5.038384','gp':'11.965740','op':'6.724746','cfo':'3.637324','ppe':'0.673560','cash':'12.442065'}}
for a in annual.values():
 a.update({k:D(v) for k,v in a.items()});a.update(simple_fcf=a['cfo']-a['ppe'],gm=a['gp']/a['revenue'],opm=a['op']/a['revenue'],cfo_net=a['cfo']/a['net'],fcf_net=(a['cfo']-a['ppe'])/a['net'])
netcash=D('12.442065')+D('1.520187')-D('3.061836')-D('0.665736')
operating_lease_cash_adjust=D('12.442065')+D('1.520187')-D('4')
ttmrev=D('37.120052')+D('17.172921')-D('13.876276')
ttmnet=D('12.775689')+D('5.038384')-D('4.574368')
ttmcfo=D('10.865152')+D('3.637324')-D('5.977473')
ttmppe=D('.985250')+D('.673560')-D('.353623')
ttmint=D('.186287')+D('.050579')-D('.020900')
ttmlease=D('.608288')+D('.502889')-D('.263592')
sc={
'bear':dcf('6','0','0','.13','.01','5'),
'base':dcf('8.5','.07','.04','.11','.025',operating_lease_cash_adjust),
'bull':dcf('10.5','.12','.06','.10','.03','10')}
target=PRICE*SH*FX/D(10)**9
lo=D('-.30');hi=D('.50')
for _ in range(140):
 m=(lo+hi)/2
 if dcf('8.5',m,'.04','.11','.025',operating_lease_cash_adjust)['equity_cny_bn']<target:lo=m
 else:hi=m
three={}
for n,g,pe in [('bear','-.08','10'),('base','.07','16'),('bull','.15','22')]:
 g,pe=D(g),D(pe);eps=D('10.5')*D(10)**9/SH/FX
 div=[eps*(1+g)**y*D('.25') for y in (1,2,3)]
 exitprice=eps*(1+g)**3*pe
 three[n]={'profit_growth':g,'pe':pe,'exit_price':exitprice,'dividends':sum(div),'pv':exitprice/D('1.11')**3+sum(x/D('1.11')**(i+1) for i,x in enumerate(div)),'total_return':(exitprice+sum(div))/PRICE-1,'annualized':((exitprice+sum(div))/PRICE)**(D(1)/3)-1}
o={'price':PRICE,'shares':SH,'cny_per_hkd':FX,'marketcap_hkd_bn':PRICE*SH/D(10)**9,'annual_bn_cny':annual,'ttm_revenue_bn':ttmrev,'ttm_net_bn':ttmnet,'ttm_cfo_bn':ttmcfo,'ttm_simple_fcf_bn':ttmcfo-ttmppe,'ttm_after_intangible_lease_bn':ttmcfo-ttmppe-ttmint-ttmlease,'netcash_bn':netcash,'excesscash_bn':operating_lease_cash_adjust,'pe':PRICE*SH*FX/D(10)**9/ttmnet,'ps':target/ttmrev,'pb':target/D('23.059024'),'fcf_yield':(ttmcfo-ttmppe)/target,'eps_hkd':ttmnet*D(10)**9/SH/FX,'bvps_hkd':D('23.059024')*D(10)**9/SH/FX,'fcfps_hkd':(ttmcfo-ttmppe)*D(10)**9/SH/FX,'dcf':sc,'reverse_first5_growth':(lo+hi)/2,'three_year':three,'buy_line':sc['base']['price']*D('.75'),'wang_lookthrough':(D('561131960')+D('31196420')+D('62053027')*D('.4096'))/SH,'h1_full_fcf':D('3.637324')-D('.673560')-D('.050579')-D('.502889')}
(ROOT/'计算结果.json').write_text(json.dumps(o,ensure_ascii=False,indent=2,default=str))
print(json.dumps(o,ensure_ascii=False,indent=2,default=str))
