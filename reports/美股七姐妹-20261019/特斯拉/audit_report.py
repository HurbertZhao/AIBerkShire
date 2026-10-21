#!/usr/bin/env python3
"""Classify the unchanged 15% random sample; model checks are not fact verification."""
from pathlib import Path
from decimal import Decimal as D
import sys,json,subprocess,re
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import report_audit as ra
report=HERE/'特斯拉投资研究报告-20261019.md'
data=json.loads((HERE/'calculations.json').read_text()); m=data['metrics']
sec='https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm'
annual='https://www.sec.gov/Archives/edgar/data/1318605/000162828026003837/exhibit991.htm'
sa='https://stockanalysis.com/stocks/tsla/financials/'
cf=sa+'cash-flow-statement/'; bs=sa+'balance-sheet/'
qpdf='https://assets-ir.tesla.com/tesla-contents/IR/TSLA-Q2-2026-Update.pdf'
# Independently read observations, not copied from extracted reported_value.
facts={
'现金及短期投资 · 数值':(43524,sec,43524,bs),
'债务及融资租赁 · 数值':(1418+7924,sec,None,None),
'TTM自由现金流 · 数值':(18685-12923,qpdf,5762,cf),
'收入 · 2025':(94827,annual,94827,sa),
'收入 · 2023':(96773,annual,96773,sa),
'毛利率 · 2022':(float(D(20853)/D(81462)*100),annual,25.60,sa),
'归母净利润 · 2022':(12556,annual,12556,cf),
'经营现金流 · 2024':(14923,annual,14923,cf),
'经营现金流 · 2022':(14724,annual,14724,cf),
'经营现金流 · 2023':(13256,annual,13256,cf),
'资本开支 · 2024':(11342,annual,11342,cf),
'资本开支 · 2021':(6514,annual,6514,cf),
'现金及短投 · 2022':(22185,annual,22185,bs),
'汽车 · 2026Q1':(float((D(16234)-12812)/16234*100),qpdf,None,None),
'汽车 · 2025Q4':(float((D(17693)-14080)/17693*100),qpdf,None,None),
'FCF收益率 · 本文计算':(float(D(5762)/(D('354.72')*D('3949547394')/1000000)*100),'S1/S2现金流与股数价格重算',.41,sa+'ratios/'),
'TTM归母/每股计算分子 · 第三方':(3806,sa,None,None),
'TTM归母/每股计算分子 · 原始来源':(1373+840+477+1114,qpdf,3804,cf),
'TTM归母/每股计算分子 · 处理':(float(D(2)/3804*100),'原报3804与第三方3806差异重算',None,None),
'净现金含经营租赁 · 处理':(1418+7924,sec,None,None)}
models={
'基准 · 三年后PE假设':45,
'乐观 · 年化利润增长':float(D(data['scenarios3'][2]['growth'])*100),
'能源 · 基准':100,
'独立增量软件/无人出行 · 基准':40,
'净利润合计 · 乐观':float(sum(D(str(a))*D(b) for a,b in data['profit2036_components_billions'][2])),
'悲观 · 终值PE':float((1-D('.01')/D('.20'))/(D('.10')-D('.01'))),
'基准 · 十年近似年化回报':float(D(data['scenarios10'][1]['irr_percent']))}
excluded={'研究日':'年份并非财务指标','现金及短期投资 · 来源与解释':'误提取日期2026','TTM资本开支 · 来源与解释':'误提取来源编号S1'}
sample=ra.sample_points(ra.extract_data_points(report.read_text()),seed=42)
included=[]; allrows=[]
for item in sample:
 label=item['label']; x=dict(item)
 if label in excluded:
  x.update(category='parser_false_positive',exclusion_reason=excluded[label])
 elif label in facts:
  a,s,b,s2=facts[label]
  x.update(category='external_dual_or_derived' if b is not None else 'single_source_or_derived',fetched_value=a,fetched_source=s,fetched_value2=b,fetched_source2=s2)
  included.append(x)
 elif label in models:
  x.update(category='model_recalculation_or_assumption',fetched_value=models[label],fetched_source='reproduce.py / calculations.json：算式或假设一致性，非外部事实')
  included.append(x)
 else:raise RuntimeError('Unclassified random sample: '+label)
 allrows.append(x)
(HERE/'audit-sample-classified.json').write_text(json.dumps(allrows,ensure_ascii=False,indent=2)+'\n')
(HERE/'audit-results.json').write_text(json.dumps(included,ensure_ascii=False,indent=2)+'\n')
r=subprocess.run([sys.executable,str(ROOT/'tools/report_audit.py'),'extract','--report',str(report),'--seed','42'],capture_output=True,text=True)
(HERE/'audit-extract.txt').write_text(r.stdout+r.stderr)
r=subprocess.run([sys.executable,str(ROOT/'tools/report_audit.py'),'verdict','--report',report.name,'--results',json.dumps(included,ensure_ascii=False)],capture_output=True,text=True)
(HERE/'audit-verdict.txt').write_text(re.sub(r'\x1b\[[0-9;]*m','',r.stdout+r.stderr))
counts={k:sum(x['category']==k for x in allrows) for k in sorted(set(x['category'] for x in allrows))}
(HERE/'audit-coverage.md').write_text('# 数据抽检覆盖说明\n\n随机种子42，15%抽样（最多30项）。没有改变抽样种子来回避差异。\n\n'+json.dumps(counts,ensure_ascii=False,indent=2)+'\n\n外部双源包括使用两源输入的派生计算；单源/同发行人重复披露不称独立双源。模型项仅检查假设转写和运算一致性，不意味着预测真实。三项解析误报保留在分类文件而排除数字判决；没有空值冒充通过。原始第三方重分类差异另见validation-log.txt及正文，未被悄悄改为一致。\n\n核心事实收入、净利、现金、股价、股本和FCF另由financial_rigor检查；季度细分毛利成本仍有独立第二来源缺口，不能将本次准出视为全报告审计。\n')
print(r.stdout);print(counts)
if r.returncode:raise SystemExit(r.returncode)
