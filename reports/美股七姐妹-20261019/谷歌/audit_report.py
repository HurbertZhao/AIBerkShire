#!/usr/bin/env python3
"""Replay the audit against preserved, manually sourced verification evidence.
This does not fetch the web again and does not claim full dual-source coverage.
"""
import json, subprocess, sys
from pathlib import Path
P=Path(__file__).resolve().parent
root=P.parents[2]
report=P/'谷歌投资研究报告-20261019.md'
cmd=[sys.executable,str(root/'tools/report_audit.py')]
r=subprocess.run(cmd+['extract','--report',str(report),'--seed','42'],text=True,capture_output=True,check=True)
(P/'report-extract.log').write_text(r.stdout)
sample=json.loads(r.stdout[r.stdout.index('[\n'):])
evidence=json.loads((P/'audit-results.json').read_text())
lookup={x['id']:x for x in evidence}
updated=[]
for item in sample:
    prior=lookup[item['id']]
    assert prior['label']==item['label'], 'Sample changed; new manual source review required'
    assert prior['reported_value']==item['reported_value'], 'Reported number changed; recheck source'
    prior.update(line_number=item['line_number'],raw_text=item['raw_text'])
    updated.append(prior)
(P/'audit-results.json').write_text(json.dumps(updated,ensure_ascii=False,indent=2))
r=subprocess.run(cmd+['verdict','--results',json.dumps(updated,ensure_ascii=False),'--report',str(report),'--output-json'],text=True,capture_output=True,check=True)
(P/'report-verdict.log').write_text(r.stdout)
print(r.stdout)
