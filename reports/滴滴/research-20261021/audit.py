"""数据抽检（seed=42）：填入取数结果，模型假设类点单独归类、不进判决，然后调用 report_audit.py verdict。

运行：python3 reports/滴滴/research-20261021/audit.py
"""
from decimal import Decimal as D
from pathlib import Path
import json
import re
import subprocess
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import report_audit  # noqa: E402

report = P.parent / "滴滴研究报告-20261021.md"
pts = report_audit.sample_points(report_audit.extract_data_points(report.read_text()), ratio=0.15, seed=42)

F25 = "https://www.sec.gov/Archives/edgar/data/1764757/000110465926042350/didi-20251231x20f.htm"
F23 = "https://www.sec.gov/Archives/edgar/data/1764757/000110465924047255/didi-20231231x20f.htm"
SA_IS = "https://stockanalysis.com/quote/otc/DIDIY/financials/"
SA_CF = "https://stockanalysis.com/quote/otc/DIDIY/financials/cash-flow-statement/"
SA_BS = "https://stockanalysis.com/quote/otc/DIDIY/financials/balance-sheet/"
Q4 = "https://ir.didiglobal.com/static-files/433e2d74-b1a6-4551-8449-477fd20cbb7a"
Q1 = "https://ir.didiglobal.com/static-files/4b89fb29-83da-4338-a136-7e557f6cdab9"


def f(x):
    return float(x)


verified = {
    7: (f(D("-23784") / 100), F23 + " Item 3 合并简表 FY2022 Net loss attributable -23,784 RMB mn（美国会计准则）", None,
        "StockAnalysis 为 IFRS 重述口径 -11,720，口径不同不作第二来源"),
    9: (f(D("1258329") / 100000), F25 + " F-4 合并利润表 1,258,329 千元", f(D("1258") / 100), SA_IS + " FY2024 Net Income 1,258"),
    8: (f(D("-4793564") / 100000), F25 + " F-4 合并利润表 -4,793,564 千元", f(D("-4794") / 100), SA_IS + " FY2023 Net Income -4,794"),
    23: (f((D("226701433") - D("183196860")) / D("226701433") * 100), F25 + " F-4 收入与营业成本推算", None, ""),
    24: (f(D("-2838457") / D("192379918") * 100), F25 + " F-4 经营亏损/收入推算", None, ""),
    29: (f((D("9816065") - D("3355749") - D("556774")) / 100000), F25 + " F-11 经营现金流-购建资产-租赁本金推算",
         f((D("9816") - D("3356") - D("556.77")) / 100), SA_CF + " FY2025 OCF/CapEx/Lease Payments 推算"),
    27: (f((D("3186263") - D("2340490") - D("700021")) / 100000), F25 + " F-11 2023 列推算",
         f((D("3186") - D("2340") - D("700.02")) / 100), SA_CF + " FY2023 OCF/CapEx/Lease Payments 推算"),
    36: (f(D("7842") / 100), F25 + " Item 5A 国际分部表 Revenues 2023 = 7,842 RMB mn", None, ""),
    51: (10809.0, F25 + " Item 5A 中国出行分部表 Transactions 2023 = 10,809 百万", None, ""),
    56: (f(D("333759") / 100), F25 + " Item 5A 中国出行 GTV 2025 = 333,759 RMB mn", f(D("333759") / 100), Q4 + " 2025 全年列 China Mobility GTV 333,759"),
    58: (f(D("60057") / D("301436") * 100), F25 + " Item 5A 平台销售额/交易额推算 2024", None, ""),
    57: (f(D("47878") / D("270721") * 100), F25 + " Item 5A 平台销售额/交易额推算 2023", None, ""),
    60: (f(D("5323") / D("270721") * 100), F25 + " Item 5A 调整后EBITA/交易额推算 2023", None, ""),
    63: (f(D("23808032") / 100000), F25 + " F-7 现金及现金等价物 23,808,032 千元", f(D("23808") / 100), SA_BS + " FY2025 Cash & Equivalents 23,808"),
    71: (f((D("12353652") + D("230831")) / 100000), F25 + " F-7 流动借款 12,353,652 + 非流动借款 230,831 千元",
         f((D("12354") + D("231")) / 100), Q1 + " 资产负债表 2025-12-31 列 12,354 + 231"),
    183: (2016.0, F25 + " Item 4A 时间线：2016 年收购优步中国", None, ""),
    109: (f(D("1165462746") / D("100000000")), Q1 + " 2026Q1 基本加权普通股 1,165,462,746 股", None, ""),
    108: (f(D("3.19") * 4 * D("1165462746") * D("6.7208") / D("100000000")),
          "推算：2026-10-19 收盘 3.19 美元×4×1,165,462,746 股×中间价 6.7208（收盘价三源一致，股数为 Q1 原件）", None, ""),
    115: (f(D("3.19") * 4 * D("1126879059") * D("6.7208") / ((D("2983") + D("2618") + D("3967") + D("4200")) * D("1000000"))),
          "推算：法定股本市值 / 滚动四季度中国出行调整后EBITA（Q3/Q4 2025、Q1 2026 原件 + Q2 2026 财新 42 亿元）", None, ""),
}
model_ids = {130, 140, 144, 151, 152, 155, 164, 174, 176}

facts, classes = [], []
for x in pts:
    if x["id"] in model_ids:
        x.update(classification="MODEL_ASSUMPTION_OR_OUTPUT", external_fact_verification=False, fetched_value=None,
                 note="情景假设、模型输出或行动条件；由 model.py/inputs.json/results.json 复算，不是外部事实，不进判决")
        classes.append(x)
        continue
    v, src, v2, src2 = verified[x["id"]]
    x.update(fetched_value=v, fetched_source=src, fetched_value2=v2, fetched_source2=src2,
             classification="FACT_DUAL_SOURCE" if v2 is not None else "FACT_SINGLE_SOURCE_OR_DERIVED")
    facts.append(x)
    classes.append(x)

missing = [x["id"] for x in pts if x["id"] not in model_ids and x["id"] not in verified]
assert not missing, missing
P.joinpath("audit-classified.json").write_text(json.dumps(classes, ensure_ascii=False, indent=2) + "\n")
z = subprocess.run(["python3", str(ROOT / "tools/report_audit.py"), "verdict", "--results", json.dumps(facts, ensure_ascii=False),
                    "--report", report.name, "--output-json"], capture_output=True, text=True)
model_note = "\n模型假设/输出类抽样点（不进判决）：" + ", ".join(str(i) for i in sorted(model_ids)) + "\n"
P.joinpath("audit-verdict.txt").write_text(re.sub(r"\x1b\[[0-9;]*m", "", z.stdout + z.stderr) + model_note)
print(z.returncode)
print(z.stdout[-900:])
