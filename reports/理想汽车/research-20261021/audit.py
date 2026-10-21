"""理想汽车研究报告数据抽检：复现 seed=42 抽样，填入核验值，模型假设类单独归类，调用 report_audit.py verdict。
运行：python3 reports/理想汽车/research-20261021/audit.py
"""
from pathlib import Path
from decimal import Decimal as D
import json, re, subprocess, sys

P = Path(__file__).resolve().parent
root = P.parents[2]
sys.path.insert(0, str(root / "tools"))
import report_audit  # noqa: E402

report = P.parent / "理想汽车研究报告-20261021.md"
pts = report_audit.sample_points(report_audit.extract_data_points(report.read_text()), ratio=0.15, seed=42)

E = "https://www.sec.gov/Archives/edgar/data/1791706/"
Q2 = E + "000110465926101065/tm2624080d1_ex99-1.htm"   # 2026Q2 业绩公告
Q1 = E + "000110465926067465/tm2615887d1_ex99-1.htm"   # 2026Q1 业绩公告
Q3_25 = E + "000110465925116474/tm2532303d1_ex99-1.htm"  # 2025Q3 业绩公告
FY = E + "000110465926026803/tm268559d1_ex99-1.htm"    # 2025Q4及全年业绩公告
XBRL = "https://data.sec.gov/api/xbrl/companyfacts/CIK0001791706.json (20-F FY2025)"
SA = "https://stockanalysis.com/stocks/li/financials/"
YH = "https://query1.finance.yahoo.com/v8/finance/chart/"
pct = lambda a, b: float(D(a) / D(b) * 100)
yi = lambda x: float(D(x) / 100)  # 百万元 -> 亿元

verified = {
    7: (pct("8790.456", "45286.816"), XBRL + " GrossProfit/Revenue 2022", 19.41, SA + " Gross Margin FY2022"),
    9: (pct("29656.138", "144459.946"), XBRL + " GrossProfit/Revenue 2024", 20.53, SA + " Gross Margin FY2024"),
    8: (pct("27496.751", "123851.332"), XBRL + " GrossProfit/Revenue 2023", 22.20, SA + " Gross Margin FY2023"),
    23: (yi(D("50693.521") - D("6507.190")), XBRL + " CFO-PaymentsToAcquireProductiveAssets 2023", 441.86, SA + "cash-flow-statement/ FCF FY2023 44,186"),
    24: (yi(D("15933.160") - D("7730.022")), XBRL + " CFO-capex 2024", 82.031, FY + " FY2024 free cash flow 8,203.1"),
    27: (500508, FY + " FY2024 deliveries table", 500508, E + "000110465926041705/li-20251231x20f.htm MD&A deliveries of 500,508 vehicles in 2024"),
    29: (93211, Q2 + " deliveries table 2025Q3", 93211, FY + " deliveries table 2025Q3"),
    36: (yi("25666.890"), Q2 + " total revenues", yi("25667"), SA + "?p=quarterly Q2 2026"),
    51: (yi("-2289.531"), Q1 + " net loss attributable", yi("-2290"), SA + "?p=quarterly Q1 2026"),
    56: (yi("15.025"), Q2 + " cash flow statement CFO", yi("15.03"), SA + "?p=quarterly Q2 2026 OCF"),
    58: (yi("2467.601"), Q1 + " FCF 2025Q4 column", yi("2467.6"), FY + " Key results FCF Q4 2025 (StockAnalysis capex differs, not used)"),
    60: (yi("-1300.765"), Q2 + " FCF", yi("-1301"), SA + "?p=quarterly Q2 2026 FCF"),
    57: (yi("-8912.187"), Q3_25 + " FCF", yi("-8912.2"), FY + " Key results FCF Q3 2025"),
    63: (1124.438, XBRL + " NetIncomeLossAvailableToCommonStockholdersBasic 2025", 1124, SA + " Net Income FY2025"),
    71: (45.64, YH + "2015.HK close 2026-10-20", 45.64, "https://stockanalysis.com/quote/hkg/2015/history/"),
    72: (11.29, YH + "LI close 2026-10-19", 11.29, "https://stockanalysis.com/stocks/li/history/"),
    108: (0.85, "https://stockanalysis.com/stocks/xpev/statistics/ PS Ratio (single third-party source)", None, ""),
    109: (yi(D("40117.782") + D("14.782") + D("45474.274")), Q2 + " balance sheet cash+restricted+TD/STI", yi(D("85592") + D("14.78")), SA + "balance-sheet/ Cash&ST + restricted"),
}
model_ids = {115: "经营缓冲200亿元为研究假设", 130: "中性情景2028年每股价值为模型输出", 140: "悲观档退出市盈率为永续增长公式输出",
             144: "2036基准经营利润为情景假设", 152: "10%为风险阈值/情景描述", 156: "15%为加仓行动条件"}
non_data = {162: "2023为年份，被抽取器误识别为数值"}

facts, classes = [], []
for x in pts:
    i = x["id"]
    if i in model_ids or i in non_data:
        x.update(classification="MODEL_ASSUMPTION_OR_CONDITION" if i in model_ids else "NON_DATA_PARSE_ARTIFACT",
                 note=model_ids.get(i) or non_data.get(i), fetched_value=None, external_fact_verification=False)
        classes.append(x)
        continue
    v, s, v2, s2 = verified[i]
    x.update(fetched_value=v, fetched_source=s, fetched_value2=v2, fetched_source2=s2,
             classification="FACT_DUAL_SOURCE" if v2 is not None else "FACT_SINGLE_SOURCE")
    facts.append(x)
    classes.append(x)

P.joinpath("audit-classified.json").write_text(json.dumps(classes, ensure_ascii=False, indent=2) + "\n")
z = subprocess.run([sys.executable, str(root / "tools/report_audit.py"), "verdict", "--results",
                    json.dumps(facts, ensure_ascii=False), "--report", report.name], capture_output=True, text=True)
txt = re.sub(r"\x1b\[[0-9;]*m", "", z.stdout + z.stderr)
summary = (f"\n抽样总数 {len(pts)}；进入判决的事实项 {len(facts)}（双源 {sum(1 for f in facts if f['fetched_value2'] is not None)}，单源 {sum(1 for f in facts if f['fetched_value2'] is None)}）；"
           f"模型假设/行动条件 {len(model_ids)} 项与解析误识别 {len(non_data)} 项单独归类，不进判决，见 audit-classified.json。\n")
P.joinpath("audit-verdict.txt").write_text(txt + summary)
print(txt[-1500:] + summary)
