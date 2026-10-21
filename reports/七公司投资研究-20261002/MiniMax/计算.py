from decimal import Decimal as D,getcontext
from pathlib import Path
import json
getcontext().prec=40
ROOT=Path(__file__).resolve().parent
FX=D('6.7351')/D('.85842');SH=D('352480183');PRICE=D('242.8')
# Lease payments are operating outflows in forecast FCF; do not subtract lease principal again.
cash=D('930.905')+D('14.038')+D('278.347')-D('133.555')
net_july=(D('9443.71')+D('6433.3')-D('6500'))/FX
q3burn=D('505.732')/2
startcash=(cash+net_july-q3burn)/1000
def value(flows,r,g,dilution,cash_adjust=startcash):
 flows=list(map(D,flows));r,g,di=map(D,(r,g,dilution));pv=D(0)
 for y,f in enumerate(flows,1):pv+=f*D(10)**9/SH/(1+di)**y/(1+r)**y
 tv=flows[-1]*(1+g)/(r-g)*D(10)**9/SH/(1+di)**10/(1+r)**10
 # Conservatively treat retained opening cash as subject to all future employee dilution.
 c=D(cash_adjust)*D(10)**9/SH/(1+di)**10
 return {'fcf_usd_bn':flows,'discount':r,'terminal_growth':g,'annual_share_dilution':di,'pv_operations_usd_per_share':pv,'pv_terminal_usd_per_share':tv,'cash_usd_per_share':c,'price_hkd':max(D(0),(pv+tv+c)*FX),'terminal_weight':tv/(pv+tv) if pv+tv else None,'shares_year10':SH*(1+di)**10}
base=['-.7','-.55','-.25','0','.25','.5','.75','1','1.25','1.5']
sc={'bear':value(['-.8','-.65','-.5','-.3','-.1','0','.1','.2','.3','.4'],'.20','.02','.04'),
'base':value(base,'.15','.03','.02'),
'bull':value(['-.6','-.3','.1','.5','1','1.5','2','2.6','3.3','4'],'.13','.035','.015')}
lo=D('.01');hi=D('10')
for _ in range(140):
 m=(lo+hi)/2;fs=[D(x)*(m if D(x)>0 else 1) for x in base]
 if value(fs,'.15','.03','.02')['price_hkd']<PRICE:lo=m
 else:hi=m
scale=(lo+hi)/2
three={}
for name,rev,ps,shares in [('bear','.8','3','550000000'),('base','2','8','440000000'),('bull','4','12','400000000')]:
 ex=D(rev)*D(10)**9*D(ps)*FX/D(shares)
 three[name]={'year3_revenue_usd_bn':D(rev),'equity_ps':D(ps),'shares':D(shares),'exit_price':ex,'pv':ex/D('1.15')**3,'total_return':ex/PRICE-1,'annualized':(ex/PRICE)**(D(1)/3)-1,'dividend':D(0)}
o={'price':PRICE,'shares':SH,'hkd_per_usd':FX,'marketcap_hkd_bn':PRICE*SH/D(10)**9,'marketcap_usd_bn':PRICE*SH/FX/D(10)**9,'ttm_revenue_usd_m':D('79.038')+D('116.573')-D('30.429'),'cash_june_usd_m':cash,'netcash_july_increment_m':net_july,'assumed_q3_burn_m':q3burn,'estimated_start_netcash_bn':startcash,'h1_cfo_m':D('-318.106'),'h1_simple_fcf_m':D('-318.106')-D('187.626'),'runway_years_at_h1_burn':startcash/(D('505.732')*2/1000),'dcf':sc,'reverse_positive_fcf_scale':scale,'reverse_year10_fcf_bn':D('1.5')*scale,'reverse_year10_revenue_at_base_margin_bn':D('8.5')*scale,'three_year':three,'buy_line':sc['base']['price_hkd']*D('.65'),'economic_interest':D('79102534')/SH,'voting_interest':(D('74102534')*10+D('5000000'))/(D('81102534')*10+D('271377649'))}
o['ps_ttm']=o['marketcap_usd_bn']*1000/o['ttm_revenue_usd_m']
o['ev_ttm']= (o['marketcap_usd_bn']-startcash)*1000/o['ttm_revenue_usd_m']
(ROOT/'计算结果.json').write_text(json.dumps(o,ensure_ascii=False,indent=2,default=str))
print(json.dumps(o,ensure_ascii=False,indent=2,default=str))
