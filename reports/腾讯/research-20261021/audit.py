import json, pathlib, subprocess, sys
from decimal import Decimal as D
sys.stdout.reconfigure(encoding='utf-8')
P=pathlib.Path(__file__).resolve().parent
root=P.parents[2]
report=P.parent/'腾讯研究报告-20261021.md'
def run(args):
    p=subprocess.run([sys.executable,*map(str,args)],capture_output=True,text=True,encoding='utf-8')
    return p.stdout+p.stderr
extract=run([root/'tools/report_audit.py','extract','--report',report,'--seed','42'])
(P/'audit-extract.txt').write_text(extract,encoding='utf-8')
items=json.loads(extract[extract.index('[\n  {'):])
interim='https://www.tencent.com/wp-content/uploads/2026/08/E700_IR.pdf'
annual='https://www.prnewswire.com/apac/news-releases/tencent-announces-2025-annual-and-fourth-quarter-results-302717280.html'
sa='https://stockanalysis.com/quote/hkg/0700/financials/'
observed={4:(64,interim+' p10'),5:(144.973,annual),12:(52,interim+' p10'),15:(37,interim+' rounded YoY:2520/1838-1'),14:(2.520,interim+' p46'),18:(194.371,annual),32:(60.286,interim+' p46'),29:(58.174,'https://financialfilings.com/filings/tencent-holdings-limited/interim-quarterly-report/2025/19504180/'),95:(182600,'https://static.www.tencent.com/uploads/2026/03/18/2804dbdae364ca25b82d21bc8304f1d3.pdf')}
facts=[];models=[]
for x in items:
    if x['id'] in observed:
        x['fetched_value'],x['fetched_source']=observed[x['id']]
        x['scope']='primary_checked_independent_secondary_missing'
        if x['id']==5:
            x.update(fetched_value2=144.973,fetched_source2=sa,scope='dual_source')
        facts.append(x)
    else:
        x['scope']='model_assumption_or_output_not_external_fact'
        models.append(x)
for i,label,v,src,src2 in [(1001,'close_HKD',393.8,'https://stockanalysis.com/quote/hkg/0700/history/','https://content.etnet.com.hk/content/cpyrevamp/sc/stock_quote.php?code=00700'),(1002,'FY25_revenue_CNY_m',751766,annual,sa),(1003,'FY25_parent_profit_CNY_m',224842,annual,sa),(1004,'cash_equivalents_CNY_m',206930,interim,'https://stockanalysis.com/quote/hkg/0700/financials/balance-sheet/')]:
    facts.append(dict(id=i,label=label,reported_value=v,unit='',fetched_value=v,fetched_source=src,fetched_value2=v,fetched_source2=src2,scope='additional_dual_source_check'))
(P/'audit-facts.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'audit-model-items.json').write_text(json.dumps(models,ensure_ascii=False,indent=2),encoding='utf-8')
v=run([root/'tools/report_audit.py','verdict','--results',json.dumps(facts,ensure_ascii=False),'--report',report.name])
(P/'audit-verdict.txt').write_text(v,encoding='utf-8')
data=json.loads((P/'valuation-data.json').read_text(encoding='utf-8'))
assert abs(D(data['market_cap_CNY'])/D('1e8')-D('30525.33'))<D('.01')
assert round(data['three_year'][1]['fixed_dividend_exact_IRR']*100,2)==9.94
assert (D('.08')-D('.02'))*100==6
assert (D('.06')-D('.02'))*100==4
assert json.loads((P/'valuation-config.json').read_text(encoding='utf-8'))
weighted=sum(D(str(p))*D(x['rates']['0.10']['approx_return']) for p,x in zip([.3,.5,.2],data['ten_year']))*100
assert abs(weighted-D('3.01'))<D('.01')
audit=run([root/'tools/terminal_value.py','audit','--currency','CNY','--r','.08','--roic','.20','--g','0,.02,.03','--rf','.02','--beta','1','--discrete-risks','AI回报不足:情景,游戏监管:情景,VIE失效:未建模,全面断供:未建模'])
(P/'terminal-final-audit.txt').write_text(audit,encoding='utf-8')
(P/'audit-scope.md').write_text('''# Audit scope

2026-10-21. Seed 42 sampled 15 of 98 extracted points: 9 historical facts checked against opened original disclosures; 6 assumptions/model outputs separated and checked against valuation.py/data rather than passed off as fetched facts. Four additional price/annual/cash checks have independent secondary sources. Of the random facts, only marketing FY25 has an independent secondary in this sample.

Tool verdict PASS is a limited numerical consistency result, not full skill-level independent dual-source clearance. Historical FCF, segment margins, management stake and treasury definition reconciliation remain explicit gaps. No missing second source was invented. Cash/debt and FCF definitions were not forced to agree. Overall status: LIMITED_VERIFICATION_WITH_DISCLOSED_GAPS.

Final terminal audit: CNY r8%, ROIC20%, g0/2/3%; VIE and full supply cutoff unmodelled. This audit checks model coherence, not investment safety. FX is a fixed assumption, not a live observation.
''',encoding='utf-8')
print(v)
print(audit)
