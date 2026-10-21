#!/usr/bin/env python3
"""Frozen independently reviewed source observations; preserves extracted false positive."""
import json,subprocess,sys
from pathlib import Path
from decimal import Decimal as D
P=Path(__file__).resolve().parent;R=P.parents[2];report=P/'微软投资研究报告-20261019.md'
a=subprocess.run([sys.executable,str(R/'tools/report_audit.py'),'extract','--report',str(report),'--seed','42'],capture_output=True,text=True)
(P/'report_extract.log').write_text(a.stdout)
rows=json.loads(a.stdout[a.stdout.index('[\n'):])
base='https://www.microsoft.com/en-us/investor/earnings/fy-2026-'
q1=base+'q1/press-release-webcast';q2=base+'q2/press-release-webcast';q3=base+'q3/press-release-webcast';q4=base+'q4/press-release-webcast'
a24='https://www.microsoft.com/investor/reports/ar24/index.html';a23='https://www.microsoft.com/investor/reports/ar23/index.html'
sa='https://stockanalysis.com/stocks/msft/financials/'
# Numeric values here were read from original sources, not copied from reported_value.
evidence={
7:(D(89035)-D(23886),a24+' OCF-capex',65149,sa+'cash-flow-statement/','derived fact'),
8:(104757,a23,104749,sa+'balance-sheet/','fact; standardized source differs slightly'),
2:(72738,a24,72738,sa+'income-statement/','fact'),
9:(211915,a24,211915,sa+'income-statement/','fact'),
23:(D(118548)-D(44477),a24+' OCF-capex',74071,sa+'cash-flow-statement/','derived fact'),
24:(75543,a24,75531,sa+'balance-sheet/','fact; standardized source differs slightly'),
29:(136162,q4,136162,sa+'cash-flow-statement/','fact'),
27:(D(193893)/D(281724)*100,q4+' gross/revenue',68.82,sa+'income-statement/','derived fact'),
36:(D(155237)/D(331839)*100,q4+' operating/revenue',46.78,sa+'income-statement/','derived fact'),
41:(33020,q1,None,'','fact; primary only'),
51:((D(13756)-D(6008))/D(13756)*100,q1+' (13756-6008)/13756',None,'','derived; primary only'),
56:(D(20599)/D(34116)*100,q2+' 20599/34116',None,'','derived; primary only'),
58:((D(32907)/D(25544)-1)*100,q2+' 32907/25544-1',None,'','derived; primary only'),
60:(D(13873)/D(32907)*100,q2+' 13873/32907',None,'','derived; primary only'),
57:(32907,q2,None,'','fact; primary only'),
63:((D(14250)-D(6302))/D(14250)*100,q2+' (14250-6302)/14250',None,'','derived; primary only'),
71:((D(34681)-D(15120))/D(34681)*100,q3+' (34681-15120)/34681',None,'','derived; primary only'),
72:(D(13753)/D(34681)*100,q3+' 13753/34681',None,'','derived; primary only'),
108:(1.70,'https://stockanalysis.com/stocks/msft/statistics/',None,'','third-party forecast metric, not independently verified'),
156:(155237,q4,155237,sa+'income-statement/','fact'),
115:(700000,'reproduce.py profits[2]; declared scenario assumption',None,'','ASSUMPTION: consistency only, not outside fact'),
130:(25,'reproduce.py prob[2]; declared subjective probability',None,'','ASSUMPTION: consistency only, not outside fact'),
140:((1-D('.02')/D('.21'))/(D('.10')-D('.02')),'terminal_value.py pe and independent Decimal recomputation',None,'','MODEL: arithmetic only, not outside fact')}
for row in rows:
    if row['id']==109:
        row.update(classification='EXTRACTION FALSE POSITIVE',review_note='Parser extracted source identifier [S9] as financial datum 9; excluded, preserved original row. Not a missing financial fact.')
        continue
    v,s,v2,s2,category=evidence[row['id']]
    row.update(fetched_value=float(v),fetched_source=s,fetched_value2=v2,fetched_source2=s2,classification=category)
(P/'report_audit_results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
res=subprocess.run([sys.executable,str(R/'tools/report_audit.py'),'verdict','--results',json.dumps(rows,ensure_ascii=False),'--report',str(report),'--output-json'],capture_output=True,text=True)
(P/'report_verdict.log').write_text(res.stdout+res.stderr)
print(res.stdout)
cmd=[sys.executable,str(R/'tools/terminal_value.py'),'audit','--currency','USD','--r','.10','--roic','.21','--g','.02,.03,.04','--rf','.051','--beta','1','--discrete-risks','AI overcapacity:情景,agent displacement:情景,forced breakup:未建模,export shutdown:未建模']
end=subprocess.run(cmd,capture_output=True,text=True)
(P/'terminal_final_audit.log').write_text('$ '+' '.join(cmd)+'\n'+end.stdout+end.stderr+'\nexit='+str(end.returncode))
sys.exit(max(res.returncode,end.returncode))
