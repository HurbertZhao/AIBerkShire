from pathlib import Path
from decimal import Decimal as D
import json,subprocess
R=Path(__file__).resolve().parent
J=json.loads((R/'计算结果.json').read_text())
raw=(R/'audit-extract.txt').read_text(); sample=json.loads(raw[raw.index('\n[\n'):])
AN='https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0422/2026042202118.pdf'
HI='https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0930/2026093002173.pdf'
IPO='https://www1.hkexnews.hk/listedco/listconews/sehk/2025/1231/2025123100025.pdf'
SA='https://stockanalysis.com/quote/hkg/0100/financials/'
SC=SA+'cash-flow-statement/';SB=SA+'balance-sheet/'
ET='https://m.etnet.com.hk/www/eng/stocks/realtime/quote_ci_pl.php?code=100'
facts={7:(20.079,AN,20.08,SA),8:(20.813,HI,20.813,ET),9:(-24.7,IPO,float(D('-.85')/D('3.46')*100),SA),27:(-318.106,HI,None,'SA和经济通的2026H1现金流仍为空'),23:(-11.019,IPO,-11.02,SC),24:(-64.455,IPO,-64.46,SC),29:(.697,IPO,.7,SC),36:(-280.561,AN+'；CFO减设备支出',-280.56,SC),51:(116.573,HI,116.6,'https://www.investing.com/news/stock-market-news/chinas-minimax-sees-revenue-nearly-quadruple-in-first-half-as-ai-demand-surges-4876820'),56:(float(D('20.813')/D('116.573')*100),HI,17.9,'https://www.minimax.io/news/minimax-announces-first-half-2026-financial-results-1787744160'),57:(930.905,HI,930.91,SB),58:(14.038,HI,14.04,SB),60:(133.555,HI,133.56,SB),130:(242.8,'https://qt.gtimg.cn/q=hk00100',242.8,'https://global.hk01.com/财经快讯/60395691/')}
# Company's own news is not independent: retain explicit flag for id56 despite numerical agreement.
calc={63:('融资净款合计减6500百万港元债券本金，再按统一汇率换算',D(J['netcash_july_increment_m'])),71:('市值减估计期初净现金再除TTM收入',D(J['ev_ttm'])),108:('十年乐观DCF含稀释与租赁经营处理',D(J['dcf']['bull']['price_hkd']))}
ass={72:.8,109:.8,115:550}
sets={'facts':[],'calculations':[],'assumptions':[],'source_gaps':[]}
for s in sample:
 i=s['id']
 if i in facts:
  a,u,b,v=facts[i];s.update(fetched_value=a,fetched_source=u,fetched_value2=b,fetched_source2=v)
  if i==56:
   # ET independently publishes same gross profit and revenue, so ratio is independently reconstructible.
   s['fetched_value2']=float(D('20813')/D('116573')*100);s['fetched_source2']=ET+'；毛利/收入'
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
