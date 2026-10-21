#!/usr/bin/env python3
"""Audit observed-source transcription and model arithmetic separately.
This does NOT verify future predictions, original broker PDFs, or a census.
"""
from pathlib import Path
from decimal import Decimal as D
import collections
import json
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REPORT=HERE.parent/'泡泡玛特-机构调研汇总与经营展望-20261021.md'
source=json.loads((HERE/'sources.json').read_text())
records={x['id']:x for x in source['records']+source['official_sources']}
extract=subprocess.run([sys.executable,str(ROOT/'tools/report_audit.py'),'extract','--report',str(REPORT.relative_to(ROOT)),'--ratio','.15','--seed','42'],capture_output=True,text=True,check=True).stdout
(HERE/'audit-extract.txt').write_text('\n'.join(line.rstrip() for line in extract.splitlines())+'\n')
sample=json.loads(extract.split('抽检清单 JSON（填入 fetched_value 后，传给 verdict 命令）：')[1])

# These values were read from the linked public text, not copied from the report.
observed={
    27:('145.19','R09','broker_forecast_transcription'),
    29:('109.9','R11','broker_forecast_transcription'),
    51:('97.72','R26','broker_forecast_transcription'),
    56:('166.9','R25','broker_forecast_transcription'),
    57:('187.7','R25','broker_forecast_transcription'),
    60:('128.7','R21','broker_adjusted_profit_forecast_transcription'),
    63:('169.5','R24','broker_forecast_definition_unresolved'),
    71:('130.83646','F02','issuer_reported_fact'),
}
checks=[]
for row in sample:
    k=row['id']
    if k in observed:
        value,sid,kind=observed[k]
        row.update(classification=kind,fetched_value=float(value),fetched_source=records[sid]['url'],audit_scope='摘录与可见来源一致；机构未来预测不是已实现事实')
        checks.append(row)
    elif k==108:
        val=((D('320')/D('93.96592'))**(D(1)/D(10))-1)*100
        row.update(classification='author_assumption_arithmetic',fetched_value=float(val),fetched_source='Decimal: (320/93.96592)^(1/10)-1',audit_scope='仅核验运算，不验证情景发生概率')
        checks.append(row)
    else:
        row.update(classification='parser_false_positive',audit_scope='抽中了年份、日期、参考编号或B2等级中的数字；非财务数据，不伪造核验值')

# Add purposive checks because many random samples are parser false positives.
extra=[
 ('2026H1营业收入','171.73','171.72921','F01','issuer_reported_fact'),
 ('2026H1归母利润','50.38','50.38384','F01','issuer_reported_fact'),
 ('2026H1海外收入','49.72','49.72412','F01','issuer_reported_fact'),
 ('2026H1海外分部利润','15.08','15.08492','F01','issuer_reported_fact'),
 ('2025H1海外分部利润','24.65','24.64510','F01','issuer_reported_fact'),
 ('2026H1经营现金流','36.37','36.37324','F01','issuer_reported_fact'),
 ('2026年中库存','61.02','61.01530','F01','issuer_reported_fact'),
 ('2025年末库存','54.73','54.72839','F01','issuer_reported_fact'),
 ('高盛9月天猫抖音同比','-44','-44','R01','channel_sample_transcription'),
 ('高盛第三季美国支付样本同比','-58','-58','R01','channel_sample_transcription'),
 ('花旗Q3收入预测同比','-35','-35','R02','broker_forecast_transcription'),
 ('花旗Q4收入预测同比','-17','-17','R02','broker_forecast_transcription'),
 ('高盛当时目标价港元','139.5','139.5','R01','dated_broker_target'),
 ('花旗当时目标价港元','198','198','R02','dated_broker_target'),
 ('长城2028归母预测','166.52','166.52','R13','broker_forecast_transcription'),
]
for idx,(label,report,val,sid,kind) in enumerate(extra,1001):
    checks.append({'id':idx,'label':label,'reported_value':float(report),'fetched_value':float(val),'fetched_source':records[sid]['url'],'classification':kind,'audit_scope':'人工定向补检；预测仅检查摘录，不保证实现'})

def arithmetic(label,reported,value,formula):
    checks.append({'id':2001+sum(x['id']>=2001 for x in checks),'label':label,'reported_value':float(reported),'fetched_value':float(value),'fetched_source':formula,'classification':'author_assumption_arithmetic'})

rev25h2=D('371.20052')-D('138.76276')
for name,g,m,rev,np in [('压力','-.35','.22','322.81','83.62'),('基准','-.25','.25','346.06','93.97'),('修复较快','-.15','.28','369.30','105.70')]:
    h2=rev25h2*(1+D(g))
    arithmetic(name+'2026收入',rev,D('171.72921')+h2,'171.72921 + 232.43776*(1+H2增速假设)')
    arithmetic(name+'2026归母利润',np,D('50.38384')+h2*D(m),'50.38384 + H2收入假设*H2归母净利率假设')
arithmetic('星星人占集团增量比例','68.57',(D('26.49969')-D('3.89363'))/(D('171.72921')-D('138.76276'))*100,'两期IP及集团收入差额；F01')
arithmetic('海外分部利润同比','-38.79',(D('15.08492')/D('24.64510')-1)*100,'两期海外分部利润；F01')
arithmetic('2026H1资本开支及租赁后现金','24.10',D('36.37324')-D('6.73560')-D('.50579')-D('5.02889'),'CFO-PPE支出-无形资产支出-租赁付款；F01')

# Tight independent tolerance avoids relying on the shared tool's broad threshold.
for item in checks:
    assert abs(D(str(item['reported_value']))-D(str(item['fetched_value'])))<=D('.00501'),item
assert len(records)==32
assert len(source['records'])==len({r['institution'] for r in source['records']})==29
assert source['full_broker_report_files_obtained']==0

dispositions={
 'scope':'来源摘录和计算核验；不是审计意见，不证实券商原文或预测结果',
 'report':str(REPORT.relative_to(ROOT)),
 'random_sample_count':len(sample),
 'sample_classifications':dict(collections.Counter(x['classification'] for x in sample)),
 'random_sample_dispositions':sample,
 'numeric_checks_including_purposive':len(checks),
 'source_limitations':source['gaps'],
}
(HERE/'audit-dispositions.json').write_text(json.dumps(dispositions,ensure_ascii=False,indent=2)+'\n')
(HERE/'audit-results.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
verdict=subprocess.run([sys.executable,str(ROOT/'tools/report_audit.py'),'verdict','--results',json.dumps(checks,ensure_ascii=False),'--report',REPORT.name],capture_output=True,text=True,check=True)
clean=re.sub(r'\x1b\[[0-9;]*m','',verdict.stdout)
clean='\n'.join(line.rstrip() for line in clean.splitlines())+'\n'
(HERE/'audit-verdict.txt').write_text('范围限定：仅检查公开摘录及计算；不等于研报原文验证或预测兑现保证。\n'+clean)
print(json.dumps({'random':dispositions['sample_classifications'],'numeric_checks':len(checks),'strict_tolerance_passed':True},ensure_ascii=False))
