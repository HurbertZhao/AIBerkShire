"""Fact-check ledger transcribed from opened sources; this is not a model truth test."""
import json,pathlib,subprocess,sys
P=pathlib.Path(__file__).resolve().parent
s=(P/'audit-extract.txt').read_text();items=json.loads(s[s.index('[\n  {'):])
a='https://investor.pddholdings.com/static-files/92dafbdc-3125-4f2c-a28f-3d61203efbaf'
q3='https://investor.pddholdings.com/news-releases/news-release-details/pdd-holdings-announces-third-quarter-2025-unaudited-financial'
q2='https://investor.pddholdings.com/news-releases/news-release-details/pdd-holdings-announces-second-quarter-2026-unaudited-financial'
sa='https://stockanalysis.com/stocks/pdd/financials/'
# Observations are independently transcribed from original source tables, not copied from the report.
observed={4:(456.414,q2+' cash128918+shortinvestment327496 million'),5:(217.783028,a+' note13'),18:(29.328184,q3+' income statement'),14:(108.276512,q3+' revenue'),12:(53.347570,q3+' revenue notes'),29:(14.2,'https://stockanalysis.com/stocks/pdd/statistics/'),32:(115.25,'https://www.marketbeat.com/stocks/NASDAQ/PDD/chart/ 20261016 row'),36:(97.842539,a+' F-8')}
facts=[];excluded=[]
for x in items:
 if x['id'] in observed:
  x['fetched_value'],x['fetched_source']=observed[x['id']];x['audit_scope']='source_checked; independent_second_missing'
  if x['id']==4:x.update(fetched_value2=456.414,fetched_source2=sa,audit_scope='two_source_fact')
  if x['id']==36:x.update(fetched_value2=97.843,fetched_source2=sa,audit_scope='two_source_fact')
  if x['id']==29:x['audit_scope']='rounded_aggregator_share_fact_only; not_verification_of_current_legal_count'
  facts.append(x)
 else:
  x['audit_scope']='DATE_FALSE_POSITIVE' if x['id']==28 else 'DERIVED_RATIO_OR_MODEL_ASSUMPTION_NOT_EXTERNAL_FACT'
  excluded.append(x)
for i,label,value,other,source,source2 in [(1001,'2025收入十亿元',431.845713,431.846,a+' F-8',sa),(1002,'2025经营现金流十亿元',106.938690,106.939,a+' F-12',sa),(1003,'20261016正规收盘美元',80.97,80.97,'https://stockanalysis.com/stocks/pdd/history/','https://www.marketbeat.com/stocks/NASDAQ/PDD/chart/')]:
 facts.append(dict(id=i,label=label,reported_value=value,fetched_value=value,fetched_source=source,fetched_value2=other,fetched_source2=source2,audit_scope='additional_nonrandom_two_source_fact'))
(P/'audit-facts.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n');(P/'audit-excluded.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2)+'\n')
p=subprocess.run([sys.executable,str(P.parents[2]/'tools/report_audit.py'),'verdict','--results',json.dumps(facts,ensure_ascii=False),'--report','拼多多研究报告-20261020.md'],capture_output=True,text=True);(P/'audit-verdict.txt').write_text(p.stdout+p.stderr)
(P/'audit-scope.md').write_text('''# Audit scope

2026-10-20 live sources, 2026-10-16 locked reference price. Model inputs are not independent verification of model forecasts.

Extract seed42: 94 points, 15 samples. Eight sampled historical observations checked against source pages; seven excluded (one date false positive, two derived ratios, four scenario assumptions). Three additional non-random facts (annual revenue, CFO, price) independently dual sourced. Eleven factual entries in verdict; five have two independent sources. The other six are limited single-source checks. Tool acceptance is narrower than full workflow verification. Overall: LIMITED_FACT_VERIFICATION_WITH_EXPLICIT_GAPS.

Audited 2025 net income97.842539bn versus preliminary99.364469bn, 1.5555% pairwise difference, above project1% even though tool compares each to a midpoint and uses2%. Audited G&A8.157733bn vs preliminary6.635803bn explains the arithmetic difference1.521930bn; no unsupported allocation to a particular quarter. TTM uses audited year plus current half less prior half.

Legal count is March18,2026, not exact October count. 5,693,585,848 ordinary/4=1,423,396,462 ADS. Independent1.42bn is rounded; share-count date gap remains. EPS diluted count is not current legal shares. Existing unvested awards are denominator sensitivity; recurring future SBC is already in normalized GAAP operating profit and is not also added back or compounded as future dilution.

FCFF/RMB9% WACC paired. Core earnings exclude financial investment income; excess assets added once. Lease expense remains operating, no duplicate debt deduction. Merchant float gains are not extrapolated. Surplusassets300bn and liquiditybuffer156.414bn are assumptions, not independently verified distributable amounts; restrictedcash77.274bn excluded; othernoncurrentassets96.383bn not separately added. Company no-dividend policy and restricted netassets checked in annual20F.

Sources: 2025 20-F F-8/F-12/ShareOwnership; 2023 20-F F-7/F-11; 2025Q3/Q4,2026Q1/Q2 original releases; StockAnalysis financial/history/statistics; MarketBeat historical row; official TexasAG Oct16,EU Council customs,US FederalRegister Oct8; NBS,JD andAlibaba official current releases. Source originals were opened remotely; no claim of downloaded PDF archives. Macrotrends opened unsuccessfully and not counted as verified evidence.

No claim that single-source governance, Temu unit economics, undisclosed quarterly capex, ten-year forecasts or investment conclusions are audit PASS.
''');print(p.stdout)
