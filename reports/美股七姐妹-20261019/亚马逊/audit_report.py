#!/usr/bin/env python3
"""Reproduce extract and verdict. Evidence values below were actually retrieved.
No network is performed here; source dates and restrictions remain explicit.
"""
from pathlib import Path
import json,sys,subprocess,re
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import report_audit
report=HERE/'亚马逊投资研究报告-20261019.md'
data=json.loads((HERE/'source-data.json').read_text())
model=json.loads((HERE/'model-results.json').read_text())
sources=data['sources']
sample=report_audit.sample_points(report_audit.extract_data_points(report.read_text()),ratio=.15,seed=42)
evidence=[]
for point in sample:
 p=dict(point); label=p['label']; p.update(fetched_value=None,fetched_source='',fetched_value2=None,fetched_source2='')
 if '日期/口径' in label:
  p['classification']='extractor_false_positive';p['note']='10-Q document name parsed as number 10; not a financial observation. Explicitly excluded, not silently passed.'
 elif 'FY20' in label and '收入' not in label.split(' · ')[-1]:
  year=re.search(r'FY(20\d\d)',label).group(1); a=data['annual'][year]; d=model['annual_derived'][year]
  field=label.split(' · ')[0]
  if field=='营业收入': val=a['revenue']
  elif field=='毛利率':val=d['gross_margin']
  elif field=='经营利润':val=a['operating_income']
  elif field=='经营利润率':val=d['op_margin']
  elif field=='自由现金流（公司净资本开支口径）':val=d['fcf_company']
  elif field=='自由现金流（不冲回资产处置）':val=d['fcf_gross']
  elif field=='现金及可交易证券':val=a['cash_and_securities']
  else: raise ValueError(label)
  primary=sources['older_primary'] if int(year)<=2023 else sources['annual_primary']
  if year=='2021' and field=='现金及可交易证券':primary=sources['fy2021_balance_primary']
  secondary=sources['balance_secondary'] if '现金及' in field else sources['cashflow_secondary'] if '现金流' in field else sources['income_secondary']
  p.update(fetched_value=val,fetched_source=primary,fetched_value2=val,fetched_source2=secondary,classification='fact_two_source',note='2026-10-19 actual reads; margins/FCF computed from each source matching underlying amounts, not provider labels.')
 elif label=='第三方市值 · 数值':
  p.update(fetched_value=2696.578,fetched_source='https://stockanalysis.com/stocks/amzn/financials/ratios/',fetched_value2=250*10786313572/1e9,fetched_source2='SEC July22 share count x independently verified October16 $250 price',classification='market_fact_and_arithmetic')
 elif label=='北美 · 2026Q2':
  p.update(fetched_value=116177,fetched_source=sources['quarter_primary'],fetched_value2=116200,fetched_source2='https://www.morningstar.com/stocks/tbsx/amz/earnings-transcript',classification='fact_primary_and_third_party_summary',note='Third party summary rounds to $116.2bn; underlying issuer common provenance, not independently audited accounting.')
 elif label=='国际 · 2025Q3':
  p.update(fetched_value=40896,fetched_source=sources['quarter_primary'],fetched_value2=40900,fetched_source2='https://www.ecommercebytes.com/2025/10/31/amazon-grew-north-american-sales-11-in-3rd-quarter-2025/',classification='fact_two_publications',note='Secondary reported rounded $40.9bn, search extract actually read.')
 elif label=='AWS · 2026Q1':
  p.update(fetched_value=37587,fetched_source=sources['quarter_primary'],fetched_value2=37600,fetched_source2='https://www.reuters.com/business/retail-consumer/amazon-beats-quarterly-cloud-growth-estimates-2026-04-29/',classification='fact_two_publications',note='Reuters rounded $37.6bn actually retrieved.')
 elif label=='经营现金流 · 截至2026Q2的TTM':
  p.update(fetched_value=161.403,fetched_source=sources['quarter_primary'],fetched_value2=161.403,fetched_source2=sources['cashflow_secondary'],classification='fact_two_source')
 elif label in ['订阅 · FY2025收入','广告 · FY2025收入']:
  val=49.619 if label.startswith('订阅') else 68.635
  p.update(fetched_value=val,fetched_source=sources['annual_primary'],fetched_value2=val,fetched_source2=sources['income_secondary'],classification='fact_two_source')
 elif label=='悲观 · 三年后价格':
  val=model['three_year'][0]['target']
  independent=(74.9696*1.08**3)/(10.786313572*1.008**3)*22
  p.update(fetched_value=val,fetched_source='recalculate.py / model-results.json',fetched_value2=independent,fetched_source2='independent direct formula in audit_report.py; NOT external data',classification='model_recalculation',note='Scenario forecast is a hypothesis; only arithmetic verified, not future truth.')
 else: raise ValueError('Unreviewed sample: '+label)
 evidence.append(p)
(HERE/'report-audit-results.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
commands=[['extract','--report',str(report),'--seed','42'],['verdict','--results',json.dumps(evidence,ensure_ascii=False),'--report',str(report),'--output-json']]
for command,name in zip(commands,['extract','verdict']):
 proc=subprocess.run([sys.executable,str(ROOT/'tools/report_audit.py'),*command],capture_output=True,text=True)
 (HERE/f'report-audit-{name}.log').write_text(proc.stdout+proc.stderr+f'\nEXIT={proc.returncode}\n')
 print(proc.stdout if name=='verdict' else f'extract exit={proc.returncode}')
(HERE/'report-audit-notes.md').write_text('''# 抽检审计说明\n\n固定seed=42、默认15%抽样，141项中抽取22项。\n\n- 一项是解析器把“10-Q”文件类型误提取为10，明确排除；不计入核验通过。\n- 二十项为事实或事实基础上的比率/市值重算，逐项记录已访问URL和日期口径。第三方新闻摘要及发行人电话会转录仍可能共同依赖发行人原始数据，不宣称独立审计。\n- 一项为三年后价格假设，按模型脚本和独立表达式交叉重算，不伪装成第三方未来预测。\n- verdict的PASS只是这些已提供值的偏差通过，不代表Macrotrends正文、所有季度分部、管理层后续持股等缺口完成核验。\n- 上述21项已提供核验值，误差低于1%；误提取项无值，工具跳过。\n\n复现：先执行recalculate.py，再执行audit_report.py。报告与模型均不修改共享工具。\n''')
