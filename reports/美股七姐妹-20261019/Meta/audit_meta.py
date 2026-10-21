#!/usr/bin/env python3
"""Audit sampled reported claims against fetched evidence or independent arithmetic.
No fetched value is copied from reported_value. Model checks are explicitly not factual verification.
"""
from pathlib import Path
import json,re,subprocess
from decimal import Decimal as D
P=Path(__file__).resolve().parent; root=P.parents[2]
raw=(P/'audit-extract.log').read_text(); items=json.loads(raw[raw.index('[\n  {'):])
sec23='https://www.sec.gov/Archives/edgar/data/1326801/000132680124000012/meta-20231231.htm'
sec25='https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm'
secq='https://www.sec.gov/Archives/edgar/data/1326801/000162828026050705/meta-20260630.htm'
sa='https://stockanalysis.com/stocks/meta/financials/?p=ttm'; sab='https://stockanalysis.com/stocks/meta/financials/balance-sheet/'
lookup={
'收入 · 2022':(116609,sec23,116609,sa,'external_fact'),
'GAAP 净利润 · 2022':(23200,sec23,23200,sa,'external_fact'),
'GAAP 净利润 · 2023':(39098,sec23,39098,sa,'external_fact'),
'GAAP 净利润 · 2024':(62360,sec25,62360,sa,'external_fact'),
'经营利润率 · 2023':(46751/134902*100,sec23+' derived op/revenue',34.66,sa,'derived_historical'),
'经营利润率 · 2024':(69380/164501*100,sec25+' derived op/revenue',42.18,sa,'derived_historical'),
'经营现金流 · 2024':(91328,sec25,91328,sa,'external_fact'),
'经营现金流 · 2022':(50475,sec23,50475,sa,'external_fact'),
'现金及有价证券 · 2021':(16601+31397,'https://investor.atmeta.com/investor-news/press-release-details/2022/Meta-Reports-Fourth-Quarter-and-Full-Year-2021-Results/default.aspx cash+marketable',47998,sa,'derived_historical'),
'税项调整后EPS（美元） · 日期/说明':(26.54,sa,26.54,'https://stockanalysis.com/stocks/meta/statistics/','parser_context_only'),
'含租赁总债务 · 数值':(83664+2425+26229,secq+' bonds+current/noncurrent operating lease liabilities',112318,sab,'derived_historical'),
'含租赁净负债 · 数值':(83664+2425+26229-15462-74798,secq+' debt minus cash and marketable',22058,sab+' absolute debt position','derived_historical'),
'股东权益 · 数值':(261221,secq,261221,sab,'external_fact'),
'TTM公司口径FCF · 数值':(43585+13170-18883,sec25+' and Q2 2026 company FCF reconciliation',40976-(2524+1805-1225),'StockAnalysis FCF 40976 less trailing finance lease payments, primary lease reconciliation','derived_historical'),
'2025收入 · StockAnalysis原值':(200966,sa,200966,sec25,'external_fact'),
'2022毛利率 · StockAnalysis原值':(79.63,sa,None,'','source_transcription_conflict_retained'),
'2022毛利率 · 处理':(25249,sec23,None,'','parser_context_primary_fact'),
'基准 · 以10%折现的现值':(float(D('29.61')*D('1.12')**3*24/D('1.1')**3),'independent Decimal arithmetic: 29.61*1.12^3*24/1.1^3',None,'','model_recalculation_not_fact'),
'基准 · 2029价格':(float(D('29.61')*D('1.12')**3*24),'independent Decimal arithmetic: 29.61*1.12^3*24',None,'','model_recalculation_not_fact'),
'乐观 · 以10%折现的现值':(float(D('29.61')*D('1.20')**3*28/D('1.1')**3),'independent Decimal arithmetic: 29.61*1.2^3*28/1.1^3',None,'','model_recalculation_not_fact'),
'乐观 · 2036净利润（百万美元）':(1000000*.36,'scenario assumption 1000000 revenue * .36 net margin; not outside forecast',None,'','model_recalculation_not_fact')}
for it in items:
 v,s,v2,s2,kind=lookup[it['label']];it.update(fetched_value=v,fetched_source=s,fetched_value2=v2,fetched_source2=s2,verification_kind=kind)
 if kind=='source_transcription_conflict_retained':it['note']='This verifies quoted third-party figure, not its correctness; GAAP margin is 78.3473%, conflict explicitly resolved in report.'
 if kind.startswith('parser_context'):it['note']='Extractor selected a number in explanation, not the displayed metric. Value checked by its actual context.'
(P/'audit-results.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
r=subprocess.run(['python3',str(root/'tools/report_audit.py'),'verdict','--results',json.dumps(items,ensure_ascii=False),'--report','Meta投资研究报告-20261019.md'],capture_output=True,text=True)
(P/'audit-verdict.log').write_text(r.stdout+r.stderr)
print(r.stdout)
