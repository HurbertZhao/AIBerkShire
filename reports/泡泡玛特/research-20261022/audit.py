#!/usr/bin/env python3
"""Source transcription and independent arithmetic checks; not a forecast audit."""
from pathlib import Path
from decimal import Decimal as D, getcontext
import json, subprocess, sys, re
getcontext().prec=36
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REPORT=HERE/'泡泡玛特投资研究报告-20261022.md'
def command(*args):
    p=subprocess.run([sys.executable,*map(str,args)],capture_output=True,text=True,check=True,cwd=ROOT)
    return p.stdout+p.stderr
text=command(ROOT/'tools/report_audit.py','extract','--report',REPORT.relative_to(ROOT),'--ratio','.15','--seed','42')
(HERE/'audit-extract.txt').write_text(text)
sample=json.loads(text.split('抽检清单 JSON（填入 fetched_value 后，传给 verdict 命令）：')[1])
annual='https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0421/2026042100395_c.pdf'
interim='https://www.hkexnews.hk/listedco/listconews/sehk/2026/0924/2026092400544.pdf'
income='https://stockanalysis.com/quote/hkg/9992/financials/'
cashflow='https://stockanalysis.com/quote/hkg/9992/financials/cash-flow-statement/'
media='https://finance.eastmoney.com/a/202608203847978543.html'
observed={
 7:('FY2021 · 无形资产现金采购','.46250',cashflow,None,None),
 9:('FY2022 · 归母净利润','4.75660',annual,'4.7566',income),
 8:('FY2022 · 收入','46.17324',annual,'46.17',income),
 27:('FY2024 · 固定资产现金采购','3.72668',annual,'3.7267',cashflow),
 23:('FY2024 · 归母净利润','31.25473',annual,'31.25',income),
 24:('FY2024 · 毛利率','66.8',annual,'66.79',income),
 29:('FY2025 · 收入','371.20052',annual,'371.20',income),
 56:('报表经营利润 · 2025H1','60.43741',interim,None,None),
 57:('报表经营利润 · 2026H1','67.24746',interim,'67.25','https://www.guandian.cn/article/20260820/588017.html'),
 60:('经营现金流净额 · 2026H1','36.37324',interim,'36.37','https://finance.sina.com.cn/stock/relnews/hk/2026-08-21/doc-iniparan1301568.shtml'),
 71:('MOLLY · 2026H1收入','9.00631',interim,None,None),
 109:('经营现金流 · 2026H1','36.37324',interim,'36.37','https://finance.sina.com.cn/stock/relnews/hk/2026-08-21/doc-iniparan1301568.shtml'),
 108:('经营现金流 · 2025H1','59.77473',interim,None,None),
 115:('无形资产现金采购 · 2025全年','1.86287',annual,'1.8629',cashflow),
}
n,fx=D('13.31779203'),D('.85619')
cap=D('129.8')*n*fx
base=D('50.38384')+(D('371.20052')-D('138.76276'))*D('.75')*D('.25')
def future(gr,pe):return base*(1+D(gr))**3*D(pe)/n/fx
def pv(gr,pe):return future(gr,pe)/D('1.08')**3
pe=(1-D('.01')/D('.25'))/(D('.08')-D('.01'))
arithmetic={
36:('FY2021 · CFO减两项采购，未扣租赁',D('7.791')-D('2.875')-D('.4625'),'CFO-PPE-intangible; S&P historical inputs'),
51:('归母净利润 · 解读',(D('50.38384')/D('45.74368')-1)*100,'HKEX H1 attributable profit ratio'),
58:('报表经营利润 · 解读',(D('67.24746')/D('60.43741')-1)*100,'HKEX H1 operating profit ratio'),
130:('悲观 · FY2026归母净利润',D('50.38384')+(D('371.20052')-D('138.76276'))*D('.65')*D('.22'),'Author H2 assumptions; arithmetic only'),
144:('乐观 · 再留25%边际HKD',pv('.20','24')*D('.75'),'Independent Decimal three-year model'),
155:('悲观 · 今日折现值HKD',pv('-.12','12'),'Independent Decimal three-year model'),
170:('基准 · 终值PE',pe,'(1-.01/.25)/(.08-.01)'),
176:('乐观 · 十年年化回报近似',((D(320)*pe/cap)**(D(1)/10)-1+D('.015'))*100,'Independent Decimal terminal return, not exact dividend-date IRR'),
}
assumptions={
140:('乐观 · 三年退出PE',D(24)),
152:('悲观 · 三年退出PE',D(12)),
151:('悲观 · 年利润增速假设',D(-12)),
164:('悲观 · FY2036归母利润假设',D(50)),
}
checks=[];dispositions=[]
for row in sample:
    rid=row['id']
    if rid in observed:
        label,value,url,value2,url2=observed[rid];assert row['label']==label
        row.update(classification='observed_financial_fact',fetched_value=float(value),fetched_source=url,
                   fetched_value2=float(value2) if value2 else None,fetched_source2=url2 or '',
                   audit_scope='Transcription; single source where second provider unavailable, not an audit opinion')
    elif rid in arithmetic:
        label,value,formula=arithmetic[rid];assert row['label']==label
        row.update(classification='derived_arithmetic',fetched_value=float(value),fetched_source=formula,
                   audit_scope='Independent Decimal recalculation; does not verify future assumptions')
    elif rid in assumptions:
        label,value=assumptions[rid];assert row['label']==label
        row.update(classification='author_assumption',fetched_value=float(value),
                   fetched_source='Explicit author input specification: '+label,
                   audit_scope='Input transcription only; no claim of external confirmation')
    elif rid==63:
        assert row['reported_value']==3 and 'Q3' in row['raw_text']
        row.update(classification='parser_false_positive',audit_scope='Parser reads Q3 as 3; not a financial amount; excluded explicitly')
        dispositions.append(row);continue
    else:raise AssertionError(row)
    checks.append(row);dispositions.append(row)
def extra(label,reported,value,formula):
    checks.append(dict(id=1001+len(checks),label=label,reported_value=float(reported),fetched_value=float(value),fetched_source=formula,classification='purposive_arithmetic'))
extra('股价乘股本，港元亿','1728.65',D('129.8')*n,'HKEX Sep shares and Oct21 close; Decimal')
extra('人民币市值','1480.05',cap,'HKD market cap times .85619 midpoint')
extra('2026H1租赁后合并现金','24.10',D('36.37324')-D('6.7356')-D('.50579')-D('5.02889'),'HKEX CFO minus PPE, intangible, lease cash payments')
extra('TTM租赁后合并现金','61.56',D('108.65152')-D('59.77473')+D('36.37324')-(D('9.85250')-D('3.53623')+D('6.73560'))-(D('1.86287')-D('.20900')+D('.50579'))-(D('6.08288')-D('2.63592')+D('5.02889')),'FY25-H125+H126 cash bridge')
extra('现金定存减租赁','104.36',D('124.42065')+D('15.20187')+D('2.01773')-D('37.27572'),'HKEX cash and deposit footnotes; not added to equity DCF')
extra('新IP占增量比例','68.6',(D('26.49969')-D('3.89363'))/(D('171.72921')-D('138.76276'))*100,'HKEX group/IP revenue deltas')
extra('基准三年折现价港元','140.24',pv('.06','18'),'Independent Decimal')
extra('基准安全边际价港元','105.18',pv('.06','18')*D('.75'),'Independent Decimal')
annuity=(1-D('1.08')**-10)/D('.08')
flat80=(D(80)*annuity+D(80)*D('1.01')/D('.07')/D('1.08')**10)/n/fx
extra('80现金零增长反向DCF港元','93.97',flat80,'Closed-form annuity plus perpetual terminal; independent of model summation')
for r,report in [('.06','7.00'),('.07','5.17'),('.08','3.64'),('.09','2.33'),('.10','1.18')]:
    returns=[]
    for profit,g in [(50,'0'),(170,'.01'),(320,'.01')]:
        exitpe=(1-D(g)/D('.25'))/(D(r)-D(g))
        returns.append(((D(profit)*exitpe/cap)**(D(1)/10)-1+D('.015'))*100)
    extra('r='+r+'加权十年回报',report,sum(v*w for v,w in zip(returns,map(D,['.3','.5','.2']))),'Independent Decimal terminal PE and weighted geometric returns')
for row in checks:
    v,ref=D(str(row['reported_value'])),D(str(row['fetched_value']))
    assert abs(v-ref)/abs(v)<=D('.01'),row
    if row.get('fetched_value2') is not None:
        assert abs(v-D(str(row['fetched_value2'])))/abs(v)<=D('.01'),row
(HERE/'audit-results.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
(HERE/'audit-dispositions.json').write_text(json.dumps(dict(random_count=len(sample),random_financial_or_model_count=len(sample)-1,
    excluded_false_positives=1,scope='Observed facts, author inputs, and arithmetic classified separately. Not all facts have two providers.',dispositions=dispositions),ensure_ascii=False,indent=2)+'\n')
verdict=command(ROOT/'tools/report_audit.py','verdict','--results',json.dumps(checks,ensure_ascii=False),'--report',REPORT.relative_to(ROOT))
(HERE/'audit-verdict.txt').write_text(verdict)
final=command(ROOT/'tools/terminal_value.py','audit','--currency','CNY','--r','.08','--roic','.25','--g','0,.01,.01','--rf','.02','--beta','1','--discrete-risks','IP热度衰退:情景,海外需求萎缩:情景,授权终止:未建模,重大产品召回:未建模,跨境监管冲击:未建模')
(HERE/'terminal-final-audit.txt').write_text(final)
# Validate relative Markdown artifact links; web links are recorded, not fetched here.
for target in re.findall(r'\]\(([^)]+)\)',REPORT.read_text()):
    if '://' not in target and not target.startswith('#'):
        assert (HERE/target.split('#')[0]).exists(),target
print(verdict)
print(final)
