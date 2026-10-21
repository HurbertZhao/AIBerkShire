"""网易（NTES / 9999.HK）研究模型：Decimal 精确计算。

运行：python3 reports/网易/research-20261021/model.py
输出：inputs.json（全部输入及口径）、results.json（全部输出）、financial-rigor.txt（工具实跑记录）。
单位：除特别说明外，金额为人民币十亿元（bn CNY）；每 ADS 价值为美元；1 ADS = 5 股普通股。
所有历史数字来自公司原件（HKEX/SEC），出处见 sources.md；情景参数是假设，不是事实。
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json, subprocess, re

getcontext().prec = 40
P = Path(__file__).resolve().parent
ROOT = P.parents[2]

inputs = {
    "price_usd_ads": "125.25", "price_date": "2026-10-19 (NASDAQ close; 10-20 US session not closed at research time)",
    "price_hkd_9999": "195.20", "price_hkd_date": "2026-10-20 (HKEX close)",
    "shares_ex_treasury": "3201652151", "shares_date": "2026-09-30 HKEX monthly return (SEC 6-K 2026-10-07)",
    "ads_ratio": "5",
    "usd_cny": "6.6807", "usd_cny_date": "2026-10-19 ECB reference via frankfurter; Yahoo 6.6909 as second source",
    "usd_hkd": "7.8487", "usd_hkd_date": "2026-10-20 ECB reference",
    # 原件：千元人民币 → 这里统一换成十亿元
    "FY2025": {"revenue": "112.625807", "gross_profit": "72.401868", "op_profit": "35.834867", "ni_attr": "33.759800",
               "nongaap_ni": "37.343702", "cfo": "50.739800", "capex_ppe": "1.065376", "capex_intangible": "0.987089",
               "da": "2.247427", "interest_income": "3.953486", "nci": "1.033718", "sbc": "3.647662",
               "dividends_paid": "13.825681", "buyback": "0.639335", "tax": "6.032686", "pretax": "40.830470"},
    "H1_2025": {"revenue": "56.720209", "gross_profit": "36.531888", "op_profit": "19.502243", "ni_attr": "18.902167",
                "nongaap_ni": "20.768658", "cfo": "22.968515", "capex_ppe": "0.643913", "capex_intangible": "0.612120",
                "da": "0.909188", "interest_income": "2.014376", "nci": "0.730969", "sbc": "1.898267"},
    "H1_2026": {"revenue": "60.697827", "gross_profit": "42.434397", "op_profit": "24.746171", "ni_attr": "17.654762",
                "nongaap_ni": "19.021538", "cfo": "23.706000", "capex_ppe": "0.330933", "capex_intangible": "0.351573",
                "da": "0.870022", "interest_income": "1.753468", "nci": "0.355211", "sbc": "1.397836",
                "tax": "4.982512", "pretax": "22.994676"},
    "BS_2026_06_30": {"cash": "22.814542", "time_deposits_current": "101.978645", "restricted_current": "4.447483",
                      "short_term_investments": "50.599638", "time_deposits_noncurrent": "0.260000",
                      "restricted_noncurrent": "0.003775", "short_term_loans": "12.604170",
                      "long_term_investments": "21.336343", "contract_liabilities": "19.297191",
                      "equity_attr": "167.090540"},
    "company_net_cash_2026_06_30": "167.5",
    "dividends_declared_ttm_usd_per_share": ["0.114", "0.232", "0.144", "0.096"],
    "weighted_basic_shares_q2_2025_k": "3188634", "weighted_basic_shares_q2_2026_k": "3203046",
    "normalization": {"tax_rate": "0.18", "note": "FY2025 实际税率14.8%，2026H1 21.7%，取18%为中值假设"},
    "operating_buffer_bn": "10",
    "pre_tax_cash_yield": "0.018", "interest_tax": "0.20",
    "r": "0.08", "rf_cny": "0.016385", "roic_incremental": "0.25",
    "scenarios": {
        "bear": {"p": "0.25", "steps": ["-0.10", "-0.02", "-0.02", "-0.02", "-0.02", "-0.02", "-0.02", "-0.02", "-0.02", "-0.02"], "g": "0.005",
                 "story": "旧IP加速衰退、新品连续失利、渠道分成红利回吐，2027年经营利润回落10%后每年-2%"},
        "base": {"p": "0.50", "steps": ["0.02", "0.04", "0.04", "0.04", "0.04", "0.03", "0.03", "0.03", "0.03", "0.03"], "g": "0.02",
                 "story": "利润率从2026H1高位小幅回落，收入中个位数增长，经营利润年增3%-4%"},
        "bull": {"p": "0.20", "steps": ["0.08", "0.08", "0.08", "0.08", "0.08", "0.05", "0.05", "0.05", "0.05", "0.05"], "g": "0.025",
                 "story": "海外与主机产品形成第二曲线，新品（如Ananta）成功，前五年年增8%"},
        "tail": {"p": "0.05", "story": "监管重击或境外上市结构受损：可动用净现金按5折、经营利润按5倍计"},
    },
    "explicit_cash_model": {"dividend_payout_of_earnings": "0.40", "annual_buyback_bn": "3.0",
                            "note": "回购只用于抵消股权激励稀释，股本按不变处理；现金在第十年按1倍计入"},
    "three_scenario_tool": {"growth": ["0.08", "0.04", "-0.05"], "pe": ["18", "15", "11"], "years": 3},
}
P.joinpath("inputs.json").write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + "\n")

I = inputs
price = D(I["price_usd_ads"]); shares = D(I["shares_ex_treasury"]); ads = shares / D(I["ads_ratio"])
fx = D(I["usd_cny"]); bn = D(10) ** 9
F, A, B = ({k: D(v) for k, v in I[x].items()} for x in ("FY2025", "H1_2025", "H1_2026"))
ttm = {k: F[k] - A[k] + B[k] for k in A}
out = {"ads_equivalent": ads, "market_cap_usd_bn": price * ads / bn}
out["market_cap_cny_bn"] = out["market_cap_usd_bn"] * fx
out["hk_price_in_usd_per_ads"] = D(I["price_hkd_9999"]) * 5 / D(I["usd_hkd"])
out["hk_vs_us_gap_pct"] = (out["hk_price_in_usd_per_ads"] / price - 1) * 100
out["TTM"] = ttm
out["TTM"]["capex_total"] = ttm["capex_ppe"] + ttm["capex_intangible"]
out["TTM"]["simple_fcf"] = ttm["cfo"] - out["TTM"]["capex_total"]
out["TTM"]["gross_margin_pct"] = ttm["gross_profit"] / ttm["revenue"] * 100
out["TTM"]["op_margin_pct"] = ttm["op_profit"] / ttm["revenue"] * 100
out["FY2025_margins_pct"] = {"gross": F["gross_profit"] / F["revenue"] * 100, "op": F["op_profit"] / F["revenue"] * 100,
                             "net": F["ni_attr"] / F["revenue"] * 100, "eff_tax": F["tax"] / F["pretax"] * 100}
out["H1_2026_eff_tax_pct"] = B["tax"] / B["pretax"] * 100

bs = {k: D(v) for k, v in I["BS_2026_06_30"].items()}
net_cash = (bs["cash"] + bs["time_deposits_current"] + bs["restricted_current"] + bs["short_term_investments"]
            + bs["time_deposits_noncurrent"] + bs["restricted_noncurrent"] - bs["short_term_loans"])
usable = net_cash - bs["restricted_current"] - bs["restricted_noncurrent"] - D(I["operating_buffer_bn"])
out["net_cash_recomputed_bn"] = net_cash
out["net_cash_vs_company_gap_pct"] = (net_cash / D(I["company_net_cash_2026_06_30"]) - 1) * 100
out["usable_net_cash_bn"] = usable
out["usable_net_cash_per_ads_usd"] = usable * bn / fx / ads
out["net_cash_share_of_mcap_pct"] = net_cash / out["market_cap_cny_bn"] * 100

tax = D(I["normalization"]["tax_rate"])
nopat_parent = ttm["op_profit"] * (1 - tax) - ttm["nci"]
fcff0 = nopat_parent + ttm["da"] - out["TTM"]["capex_total"]
interest_at = usable * D(I["pre_tax_cash_yield"]) * (1 - D(I["interest_tax"]))
norm_ni = nopat_parent + interest_at
out["normalized"] = {"nopat_parent_bn": nopat_parent, "fcff_parent_bn": fcff0, "after_tax_interest_bn": interest_at,
                     "normalized_ni_bn": norm_ni, "normalized_eps_usd_per_ads": norm_ni * bn / fx / ads}
divs = sum(D(x) for x in I["dividends_declared_ttm_usd_per_share"]) * 5
dil = D(I["weighted_basic_shares_q2_2026_k"]) / D(I["weighted_basic_shares_q2_2025_k"]) - 1
gaap_eps_ads = ttm["ni_attr"] * bn / fx / ads
ev_ops = out["market_cap_cny_bn"] - usable
out["valuation"] = {
    "gaap_eps_ttm_usd_per_ads": gaap_eps_ads, "PE_ttm_gaap": price / gaap_eps_ads,
    "PE_ttm_nongaap": out["market_cap_cny_bn"] / ttm["nongaap_ni"],
    "PE_fy2025_gaap": out["market_cap_cny_bn"] / F["ni_attr"],
    "PE_normalized": price / out["normalized"]["normalized_eps_usd_per_ads"],
    "PS_ttm": out["market_cap_cny_bn"] / ttm["revenue"],
    "ev_ops_bn": ev_ops, "EV_ops_over_nopat": ev_ops / nopat_parent, "EV_ops_over_ttm_op_profit": ev_ops / ttm["op_profit"],
    "fcf_yield_simple_pct": out["TTM"]["simple_fcf"] / out["market_cap_cny_bn"] * 100,
    "dividend_ttm_usd_per_ads": divs, "dividend_yield_pct": divs / price * 100,
    "share_count_change_yoy_pct": dil * 100, "k_div_minus_dilution": divs / price - dil,
    "PB": out["market_cap_cny_bn"] / bs["equity_attr"],
}

# 历史年末 PE（年末收盘 × 当日 ECB 汇率 ÷ 稀释每 ADS 收益）
hist = {"2021": ("101.78", "6.3524", "5.01"), "2022": ("72.63", "6.8987", "6.17"), "2023": ("93.16", "7.1049", "9.05"),
        "2024": ("89.21", "7.2994", "9.19"), "2025": ("137.62", "7.001", "10.48")}
I["historical_pe_inputs"] = {y: {"close_usd": a, "usd_cny": b, "diluted_eps_rmb_per_share": c} for y, (a, b, c) in hist.items()}
out["historical_year_end_PE"] = {y: D(a) * D(b) / (D(c) * 5) for y, (a, b, c) in hist.items()}

r = D(I["r"]); roic = D(I["roic_incremental"])
def exit_pe(g): return (1 - g / roic) / (r - g)
def path(steps):
    v, res = fcff0, []
    for s in steps:
        v = v * (1 + D(s)); res.append(v)
    return res
def dcf(cfs, g, rate):
    pv = sum(c / (1 + rate) ** (i + 1) for i, c in enumerate(cfs))
    tv = cfs[-1] * (1 + g) / (rate - g) / (1 + rate) ** len(cfs)
    return pv + tv, tv
out["scenarios"] = {}
for name in ("bear", "base", "bull"):
    s = I["scenarios"][name]; cfs = path(s["steps"]); g = D(s["g"])
    ev, tv = dcf(cfs, g, r); eq = ev + usable
    out["scenarios"][name] = {"fcff_path_bn": cfs, "ev_bn": ev, "terminal_share_pct": tv / ev * 100, "equity_bn": eq,
                              "value_per_ads_usd": eq * bn / fx / ads, "upside_pct": (eq * bn / fx / ads / price - 1) * 100,
                              "fcff_2036_bn": cfs[-1], "exit_pe_formula": exit_pe(g), "r_minus_g": r - g}
tail_eq = usable * D("0.5") + nopat_parent * 5
out["scenarios"]["tail"] = {"equity_bn": tail_eq, "value_per_ads_usd": tail_eq * bn / fx / ads,
                            "upside_pct": (tail_eq * bn / fx / ads / price - 1) * 100}
pw = sum(D(I["scenarios"][n]["p"]) * out["scenarios"][n]["value_per_ads_usd"] for n in ("bear", "base", "bull", "tail"))
out["probability_weighted_value_usd"] = pw
out["action_prices_usd"] = {"buy_below_70pct_of_weighted": pw * D("0.70"), "add_below_bear": out["scenarios"]["bear"]["value_per_ads_usd"],
                            "trim_above_base": out["scenarios"]["base"]["value_per_ads_usd"]}

# 反向 DCF：当前经营市值隐含的永续增速（从 2027 年 FCFF = fcff0 起）
def implied_g(rate):
    return (ev_ops * rate - fcff0) / (ev_ops + fcff0)
out["reverse_dcf"] = {"implied_perpetual_g_r8": implied_g(D("0.08")), "implied_perpetual_g_r10": implied_g(D("0.10")),
                      "implied_perpetual_g_r12": implied_g(D("0.12")),
                      "zero_growth_value_r8_bn": fcff0 / D("0.08") + usable}

# 敏感性：基准情景每 ADS 价值随 r、税率变化
sens = {}
for rate in ("0.07", "0.08", "0.09", "0.10"):
    ev, _ = dcf(path(I["scenarios"]["base"]["steps"]), D("0.02"), D(rate)); sens["r=" + rate] = (ev + usable) * bn / fx / ads
for tr in ("0.15", "0.22"):
    f0 = ttm["op_profit"] * (1 - D(tr)) - ttm["nci"] + ttm["da"] - out["TTM"]["capex_total"]
    v, cfs = f0, []
    for s_ in I["scenarios"]["base"]["steps"]:
        v = v * (1 + D(s_)); cfs.append(v)
    ev, _ = dcf(cfs, D("0.02"), r); sens["tax=" + tr] = (ev + usable) * bn / fx / ads
out["sensitivity_base_value_usd"] = sens

# 三年三情景（与 financial_rigor three-scenario 同算法，便于交叉核对）
eps0 = out["normalized"]["normalized_eps_usd_per_ads"]; ts = I["three_scenario_tool"]
out["three_year"] = {n: {"eps_2029": eps0 * (1 + D(gr)) ** 3, "price": eps0 * (1 + D(gr)) ** 3 * D(pe)}
                     for n, gr, pe in zip(("bull", "base", "bear"), ts["growth"], ts["pe"])}

# 十年 IRR：工具口径（现金只以利息进入利润）与显式现金口径
mcap = out["market_cap_cny_bn"]; k = out["valuation"]["k_div_minus_dilution"]
def solve_irr(flows):
    lo, hi = D("-0.5"), D("0.6")
    for _ in range(200):
        mid = (lo + hi) / 2
        npv = sum(c / (1 + mid) ** t for t, c in enumerate(flows))
        lo, hi = (mid, hi) if npv > 0 else (lo, mid)
    return mid
ec = I["explicit_cash_model"]; pay = D(ec["dividend_payout_of_earnings"]); bb = D(ec["annual_buyback_bn"])
yld = D(I["pre_tax_cash_yield"]) * (1 - D(I["interest_tax"]))
out["irr10"] = {}
for name in ("bear", "base", "bull"):
    sc = out["scenarios"][name]; pe = sc["exit_pe_formula"]
    profit_tool = sc["fcff_2036_bn"] + interest_at
    irr_tool = (profit_tool * pe / mcap) ** (D(1) / 10) if False else None
    import math
    irr_tool = D(str(math.pow(float(profit_tool * pe / mcap), 0.1))) - 1 + k
    irr_tool_r10 = D(str(math.pow(float(profit_tool * ((1 - D(I['scenarios'][name]['g']) / roic) / (D('0.10') - D(I['scenarios'][name]['g']))) / mcap), 0.1))) - 1 + k
    cash, flows = usable, [-mcap]
    for t, f in enumerate(sc["fcff_path_bn"]):
        inte = cash * yld; earn = f + inte; div = earn * pay
        cash = cash + earn - div - bb
        flows.append(div if t < 9 else div + f * pe + cash)
    out["irr10"][name] = {"profit_2036_tool_bn": profit_tool, "exit_pe": pe, "irr_tool_pct": irr_tool * 100,
                          "irr_tool_at_r10_pct": irr_tool_r10 * 100,
                          "irr_explicit_cash_pct": solve_irr(flows) * 100, "cash_2036_bn": cash}
p3 = {"bear": D("0.30"), "base": D("0.50"), "bull": D("0.20")}
out["irr10"]["expected_tool_pct"] = sum(p3[n] * out["irr10"][n]["irr_tool_pct"] for n in p3)
out["irr10"]["expected_explicit_pct"] = sum(p3[n] * out["irr10"][n]["irr_explicit_cash_pct"] for n in p3)
out["irr10"]["note"] = "三档概率把5%尾部并入悲观档（0.25+0.05）"

P.joinpath("inputs.json").write_text(json.dumps(I, ensure_ascii=False, indent=2) + "\n")
P.joinpath("results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=lambda x: str(round(x, 6)) if isinstance(x, D) else str(x)) + "\n")

# 工具实跑
def q(x, n=4): return str(round(x, n))
nopat_ads_eps = q(out["normalized"]["normalized_eps_usd_per_ads"])
checks = [
    ("financial_rigor.py", ["verify-market-cap", "--price", I["price_usd_ads"], "--shares", q(ads, 1), "--reported", q(out["market_cap_usd_bn"] * bn, 0), "--currency", "USD"]),
    ("financial_rigor.py", ["calc", "--expr", f"{I['price_hkd_9999']}*{I['shares_ex_treasury']}"]),
    ("financial_rigor.py", ["cross-validate", "--field", "NTES close 2026-10-19", "--values", '{"Yahoo": 125.25, "StockAnalysis": 125.25}', "--unit", "USD"]),
    ("financial_rigor.py", ["cross-validate", "--field", "9999.HK close 2026-10-20 (HKD) vs NTES-implied", "--values", json.dumps({"StockAnalysis_HK_x5_div_USDHKD": float(round(out['hk_price_in_usd_per_ads'], 4)), "NTES_close": 125.25}), "--unit", "USD per ADS"]),
    ("financial_rigor.py", ["cross-validate", "--field", "shares outstanding", "--values", '{"HKEX monthly return 2026-09-30": 3201652151, "20-F cover 2025-12-31": 3192111251, "StockAnalysis": 3200000000}', "--unit", "shares"]),
    ("financial_rigor.py", ["cross-validate", "--field", "USD/CNY 2026-10-19", "--values", '{"ECB_frankfurter": 6.6807, "Yahoo": 6.6909}', "--unit", "CNY"]),
    ("financial_rigor.py", ["cross-validate", "--field", "FY2025 revenue", "--values", '{"HKEX FY2025 results / 20-F": 112625.807, "StockAnalysis": 112626}', "--unit", "CNY million"]),
    ("financial_rigor.py", ["cross-validate", "--field", "FY2025 net income attributable", "--values", '{"HKEX FY2025 results / 20-F": 33759.8, "StockAnalysis": 33760}', "--unit", "CNY million"]),
    ("financial_rigor.py", ["cross-validate", "--field", "TTM revenue to 2026-06-30", "--values", json.dumps({"computed FY25-H1'25+H1'26": float(ttm['revenue'] * 1000), "StockAnalysis TTM": 116603}), "--unit", "CNY million"]),
    ("financial_rigor.py", ["cross-validate", "--field", "TTM net income attributable", "--values", json.dumps({"computed": float(round(ttm['ni_attr'] * 1000, 1)), "StockAnalysis TTM": 32512}), "--unit", "CNY million"]),
    ("financial_rigor.py", ["cross-validate", "--field", "TTM operating cash flow", "--values", json.dumps({"computed": float(round(ttm['cfo'] * 1000, 1)), "StockAnalysis TTM": 51477}), "--unit", "CNY million"]),
    ("financial_rigor.py", ["cross-validate", "--field", "net cash 2026-06-30", "--values", json.dumps({"company stated": 167.5, "recomputed from balance sheet": float(round(net_cash, 3))}), "--unit", "CNY bn"]),
    ("financial_rigor.py", ["cross-validate", "--field", "Ding beneficial ownership", "--values", '{"20-F (2026-02-28)": 45.5, "StockAnalysis insider": 45.32}', "--unit", "%"]),
    ("financial_rigor.py", ["verify-valuation", "--price", I["price_usd_ads"], "--eps", q(gaap_eps_ads), "--bvps", q(bs["equity_attr"] * bn / fx / ads), "--fcf-per-share", q(out["TTM"]["simple_fcf"] * bn / fx / ads), "--dividend", q(divs)]),
    ("financial_rigor.py", ["verify-valuation", "--price", I["price_usd_ads"], "--eps", nopat_ads_eps]),
    ("financial_rigor.py", ["three-scenario", "--price", I["price_usd_ads"], "--eps", nopat_ads_eps, "--shares", q(ads / D(10) ** 8, 4),
                            "--growth", *ts["growth"], "--pe", *ts["pe"], "--years", "3", "--currency", "USD"]),
    ("terminal_value.py", ["audit", "--currency", "CNY", "--r", I["r"], "--roic", I["roic_incremental"], "--g", "0.005,0.02,0.025", "--rf", I["rf_cny"], "--beta", "1.0",
                           "--discrete-risks", "游戏监管重击:尾部档,境外上市结构或退市:尾部档,海外地缘与出口管制:情景,新品失败:情景,境内现金汇出预提税:未建模"]),
]
for name in ("bear", "base", "bull"):
    checks.append(("terminal_value.py", ["pe", "--roic", I["roic_incremental"], "--g", I["scenarios"][name]["g"], "--r", I["r"]]))
    checks.append(("terminal_value.py", ["irr", "--profit", q(out["irr10"][name]["profit_2036_tool_bn"]), "--mcap", q(mcap), "--pe", q(out["irr10"][name]["exit_pe"]), "--years", "10", "--payout", q(k, 5)]))
irr10_anchor = ",".join(q(out["irr10"][n]["irr_tool_at_r10_pct"], 2) for n in ("bear", "base", "bull"))
for delta in ("0.02", "0.01"):
    checks.append(("terminal_value.py", ["flip", "--name", "网易", "--roic", I["roic_incremental"], "--g", "0.005,0.02,0.025", "--p", "0.30,0.50,0.20",
                                         f"--irr10={irr10_anchor}", "--k", q(k, 5), "--r", I["r"], "--delta", delta, "--currency", "CNY", "--g-shift", "0", "--rf", I["rf_cny"]]))
logs = []
for tool, c in checks:
    z = subprocess.run(["python3", str(ROOT / "tools" / tool), *c], capture_output=True, text=True)
    logs.append(f"COMMAND: python3 tools/{tool} " + " ".join(c) + f"\nEXIT: {z.returncode}\n" + z.stdout + z.stderr)
P.joinpath("financial-rigor.txt").write_text(re.sub(r"\x1b\[[0-9;]*m", "", "\n".join(logs)))
print(json.dumps(out, ensure_ascii=False, indent=1, default=lambda x: str(round(x, 4)) if isinstance(x, D) else str(x)))
