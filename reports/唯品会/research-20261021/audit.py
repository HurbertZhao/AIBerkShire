"""唯品会研究报告数据抽检：复现 seed=42 抽样，填入取数结果，模型假设类点单独归类不进判决。
运行：python3 reports/唯品会/research-20261021/audit.py
"""
from pathlib import Path
from decimal import Decimal as D
import json, sys, subprocess, re

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import report_audit

report = P.parent / "唯品会研究报告-20261021.md"
pts = report_audit.sample_points(report_audit.extract_data_points(report.read_text()), ratio=.15, seed=42)

XB = "https://data.sec.gov/api/xbrl/companyfacts/CIK0001529192.json"
F20 = "https://www.sec.gov/Archives/edgar/data/1529192/000110465926044015/vips-20251231x20f.htm"
Q3 = "https://www.sec.gov/Archives/edgar/data/1529192/000119312525288927/d842251dex991.htm"
Q4 = "https://www.sec.gov/Archives/edgar/data/1529192/000110465926019965/tm267413d1_ex99-1.htm"
Q1 = "https://www.sec.gov/Archives/edgar/data/1529192/000110465926064870/tm2615319d1_ex99-1.htm"
Q2 = "https://www.sec.gov/Archives/edgar/data/1529192/000110465926100484/tm2623972d1_ex99-1.htm"
SA = "https://stockanalysis.com/stocks/vips/financials/"
SAQ = "https://stockanalysis.com/stocks/vips/financials/?p=quarterly"
SACF = "https://stockanalysis.com/stocks/vips/financials/cash-flow-statement/"

def pct(a, b):
    return float((D(a) / D(b) * 100).quantize(D("0.0001")))

# id: (值1, 来源1, 值2, 来源2)；单位与报告一致（亿元或%）
verified = {
    7: (pct("21616.1", "103152.5"), XB + " FY2022 GrossProfit/Revenue", 20.95, SA + " gross margin FY2022"),
    9: (pct("25469.654", "108420.832"), F20 + " F-7 income statement 2024", 23.49, SA + " gross margin FY2024"),
    8: (pct("25720.892", "112856.020"), F20 + " F-7 income statement 2023", 22.79, SA + " gross margin FY2023"),
    23: (pct("8116.624", "112856.020"), F20 + " F-8 NI attributable / revenue 2023", 7.19, SA + " profit margin FY2023"),
    24: (pct("7739.935", "108420.832"), F20 + " F-8 NI attributable / revenue 2024", 7.14, SA + " profit margin FY2024"),
    29: (91.29, F20 + " F-13 net cash from operating activities 2024 (9,128,983k)", 91.29, SACF + " FY2024 9,129"),
    27: (105.20, XB + " NetCashProvidedByUsedInOperatingActivities FY2022 10519.7m", 105.20, SACF + " FY2022 10,520"),
    36: (float(D("67.446") - D("27.324")), XB + " FY2021 CFO 6744.6 - PP&E purchases 2732.4 (derived)", 40.12, SACF + " FY2021 FCF 4,012"),
    51: (213.71, Q3 + " total net revenues 21,370,865k", 213.71, SAQ + " Q3 2025 21,371"),
    58: (pct("6495.150", "26574.509"), Q1 + " gross profit / revenue", 24.44, SAQ + " Q1 2026 gross margin"),
    56: (pct("4908.911", "21370.865"), Q3 + " gross profit / revenue", 22.97, SAQ + " Q3 2025 gross margin"),
    60: (pct("24602.952", "105126.302"), "sum of four 6-K quarters (derived)", 23.40, SA + " TTM gross margin"),
    57: (pct("7444.199", "32473.779"), Q4 + " gross profit / revenue", 22.92, SAQ + " Q4 2025 gross margin"),
    63: (24.98, Q1 + " income from operations 2,497,769k", None, ""),
    71: (15.01, Q3 + " non-GAAP NI attributable 1,501,489k", None, ""),
    108: (1522, F20 + " Item 6.D employees: research and development 1,522", None, ""),
    130: (float((D("12.80") * D("475.5") * D("6.6807") / D("7242.490")).quantize(D("0.0001"))),
          "derived: 12.80 USD (Nasdaq 10-19 close) x 475.5m ADS (" + Q2 + " 95.1m shares x5) x 6.6807 / FY2025 NI 7,242.49m (" + F20 + ")", None, ""),
    140: (2025, Q4 + " 'annual cash dividend for fiscal year 2025 ... US$0.62 per ADS'", None, ""),
}
model_ids = {109, 115, 144, 152, 151, 155, 164, 167, 174, 184, 190}
meta_ids = {192}

facts, classes = [], []
for x in pts:
    i = x["id"]
    if i in meta_ids:
        x.update(classification="METADATA_NOT_FINANCIAL", note="front matter date, not a data point"); classes.append(x); continue
    if i in model_ids:
        x.update(classification="MODEL_ASSUMPTION_OR_DERIVATION", external_fact_verification=False, fetched_value=None,
                 note="scenario assumption / model output / action rule; reproduced by model.py & results.json, not external evidence")
        classes.append(x); continue
    v, s1, v2, s2 = verified[i]
    x.update(fetched_value=v, fetched_source=s1, fetched_value2=v2, fetched_source2=s2,
             classification="FACT_DUAL_SOURCE" if v2 is not None else "FACT_SINGLE_SOURCE_OR_DERIVED")
    facts.append(x); classes.append(x)

missing = [x["id"] for x in pts if x["id"] not in verified and x["id"] not in model_ids and x["id"] not in meta_ids]
assert not missing, f"unclassified sample ids: {missing}"
P.joinpath("audit-classified.json").write_text(json.dumps(classes, ensure_ascii=False, indent=2) + "\n")
P.joinpath("audit-facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n")
z = subprocess.run(["python3", str(ROOT / "tools/report_audit.py"), "verdict", "--results", json.dumps(facts, ensure_ascii=False),
                    "--report", report.name, "--output-json"], capture_output=True, text=True)
summary = (f"\n抽样总数 {len(pts)}：事实类进入判决 {len(facts)}（双源 {sum(1 for f in facts if f['fetched_value2'] is not None)}），"
           f"模型假设/输出/行动条件 {len(model_ids)} 单独归类不进判决，元数据 {len(meta_ids)}。\n")
P.joinpath("audit-verdict.txt").write_text(re.sub(r"\x1b\[[0-9;]*m", "", z.stdout + z.stderr) + summary)
print(z.returncode); print(z.stdout[-2500:]); print(summary)
