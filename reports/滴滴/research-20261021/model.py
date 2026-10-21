"""滴滴全球（DIDIY）研究模型，2026-10-21。

全部计算用 Decimal。单位：人民币十亿元（bn）除非另注明。
运行：python3 reports/滴滴/research-20261021/model.py
输出：inputs.json、results.json、financial-rigor.txt（调用 tools/financial_rigor.py 与 tools/terminal_value.py）
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json
import re
import subprocess

getcontext().prec = 40
P = Path(__file__).resolve().parent
ROOT = P.parents[2]

inputs = {
    "price_usd_per_ads": "3.19",
    "price_date": "2026-10-19（美股最近一个完整交易日收盘；10-20 盘中未收盘，不采用）",
    "ads_per_share": "4",
    "shares_legal": "1126879059",
    "shares_legal_date": "2026-03-20（FY2025 20-F 实益持股表口径，已剔除已回购未注销股份）",
    "shares_economic": "1165462746",
    "shares_economic_note": "2026Q1 基本加权股数，含已归属未发行的限制性股份/RSU，作为每股价值的保守分母",
    "usd_cny": "6.7208",
    "usd_cny_date": "2026-10-19 人民币兑美元中间价（中国外汇交易中心）",
    "bridge_snapshot": "2026-03-31（2026Q1 公司公告；Q2 公告原件本轮无法取得）",
    "cash_and_treasury": "48.725",
    "borrowings": "16.310",
    "preferred_shares_by_subsidiaries": "10.557",
    "operating_buffer": "10",
    "noncore_investments_ye2025": "15.007",
    "noncore_haircut": "0.5",
    "r": "0.09",
    "r_note": "人民币口径，取技能规定区间 6%-9% 上沿；离散风险不进 r，放情景",
    "roic_terminal": "0.20",
    "payout_minus_dilution": "0.02",
    "probabilities": {"bear": "0.30", "base": "0.50", "bull": "0.20"},
    "fcff_definition": "分部税后自由现金流（扣全部股权激励经济成本、现金税、资本开支、租赁现金与营运资本），不含利息收入与投资收益；中国出行承担集团全部股权激励与总部成本",
    "scenarios": {
        "bear": {
            "china_mobility": ["9", "9", "8.5", "8.5", "8", "8", "7.5", "7.5", "7", "7"],
            "international": ["-9", "-8", "-6", "-4", "-3", "-2", "-1", "0", "0", "0"],
            "other": ["-3", "-3", "-3", "-3", "-3", "-3", "-3", "-3", "-3", "-3"],
            "g": "0",
            "other_terminal_zero": True,
        },
        "base": {
            "china_mobility": ["10", "11", "12", "12.5", "13", "13.5", "14", "14.5", "15", "15.5"],
            "international": ["-8", "-5", "-3", "-1", "0.5", "1.5", "2.5", "3", "3.5", "4"],
            "other": ["-2.5", "-2.5", "-2", "-1.5", "-1", "-0.5", "0", "0.5", "1", "1"],
            "g": "0.02",
            "other_terminal_zero": False,
        },
        "bull": {
            "china_mobility": ["11", "12.5", "14", "15.5", "17", "18", "19", "20", "21", "22"],
            "international": ["-6", "-3", "0", "2", "3.5", "5", "6", "7", "8", "9"],
            "other": ["-2.5", "-2", "-1", "0", "1", "2", "3", "4", "5", "6"],
            "g": "0.025",
            "other_terminal_zero": False,
        },
    },
    "base_2027_china_mobility_bridge": {
        "adjusted_EBITA": "16.5",
        "group_SBC_economic_cost": "3.0",
        "cash_tax_rate": "0.20",
        "capex_minus_depreciation": "0.3",
        "working_capital_and_lease": "0.4",
    },
}

price = D(inputs["price_usd_per_ads"])
ads_ratio = D(inputs["ads_per_share"])
sh_legal = D(inputs["shares_legal"])
sh_econ = D(inputs["shares_economic"])
fx = D(inputs["usd_cny"])
r = D(inputs["r"])
bn = D(10) ** 9

price_per_share = price * ads_ratio
out = {}
out["price_per_ordinary_share_usd"] = price_per_share
out["market_cap_legal_usd_bn"] = price_per_share * sh_legal / bn
out["market_cap_legal_cny_bn"] = out["market_cap_legal_usd_bn"] * fx
out["market_cap_economic_usd_bn"] = price_per_share * sh_econ / bn
out["market_cap_economic_cny_bn"] = out["market_cap_economic_usd_bn"] * fx
out["ads_equivalent_legal_bn"] = sh_legal * ads_ratio / bn

# 历史与 TTM（RMB 百万，Q2 2026 为二手来源）
q = {
    "Q3_2025": {"rev": D(58590), "ni": D(1459), "cm": D(2983), "intl": D(-1683), "other": D(-439)},
    "Q4_2025": {"rev": D(58445), "ni": D(-338), "cm": D(2618), "intl": D(-3443), "other": D(-1290)},
    "Q1_2026": {"rev": D(58743), "ni": D(-1220), "cm": D(3967), "intl": D(-2885), "other": D(-905)},
    "Q2_2026": {"rev": D(62522), "ni": D(866), "cm": D(4200), "intl": D(-2890), "other": None},
}
out["TTM_revenue_mn"] = sum(v["rev"] for v in q.values())
out["TTM_attrib_profit_mn"] = sum(v["ni"] for v in q.values())
out["TTM_CM_adj_EBITA_mn"] = sum(v["cm"] for v in q.values())
out["TTM_Intl_adj_EBITA_mn"] = sum(v["intl"] for v in q.values())
out["FY2025"] = {
    "revenue_mn": D("226701.433"), "attrib_profit_mn": D("992.647"), "OCF_mn": D("9816.065"),
    "capex_gross_mn": D("3355.749"), "lease_principal_mn": D("556.774"), "class_action_accrual_mn": D("5298"),
}
f = out["FY2025"]
f["FCF_simple_mn"] = f["OCF_mn"] - f["capex_gross_mn"]
f["FCF_after_lease_mn"] = f["FCF_simple_mn"] - f["lease_principal_mn"]
f["FCF_after_lease_ex_unpaid_class_action_mn"] = f["FCF_after_lease_mn"] - f["class_action_accrual_mn"]
f["adj_EBITA_mn"] = D(3671)
f["CM_adj_EBITA_margin_on_revenue_pct"] = D(12351) / D(201915) * 100
f["CM_adj_EBITA_over_GTV_pct"] = D(12351) / D(333759) * 100
f["CM_platform_sales_over_GTV_pct"] = D(74668) / D(333759) * 100
f["gross_margin_pct"] = (D("226701.433") - D("183196.860")) / D("226701.433") * 100

hist = {
    "2023": {"rev": D("192379.918"), "cogs": D("162915.978"), "op": D("-2838.457"), "ocf": D("3186.263"), "capex": D("2340.490"), "lease": D("700.021"), "cm_ebita": D(5323), "cm_gtv": D(270721), "cm_ps": D(47878)},
    "2024": {"rev": D("206798.631"), "cogs": D("168993.092"), "op": D("1942.439"), "ocf": D("6454.554"), "capex": D("3607.603"), "lease": D("566.110"), "cm_ebita": D(9184), "cm_gtv": D(301436), "cm_ps": D(60057)},
    "2025": {"rev": D("226701.433"), "cogs": D("183196.860"), "op": D("-3629.465"), "ocf": D("9816.065"), "capex": D("3355.749"), "lease": D("556.774"), "cm_ebita": D(12351), "cm_gtv": D(333759), "cm_ps": D(74668)},
}
out["history"] = {}
for y, h in hist.items():
    out["history"][y] = {"gross_margin_pct": (h["rev"] - h["cogs"]) / h["rev"] * 100, "op_margin_pct": h["op"] / h["rev"] * 100,
                         "FCF_after_lease_mn": h["ocf"] - h["capex"] - h["lease"], "CM_EBITA_over_GTV_pct": h["cm_ebita"] / h["cm_gtv"] * 100,
                         "CM_PS_over_GTV_pct": h["cm_ps"] / h["cm_gtv"] * 100, "CM_EBITA_over_PS_pct": h["cm_ebita"] / h["cm_ps"] * 100}
out["Q1_2026_bridge_inputs"] = {"buyback_cum_ADS_mn": D("408.7"), "buyback_cum_usd_mn": D("1825.2"), "avg_price_per_ADS": D("1825.2") / D("408.7")}
out["options_outstanding_shares"] = D(33873326) + D(55894496)
out["options_pct_of_legal"] = out["options_outstanding_shares"] / sh_legal * 100
out["PE_FY2025_legal"] = out["market_cap_legal_cny_bn"] * 1000 / D("992.647")
out["PE_TTM_legal"] = out["market_cap_legal_cny_bn"] * 1000 / out["TTM_attrib_profit_mn"]
out["PS_TTM_legal"] = out["market_cap_legal_cny_bn"] * 1000 / out["TTM_revenue_mn"]
out["mcap_over_TTM_CM_EBITA"] = out["market_cap_legal_cny_bn"] * 1000 / out["TTM_CM_adj_EBITA_mn"]

out["TTM_EPS_economic_cny"] = out["TTM_attrib_profit_mn"] / (sh_econ / D(10) ** 6)
out["three_year_per_ADS_usd"] = {}
for nm, gr, pe_ in (("bull", "1.60", "18"), ("base", "1.30", "14"), ("bear", "0.30", "10")):
    eps3 = out["TTM_EPS_economic_cny"] * (1 + D(gr)) ** 3
    out["three_year_per_ADS_usd"][nm] = {"EPS_2029_cny": eps3, "price_cny_per_share": eps3 * D(pe_),
                                         "per_ADS_usd": eps3 * D(pe_) / fx / ads_ratio}

# 现金桥
noncore = D(inputs["noncore_investments_ye2025"]) * (1 - D(inputs["noncore_haircut"]))
bridge = (D(inputs["cash_and_treasury"]) - D(inputs["borrowings"]) - D(inputs["preferred_shares_by_subsidiaries"])
          - D(inputs["operating_buffer"]) + noncore)
out["noncore_investments_after_haircut_bn"] = noncore
out["bridge_bn"] = bridge
bridge_june = (D("45.282") + D("2.639") - D("22.653") - D(inputs["preferred_shares_by_subsidiaries"])
               - D(inputs["operating_buffer"]) + noncore)
out["bridge_june_secondary_bn"] = bridge_june
out["bridge_june_per_ADS_change_usd"] = (bridge_june - bridge) * bn / fx / sh_econ / ads_ratio
out["simple_net_cash_bn"] = D(inputs["cash_and_treasury"]) - D(inputs["borrowings"])


def pv(cf, g, rate=None, terminal_zero=False):
    rate = r if rate is None else rate
    flows = sum((D(c) / (1 + rate) ** (i + 1) for i, c in enumerate(cf)), D(0))
    if terminal_zero:
        term = D(0)
    else:
        term = D(cf[-1]) * (1 + g) / (rate - g) / (1 + rate) ** len(cf)
    return flows + term, term


out["scenarios"] = {}
for name, s in inputs["scenarios"].items():
    g = D(s["g"])
    cm, cm_t = pv(s["china_mobility"], g)
    it, it_t = pv(s["international"], g)
    ot, ot_t = pv(s["other"], g, terminal_zero=s["other_terminal_zero"])
    ev = cm + it + ot
    equity = ev + bridge
    per_share_usd = equity * bn / fx / sh_econ
    per_ads_usd = per_share_usd / ads_ratio
    fcff_2036 = D(s["china_mobility"][-1]) + D(s["international"][-1]) + D(s["other"][-1])
    out["scenarios"][name] = {
        "PV_china_mobility_bn": cm, "PV_international_bn": it, "PV_other_bn": ot,
        "EV_bn": ev, "equity_bn": equity, "value_per_ADS_usd": per_ads_usd,
        "upside_pct": (per_ads_usd / price - 1) * 100,
        "terminal_share_pct": (cm_t + it_t + ot_t) / ev * 100 if ev != 0 else None,
        "FCFF_2036_bn": fcff_2036,
    }

pw = sum(D(inputs["probabilities"][k]) * out["scenarios"][k]["value_per_ADS_usd"] for k in ("bear", "base", "bull"))
out["probability_weighted_value_per_ADS_usd"] = pw
out["base_x_0_75_per_ADS_usd"] = out["scenarios"]["base"]["value_per_ADS_usd"] * D("0.75")

# 折现率敏感性（基准情景）
out["sensitivity_base_per_ADS"] = {}
for rate in ("0.07", "0.08", "0.09", "0.10", "0.11"):
    rr = D(rate)
    s = inputs["scenarios"]["base"]
    g = D(s["g"])
    ev = pv(s["china_mobility"], g, rr)[0] + pv(s["international"], g, rr)[0] + pv(s["other"], g, rr)[0]
    out["sensitivity_base_per_ADS"][rate] = (ev + bridge) * bn / fx / sh_econ / ads_ratio

# 国际业务亏损永续化的压力：基准中国出行 + 国际维持 -8bn 十年后清零 + 其他基准
s = inputs["scenarios"]["base"]
stress_intl = ["-8"] * 10
ev_stress = pv(s["china_mobility"], D("0.02"))[0] + pv(stress_intl, D(0), terminal_zero=True)[0] + pv(s["other"], D("0.02"))[0]
out["stress_intl_burn_10y_per_ADS"] = (ev_stress + bridge) * bn / fx / sh_econ / ads_ratio

# 反向估值：市值（经济股本）减净余量后，需要的稳定 FCFF
op_value = out["market_cap_economic_cny_bn"] - bridge
out["implied_operating_value_bn"] = op_value
out["reverse_flat_FCFF_bn"] = op_value * r
out["reverse_g2_FCFF_year1_bn"] = op_value * (r - D("0.02"))

# 2027 基准中国出行桥
b = {k: D(v) for k, v in inputs["base_2027_china_mobility_bridge"].items()}
ebit = b["adjusted_EBITA"] - b["group_SBC_economic_cost"]
nopat = ebit * (1 - b["cash_tax_rate"])
out["base_2027_CM_bridge"] = {
    "EBIT_after_SBC": ebit, "NOPAT": nopat,
    "FCFF": nopat - b["capex_minus_depreciation"] - b["working_capital_and_lease"],
}

# 十年压力测试：2036 归母利润 = FCFF / (1 - g/ROIC)；IRR = (利润x退出PE/今日市值)^(1/10) - 1 + k
roic = D(inputs["roic_terminal"])
k = D(inputs["payout_minus_dilution"])
out["ten_year"] = {}
for name in ("bear", "base", "bull"):
    g = D(inputs["scenarios"][name]["g"])
    fcff = out["scenarios"][name]["FCFF_2036_bn"]
    ni = fcff / (1 - g / roic)
    row = {"NI_2036_bn": ni}
    for rate in ("0.09", "0.10"):
        rr = D(rate)
        pe = (1 - g / roic) / (rr - g)
        exit_value = ni * pe
        irr = (exit_value / out["market_cap_economic_cny_bn"]) ** (D(1) / D(10)) - 1 + k
        row["r" + rate] = {"exit_PE": pe, "exit_equity_bn": exit_value, "IRR_pct": irr * 100}
    out["ten_year"][name] = row
pr = inputs["probabilities"]
out["ten_year_expected_IRR_pct_r0.09"] = sum(D(pr[n]) * out["ten_year"][n]["r0.09"]["IRR_pct"] for n in ("bear", "base", "bull"))

P.joinpath("inputs.json").write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + "\n")


def q2(x):
    if isinstance(x, D):
        return str(x.quantize(D("0.0001")))
    if isinstance(x, dict):
        return {k: q2(v) for k, v in x.items()}
    return x


P.joinpath("results.json").write_text(json.dumps(q2(out), ensure_ascii=False, indent=2) + "\n")

# 工具验证（实际输出写入 financial-rigor.txt）
mc_legal_usd = (price_per_share * sh_legal).quantize(D(1))
checks = [
    ["financial_rigor.py", "verify-market-cap", "--price", str(price_per_share), "--shares", str(sh_legal),
     "--reported", str(mc_legal_usd), "--currency", "USD"],
    ["financial_rigor.py", "verify-market-cap", "--price", str(price), "--shares", str(sh_legal * ads_ratio),
     "--reported", "14380000000", "--currency", "USD"],
    ["financial_rigor.py", "cross-validate", "--field", "FY2025 revenue (RMB mn)", "--values",
     '{"20-F 2025": 226701.433, "StockAnalysis": 226701}', "--unit", "RMB mn"],
    ["financial_rigor.py", "cross-validate", "--field", "FY2025 profit attributable (RMB mn)", "--values",
     '{"20-F 2025": 992.647, "StockAnalysis": 992.65}', "--unit", "RMB mn"],
    ["financial_rigor.py", "cross-validate", "--field", "2026-10-19 DIDIY close", "--values",
     '{"StockAnalysis": 3.19, "Investing": 3.19, "Stooq": 3.19}', "--unit", "USD"],
    ["financial_rigor.py", "cross-validate", "--field", "ordinary shares (bn)", "--values",
     '{"20-F 2026-03-20": 1.126879059, "StockAnalysis 4.51bn ADS / 4": 1.1275}', "--unit", "bn shares"],
    ["financial_rigor.py", "cross-validate", "--field", "Q2 2026 revenue (RMB mn)", "--values",
     '{"StockAnalysis": 62522, "Reuters via MarketScreener": 62500}', "--unit", "RMB mn"],
    ["financial_rigor.py", "cross-validate", "--field", "2025-12-31 cash+treasury (RMB mn)", "--values",
     '{"20-F 2025 MD&A": 55706, "Q4 2025 release": 55706, "Q1 2026 release prior column": 55706}', "--unit", "RMB mn"],
    ["financial_rigor.py", "verify-valuation", "--price", str((price_per_share * fx).quantize(D("0.0001"))),
     "--eps", str((D("992.647") / D("1190.875193")).quantize(D("0.0001"))),
     "--bvps", str((D("98071.318") / D("1139.645180")).quantize(D("0.0001")))],
    ["financial_rigor.py", "three-scenario", "--price", str((price_per_share * fx).quantize(D("0.01"))),
     "--eps", str((out["TTM_attrib_profit_mn"] / (sh_econ / D(10) ** 6)).quantize(D("0.0001"))), "--shares", str((sh_econ / D(10) ** 8).quantize(D("0.01"))),
     "--growth", "1.60", "1.30", "0.30", "--pe", "18", "14", "10", "--years", "3", "--currency", "CNY"],
    ["financial_rigor.py", "calc", "--expr", "9816.065-3355.749-556.774-5298"],
    ["financial_rigor.py", "calc", "--expr", "58590+58445+58743+62522"],
    ["terminal_value.py", "audit", "--currency", "CNY", "--r", "0.09", "--roic", "0.20", "--g", "0,0.02,0.025",
     "--rf", "0.0163", "--beta", "1.0", "--discrete-risks",
     "监管抽成上限:情景,国际外卖补贴战:情景,VIE与跨境上市监管:尾部档,场外流动性与退市:尾部档,自动驾驶替代:情景"],
    ["terminal_value.py", "pe", "--roic", "0.20", "--g", "0.02", "--r", "0.09"],
]
for name in ("bear", "base", "bull"):
    t = out["ten_year"][name]["r0.09"]
    checks.append(["terminal_value.py", "irr", "--profit", str(out["ten_year"][name]["NI_2036_bn"].quantize(D("0.0001"))),
                   "--mcap", str(out["market_cap_economic_cny_bn"].quantize(D("0.0001"))),
                   "--pe", str(t["exit_PE"].quantize(D("0.0001"))), "--years", "10", "--payout", inputs["payout_minus_dilution"]])
irr10 = ",".join(str(out["ten_year"][n]["r0.10"]["IRR_pct"].quantize(D("0.1"))) for n in ("bear", "base", "bull"))
checks.append(["terminal_value.py", "flip", "--name", "滴滴", "--roic", "0.20", "--g", "0,0.02,0.025",
               "--p", "0.30,0.50,0.20", "--irr10=" + irr10, "--k", inputs["payout_minus_dilution"],
               "--r", "0.09", "--delta", "0.02", "--currency", "CNY", "--g-shift", "0", "--rf", "0.0163"])
checks.append(["terminal_value.py", "flip", "--name", "滴滴", "--roic", "0.20", "--g", "0,0.02,0.025",
               "--p", "0.30,0.50,0.20", "--irr10=" + irr10, "--k", inputs["payout_minus_dilution"],
               "--r", "0.09", "--delta", "0.01", "--currency", "CNY", "--g-shift", "0", "--rf", "0.0163"])
logs = []
for c in checks:
    z = subprocess.run(["python3", str(ROOT / "tools" / c[0]), *c[1:]], capture_output=True, text=True)
    logs.append("COMMAND: " + " ".join(c) + "\n" + z.stdout + z.stderr)
P.joinpath("financial-rigor.txt").write_text(re.sub(r"\x1b\[[0-9;]*m", "", "\n".join(logs)))
print(json.dumps(q2(out), ensure_ascii=False, indent=2))
