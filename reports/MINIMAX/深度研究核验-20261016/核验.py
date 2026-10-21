#!/usr/bin/env python3
"""Audit numbers and classify assumptions. Public-source transcription is human reviewed.

The shared audit tool checks numeric agreement only. Single-source status and
forward-looking assumptions remain explicit even if its mechanical verdict passes.
"""
import hashlib
import json
import re
import subprocess
import sys
from decimal import Decimal as D
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPORT = HERE.parent / "MiniMax研究报告-20261016.md"
F1 = "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0930/2026093002173.pdf"
F2 = "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0422/2026042202118.pdf"
SA = "https://stockanalysis.com/quote/hkg/0100/financials/"
CF = "https://stockanalysis.com/quote/hkg/0100/financials/cash-flow-statement/"
IS = "https://stockanalysis.com/quote/hkg/0100/financials/income-statement/"
REUTERS = "https://www.investing.com/news/stock-market-news/chinas-minimax-sees-revenue-nearly-quadruple-in-first-half-as-ai-demand-surges-4876820"

def run(args):
    p = subprocess.run([sys.executable] + [str(a) for a in args], cwd=str(ROOT),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    if p.returncode:
        raise RuntimeError(p.stderr or p.stdout)
    plain = re.sub(r"\x1b\[[0-9;]*m", "", p.stdout)
    return "\n".join(line.rstrip() for line in plain.splitlines()) + "\n"

def save(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str)+"\n", encoding="utf-8")

run([HERE / "模型复算.py"])
model = json.loads((HERE / "计算结果.json").read_text(encoding="utf-8"))
checks = model["derived_checks"]
cross_inputs = [
    ("股价_20261015_HKD", "179.50", "179.50", "腾讯16:08:42", "StockAnalysis16:08及Investing收盘", "港元"),
    ("已发行股本_20260930", "352480183", "352480183", "HKEX月报A加B", "腾讯最新总股本", "股"),
    ("2025收入", "79.038", "79.04", "年报", "StockAnalysis", "百万美元"),
    ("2026H1收入", "116.573", "116.6", "中报", "Reuters", "百万美元"),
    ("2026H1平台收入", "73.929", "73.9", "中报", "Reuters", "百万美元"),
    ("2026H1原生产品收入", "42.644", "42.6", "中报", "Reuters", "百万美元"),
    ("2026H1净利润", "-357.997", "-358", "中报IFRS", "Reuters", "百万美元"),
    ("2026H1研发", "296.870", "296.873", "中报", "第三方TTM425.31-全年252.77+同期124.333", "百万美元"),
    ("2026H1CFO", "-318.106", "-318.108", "中报", "第三方TTM-429.21-全年(-279.64)+同期(-168.538)", "百万美元"),
    ("2026H1PPE采购", "187.626", "187.623", "中报", "第三方TTM188.16-全年0.92+同期0.383", "百万美元"),
]
records = []
for name, a, b, sourcea, sourceb, unit in cross_inputs:
    output = run([ROOT / "tools/financial_rigor.py", "cross-validate", "--field", name,
                  "--values", json.dumps({sourcea:a,sourceb:b},ensure_ascii=False), "--unit", unit])
    records.append({"field":name,"source_a":sourcea,"value_a":a,"source_b":sourceb,
                    "value_b":b,"deviation_pct":abs(D(a)-D(b))/abs(D(a))*100,"tool_output":output})
    assert abs(D(a)-D(b))/abs(D(a)) < D(".01")
expressions = {
    "market_cap_hkd": "179.50 * 352480183",
    "ttm_revenue_musd": "79.038 + 116.573 - 30.429",
    "h12026_simple_fcf_musd": "-318.106 - 187.626",
    "cb_redemption_mhkd": "6500 * 1.0275",
    "base_net_profit_busd": "8 * (0.55 - 0.22 - 0.08 - 0.05) * 0.8",
    "base_net_profit_rmb_100m": "8 * (0.55 - 0.22 - 0.08 - 0.05) * 0.8 * 70",
    "base_fcf_busd": "1.28 + 0.32 - 0.4 - 0.08",
    "base_valuation_busd": "1.28 * 25 * 0.70 / (1.20 ** 10)",
    "example_raise_premoney_busd": "5 * 0.7 / 0.3",
    "proforma_gross_liquidity_busd": "1.223290 + (9443.71 + 6433.3) / 7.8 / 1000",
}
for label, expr in expressions.items():
    records.append({"field":label,"expression":expr,"tool_output":run([ROOT / "tools/financial_rigor.py","calc","--expr",expr])})
records.append({"field":"market_cap_verified","tool_output":run([ROOT/"tools/financial_rigor.py","verify-market-cap","--price","179.50","--shares","352480183","--reported","63270192848.50","--currency","HKD"])})
save("financial-rigor.json",records)

extraction = run([ROOT/"tools/report_audit.py","extract","--report",REPORT.relative_to(ROOT),"--ratio","0.15","--seed","42"])
(HERE/"audit-extract.txt").write_text(extraction,encoding="utf-8")
samples = json.loads(extraction[extraction.index("[\n  {"):])
fact_map = {
    "毛利 · 2024": ("3.738", F2+" p4", "3.74", SA, "independent_channel"),
    "毛利 · 2025H1": ("3.685", F1+" p6", "3.683", SA+" third-party TTM bridge 20.08+20.813-37.21", "ttm_bridge"),
    "毛利 · 2025": ("20.079", F2+" p4", "20.08", SA, "independent_channel"),
    "IFRS净利润 · 2025": ("-1871.617", F2+" p4", "-1872", IS, "independent_channel"),
    "IFRS净利润 · 2025H1": ("-402.188", F1+" p6", "-402.2", REUTERS, "independent_channel"),
    "调整后净利润 · 2025H1": ("-138.735", F1+" p6", None, None, "single_issuer_source"),
    "调整后净利润 · 2024": ("-244.243", F2+" p4", None, None, "single_issuer_source"),
    "开放平台及其他基于AI的企业服务 · 收入，百万美元": ("73.929", F1+" p7", "73.9", REUTERS, "independent_channel"),
}
calc_map = {
    "外部生产API与模型服务 · 毛利，亿美元": (D("100000")*D("20000")/D("1e8")*D(".4"), "100000*20000/1e8*.4"),
    "企业Agent与工作流 · 毛利，亿美元": (D("40000")*D("60000")/D("1e8")*D(".65"), "40000*60000/1e8*.65"),
    "毛利 · 亿美元": (D("8")+D("15.6")+D("14.4")+D("6"), "8+15.6+14.4+6"),
    "毛利 · 占收入": (D("44")/80*100, "44/80*100"),
    "2027E · 正常化净利润": (D("6.5")*(D(".3")-D(".17"))-15, "6.5*(.3-.17)-15"),
    "2029E · 经济口径现金流代理": (D("15")*(D(".42")-D(".15"))-15+D(".9")-2-D(".4"), "15*(.42-.15)-15+.9-2-.4"),
    "2036E · 经济口径现金流代理": (D("12.8")+D("3.2")-4-D(".8"), "12.8+3.2-4-.8"),
}
assumption_labels = {
    "专业创作订阅与工具 · 年度净收入单价":"300 USD/year, assumption",
    "专业创作订阅与工具 · 毛利率假设":"60%, assumption",
    "专业创作订阅与工具 · 客户/用户假设":"800万=8000000 accounts; extractor omitted 万; assumption",
    "消费互动与娱乐 · 年度净收入单价":"60 USD/year, assumption",
    "2027E · 研发费用":"15亿美元, assumption",
}
facts, calculations, assumptions = [], [], []
for item in samples:
    label = item["label"]
    if label in fact_map:
        val,src,val2,src2,scope = fact_map[label]
        item.update(fetched_value=float(val),fetched_source=src,fetched_value2=float(val2) if val2 else None,fetched_source2=src2 or "",source_status=scope)
        facts.append(item)
    elif label in calc_map:
        val,expr = calc_map[label]
        assert abs(D(str(item["reported_value"]))-val)/abs(val) <= D(".01")
        item.update(fetched_value=float(val),fetched_source="Independent Decimal arithmetic of disclosed assumptions: "+expr, classification="calculation_only_not_forecast_validation")
        calculations.append(item)
    elif label in assumption_labels:
        item.update(classification="unverified_forward_assumption",boundary=assumption_labels[label])
        assumptions.append(item)
    else:
        raise ValueError("Unclassified sample: "+label)
assert (len(facts),len(calculations),len(assumptions)) == (8,7,5)
save("audit-facts.json",facts)
save("audit-calculations.json",calculations)
save("audit-assumptions.json",assumptions)
for name, rows in (("facts",facts),("calculations",calculations)):
    out = run([ROOT/"tools/report_audit.py","verdict","--results",json.dumps(rows,ensure_ascii=False),"--report",name,"--output-json"])
    (HERE/("audit-"+name+"-verdict.txt")).write_text(out,encoding="utf-8")
    assert '"verdict": "PASS"' in out

manifest = {"date":"2026-10-16","report_sha256":hashlib.sha256(REPORT.read_bytes()).hexdigest(),
            "sample_total":20,"fact_samples":8,"facts_independent_or_ttm":6,"facts_primary_only":2,
            "arithmetic_samples":7,"unverified_assumptions":5,
            "boundary":"PASS is numerical agreement only; no empirical validation of moat, forecasts, probabilities or valuations.",
            "primary_urls":{"interim":F1,"annual":F2},
            "crosscheck_urls":{"financials":SA,"income":IS,"cashflow":CF,"reuters":REUTERS}}
save("audit-scope.json",manifest)
print(json.dumps(manifest,ensure_ascii=False,indent=2))
