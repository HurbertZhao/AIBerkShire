#!/usr/bin/env python3
"""Audit fixed random sample; classify assumptions separately from facts.
Source values were read from the linked documents on 2026-10-19.
No forecast is presented as externally verified fact.
"""
from pathlib import Path
from decimal import Decimal as D, getcontext
import json
import re
import subprocess
import sys

getcontext().prec = 40
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORT = HERE / '泡泡玛特研究报告-20261019.md'
TOOL = ROOT / 'tools/report_audit.py'
def save(name, obj):
    HERE.joinpath(name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str)+'\n')
def clean_log(text):
    return '\n'.join(line.rstrip() for line in re.sub(r'\x1b\[[0-9;]*m', '', text).splitlines())+'\n'
annual = 'https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0421/2026042100395_c.pdf'
interim = 'https://www.hkexnews.hk/listedco/listconews/sehk/2026/0924/2026092400544.pdf'
oldinterim = 'https://www1.hkexnews.hk/listedco/listconews/sehk/2025/0819/2025081900626.pdf'
sa = 'https://stockanalysis.com/quote/hkg/9992/financials/'
sacf = sa+'cash-flow-statement/'
finet = 'https://www.finet.hk/newscenter/news_content/6a86c2d02308290c11eadd7c'

raw = subprocess.run([sys.executable,str(TOOL),'extract','--report',str(REPORT),'--seed','42'],capture_output=True,text=True,check=True).stdout
HERE.joinpath('审计抽样.txt').write_text(clean_log(raw))
sample = json.loads(raw[raw.index('\n[\n')+1:])
save('审计原始样本.json',sample)
facts = {
 '营业收入 · 2024': ('130.37749',annual,'130.38',sa),
 '营业收入 · 2025': ('371.20052',annual,'371.20',sa),
 '毛利率 · 2025': ('72.1',annual,'72.10',sa),
 '毛利率 · 2024': ('66.8',annual,'66.79',sa),
 '毛利率 · 2022': ('57.5',annual,'57.49',sa),
 '收入 · 同比或解释': ('23.8',interim,'23.8',finet),
 '中国收入，含港澳台 · 同比或解释': ('47.3',interim,'47.3',finet),
 '中国收入，含港澳台 · 2026上半年': ('122.00509',interim,'122',finet),
 '美洲 · 2025上半年': ('22.64882',interim,None,None),
 '经营现金流CFO · 2025上半年': ('59.77473',interim+' 报告第69页',None,None),
}
calcs = {
 '海外合计收入 · 同比或解释': ((D('4972412')/D('5593464')-1)*100,interim+' 区域合计同口径公式',None,None),
 'TTM经营现金流，亿元人民币 · 数值': (D('108.65152')-D('59.77473')+D('36.37324'),annual+' 与 '+interim+' 年度减上年半年加本年半年','85.25',sacf),
 '当前PB · 数值': (D('142.2')*D('1331779203')*D('.8520')/D('23059024000'),'价格×期末股数×汇率/归母净资产；见市场证据及中报',None,None),
}
assumptions = {
 '2036经营归母净利率 · 全球多场景品牌，乐观': '25',
 '2036股东现金转换率 · 全球多场景品牌，乐观': '95',
 '首年股东现金转换率 · 基准': '85',
}
groups = {'facts':[], 'calculations':[], 'assumptions':[]}
for row in sample:
    label = row['label']
    if label in assumptions:
        assert D(str(row['reported_value'])) == D(assumptions[label])
        row.update({'classification':'model_assumption','status':'与模型输入一致；不可外部验证为未来事实'})
        groups['assumptions'].append(row)
        continue
    kind = 'facts' if label in facts else 'calculations'
    v1,s1,v2,s2 = (facts if kind=='facts' else calcs)[label]
    row.update({'fetched_value':str(v1),'fetched_source':s1,'fetched_value2':v2,
                'fetched_source2':s2,'classification':kind,
                'independent_second_source': bool(v2 is not None)})
    groups[kind].append(row)

# Directed checks supplement the regex sample, which misses most prose numbers.
direct = [
 ('股价，港元','142.2','142.2','ETNet 2026-10-16','142.2','Webull 2026-10-16'),
 ('股本，股','1331779203','1331779203','HKEX 九月月报','1331779203','Webb 10月16日'),
 ('2026H1归母，亿元','50.38','50.38384',interim,'50.38',finet),
 ('2026H1现金等价物，亿元','124.42','124.42065',interim,'124.42065','ETNet资产负债表，市场证据F8'),
 ('2026H1库存周转，天','201','201',interim+' 第32页',None,None),
 ('2025H1库存周转，天','83','83',oldinterim+' 第32页',None,None),
 ('2026H1会员复购，%','51.6','51.6',interim+' 第13页',None,None),
 ('2025H1会员复购，%','50.8','50.8',oldinterim+' 第20页',None,None),
]
for n,(label,reported,v1,s1,v2,s2) in enumerate(direct,1001):
    groups['facts'].append(dict(id=n,label=label,reported_value=reported,unit='',
        fetched_value=v1,fetched_source=s1,fetched_value2=v2,fetched_source2=s2,
        classification='directed_fact',independent_second_source=bool(v2 is not None)))

for name, vals in groups.items():
    save('审计-'+name+'.json', vals)
    if name=='assumptions': continue
    out = subprocess.run([sys.executable,str(TOOL),'verdict','--results',json.dumps(vals,ensure_ascii=False),
                          '--report',REPORT.name+' '+name],capture_output=True,text=True,check=True).stdout
    assert '【准出】' in out and '不通过: \x1b[91m0' in out
    HERE.joinpath('审计-'+name+'-判决.txt').write_text(clean_log(out))

# Independent model recomputation from report endpoints, without importing the model script.
model = json.loads(HERE.joinpath('计算结果.json').read_text())
independent = {}
for k, p in {'bear':('340','250','.20','.12','.85','.85','0'),
             'base':('400','700','.25','.22','.85','.90','.02'),
             'bull':('440','1200','.28','.25','.85','.95','.03')}.items():
    a,b,m0,m9,c0,c9,g = map(D,p)
    flows = []
    for t in range(10):
        weight = D(t)/9
        # Direct weighted geometric endpoints, unlike iterative growth used in main model.
        rev = a**(1-weight)*b**weight
        flows.append(rev*(m0*(1-weight)+m9*weight)*(c0*(1-weight)+c9*weight))
    def pv(rate):
        result = sum(cf/(1+rate)**(t+1) for t,cf in enumerate(flows))
        result += flows[-1]*(1+g)/(rate-g)/(1+rate)**10
        result += D('124.42065')+D('15.20187')-40
        return result/D('13.31779203')/D('.8520')
    value = pv(D('.11'))
    assert abs(value-D(model['models'][k]['price_hkd']))<D('0.0000000001')
    independent[k] = {'value_hkd': value,'2036_profit':b*m9,'2036_cash':flows[-1]}
    if k=='base':
        independent['sensitivity'] = {str(r):pv(r) for r in (D('.09'),D('.11'),D('.13'))}
save('独立估值复算.json',independent)

text = '''# 审计说明

审核对象：泡泡玛特研究报告-20261019.md；截至2026-10-19。

固定种子42、默认15%随机抽检，提取104项、抽取16项：10项历史事实、3项派生计算、3项未来模型假设。另定向补核8项关键事实，防止正文中的库存、复购、现金和价格未被正则抽样覆盖。

- 历史事实及定向补核共18项：全部与列明来源相符，偏差均不超过1%；其中12项有独立第二取数渠道，6项采用公司原始披露，未伪装成独立双源。细分表数据取数渠道单一的边界已披露。
- 派生计算3项：全部通过公式与输入核验；TTM经营现金流另与StockAnalysis核对。
- 模型假设3项：只核对主文与模型输入一致，不交给工具假装未来事实已经验证。
- 三情景全部采用独立Decimal公式复算，与主模型误差低于0.0000000001港元；此项只检验算术，不检验假设实现概率。
- 无解析误抓项，无空值被当作通过，无核验失败和未处理警告。

工具文件保留抽样及判决；“准出”限定为抽中的历史/公式一致。报告的十年经营假设、风险判断和价格区间不具有事实核验意义。正文新增的分部利润率、库存同比、汇兑和税款桥等，另由经营底稿Decimal附录逐项复算。

特别口径：库存同比用2025H1的83天对2026H1的201天；复购同比用50.8%对51.6%；THE MONSTERS不是LABUBU单款收入；股份采用期末股数，归母利润与集团现金流区别列示；租赁负债付款已扣于现金流时，估值不再重复减全部租赁债务。

数据商的Inventory含预付存货，与公司净库存不能硬对；部分数据商经营利润及租赁后FCF采用标准化口径，本稿采用公司原报逐项构造，不以数据商结果替换。

financial_rigor.py的calc子命令内部存在先浮点求值再转换Decimal的实现；本研究没有修改共享工具。严格精算以本目录Decimal脚本为准，共享工具承担市值、交叉验证和显示精度下的算术复核。

未纳入发布的内容：无来源预测、未取得的Q3实际数据、私人账户信息，以及完整第三方原文镜像。所有历史报告保持原状。
'''
HERE.joinpath('审计说明.md').write_text(text)
print('PASS: 16 samples classified; 18 facts + 3 calculations; 3 assumptions disclosed; three scenario values reproduced.')
