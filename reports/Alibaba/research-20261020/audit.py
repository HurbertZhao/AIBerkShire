"""Scope-aware source and formula sample audit, seed 42. No network on rerun.
Independent values below are transcribed from publications, not inferred from prose.
"""
from pathlib import Path
from decimal import Decimal as D
import json,sys,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools'));import report_audit
annual='https://www.hkexnews.hk/listedco/listconews/sehk/2026/0618/2026061800844.pdf'
q='https://www.hkexnews.hk/listedco/listconews/sehk/2026/0820/2026082000745.pdf'
sp='https://stockanalysis.com/quote/hkg/9988/financials/income-statement/'
cf='https://stockanalysis.com/quote/hkg/9988/financials/cash-flow-statement/'
ap='https://apnews.com/article/8a30302d23a96fc7b9aab664b9c1897d'
apmarch='https://apnews.com/article/e83a76c7188e27f69c9c3d7e4f8d9d83'
march='https://www.hkexnews.hk/listedco/listconews/sehk/2026/0513/2026051300653.pdf'
V={
'FY2022 · 简单FCF':(D(142759-53309)/100,'derived_single_source',cf,None,''),
'FY2022 · 归普通股净利':(D(61959)/100,'fact',annual,D('619.59'),sp),
'FY2023 · 归普通股净利':(D(72509)/100,'fact',annual,D('725.09'),sp),
'FY2023 · 收入':(D(868687)/100,'fact',annual,D('8686.87'),sp),
'FY2025 · 购建固定资产':(D(85972)/100,'fact',annual,D('859.72'),cf),
'FY2025 · 归普通股净利':(D(129470)/100,'fact',annual,D('1294.70'),sp),
'FY2025 · 毛利率%':((1-D(598285)/D(996347))*100,'derived',annual,D('39.95'),sp),
'FY2026 · 收入':(D(1023670)/100,'fact',annual,D('10236.70'),sp),
'2026June · 收入':(D(268953)/100,'fact',q,D('2690'),ap),
'2025年12月季 · 云分部收入':(D(43284)/100,'fact','https://www.hkexnews.hk/listedco/listconews/sehk/2026/0319/2026031900801.pdf',None,''),
'2026年3月季 · 云分部收入':(D(41626)/100,'fact',march,D('416'),apmarch),
'2026年3月季 · 云同比':(D(38),'fact',march,D(38),apmarch),
'2026年6月季 · 收入':(D(268953)/100,'fact',q,D('2690'),ap),
'2026年6月季 · 归普通股净利':(D(10537)/100,'fact',q,D(105),ap),
'港股收盘 · 采用值':(D('108.8'),'fact','https://stockanalysis.com/quote/hkg/9988/history/',D('108.8'),'https://www.webull.hk/quote/hkex-09988'),
'自算TTM PS · 采用值':(D('108.8')*D('199.01959514')*D('.8525')/D('10449.71'),'formula','September monthly shares, price, June/FY filings',None,''),
'PB（六月权益基数） · 采用值':(D('108.8')*D('199.01959514')*D('.8525')/D('10490.38'),'formula',q,None,''),
'基准 · 第6年至第10年FCFF':(D(1500),'assumption_transcription','model.py base flows[5]; extraction captures first element only',None,''),
'基准 · 第1年至第5年FCFF':(D(-500),'assumption_transcription','model.py base flows[0]; extraction captures first element only',None,''),
'悲观 · 五年后净利':(D(600),'assumption_transcription','model.py bear profit5',None,''),
'乐观 · 五年末股价/股':(D(2300)*28/D('199.01959514')/D('.8525'),'assumption_formula','profit5 x PE28 / shares / FX',None,'')}
report=OUT.parent/'阿里巴巴研究报告-20261020.md';allpoints=report_audit.extract_data_points(report.read_text());sample=report_audit.sample_points(allpoints,.15,42)
results=[];dispositions=[]
for p in sample:
 if p['label'] not in V:raise ValueError('Unmapped '+p['label'])
 v,cls,src,v2,src2=V[p['label']]
 assert abs(D(str(p['reported_value']))-v)/abs(v)<D('.01')
 row=dict(p,fetched_value=float(v),fetched_source=src,classification=cls)
 if v2 is not None:row.update(fetched_value2=float(v2),fetched_source2=src2)
 results.append(row);dispositions.append(dict(id=p['id'],label=p['label'],classification=cls,independent_second_source=v2 is not None))
for fn,obj in [('audit-sample.json',sample),('audit-results.json',results),('audit-dispositions.json',dispositions)]:
 (OUT/fn).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
r=subprocess.run([sys.executable,str(ROOT/'tools/report_audit.py'),'verdict','--results',json.dumps(results,ensure_ascii=False),'--report',report.name],capture_output=True,text=True,check=True)
(OUT/'audit-verdict.txt').write_text(r.stdout);print(r.stdout)
print('Total points',len(allpoints),'sample',len(sample),'dual',sum(d['independent_second_source'] for d in dispositions))
