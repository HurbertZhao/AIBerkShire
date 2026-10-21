# -*- coding: utf-8 -*-
from pathlib import Path
from decimal import Decimal as D, getcontext
import json,sys,subprocess
getcontext().prec=40
p=Path(__file__).resolve().parent
s=(p/'audit-extract.txt').read_text(); items=json.loads(s[s.index('\n[\n')+1:])
S=D('1250081601'); eps=(D('82320067101.68')+D('44516880421.86')-D('45402962298.10'))/S
# Independently rebuild sampled formulas from primary financial inputs and explicit assumptions.
def sum_pv(o,g,r,gt,extra):
 total=D(0)
 for i in range(1,11):total+=o*(1+g)**i/(1+r)**i
 total+=o*(1+g)**10*(1+gt)/(r-gt)/(1+r)**10+extra
 return total*D('100000000')/S
checks={
 2:(D('44516880421.86')/D('1e8'),D('445.17'),'fact'),
 7:(D('184811095482.62')/D('1e8'),D('1848.11'),'fact'),
 8:(D('70690750119.06')/D('44516880421.86'),None,'calculation'),
 9:((D('70690750119.06')-D('832142752.28'))/D('44516880421.86'),None,'calculation'),
 16:(sum_pv(D(650),D('-.01'),D('.11'),D(0),D(800)),None,'calculation'),
 15:(D(800),None,'assumption'),18:(D(760),None,'assumption'),
 41:(sum((eps*D('1.04')**i*D('.75') for i in range(1,4)),D(0)),None,'calculation'),
 48:(eps*D('1.08')**3*23/D('1.10')**3+sum((eps*D('1.08')**i*D('.75')/D('1.10')**i for i in range(1,4)),D(0)),None,'calculation')}
primary='2026H1.pdf p5/p35/p82; https://static.cninfo.com.cn/finalpage/2026-08-15/1225475868.PDF'
second='新华社2026-08-14; https://www.xinhuanet.com/enterprise/20260814/7685c37162e94be69135af12ac59aaf6/c.html'
for item in items:
 a,b,kind=checks[item['id']];item['classification']=kind;item['fetched_value']=float(a);item['fetched_source']=primary if kind=='fact' else 'audit.py independent Decimal recomputation' if kind=='calculation' else 'Explicit researcher assumption; no external validation'
 if b is not None:item['fetched_value2']=float(b);item['fetched_source2']=second
 assert abs(D(str(item['reported_value']))-a)/abs(a)<D('.01')
(p/'audit-results.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
z=subprocess.run([sys.executable,str(p.parents[2]/'tools/report_audit.py'),'verdict','--results',json.dumps(items,ensure_ascii=False),'--report','茅台研究报告-20261002','--output-json'],capture_output=True,text=True)
(p/'audit-verdict.txt').write_text(z.stdout+z.stderr)
(p/'audit-notes.md').write_text('''# 茅台核查边界\n\n2026-10-02：报告固定 seed 42 提取55项、抽9项。样本中2项为历史事实（中报与新华社独立取数），5项为公式结果，2项为研究者输入假设。无误提取项目。历史事实双源差异与公式复算差异均不超过1%；假设只核对录入，不能称作事实准出。共享工具机械 verdict PASS 不验证需求、估值与未来回报。\n\n另手工逐表检查五年营收、归母、CFO、capex并运行20项双源一致性检查；最新股本、现金等价物、报价及控股权益另4项。工具cross-validate默认阈值2%，本任务另以Decimal逐项严格检查1%阈值。最终24项均小于1%。\n\n尚未独立双源覆盖的细项：季度产品分部、部分金融余额及现金残余桥接、管理层任命，均由原始公告支持；同行五粮液仅单源概览，不用于本公司目标价。框架研究完成，全面外部数据审计没有完成。\n\n上交所2023年报下载返回非PDF页，未作为有效来源；2023历史采用2024年报比较数。\n''')
print(z.stdout[-1300:])
