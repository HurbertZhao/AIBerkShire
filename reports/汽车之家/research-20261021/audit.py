"""汽车之家研究报告数据抽检：填入核验值并调用 report_audit.py verdict。

运行：python3 reports/汽车之家/research-20261021/audit.py
分类：FACT_DUAL_SOURCE（两个来源）、FACT_SINGLE_SOURCE_OR_DERIVED（原件单一来源或由原件数字推算）进入判决；
MODEL_ASSUMPTION_OR_OUTPUT（情景假设或模型输出）与 EXTRACTION_NOISE（日期、文件编号等被误抽成数值）单独归类，不进判决。
"""
from pathlib import Path
from decimal import Decimal as D
import json, re, subprocess, sys

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import report_audit

report = P.parent / "汽车之家研究报告-20261021.md"
pts = report_audit.sample_points(report_audit.extract_data_points(report.read_text()), ratio=.15, seed=42)

SEC = "https://www.sec.gov/Archives/edgar/data/1527636/"
F20 = SEC + "000119312526155932/athm-20251231.htm"
Q2 = SEC + "000119312526357963/d404747dex991.htm"
Q1 = SEC + "000119312526242898/d142685dex995.htm"
Q3_25 = SEC + "000119312525267929/d95376dex991.htm"
FY25 = SEC + "000119312526092419/d102598dex991.htm"
BB = SEC + "000119312526318789/d152654dex991.htm"
SA = "https://stockanalysis.com/stocks/athm/"
YH = "https://query1.finance.yahoo.com/v8/finance/chart/ATHM"

ads = D("460683644") - 4 * ((D("10627269") - D("3465236")) + D("1895093"))
verified = {
    2: (20.16, YH + " 2026-10-20 close", 20.15, SA + "history/"),
    7: (float(ads), "derived: 20-F p136 460,683,644 shares (2026-03-31) minus 4x ADS bought back after 05-22 (" + Q1 + "; " + Q2 + ")", None, ""),
    9: (float(D("20.15") * ads / 4 / D(10) ** 8), "derived: 20.15 USD x 106,113,785 ADS", None, ""),
    23: (float(D("1.20") + D("0.66")), "Q3-2025 release (" + Q3_25 + ") US$1.20/ADS + Q1-2026 release (" + Q1 + ") US$0.66/ADS", None, ""),
    29: (280.386, Q2 + " media services Q2-2026 (RMB thousand 280,386)", None, ""),
    27: (1153.419, F20 + " F-6 media services 2025", 1153.419, FY25),
    36: (float((D("560.357") / D("732.581") - 1) * 100), "derived from " + Q2 + " leads 560,357 vs 732,581", None, ""),
    57: (2.00, FY25 + " US$200 million repurchase program", None, ""),
    58: (4.00, BB + " US$400 million repurchase program", None, ""),
    60: (float(D("1.86") / D("20.15") * 100), "derived: US$1.86 declared / US$20.15 close", None, ""),
    63: (-489.821, Q2 + " balance sheet dividends payable 489,821 (RMB thousand)", None, ""),
    109: (20.15, SA + "history/ 2026-10-20 close", 20.16, YH),
    115: (6452.030, F20 + " F-6 total net revenues 2025", 6452.0, SA + "financials/"),
}
model_ids = {51, 71, 72}
noise_ids = {8, 24, 56, 108, 130}

facts, classes = [], []
for x in pts:
    i = x["id"]
    if i in model_ids:
        x.update(classification="MODEL_ASSUMPTION_OR_OUTPUT", external_fact_verification=False, fetched_value=None,
                 note="情景假设或 model.py 输出，见 inputs.json/results.json；可复算但不是外部事实")
        classes.append(x); continue
    if i in noise_ids:
        x.update(classification="EXTRACTION_NOISE", external_fact_verification=False, fetched_value=None,
                 note="抽取器把日期、月份或文件编号（13D）识别为数值，非财务数据点")
        classes.append(x); continue
    v, src, v2, src2 = verified[i]
    x.update(fetched_value=v, fetched_source=src, fetched_value2=v2, fetched_source2=src2,
             classification="FACT_DUAL_SOURCE" if v2 is not None else "FACT_SINGLE_SOURCE_OR_DERIVED")
    facts.append(x); classes.append(x)

missing = [x["id"] for x in pts if x["id"] not in verified and x["id"] not in model_ids | noise_ids]
assert not missing, f"未分类抽检点: {missing}"
P.joinpath("audit-classified.json").write_text(json.dumps(classes, ensure_ascii=False, indent=2) + "\n")
P.joinpath("audit-facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n")
z = subprocess.run(["python3", str(ROOT / "tools/report_audit.py"), "verdict", "--results", json.dumps(facts, ensure_ascii=False),
                    "--report", report.name], capture_output=True, text=True)
summary = (f"\n分类汇总：抽样 {len(pts)} 点；进入判决 {len(facts)} 点"
           f"（双来源 {sum(1 for f in facts if f['classification']=='FACT_DUAL_SOURCE')}，单一来源或原件推算 {sum(1 for f in facts if f['classification']!='FACT_DUAL_SOURCE')}）；"
           f"模型假设/输出 {len(model_ids & {p['id'] for p in pts})} 点；抽取噪声 {len(noise_ids & {p['id'] for p in pts})} 点（不进判决）。\n")
P.joinpath("audit-verdict.txt").write_text(re.sub(r"\x1b\[[0-9;]*m", "", z.stdout + z.stderr) + summary)
print(z.returncode, z.stdout[-1500:], summary)
