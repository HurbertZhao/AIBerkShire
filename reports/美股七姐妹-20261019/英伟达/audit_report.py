#!/usr/bin/env python3
"""Audit sampled report cells against actually read source observations / explicit model recomputation.
No forecast or author-assigned probability is labelled external verification.
"""
from pathlib import Path
import subprocess,json,sys,collections
p=Path(__file__).resolve().parent; root=p.parents[2]
sys.path.insert(0,str(root/'tools'))
from report_audit import extract_data_points,sample_points
from terminal_value import irr_from_terminal
report=p/'英伟达投资研究报告-20261019.md'
cp=subprocess.run([sys.executable,str(root/'tools/report_audit.py'),'extract','--report',str(report),'--seed','42'],capture_output=True,text=True)
(p/'report-audit-extract.log').write_text(cp.stdout)
items=sample_points(extract_data_points(report.read_text()),ratio=.15,seed=42)
sec23='https://www.sec.gov/Archives/edgar/data/1045810/000104581023000017/nvda-20230129.htm'
sec25='https://www.sec.gov/Archives/edgar/data/1045810/000104581025000023/nvda-20250126.htm'
sec26='https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm'
secq1='https://www.sec.gov/Archives/edgar/data/1045810/000104581026000052/nvda-20260426.htm'
secq2='https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm'
sa='https://stockanalysis.com/stocks/nvda/financials/'
sab='https://stockanalysis.com/stocks/nvda/financials/balance-sheet/'
sas='https://stockanalysis.com/stocks/nvda/statistics/'
# Observations were retrieved independently from these URLs in this run, not inferred from report values.
facts={
7:(1990,sec23,1990,sab,'external_dual'),8:(21208,sec23,21208,sab,'external_dual'),9:(26974,sec23,26974,sa,'external_dual'),
23:(7280,sec25,7280,sab,'external_dual'),24:(25984,sec25,25984,sab,'external_dual'),
29:(81453/130497*100,sec26+' [operating income / revenue]',62.42,sa,'external_dual_derived'),
27:(97858/130497*100,sec26+' [gross profit / revenue]',74.99,sa,'external_dual_derived'),
36:(130387,sec26,130387,sa,'external_dual'),
51:(((22459-15983)/(14304-11009)-1)*100,'SEC FY26 10-K minus Q3 nine months [S1,S4]; calculation',None,'','filing_derived_single'),
58:(74.9,secq1,74.9,'NVIDIA Q1 release (same issuer, NOT independent)','issuer_corroborated'),
56:(7065,secq1,None,'','external_single'),57:((7065/4473-1)*100,secq1+' [computed from two periods]',None,'','filing_derived_single'),
63:((7922/5412-1)*100,secq2+' [computed from two periods]',None,'','filing_derived_single'),60:(88299,secq2,None,'','external_single'),
71:(22443,secq2,22443,sab,'external_dual'),72:(34143,secq2,34143,'NVIDIA Q2 release (same issuer, NOT independent)','issuer_corroborated'),
108:(215938+177837-90805,'SEC annual + H1 current - H1 prior [S1,S7]',302970,sa,'external_dual_derived'),
109:(214.13*24147/228984,'SEC shares/equity + verified price; arithmetic',22.58,sas,'external_dual_derived'),
115:(.35,sas,None,'','external_single_untransparent_method'),
130:(8.18*1.2**3*25/1.1**3,'model recomputation: EPS growth and three-year discount; not fact',None,'','model'),
140:(25,'terminal-config.json author-assigned probability; NOT factual validation',None,'','assumption_consistency'),
144:((1-.01/.4)/(.10-.01),'Gordon model arithmetic; not fact',None,'','model'),
152:(600*(1-.03/.4)/(.10-.03),'Gordon model x terminal profit assumption; not fact',None,'','model'),
172:(214.13,sa,214.13,'https://finance.yahoo.com/quote/NVDA/history/','external_dual')}
for id_,r in [(164,.09),(170,.12)]:
 exp=sum(w*irr_from_terminal(n,214.13*24147,(1-g/.4)/(r-g),10,.005)*100 for w,n,g in zip([.25,.5,.25],[150000,600000,1200000],[.01,.03,.04]))
 facts[id_]=(exp-r*100,'terminal scenario independent arithmetic rerun; not fact',None,'','model')
for item in items:
 val,src,val2,src2,kind=facts[item['id']]
 item.update(fetched_value=val,fetched_source=src,fetched_value2=val2,fetched_source2=src2,verification_kind=kind,retrieved_at='2026-10-19 Asia/Shanghai')
(p/'audit-results.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
cp=subprocess.run([sys.executable,str(root/'tools/report_audit.py'),'verdict','--results',json.dumps(items,ensure_ascii=False),'--report',report.name,'--output-json'],capture_output=True,text=True)
(p/'report-audit-verdict.log').write_text(cp.stdout+cp.stderr)
counts=collections.Counter(x['verification_kind'] for x in items)
(p/'audit-coverage.json').write_text(json.dumps(dict(sample_count=len(items),coverage=dict(counts),tool_verdict_exit_code=cp.returncode,qualification='Tool PASS does not enforce second-source coverage or distinguish assumptions. See verification_kind; single-source items and unmodelled tail risks remain disclosed.'),ensure_ascii=False,indent=2))
print(counts); print(cp.stdout[-700:])
