"""京东研究报告数据抽检：填入取数结果，模型假设与非数据噪声单独分类，不进判决。
复跑：python3 reports/京东/research-20261021/audit.py
"""
from pathlib import Path
from decimal import Decimal as D
import json, sys, subprocess, re

P = Path(__file__).resolve().parent
root = P.parents[2]
sys.path.insert(0, str(root / 'tools'))
import report_audit

report = P.parent / '京东研究报告-20261021.md'
pts = report_audit.sample_points(report_audit.extract_data_points(report.read_text()), ratio=.15, seed=42)

Q2 = 'https://www.sec.gov/Archives/edgar/data/1549802/000119312526347753/d143720dex991.htm'
Q4 = 'https://www.sec.gov/Archives/edgar/data/1549802/000119312526092445/d150586dex991.htm'
F20 = 'https://www.sec.gov/Archives/edgar/data/1549802/000119312526157870/d53690d20f.htm'
SA = 'https://stockanalysis.com/stocks/jd/financials/'
SA_PDD = 'https://stockanalysis.com/stocks/pdd/financials/'

verified = {
    2: (float((D(1309085) - D(657742) + D(662095)) / 100), Q4 + ' FY2025 收入 - ' + Q2 + ' 2025H1/2026H1 收入（推算）', 13134.38, SA + '?p=trailing TTM revenue 1,313,438'),
    7: (314.15, Q2 + ' 十二个月自由现金流表 31,415 百万元', None, ''),
    8: (float((D(3511) - D(920) + D(2286)) / 100), Q4 + ' 与 ' + Q2 + ' 少数股东损益推算', None, ''),
    9: (1928.60, Q4 + ' 资产负债表 应付账款 2024-12-31 192,860 百万元', None, ''),
    23: (1071.31, Q4 + ' 收入分类表 Marketplace and marketing revenues FY2025 107,131 百万元', None, ''),
    24: (18.9, Q4 + ' 收入分类表 同比 18.9%', None, ''),
    27: (1781.52, Q4 + ' 收入分类表 Logistics and other service revenues FY2025 178,152 百万元', None, ''),
    29: (float((D(178152) / D(1309085) * 100).quantize(D('0.01'))), Q4 + ' 178,152/1,309,085（推算）', None, ''),
    51: (float((D('104.40') * D('2688') * D('0.85628') / D('19631')).quantize(D('0.01'))), '推算：市值(104.40港元×2,688百万股×0.85628) / FY2025归母净利润19,631（' + F20 + '）', None, ''),
    56: (978.43, SA_PDD + ' FY2025 net income 97,843 百万元', None, ''),
    57: (float((D('115.88') * D('6.72') * 1000 / D('97843')).quantize(D('0.01'))), '推算：stockanalysis 拼多多市值1,158.8亿美元×6.72/978.43亿元', None, ''),
    58: (float(D('104.40') * D('2688') / 100), '推算：9618.HK 2026-10-20 收盘104.40（stockanalysis/Yahoo）× 2,688百万股（' + Q2 + '）', None, ''),
    60: (float((D('104.40') * D('2688') * D('0.85628') / D('6.72') / 100).quantize(D('0.1'))), '推算：人民币市值 / 中国外汇交易中心2026-10-20中间价6.7200', 359.9, 'stockanalysis ADS口径 35.99B 美元（26.78×1,344百万ADS）'),
    63: (16.24, 'financial-rigor.txt verify-valuation：178.79/11.007', None, ''),
    71: (float(-(D(3534) + D(13555) + D(16607) + D(36196)) / 100), Q2 + ' 资产负债表 短期借款3,534+优先票据13,555+16,607+长期借款36,196', None, ''),
    72: (float(-(D(228961) - D(188379)) / 100), Q2 + ' 资产负债表 应付账款 228,961 − 188,379', None, ''),
}
model_ids = {108, 109, 115, 130, 140}
noise_ids = {153, 159, 36}
facts, classes = [], []
for x in pts:
    if x['id'] in model_ids:
        x.update(classification='MODEL_ASSUMPTION_OR_OUTPUT', external_fact_verification=False, fetched_value=None,
                 note='情景假设或模型输出，见 inputs.json / results.json / terminal-value.txt，已复算一致但不是外部事实')
        classes.append(x); continue
    if x['id'] in noise_ids:
        x.update(classification='NON_DATA_EXTRACTION_NOISE', fetched_value=None,
                 note='提取到的是股票代码或年份，不是财务数据点')
        classes.append(x); continue
    v, src, v2, src2 = verified[x['id']]
    x.update(fetched_value=v, fetched_source=src, fetched_value2=v2, fetched_source2=src2,
             classification='FACT_DUAL_SOURCE' if v2 is not None else 'FACT_SINGLE_SOURCE_OR_DERIVED')
    facts.append(x); classes.append(x)

P.joinpath('audit-classified.json').write_text(json.dumps(classes, ensure_ascii=False, indent=2) + '\n')
z = subprocess.run(['python3', str(root / 'tools/report_audit.py'), 'verdict', '--results', json.dumps(facts, ensure_ascii=False),
                    '--report', report.name, '--output-json'], capture_output=True, text=True)
txt = re.sub(r'\x1b\[[0-9;]*m', '', z.stdout + z.stderr)
summary = (f"\n分类汇总：抽样 {len(pts)} 点；进入判决的事实/事实推算 {len(facts)} 点；"
           f"模型假设或输出 {len(model_ids & {p['id'] for p in pts})} 点；非数据噪声 {len(noise_ids & {p['id'] for p in pts})} 点（均不进判决）。\n")
P.joinpath('audit-verdict.txt').write_text(txt + summary)
print(z.returncode); print(txt[-1500:]); print(summary)
