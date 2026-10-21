"""Reproduce the publication audit from manually reviewed evidence.

This script does not fetch sources or validate forecasts. Evidence values were
read during the research session; URLs and limitations are preserved below.
"""
from pathlib import Path
from decimal import Decimal as D
import hashlib
import importlib.util
import json
import re
import subprocess
import sys

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
OUT = BASE / "audit"
REPORT = BASE / "短剧与AI短剧深度研究报告-20261019.md"

def save(name, obj):
    (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n")

def run_tool(args):
    p = subprocess.run([sys.executable, *args], capture_output=True, text=True, check=True)
    clean = re.sub(r"\x1b\[[0-9;]*m", "", p.stdout)
    return "\n".join(line.rstrip() for line in clean.splitlines())+"\n"

spec = importlib.util.spec_from_file_location("report_audit", REPO/"tools/report_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
body = REPORT.read_text()
points = audit.extract_data_points(body)
sample = audit.sample_points(points, ratio=.15, seed=42)
save("audit-sample.json", sample)
(OUT/"audit-extract.txt").write_text(run_tool([str(REPO/"tools/report_audit.py"),
    "extract", "--report", str(REPORT.relative_to(REPO)), "--seed", "42"]))

urls = {
    "iimedia": "https://www.iimedia.cn/c400/97005.html",
    "dataeye": "https://pdf.dfcfw.com/pdf/H3_AP202601211818183880_1.pdf",
    "cnnic": "https://cnnic.cn/NMediaFile/2025/0730/MAIN1753846666507QEK67ZS9DH.pdf",
    "qm": "https://eu.36kr.com/zh/p/3914660062450823",
    "st": "https://sensortower.com/blog/state-of-short-drama-apps-2026-report",
    "omdia": "https://omdia.tech.informa.com/pr/2026/oct/men-account-for-54percent-of-uk-microdrama-users-challenging-industry-assumptions",
    "ks2025": "https://ir.kuaishou.com/news-releases/news-release-details/kuaishou-technology-announces-fourth-quarter-and-full-year-2025/",
    "ks2026": "https://ir.kuaishou.com/static-files/f1aadb37-caa1-4c1d-8294-15008c09067c",
    "ks2024other": "https://finance.sina.com.cn/tech/csj/2025-03-25/doc-ineqwnhh6790035.shtml",
    "read2025": "https://dataclouds.cninfo.com.cn/shgonggao/hsomarket/2026/20260424/94528c26874e441bb95c8f655a96a349.PDF",
    "read2026": "https://static.cninfo.com.cn/finalpage/2026-08-27/1225510832.PDF",
    "read2026other": "https://finance.eastmoney.com/a/202608263854680634.html",
    "read2025other": "https://www.yicai.com/news/103151687.html",
    "readtable": "https://stock.quote.stockstar.com/finance/summary_603533.shtml",
    "read2024cash": "https://www.sohu.com/a/890859004_121418230",
    "yue2025": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0317/2026031700357_c.pdf",
    "yue2026": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0811/2026081100262_c.pdf",
    "yue2024other": "https://finance.sina.com.cn/roll/2025-03-20/doc-ineqhfmw0798020.shtml",
    "yue2025other": "https://www.cls.cn/detail/2315863",
    "yue2026other": "https://www.nbd.com.cn/articles/2026-08-12/4540090.html",
    "col": "https://static.cninfo.com.cn/finalpage/2026-08-26/1225504423.PDF",
    "holywater": "https://www.globenewswire.com/news-release/2026/07/23/3332522/0/en/holywater-tech-and-owl-co-publish-first-industry-report-on-the-vertical-series-audience.html",
}

# id -> primary value, source key, external value, external source key, limitation
evidence = {
    2: ("101.7", "iimedia", None, None, "机构估算；无独立行业审计总量"),
    7: ("1000", "dataeye", None, None, "产值估算；第3页，非终端净收入"),
    8: ("1210", "dataeye", None, None, "第3页2026预测；仅核对预测被正确引用"),
    9: ("6.26", "cnnic", None, None, "官方调查原PDF；纠正转载6.62误字"),
    51: ("177.16", "ks2025", "177.16", "ks2024other", "同一财报的外部转录核对"),
    58: ("17.8379367053", "read2026", "17.84", "read2026other", "外部仅两位小数"),
    56: ("32.4274", "read2025", "32.43", "read2025other", "主来源归一到亿元四位小数，外部两位"),
    57: ("15.2606954977", "read2026", "15.26", "readtable", "外部两位小数；半年而非全年"),
    60: ("-1.764536", "read2025", "-1.76", "read2025other", "保留负号；外部两位小数"),
    63: ("-0.7502", "read2025", "-0.75017", "read2024cash", "外部-7501.7万元换算；2024年度，非2025Q1"),
    71: ("11.4166", "yue2025", "11.42", "yue2024other", "Non-IFRS，非IFRS；外部两位小数"),
    72: ("8.5849", "yue2025", "8.58", "yue2025other", "Non-IFRS，外部两位小数"),
}
model_evidence = {
    23: (D(100)*D(".15"), "假设收入100乘假设渠道费率15%"),
    24: (D(100)*D(".15"), "假设收入100乘假设渠道费率15%"),
    27: (D(55), "明确的模型输入，不是外部观察"),
    29: (D(15), "明确的模型输入，不是外部观察"),
    36: (D(100)-D(100)*D(".15")-D(55)-D("4.5")-D(10), "Decimal独立复算项目利润"),
}
facts, models, exclusions = [], [], []
for point in sample:
    i = point["id"]
    if i in evidence:
        value, src, value2, src2, note = evidence[i]
        row = dict(point, fetched_value=float(value), fetched_source=urls[src], note=note)
        if value2 is not None:
            row.update(fetched_value2=float(value2), fetched_source2=urls[src2])
        facts.append(row)
    elif i in model_evidence:
        value, note = model_evidence[i]
        models.append(dict(point, fetched_value=float(value), fetched_source="model.py / Decimal", note=note))
    elif re.match(r"S\d+ ·", point["label"]):
        exclusions.append(dict(point, disposition="excluded_non_metric",
            reason="来源索引中的年份或标题，不是经济数据；保留原始抽样记录"))
    else:
        raise ValueError(f"Unreviewed random sample item: {point}")
assert len(facts)+len(models)+len(exclusions) == len(sample)
save("audit-facts.json", facts)
save("audit-assumptions.json", models)
save("audit-dispositions.json", exclusions)

# Material metrics that the regex/random sample misses. Boundaries are explicit.
critical_specs = [
    ("QuestMobile 2026-05去重用户", "8.51", "亿", "qm", "渠道监测，非CNNIC同口径增长序列"),
    ("红果2026-05 App MAU", "3.56", "亿", "qm", "不是收入份额"),
    ("短剧App 2026-05月时长", "26.9", "小时", "qm", "按月活用户，不是单日活跃分母"),
    ("Sensor Tower Q1 IAP", "7.5", "亿美元", "st", "约数、商店估算，不是公司会计收入"),
    ("Omdia 2026全球规模预测", "140", "亿美元", "omdia", "预测，不是实绩"),
    ("快手2026H1收入", "692.51", "亿元", "ks2026", "集团收入"),
    ("快手2026H1经调整利润", "72.87", "亿元", "ks2026", "经调整期内利润，非归母口径"),
    ("快手2025H1经调整利润", "101.98", "亿元", "ks2026", "比较期相同口径"),
    ("可灵2026Q2收入下限", "8.5", "亿元", "ks2026", "原文超过；全用途，非纯AI短剧"),
    ("掌阅2026H1销售费用", "11.0889694596", "亿元", "read2026", "集团合并费用，含阅读与短剧"),
    ("阅文2026H1短剧加AI收入下限", "4.3", "亿元", "yue2026", "原文超过；混合业务，不能全算AI"),
    ("阅文2026H1 Non-IFRS归母", "2.58838", "亿元", "yue2026", "对账表仍含税务事项"),
    ("阅文税务及滞纳金事项", "3", "亿元", "yue2026", "PDF第10—11页，166+134百万元"),
    ("CMS间接持股", "49.24", "%", "col", "PDF第157页，权益法；经营数据仅Q1"),
    ("My Muse付费转化", "23.6", "%", "holywater", "运营商自报，非随机对照"),
    ("My Drama付费转化", "23.9", "%", "holywater", "不能证明AI与真人全市场LTV相同"),
]
critical = [dict(id=1000+i, label=label, reported_value=float(v), unit=unit,
    fetched_value=float(v), fetched_source=urls[src], note=note)
    for i, (label,v,unit,src,note) in enumerate(critical_specs, start=1)]
save("critical-facts.json", critical)

model = json.loads((OUT/"model-results.json").read_text())
scenario_checks = []
for i, row in enumerate(model["global_scenarios"]):
    expected = D(row["reach_factor"])*D(row["hours_factor"])*D(row["revenue_per_hour_factor"])
    assert expected == D(row["revenue_factor"])
    assert D(14)*expected == D(row["year2036_usd_bn"])
    scenario_checks.append(dict(id=2001+i, label=f"{row['name']}十年情景金额换算",
        reported_value=float(row["year2036_usd_bn"]), unit="十亿美元",
        fetched_value=float(D(14)*expected), fetched_source="Decimal: 14 × 人群 × 时长 × 每小时变现",
        note="仅验证计算；14是外部预测校准，其他均为研究假设"))
save("scenario-checks.json", scenario_checks)

def verdict(name, items):
    for row in items:
        assert row.get("fetched_value") is not None
        for key in ("fetched_value", "fetched_value2"):
            if row.get(key) is not None:
                actual, expected = D(str(row["reported_value"])), D(str(row[key]))
                assert abs(actual-expected)/abs(actual) <= D(".01"), row
    log = run_tool([str(REPO/"tools/report_audit.py"), "verdict", "--results",
                    json.dumps(items, ensure_ascii=False), "--report", name, "--output-json"])
    result = json.loads(log[log.rfind('\n{')+1:])
    assert result["warn_count"] == result["fail_count"] == 0
    assert result["total"] == len(items)
    (OUT/f"{name}-verdict.txt").write_text(log)
    return result

outcomes = {
    "facts": verdict("facts", facts),
    "assumptions": verdict("assumptions", models),
    "critical": verdict("critical", critical),
    "scenarios": verdict("scenarios", scenario_checks),
}
cross_logs = []
for row in facts:
    if "fetched_value2" in row:
        cross_logs.append(run_tool([str(REPO/"tools/financial_rigor.py"), "cross-validate",
            "--field", row["label"], "--values", json.dumps({"primary":row["fetched_value"],
            "independent_transcription":row["fetched_value2"]}), "--unit", row["unit"] or "亿元"]))
(OUT/"cross-validation.txt").write_text("\n".join(cross_logs))

# Check local delivery links and source identifiers, excluding code examples.
source_ids = set(re.findall(r"^\| (S\d+) \|", body, re.M))
assert source_ids == {f"S{i:02d}" for i in range(1,41)}
for destination in re.findall(r"\]\(([^)]+)\)", body):
    if not destination.startswith(("https://", "http://", "#")):
        assert (BASE/destination).exists(), destination
assert not re.search(r"TODO|待补|待核实|turn\d+(search|view)|sk-[A-Za-z0-9]{20}", body)

summary = dict(report=REPORT.name, sha256=hashlib.sha256(REPORT.read_bytes()).hexdigest(),
    total_extracted=len(points), seed=42, sampled=len(sample),
    facts=len(facts), model_checks=len(models), excluded_metadata=len(exclusions),
    critical_checks=len(critical), scenario_checks=len(scenario_checks),
    status="PASS_WITH_EXPLICIT_SCOPE", outcomes=outcomes,
    limitation="No automatic source retrieval; manual evidence and arithmetic only. Forecasts, interviews, causality, and company investment value are not certified.")
save("audit-status.json", summary)
print(json.dumps({k:v for k,v in summary.items() if k != "outcomes"}, ensure_ascii=False, indent=2))
