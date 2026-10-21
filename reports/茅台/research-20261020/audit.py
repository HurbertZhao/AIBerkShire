"""Reproduce scope-aware sample checks. Sources were fetched 2026-10-20.
Actual fact values are manually transcribed from cited publications, never copied
from the report. Scenario checks only assert formula consistency, not truth.
"""
from pathlib import Path
from decimal import Decimal as D
import json,sys,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import report_audit
report=OUT.parent/'茅台研究报告-20261020.md'
points=report_audit.sample_points(report_audit.extract_data_points(report.read_text()),.15,42)
primary='https://static.cninfo.com.cn/finalpage/2026-08-15/1225475868.PDF'
annual='https://big5.sse.com.cn/site/cht/www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-04-17/600519_20260417_9QS4.pdf'
values={
'2026H1 · 营业利润率':(D('61411291686.27')/D('90703260964.48')*100,'formula',primary,None,''),
'2026H1 · CFO':(D('70690750119.06')/10**8,'fact',primary,D('706.91'),'https://finance.eastmoney.com/a/202608143842079859.html'),
'系列酒 · 2026H1收入':(D('12934186500')/10**8,'fact',primary,None,''),
'直销 · 2026H1收入':(D('51962047000')/10**8,'fact',primary,None,''),
'直销 · 2025年收入':(D('84543031854.63')/10**8,'fact',annual,None,''),
'i茅台 · 2026H1收入':(D('40263564200')/10**8,'fact',primary,D('402.64'),'https://www.thepaper.cn/newsDetail_forward_33785696'),
'客户贷款及垫款净增额 · 2026H1':(D('-1170424843.20')/10**8,'fact',primary,None,''),
'央行及同业款项净增额 · 2026H1':(D('-21895452284.18')/10**8,'fact',primary,None,''),
'剔除以上本金流动后的经营现金流代理 · 2025全年':((D('61522204989.35')-D('-5099271966.87')+D('-848113545.25')+D('12847265866.72')+D('-900000000'))/10**8,'formula',annual,None,''),
'悲观 · 三年后净利':(D('820')*D('.98')**3,'assumption_formula','model.py: profit0 820 * 0.98^3',None,''),
'乐观 · 五年末股价':(D('820')*D('1.07')**5*25/D('12.50081601'),'assumption_formula','model.py: profit0 * 1.07^5 * PE25 / shares',None,'')}
results=[];dispositions=[]
for p in points:
 if p['label']=='研究与资料截止':
  dispositions.append(dict(p,classification='date_false_positive',reason='2026 is a calendar year, not a financial observation'));continue
 if p['label'] not in values:raise ValueError('Unmapped audit point: '+p['label'])
 v,c,s,v2,s2=values[p['label']]
 assert abs(D(str(p['reported_value']))-v)/abs(v)<=D('.01')
 results.append(dict(p,fetched_value=float(v),fetched_source=s,fetched_value2=float(v2) if v2 else None,fetched_source2=s2,classification=c))
 dispositions.append(dict(p,classification=c,independent_second_source=bool(v2)))
(OUT/'audit-sample.json').write_text(json.dumps(points,ensure_ascii=False,indent=2)+'\n')
(OUT/'audit-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
(OUT/'audit-dispositions.json').write_text(json.dumps(dispositions,ensure_ascii=False,indent=2)+'\n')
p=subprocess.run([sys.executable,str(ROOT/'tools/report_audit.py'),'verdict','--results',json.dumps(results,ensure_ascii=False),'--report',report.name],capture_output=True,text=True,check=True)
(OUT/'audit-verdict.txt').write_text(p.stdout)
print(p.stdout)
