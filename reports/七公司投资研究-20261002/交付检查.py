# -*- coding: utf-8 -*-
"""Check report completeness, local links, JSON readability and Python syntax."""
from pathlib import Path
from hashlib import sha256
import json, re

P = Path(__file__).resolve().parent
companies = ['腾讯', '快手', '拼多多', '美团', '泡泡玛特', '茅台', 'MiniMax']
reports = [P/'七公司研究总览-20261002.md']
manifest = []
for company in companies:
    report = P/company/(company+'研究报告-20261002.md')
    text = report.read_text()
    assert all(('第'+number+'步') in text for number in '一二三四五六七八'), company
    assert not re.search(r'\{\{[A-Z_]+\}\}|TODO|TBD|PLACEHOLDER', text), company
    assert any((P/company/file).is_file() for file in ['financial-rigor.txt', 'financial_rigor验证.txt']), company
    assert any((P/company/file).is_file() for file in ['audit-extract.txt', '审计抽样.txt']), company
    reports.append(report)

links_checked = 0
for report in P.rglob('*.md'):
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', report.read_text()):
        if re.match(r'^(https?://|mailto:|#)', target):
            continue
        target = target.strip('<>').split('#',1)[0]
        path = Path(target) if target.startswith('/') else report.parent/target
        assert path.exists() or path.resolve() == P/'交付清单.json', (report, target)
        links_checked += 1

json_count = 0
for file in P.rglob('*.json'):
    if file.name == '交付清单.json':
        continue
    json.loads(file.read_text())
    json_count += 1
python_count = 0
for file in P.rglob('*.py'):
    compile(file.read_text(), str(file), 'exec')
    python_count += 1
for report in reports:
    manifest.append(dict(file=str(report.relative_to(P)), bytes=report.stat().st_size,
                         sha256=sha256(report.read_bytes()).hexdigest()))
result = dict(date='2026-10-02', company_reports=7, overview_reports=1,
              local_links_checked=links_checked, json_files_parsed=json_count,
              python_files_syntax_checked=python_count, reports=manifest,
              caveat='Completeness and arithmetic checks are not independent validation of all financial data or forecasts.')
(P/'交付清单.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='reports'}, ensure_ascii=False))
