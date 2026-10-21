"""网易研究报告数据抽检：固定种子42重抽，填入取数结果后调用 report_audit.py verdict。

运行：python3 reports/网易/research-20261021/audit.py
产出：audit-classified.json（全部抽中点及分类）、audit-facts.json（进入判决的事实项）、audit-verdict.txt。
分类：
  FACT_DUAL_SOURCE              原件 + 独立第三方数据库，两源均填
  FACT_SINGLE_SOURCE_OR_DERIVED 单一原件，或由原件数字推算
  MODEL_ASSUMPTION_OR_DERIVATION 情景假设或模型输出，只与 inputs/results 复算一致，不是外部事实，不进判决
  NON_DATA                      日期、星级等非财务数据，不进判决
"""
from pathlib import Path
from decimal import Decimal as D
import json, sys, subprocess, re

P = Path(__file__).resolve().parent
root = P.parents[2]
sys.path.insert(0, str(root / "tools"))
import report_audit

report = P.parent / "网易研究报告-20261021.md"
pts = report_audit.sample_points(report_audit.extract_data_points(report.read_text()), ratio=.15, seed=42)

FY25 = "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0211/2026021100732.pdf"
Q226 = "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0820/2026082000465.pdf"
F20 = "https://www.sec.gov/Archives/edgar/data/0001110646/000110465926043468/ntes-20251231x20f.htm"
SA = "https://stockanalysis.com/stocks/ntes/financials/"
MR = "https://www.sec.gov/Archives/edgar/data/1110646/000110465926114177/tm2627023d1_ex99-1.htm"
FX = "https://api.frankfurter.app/2026-10-16..2026-10-20?from=USD&to=CNY,HKD"

ads = D("3201652151") / 5
mcap_cny_bn = D("125.25") * ads * D("6.6807") / D(10) ** 9

verified = {
    23: (float(round(mcap_cny_bn * 10, 2)), "derived: 125.25 USD (Yahoo/StockAnalysis 10-19 close) x 3,201,652,151/5 ADS (" + MR + ") x 6.6807 (" + FX + "), 亿元", None, ""),
    24: (6.6807, FX + " ECB reference USD/CNY 2026-10-19", 6.6909, "https://query1.finance.yahoo.com/v8/finance/chart/CNY=X (2026-10-19 bar)"),
    27: (1675.0, Q226 + " p7 Other financial information: net cash RMB167.5 billion", float(round((D("22814.542") + D("101978.645") + D("4447.483") + D("50599.638") + D("0.260") * 1000 + D("3.775") - D("12604.170")) / 100, 2)), Q226 + " p11 balance sheet, recomputed"),
    29: (float(round(D("167.5") / mcap_cny_bn * 100, 2)), "derived: company net cash 167.5bn / market cap CNY", None, ""),
    36: (float(round((D("35834.867") - D("19502.243") + D("24746.171")) / 100, 2)), FY25 + " p11 + " + Q226 + " p12 (FY2025 - H1'25 + H1'26)", 410.79, SA + " TTM operating income 41,079 CNY m"),
    51: (float(round(D("1319.168") / D("2814.883") * 100, 2)), Q226 + " p14 segment Youdao GP/revenue H1 2026", None, ""),
    56: (float(round(D("1474.409") / D("3958.706") * 100, 2)), Q226 + " p14 segment Cloud Music GP/revenue H1 2026", None, ""),
    58: (68.09, FY25 + " p13 segment: innovative businesses FY2025 6,808,730 千元", 68.09, F20 + " Item 5 segment table (same company, audited)"),
    60: (31.88, Q226 + " p14 segment: innovative businesses H1 2026 3,188,475 千元", None, ""),
    57: (80.97, FY25 + " p13 segment: innovative businesses FY2024 8,096,528 千元", 80.97, F20 + " Item 5 segment table (same company, audited)"),
    71: (177.19, FY25 + " p11 R&D expenses FY2025 17,719,110 千元", 177.19, F20 + " consolidated statements of operations (audited)"),
    109: (float(round((D("51477.285") - D("752.376") - D("726.542")) / 10 / mcap_cny_bn, 2)), "derived: TTM CFO minus PPE and intangible purchases (" + FY25 + " p12, " + Q226 + " p13) / market cap CNY", None, ""),
    189: (112625.81, FY25 + " p11 net revenues 112,625,807 千元", 112625.81, F20 + " audited income statement"),
    190: (112626.0, SA + " FY2025 revenue", None, ""),
    192: (33760.0, SA + " FY2025 net income", None, ""),
    201: (float(round((D("45.5") - D("45.32")) / D("45.32") * 100, 2)), "derived: |45.5 (" + F20 + " Item 6.E) - 45.32 (https://stockanalysis.com/stocks/ntes/statistics/)| / 45.32", None, ""),
}
model_ids = {7, 8, 9, 108, 130, 140, 144, 152, 155, 164, 167}
non_data = {202: "front matter date", 63: "year 2026 inside date text, not a data point", 174: "star rating ★3"}

facts, classes = [], []
for x in pts:
    i = x["id"]
    if i in model_ids:
        x.update(classification="MODEL_ASSUMPTION_OR_DERIVATION", external_fact_verification=False, fetched_value=None,
                 note="See inputs.json/results.json and financial-rigor.txt; reproduced, not independent evidence")
    elif i in non_data:
        x.update(classification="NON_DATA", fetched_value=None, note=non_data[i])
    else:
        v, src, v2, src2 = verified[i]
        x.update(fetched_value=v, fetched_source=src, fetched_value2=v2, fetched_source2=src2,
                 classification="FACT_DUAL_SOURCE" if v2 is not None else "FACT_SINGLE_SOURCE_OR_DERIVED")
        facts.append(x)
    classes.append(x)

# 模型项复算核对：与 results.json 一致才算通过（不进判决）
res = json.loads(P.joinpath("results.json").read_text())
model_check = {
    7: res["probability_weighted_value_usd"], 8: res["three_year"]["base"]["price"], 9: res["irr10"]["expected_tool_pct"],
    108: res["valuation"]["EV_ops_over_ttm_op_profit"], 144: res["scenarios"]["bull"]["upside_pct"],
    155: res["irr10"]["bear"]["cash_2036_bn"], 167: res["irr10"]["expected_explicit_pct"],
}
for x in classes:
    if x["id"] in model_check:
        mv = float(model_check[x["id"]]) * (10 if x["id"] == 155 else 1)
        x["model_value"] = mv
        x["model_match_within_1pct"] = abs(mv - x["reported_value"]) / abs(mv) <= 0.01

P.joinpath("audit-classified.json").write_text(json.dumps(classes, ensure_ascii=False, indent=2) + "\n")
P.joinpath("audit-facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n")
z = subprocess.run(["python3", str(root / "tools/report_audit.py"), "verdict", "--results", json.dumps(facts, ensure_ascii=False),
                    "--report", report.name, "--output-json"], capture_output=True, text=True)
summary = "\n模型项复算核对（不进判决）：\n" + "\n".join(
    f"  [{x['id']}] {x['label']}: 报告 {x['reported_value']} / 模型 {round(x['model_value'], 4)} / 一致={x['model_match_within_1pct']}"
    for x in classes if "model_value" in x)
P.joinpath("audit-verdict.txt").write_text(re.sub(r"\x1b\[[0-9;]*m", "", z.stdout + z.stderr) + summary + "\n")
print(z.returncode, z.stdout[-1500:], summary)
