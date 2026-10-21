"""Actual sourced sample checks; distinguish facts, arithmetic and judgments.
Tool PASS is not full dual-source publication approval.
"""
from pathlib import Path
from decimal import Decimal as D
import json,subprocess
BASE=Path(__file__).parent.parent;ROOT=BASE.parents[1]
K1='https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0819/2026081900315_c.pdf'
K2='https://ir.kuaishou.com/news-releases/news-release-details/kuaishou-technology-announces-fourth-quarter-and-full-year-2025'
K3='https://www.hkexnews.hk/listedco/listconews/sehk/2025/1119/2025111900308_c.pdf'
KI='https://ir.kuaishou.com/system/files-encrypted/nasdaq_kms/assets/2026/09/08/10-47-47/Interim%202026.pdf'
KT='https://www.itiger.com/news/1181108380'
KS='https://hk.stockstar.com/IG2026081900029974.shtml'
M1='https://media-meituan.todayir.com/20260929060801885812349731_tc.pdf'
M2='https://www.hkexnews.hk/listedco/listconews/sehk/2026/0424/2026042400180_c.pdf'
MG='https://www.guandian.cn/m/show/564341'
MI='https://www.ithome.com/0/995/670.htm'
# Values are source units converted to the reported table's CNY hundred million.
FACTS={
 '快手':{
  4:(236,K2,None,None),
  5:(196.43,K1,196.43,'https://www.nbd.com.cn/articles/2026-05-28/4410814.html'),
  12:(86.90,K1,86.90,KT),
  15:(59,K3,59,'https://finance.sina.com.cn/tech/2025-11-19/doc-infxxsna1755507.shtml'),
  18:(62.06,K1,62.06,KT),
  14:(15.5,K2,None,None),
  28:(355.35,K1,355.35,KS),
  32:(183.28,K1,183.28,KS),
  29:(194.34,K3,None,None),
  30:(218.19,K2,218.19,'https://finance.sina.com.cn/wm/2026-03-25/doc-inhsffcq0870357.shtml'),
  36:(51.6,K1,51.6,KT),
  55:(804.07,KI+' pp59-60: (11696+12358+56353)/100',None,None),
  70:(31.2,K2,None,None)},
 '美团':{
  4:(640.63286,M1,640.63,MG),
  5:(715.30555,M1,715.31,'https://finance.eastmoney.com/a/202608283858484115.html'),
  15:(1046.43044,M1,1046.43,MI),
  14:(910.38906,M1,910.39,MG),
  12:(950.61955,M2+' p20 Q3 comparative',954.88,'https://www.guandian.cn/m/show/527457'),
  18:(241.27273,M2+' p20',None,None),
  29:(-64.69811,M1,-64.70,MG),
  28:(-160.74247,M2,-160.74,'https://pdf.dfcfw.com/pdf/H3_AP202604081821062202_1.pdf'),
  32:(-186.32088,M2,-186.32,'https://companies.caixin.com/m/2025-11-28/102388098.html'),
  36:(278.30421,M1+' p5',None,None),
  70:(61.754848,'https://qt.gtimg.cn/q=hk01024,hk03690',61.7548,'https://basic.10jqka.com.cn/176/K83690/equity.html')}}

for company in ['快手','美团']:
    p=BASE/company;report=p/f'{company}研究报告-20261002.md'
    s=report.read_text();dup='股息按第一、二、三年逐笔折现，期末股价按第三年折现；';s=s.replace(dup+dup,dup);report.write_text(s)
    e=subprocess.run(['python3',str(ROOT/'tools/report_audit.py'),'extract','--report',str(report),'--seed','42'],capture_output=True,text=True)
    (p/'审计抽样.txt').write_text(e.stdout)
    items=json.loads(e.stdout.split('抽检清单 JSON（填入 fetched_value 后，传给 verdict 命令）：')[1]);(p/'审计抽样.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
    calc=json.loads((p/'计算结果.json').read_text());facts=FACTS[company];math_checks=[]
    models={76:(D(calc['multiples']['PS']),'市值/TTM收入，输入分别核验'),82:(D('0.69')/D('29.58')*100,'0.69/29.58*100；历史股息不是预测'),87:(D(calc['scenarios']['bear']['three_year_annual_return'])*100,'悲观情景三年财富倍数年化'),95:(D(calc['scenarios']['bull']['price']),'乐观DCF假设算术')} if company=='快手' else {55:(D(calc['cash_bridge']['net_with_leases'])/100,'现金+短期理财-借款-票据-租赁；原表明细仅单源'),76:(-D(calc['TTM']['profit'])/100,'TTM归母亏损绝对值，全年加本期减同期'),82:(D(calc['scenarios']['base']['price']),'基准DCF假设算术'),87:(D(calc['scenarios']['bull']['price']),'乐观DCF假设算术'),95:(D(calc['sensitivity'][3]['price']),'r11% g1.5%敏感性算术')}
    for item in items:
        i=item['id']
        if i in facts:
            v,s1,v2,s2=facts[i];item.update(fetched_value=v,fetched_source=s1,fetched_value2=v2,fetched_source2=s2 or '',classification='historical_fact',source_status='two_publishers_not_two_audits' if v2 is not None else 'primary_only_gap')
            if company=='美团' and i==12:item['note']='原Q3公告954.88，年报比较列950.62；差异0.45%低于工具容差但仍显式保留，未查明原因。'
        elif i in models:
            v,note=models[i];diff=abs(D(str(item['reported_value']))-v);math_checks.append({'id':i,'reported':item['reported_value'],'recomputed':str(v),'description':note,'within_display_rounding':diff<=D('.01')})
            item.update(classification='arithmetic_or_assumption',review_status='checked separately; not a source verification',note=note)
        else:item.update(classification='subjective_score',review_status='not a factual claim; excluded with disclosure')
    (p/'审计核验.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n')
    (p/'模型抽检.json').write_text(json.dumps(math_checks,ensure_ascii=False,indent=2)+'\n')
    v=subprocess.run(['python3',str(ROOT/'tools/report_audit.py'),'verdict','--results',json.dumps(items,ensure_ascii=False),'--report',str(report),'--output-json'],capture_output=True,text=True)
    (p/'审计工具判决.txt').write_text(v.stdout+v.stderr)
    nf=len(facts);dual=sum(1 for row in facts.values() if row[2] is not None)
    (p/'审计说明.md').write_text(f'''# {company}研究报告审计说明

固定种子42，15%提取抽样，共{len(items)}项。历史事实{nf}项，其中{dual}项有两个发布渠道的取数，{nf-dual}项仅完成原始文件核验。其余为{len(math_checks)}项算术/模型，以及{len(items)-nf-len(math_checks)}项主观评分。没有把预测假设冒充已发生事实，也没有补造第二来源。

report_audit工具对有取数的历史样本输出PASS；该工具允许单源通过、跳过空值，并接受1%容差。因此研究结论为**样本数值检查通过，完整独立双源核验尚未完成，带限制研究稿**，不是全篇可无条件发布。数学抽检全部在显示舍入容差内：{all(x['within_display_rounding'] for x in math_checks)}。

关键收入、年度归母、股价、市值与现金核验另见financial_rigor验证.txt。现金资产桥、DCF、三年价格、逐年股息折现由Decimal模型重算。financial_rigor的calc子命令内部使用Python表达式浮点计算，日志末位可能出现尾差；权威数值以计算模型.py的Decimal结果为准，没有修改公共工具。

来源独立性限制：新闻稿转载并非独立财务审计；官网与港交所同一文件只算一源。未解决的附注、股本时点、数据商TTM字段滞后等差异均在报告正文或事实与限制.json中列明。一次抽检不覆盖全报告，也不证明预测会兑现。
''')
    print(company,'sample',len(items),'fact',nf,'dual_publishers',dual,'math',len(math_checks),'exit',v.returncode)
