import json,pathlib,subprocess,sys
P=pathlib.Path(__file__).resolve().parent
s=(P/'audit-extract.txt').read_text();items=json.loads(s[s.index('[\n  {'):])
primary='https://www.tencent.com/wp-content/uploads/2026/08/E700_IR.pdf'
annual='https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0409/2026040901231.pdf'
secondary='https://stockanalysis.com/quote/hkg/0700/financials/'
# Values below transcribed from pages opened on 2026-10-20. They are not copied from report values.
observed={4:(64,primary+' p10'),5:(144.973,annual+' segment note'),12:(52,primary+' p10'),15:(37,primary+' p9'),14:(2.520,primary+' p9'),18:(204.785,primary+' p3'),32:(43.565,primary+' p9'),29:(36.242,'https://financialfilings.com/filings/tencent-holdings-limited/interim-quarterly-report/2025/19504180/'),36:(60.286,primary+' p9'),55:(417.8,'https://stockanalysis.com/quote/hkg/0700/history/')}
facts=[];excluded=[]
for x in items:
 if x['id'] in observed:
  x['fetched_value'],x['fetched_source']=observed[x['id']]
  x['audit_scope']='primary_checked; independent_second_missing'
  if x['id']==5:x.update(fetched_value2=144.973,fetched_source2=secondary,audit_scope='two_source_fact')
  if x['id']==55:x.update(fetched_value2=417.8,fetched_source2='https://ms.investing.com/equities/tencent-holdings-hk-historical-data',audit_scope='two_source_fact; extractor_label_corrected_to_share_price')
  facts.append(x)
 else:
  x['audit_scope']='MODEL_ASSUMPTION_OR_MODEL_OUTPUT_NOT_EXTERNAL_FACT';excluded.append(x)
for i,label,value in [(1001,'2025收入十亿元',751.766),(1002,'2025归母利润十亿元',224.842)]:
 facts.append(dict(id=i,label=label,reported_value=value,unit='CNY_billion',fetched_value=value,fetched_source=annual+' p3',fetched_value2=value,fetched_source2=secondary,audit_scope='additional_nonrandom_two_source_fact'))
(P/'audit-facts.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
(P/'audit-excluded.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2)+'\n')
p=subprocess.run([sys.executable,str(P.parents[2]/'tools/report_audit.py'),'verdict','--results',json.dumps(facts,ensure_ascii=False),'--report','腾讯研究报告-20261020.md'],text=True,capture_output=True)
(P/'audit-verdict.txt').write_text(p.stdout+p.stderr)
(P/'audit-scope.md').write_text('''# Audit scope\n\n2026-10-20 live source checks. Extract seed 42: 98 points, 15 sampled. Ten sampled historical facts checked against opened web pages; five model assumptions/outputs excluded from external factual verdict and reproducible in model.py. Two additional annual facts checked against original and independent StockAnalysis.\n\nThe report_audit tool accepts a single source and can print 准出; that is narrower than this workflow\'s two-independent-source requirement. Only four entries in audit-facts.json have independent dual-source evidence. Other sampled facts have one original source (a mirror remains the same origin). Overall status: LIMITED_FACT_VERIFICATION_WITH_EXPLICIT_GAPS, not full dual-source PASS.\n\nShares: issued 9,092,644,829 (2026-10-15 disclosure), aggregator rounded outstanding 9.00bn; 1.029% difference unresolved, authoritative issued used. Total cash: company 511.154bn vs aggregator 458.904bn are different definitions, not matching observations. Shareholding 8.85% verified in original only; third-party insider percentage is not same definition.\n\nModel: all arithmetic Decimal. Scenarios do not establish future realization. FCFF/WACC paired; net cash added once, investments excluded from operating earnings, SBC deducted once; leases treated as operating. NCI attribution is approximate and investment marks are June snapshots.\n''')
print(p.stdout)
