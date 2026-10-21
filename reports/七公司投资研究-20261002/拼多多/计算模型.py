from decimal import Decimal as D, getcontext
import json, pathlib, subprocess, sys
getcontext().prec=36
base=pathlib.Path(__file__).resolve().parent
root=base.parents[2]
def cv(x): return D(str(x))
def dcf(cf,g1,g2,r,gt,adj,shares,fx):
 cf,g1,g2,r,gt,adj,shares,fx=map(cv,(cf,g1,g2,r,gt,adj,shares,fx)); rows=[];p=D(0)
 for t in range(1,11):
  cf*=1+(g1 if t<=5 else g2); v=cf/(1+r)**t;p+=v;rows.append({'year':t,'cash_flow_bn':str(cf),'present_value_bn':str(v)})
 tv=cf*(1+gt)/(r-gt)/(1+r)**10
 return {'explicit_pv_bn':p,'terminal_pv_bn':tv,'adjustment_bn':adj,'equity_bn':p+tv+adj,'price':(p+tv+adj)/shares*fx,'terminal_share':tv/(p+tv),'rows':rows}
cfg={'腾讯':{'price':'421.2','shares':'9.092605595','fx':str(D(1)/D('.85842')),'r':'.10','cf':'170','adj':'500','g1':'.08','g2':'.05','gt':'.025','scenarios':[['悲观',140,0,0,.12,.015,300],['中性',170,.08,.05,.10,.025,500],['乐观',200,.12,.07,.09,.03,650]],'eps':'24.153','egrowth':['-.03','.07','.13'],'pe':[13,18,23],'div':'5.3','divgrowth':'.05','mos':'.25'},
'拼多多':{'price':'76.5','shares':'1.48','market_shares':'1.423396462','fx':str(D(1)/D('6.7351')),'r':'.12','cf':'75','adj':'200','g1':'.05','g2':'.03','gt':'.02','scenarios':[['悲观',50,-.03,0,.15,0,100],['中性',75,.05,.03,.12,.02,200],['乐观',90,.10,.06,.11,.025,300]],'eps':str(D('92076')/D('1480')),'egrowth':['-.10','.05','.12'],'pe':[7,11,15],'div':'0','divgrowth':'0','mos':'.30'}}
annual={'腾讯':{'revenue':[560118,554552,609015,660257,751766],'gross':[245944,238746,293109,349246,422593],'op':[124656,110827,160074,208099,241562],'net':[224822,188243,115216,194073,224842],'cfo':[175186,146091,221962,258521,303052],'capex':[29302,22679,21008,62927,87482],'cash':[264101,290756,379155,338409,422552]},'拼多多':{'revenue':[93950,130558,247639,393836,431846],'gross':[62232,99095,155916,239936,243044],'op':[6897,30402,58699,108423,93102],'net':[7769,31538,60027,112435,97843],'cfo':[28783,48508,94163,121929,106939],'capex':[3287,635.72,583.88,967.14,1145.077],'cash':[92943,149439,217210,331560,422308]}}
for co,c in cfg.items():
 if co != base.name: continue
 dest=base;dest.mkdir(exist_ok=True)
 out={'assumptions':c,'dcf':{},'three_year':[]}
 for s in c['scenarios']:out['dcf'][s[0]]=dcf(*s[1:],c['shares'],c['fx'])
 low,high=D('-.3'),D('.3')
 for i in range(180):
  mid=(low+high)/2
  value=dcf(c['cf'],mid,mid,c['r'],c['gt'],c['adj'],c['shares'],c['fx'])['price']
  if value>cv(c['price']):high=mid
  else:low=mid
 out['reverse_dcf_growth']=mid
 for label,gr,pe in zip(['悲观','中性','乐观'],c['egrowth'],c['pe']):
  eps=cv(c['eps'])*cv(c['fx']);price3=eps*(1+cv(gr))**3*cv(pe);divs=[cv(c['div'])*(1+cv(c['divgrowth']))**t for t in range(1,4)]
  pv=price3/(1+cv(c['r']))**3+sum(d/(1+cv(c['r']))**t for t,d in enumerate(divs,1));total=price3+sum(divs)
  out['three_year'].append({'scenario':label,'eps0':eps,'growth':gr,'pe':pe,'price3':price3,'dividends3':sum(divs),'present_value':pv,'cagr':(total/cv(c['price']))**(D(1)/3)-1})
 out['sensitivity']=[{'r':r,'gt':g,'price':dcf(c['cf'],c['g1'],c['g2'],r,g,c['adj'],c['shares'],c['fx'])['price']} for r in ([.09,.10,.11] if co=='腾讯' else [.11,.12,.13]) for g in [.02,.025,.03]]
 mktshares=cv(c.get('market_shares',c['shares']));out['market_cap_quote_bn']=mktshares*cv(c['price']);out['market_cap_rmb_bn']=out['market_cap_quote_bn']/cv(c['fx']);out['buy_line_exact']=out['dcf']['中性']['price']*(1-cv(c['mos']))
 a=annual[co];out['annual']=a;out['annual_derived']={}
 for i,y in enumerate(range(2021,2026)):
  out['annual_derived'][y]={'gross_margin':cv(a['gross'][i])/cv(a['revenue'][i])*100,'op_margin':cv(a['op'][i])/cv(a['revenue'][i])*100,'simple_fcf':cv(a['cfo'][i])-cv(a['capex'][i]),'cfo_net':cv(a['cfo'][i])/cv(a['net'][i]),'fcf_net':(cv(a['cfo'][i])-cv(a['capex'][i]))/cv(a['net'][i])}
 (dest/'计算结果.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str))
 text='| 年度（百万元人民币） | 2021 | 2022 | 2023 | 2024 | 2025 |\n|---|---:|---:|---:|---:|---:|\n'
 for lab,key in [('收入','revenue'),('归母净利润','net'),('经营现金流','cfo'),('购置设备等现金支出','capex'),('标准化现金及短期投资','cash')]:text+='| '+lab+' | '+' | '.join(f'{x:,.2f}' for x in a[key])+' |\n'
 for lab,key in [('毛利率','gross_margin'),('经营利润率','op_margin'),('简单自由现金流','simple_fcf'),('CFO/归母净利润','cfo_net'),('简单FCF/归母净利润','fcf_net')]:text+='| '+lab+' | '+' | '.join(f'{out["annual_derived"][y][key]:,.2f}'+('%' if 'margin' in key else '') for y in range(2021,2026))+' |\n'
 (dest/'财务表.md').write_text(text)
 print(co,'DCF',[(k,str(v['price'])) for k,v in out['dcf'].items()],'buy',out['buy_line_exact'],'reverse',mid,'3yr',out['three_year'])
