from pathlib import Path
import json,subprocess,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
text=(P/'report_audit_extract.log').read_text(); results=json.loads(text[text.index('\n[\n')+1:])
annual='https://stockanalysis.com/stocks/aapl/financials/'
quarter='https://stockanalysis.com/stocks/aapl/financials/?p=quarterly&type=as-reported'
k22='https://www.sec.gov/Archives/edgar/data/320193/000032019322000108/aapl-20220924.htm'
k23='https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm'
k25='https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm'
q1='https://www.apple.com/newsroom/pdfs/fy2026-q1/FY26_Q1_Consolidated_Financial_Statements.pdf'
q2='https://www.apple.com/newsroom/pdfs/fy2026q2/FY26_Q2_Consolidated_Financial_Statements.pdf'
q3='https://www.apple.com/newsroom/pdfs/fy2026q3/FY26_Q3_Consolidated_Financial_Statements.pdf'
q4='https://www.apple.com/newsroom/pdfs/fy2025-q4/FY25_Q4_Consolidated_Financial_Statements.pdf'
facts={7:(99803,k22,99803,annual),9:(93736,k25,93736,annual),8:(96995,k25,96995,annual),23:(162099,k23,162099,annual),24:(156650,k25,156650,annual),29:(180683/391035*100,k25+' gross profit / revenue',46.21,annual),27:(170782/394328*100,k22+' gross profit / revenue',43.31,annual),36:(104038-11085,k22+' CFO-capex',92953,annual),51:(6914,q2,6914,quarter),56:(7883,q3,7883,quarter),58:(30013,q1,30013,quarter),60:(30739,q3,30739,quarter),57:(28750,q4,28750,quarter),63:(111184,q2,111184,quarter),71:(28055,q2,None,'未取得独立第三方该季度地域数'),72:(29395,q3,29400,'https://stockanalysis.com/stocks/aapl/financials/metrics/?p=quarterly (rounded 29.40B)'),108:(39544+22855,q3+' cash+short term securities',62399,'https://stockanalysis.com/stocks/aapl/financials/balance-sheet/'),115:(343.46/8.72,'重算：股价343.46/TTM EPS8.72',39.40,'https://stockanalysis.com/stocks/aapl/statistics/')}
models={130:(8.61*1.08**3*28/1.1**3,'模型重算，不是外部事实；recalculate.py'),140:(1,'自定悲观永续增长假设，terminal_config.json'),144:(7,'自定基准利润增长假设，recalculate.py'),152:(4,'自定乐观永续增长假设，terminal_config.json')}
for x in results:
 i=x['id']
 if i in facts:
  a,b,c,d=facts[i];x.update(fetched_value=a,fetched_source=b,fetched_value2=c,fetched_source2=d,verification_type='historical_fact_or_calculation')
 elif i in models:
  a,b=models[i];x.update(fetched_value=a,fetched_source=b,verification_type='model_assumption_or_recalculation_not_external_validation')
 else:x.update(verification_type='parser_false_positive',note='日期、来源名称或FY26季度标识，不是财务数据点；有意保留空值，不算通过')
(P/'report_audit_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
p=subprocess.run([sys.executable,str(ROOT/'tools/report_audit.py'),'verdict','--results',json.dumps(results,ensure_ascii=False),'--report','苹果投资研究报告-20261019.md'],capture_output=True,text=True)
(P/'report_audit_verdict.log').write_text(p.stdout+p.stderr+'\nExit='+str(p.returncode)+'\n范围：26项抽样，4项解析误报明确排除；18项事实/计算（其中欧洲FY26Q2仅原始一手，未达独立双源），4项模型假设/重算；工具准出不代表双源全面完备。\n')
print(p.stdout[-800:]);print('exit',p.returncode)
