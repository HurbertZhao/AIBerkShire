# -*- coding: utf-8 -*-
from pathlib import Path
from decimal import Decimal as D
import json, subprocess, sys

P = Path(__file__).resolve().parent
tool = P.parents[1]/'tools'/'report_audit.py'
report = P/'七公司研究总览-20261002.md'
z = subprocess.run([sys.executable, str(tool), 'extract', '--report', str(report), '--seed', '42'], capture_output=True, text=True, check=True)
(P/'总览抽检.txt').write_text(z.stdout)
items = json.loads(z.stdout[z.stdout.index('\n[\n')+1:])
recomputed = json.loads((P/'独立复算.json').read_text())['checks']
def value(company, scenario):
    return next(D(x['recomputed']) for x in recomputed if x['company']==company and x['scenario']==scenario and x['type']=='DCF')

calculations = {2: value('腾讯','中性'), 8: value('拼多多','中性'),
                41: value('泡泡玛特','bull'), 48: value('MiniMax','base')}
assumptions = {9: D(75), 15: D(91), 18: D(780)}
checked, decisions = [], []
for item in items:
    ident = item['id']
    if ident in calculations:
        v = calculations[ident]
        item.update(classification='calculation', fetched_value=float(v),
                    fetched_source='独立复算.py: independently rebuild scenario arithmetic; does not validate forecast')
    elif ident in assumptions:
        v = assumptions[ident]
        item.update(classification='decision_threshold', recorded_assumption=str(v),
                    note='Researcher price condition; not externally verifiable factual claim')
        assert D(str(item['reported_value'])) == v
        decisions.append(item)
        continue
    elif ident == 16:
        v = D('1258.62')
        item.update(classification='historical_quote', fetched_value=float(v),
                    fetched_source='https://hk.finance.yahoo.com/quote/600519.SS/history/ (2026-09-30)',
                    fetched_value2=float(v),
                    fetched_source2='https://cn.investing.com/equities/moutai-historical-data (2026-09-30)',
                    note='Sources already retrieved in Moutai research; this is not an additional independent retrieval')
    else:
        raise AssertionError(('Unreviewed sample after report change', item))
    assert abs(D(str(item['reported_value']))-v)/abs(v) < D('.01')
    checked.append(item)
(P/'总览抽检结果.json').write_text(json.dumps(checked, ensure_ascii=False, indent=2))
(P/'总览价格条件登记.json').write_text(json.dumps(decisions, ensure_ascii=False, indent=2))
z = subprocess.run([sys.executable,str(tool),'verdict','--results',json.dumps(checked,ensure_ascii=False),'--report',report.name,'--output-json'],capture_output=True,text=True,check=True)
(P/'总览审计原始输出.txt').write_text(z.stdout)
print('Overview: 52 extracted / 8 sampled; 1 historical quote and 4 calculations checked, 3 researcher price decisions excluded from factual verdict.')
