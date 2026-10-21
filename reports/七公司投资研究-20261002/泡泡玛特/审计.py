from pathlib import Path
from decimal import Decimal as D
import json,subprocess
R=Path(__file__).resolve().parent
J=json.loads((R/'计算结果.json').read_text())
raw=(R/'audit-extract.txt').read_text(); sample=json.loads(raw[raw.index('\n[\n'):])
AN='https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0421/2026042100395_c.pdf'
HI='https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0924/2026092400544.pdf'
SA='https://stockanalysis.com/quote/hkg/9992/financials/'
SC=SA+'cash-flow-statement/'
facts={4:(130.37749,AN,130.38,SA),5:(371.20052,AN,371.20,SA),12:(50.38384,HI,50.38,'https://www.finet.hk/newscenter/news_content/6a86c2d02308290c11eadd7c'),15:(61.3,AN,float(D('3864')/D('6301')*100),SA),18:(69.7,HI,69.7,'https://www.finet.hk/newscenter/news_content/6a86c2d02308290c11eadd7c'),14:(57.5,AN,float(D('2655')/D('4617')*100),SA),29:(108.65152,AN,108.65,SC),28:(49.54220,AN,49.54,SC),30:(36.37324,HI,None,'未取得独立第二源，SA只有TTM汇总')}
calc={36:('("3.637324"-"0.673560")*10', (D('3.637324')-D('.673560'))*10),32:('2022 CFO891022减设备266132千元，再除100000',D('624890')/100000),55:('CFO10865152/归母12775689*100',D('10865152')/D('12775689')*100),65:('价格*股本*汇率/TTM归母',D(J['pe'])),70:('TTM简单FCF/人民币市值*100',D(J['fcf_yield'])*100),87:('现金124.42065+定存15.20187-缓冲40亿元',D(J['excesscash_bn'])*10),95:('105亿归母/股份/汇率，三年按-8%增长，每年分红25%',D(J['three_year']['bear']['dividends']))}
ass={76:7,82:10}
sets={'facts':[],'calculations':[],'assumptions':[],'source_gaps':[]}
for s in sample:
 i=s['id']
 if i in facts:
  a,u,b,v=facts[i];s.update(fetched_value=a,fetched_source=u,fetched_value2=b,fetched_source2=v)
  sets['facts'].append(s)
  if b is None:sets['source_gaps'].append({'id':i,'label':s['label'],'reason':v})
 elif i in calc:
  f,v=calc[i];s.update(fetched_value=float(v),fetched_source='Decimal公式复算: '+f,fetched_value2=None,fetched_source2='计算值不是第二份事实来源');sets['calculations'].append(s)
 elif i in ass:
  s.update(assumption_value=ass[i],status='ASSUMPTION_NOT_EXTERNAL_FACT');sets['assumptions'].append(s)
 else:raise RuntimeError(s)
for n,items in sets.items():
 (R/('audit-'+n+'.json')).write_text(json.dumps(items,ensure_ascii=False,indent=2))
 if n in ('facts','calculations'):
  o=subprocess.run(['python3','tools/report_audit.py','verdict','--results',json.dumps(items,ensure_ascii=False),'--report',R.name+' '+n],capture_output=True,text=True)
  (R/('audit-'+n+'-verdict.txt')).write_text(o.stdout+o.stderr)
  print(n,len(items),o.stdout[o.stdout.find('抽检总数:'):])
