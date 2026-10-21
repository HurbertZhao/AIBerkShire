"""汽车之家（ATHM / 2518）估值模型，2026-10-21。

全部计算用 Decimal。运行：python3 reports/汽车之家/research-20261021/model.py
输出：inputs.json、results.json、financial-rigor.txt（调用 tools/financial_rigor.py 与 tools/terminal_value.py 的实际输出）。
单位：除特别注明，金额为人民币百万元；每 ADS = 4 股普通股。
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json, re, subprocess

getcontext().prec = 40
P = Path(__file__).resolve().parent
ROOT = P.parents[2]

inputs = {
    "price_usd_per_ads": "20.15",
    "price_date": "2026-10-20 (NYSE close, StockAnalysis history; Yahoo chart 20.16)",
    "hk_price_hkd": "39.50",
    "hk_price_date": "2026-10-16 (HKEX 2518 close via Yahoo; 10-19 HK holiday)",
    "usd_cny": "6.6909",
    "usd_cny_date": "2026-10-19 Yahoo CNY=X close (market reference, single source)",
    "usd_hkd": "7.8472",
    "noon_buying_rate_20260630": "6.7851",
    "shares_20260331": "460683644",
    "ads_buyback_march_program_total": "10627269",
    "ads_buyback_march_program_by_0522": "3465236",
    "ads_buyback_new_program_by_0814": "1895093",
    "usd_spent_march_program_by_0522_m": "62.3",
    "usd_march_program_total_m": "200",
    "usd_spent_new_program_by_0814_m": "43.6",
    "bs_20260630": {
        "cash": "2495.814", "restricted_cash_current": "76.276", "restricted_cash_noncurrent": "5.000",
        "short_term_investments": "15659.096", "other_long_term_investments": "1209.698",
        "long_term_equity_investments": "386.511", "dividends_payable": "489.821",
        "mezzanine_TTP_redeemable_NCI": "2220.070", "total_liabilities": "3512.527",
    },
    "operating_cash_buffer": "1500",
    "quarters": {
        "Q3_2025": {"revenue": "1778.1", "op_profit": "147.0", "ni_autohome": "436.6", "ni_ordinary": "419.4", "cfo": "66.6", "interest_inv_income": "161.814", "equity_method": "132.685"},
        "Q4_2025": {"revenue": "1461.998", "op_profit": "92.259", "ni_autohome": "233.893", "ni_ordinary": "226.409", "cfo": "193.2", "interest_inv_income": "155.802", "equity_method": "-17.957"},
        "Q1_2026": {"revenue": "1048.4", "op_profit": "-34.4", "ni_autohome": "44.3", "ni_ordinary": "44.3", "cfo": "-143.0", "interest_inv_income": "142.137", "equity_method": "-55.548"},
        "Q2_2026": {"revenue": "1198.010", "op_profit": "129.980", "ni_autohome": "247.810", "ni_ordinary": "247.810", "cfo": "261.2", "interest_inv_income": "132.868", "equity_method": "0.042"},
    },
    "fy": {
        "2021": {"revenue": "7237.004", "op_profit": "1781.612", "ni_autohome": "2248.785", "cfo": "3523.934", "capex": "218.798"},
        "2022": {"revenue": "6940.828", "op_profit": "1247.522", "ni_autohome": "1855.174", "cfo": "2565.075", "capex": "116.503"},
        "2023": {"revenue": "7184.135", "op_profit": "1137.425", "ni_autohome": "1935.310", "cfo": "2451.429", "capex": "78.567"},
        "2024": {"revenue": "7039.587", "op_profit": "1003.497", "ni_autohome": "1681.123", "cfo": "1373.135", "capex": "139.996"},
        "2025": {"revenue": "6452.030", "op_profit": "769.287", "ni_autohome": "1442.830", "cfo": "889.462", "capex": "118.057",
                 "dividends_paid": "1481.245", "buyback_paid": "1051.983"},
    },
    "r": "0.09",
    "r_note": "CNY cash flows; top of CNY 6%-9% band to reflect ADR/VIE/controller risk qualitatively; discrete risks handled as scenarios, not in r",
    "scenarios": {
        "bear": {"prob": "0.30", "op_fcf_bn": ["-0.4", "-0.4", "-0.3", "-0.2", "-0.1", "0", "0", "0", "0", "0"], "g": "0", "cash_misallocation_bn": "3.0"},
        "base": {"prob": "0.50", "op_fcf_bn": ["0.25", "0.30", "0.35", "0.40", "0.45", "0.50", "0.50", "0.50", "0.50", "0.50"], "g": "0", "cash_misallocation_bn": "0"},
        "bull": {"prob": "0.20", "op_fcf_bn": ["0.5", "0.7", "0.9", "1.0", "1.1", "1.2", "1.25", "1.3", "1.35", "1.4"], "g": "0.02", "cash_misallocation_bn": "0"},
    },
    "scenario_definition": "Unlevered operating FCF 2027-2036, RMB bn, after cash tax, after economic SBC, capex and lease; EXCLUDES interest/investment income (cash is valued at book in the bridge). Bear adds a one-off 3.0bn haircut for cash consumed by low-return offline retail / related-party use.",
    "cash_yield_after_tax": "0.017",
    "ten_year_payout_k": "0.06",
}
P.joinpath("inputs.json").write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + "\n")

M = D(10) ** 6
price = D(inputs["price_usd_per_ads"]); fx = D(inputs["usd_cny"]); fx_jun = D(inputs["noon_buying_rate_20260630"])
s0331 = D(inputs["shares_20260331"])
b_total = D(inputs["ads_buyback_march_program_total"]); b_0522 = D(inputs["ads_buyback_march_program_by_0522"]); b_new = D(inputs["ads_buyback_new_program_by_0814"])
shares_high = s0331 - 4 * ((b_total - b_0522) + b_new)  # counts only buybacks provably after 2026-03-31
shares_low = s0331 - 4 * (b_total + b_new)              # if all March-program buybacks were after 03-31
ads_high = shares_high / 4
out = {"shares": {"20260331_20F": s0331, "estimate_high_used": shares_high, "estimate_low": shares_low,
                  "ads_high": ads_high, "note": "excludes RSU vesting and any buyback after 2026-08-14"}}

mcap_usd_m = price * ads_high / M
mcap_cny_m = mcap_usd_m * fx
out["market_cap"] = {"usd_m": mcap_usd_m, "cny_m": mcap_cny_m,
                     "usd_m_with_low_share_estimate": price * shares_low / 4 / M,
                     "usd_m_with_20260331_shares": price * s0331 / 4 / M}
out["hk_parity_usd_per_ads"] = D(inputs["hk_price_hkd"]) * 4 / D(inputs["usd_hkd"])

bs = {k: D(v) for k, v in inputs["bs_20260630"].items()}
fin_assets = bs["cash"] + bs["short_term_investments"] + bs["other_long_term_investments"]
post_jun_buyback_usd_max = (D(inputs["usd_march_program_total_m"]) - D(inputs["usd_spent_march_program_by_0522_m"])) + D(inputs["usd_spent_new_program_by_0814_m"])
post_jun_buyback_cny = post_jun_buyback_usd_max * fx_jun
gross_net_cash = fin_assets - bs["dividends_payable"] - post_jun_buyback_cny
bridge = gross_net_cash - bs["mezzanine_TTP_redeemable_NCI"] - D(inputs["operating_cash_buffer"])
out["bridge_cny_m"] = {"financial_assets_company_def": fin_assets, "less_dividends_payable": bs["dividends_payable"],
                       "less_post_june_buyback_upper_bound": post_jun_buyback_cny, "gross_net_cash": gross_net_cash,
                       "less_TTP_mezzanine": bs["mezzanine_TTP_redeemable_NCI"], "less_operating_buffer": D(inputs["operating_cash_buffer"]),
                       "conservative_bridge": bridge}
per_ads = lambda cny_m: cny_m * M / ads_high / fx
out["per_ads_usd"] = {"gross_net_cash": per_ads(gross_net_cash), "conservative_bridge": per_ads(bridge)}
out["implied_operating_EV_cny_m"] = {"vs_conservative_bridge": mcap_cny_m - bridge, "vs_gross_net_cash": mcap_cny_m - gross_net_cash}

q = inputs["quarters"]
ttm = {k: sum(D(q[x][k]) for x in q) for k in ["revenue", "op_profit", "ni_autohome", "ni_ordinary", "cfo", "interest_inv_income", "equity_method"]}
ttm["ni_autohome_ex_equity_method"] = ttm["ni_autohome"] - ttm["equity_method"]
out["ttm"] = ttm
out["ttm_ratios"] = {"PE_ni_autohome": mcap_cny_m / ttm["ni_autohome"], "PE_ni_ordinary": mcap_cny_m / ttm["ni_ordinary"],
                     "PS": mcap_cny_m / ttm["revenue"], "op_margin_pct": ttm["op_profit"] / ttm["revenue"] * 100,
                     "eps_ads_usd_ni_autohome": ttm["ni_autohome"] * M / ads_high / fx}
fy = inputs["fy"]
out["fy"] = {}
for y, v in fy.items():
    r_ = D(v["revenue"]); out["fy"][y] = {"op_margin_pct": D(v["op_profit"]) / r_ * 100, "net_margin_pct": D(v["ni_autohome"]) / r_ * 100,
                                         "simple_fcf": D(v["cfo"]) - D(v["capex"])}
out["fy2025_shareholder_return"] = {"cny_m": D(fy["2025"]["dividends_paid"]) + D(fy["2025"]["buyback_paid"]),
                                    "pct_of_current_mcap": (D(fy["2025"]["dividends_paid"]) + D(fy["2025"]["buyback_paid"])) / mcap_cny_m * 100}
out["yoy"] = {"Q2_revenue_pct": (D("1198.010") / D("1758.120") - 1) * 100, "Q2_leads_pct": (D("560.357") / D("732.581") - 1) * 100,
              "Q2_media_pct": (D("280.386") / D("279.399") - 1) * 100, "Q2_marketplace_pct": (D("357.267") / D("746.140") - 1) * 100,
              "H1_revenue_pct": (D("2246.449") / D("3211.938") - 1) * 100, "H1_gross_profit_pct": (D("1715.424") / D("2392.994") - 1) * 100,
              "FY2025_media_pct": (D("1153.419") / D("1523.075") - 1) * 100, "FY2025_leads_pct": (D("2709.235") / D("3135.885") - 1) * 100,
              "revenue_2021_2025_cagr_pct": ((D("6452.030") / D("7237.004")) ** (D(1) / D(4)) - 1) * 100}
out["haier_entry"] = {"price_cny_per_share": D("13100") / D("200.884012"), "usd_per_ads": D("1800") / D("200.884012") * 4,
                      "stake_pct_of_est_shares": D("200884012") / shares_high * 100}

r = D(inputs["r"])
def pv(cf, g, rate):
    flows = sum((D(c) / (1 + rate) ** (i + 1) for i, c in enumerate(cf)), D(0))
    tv = D(cf[-1]) * (1 + g) / (rate - g) / (1 + rate) ** len(cf)
    return flows, tv
out["scenarios"] = {}
wsum = D(0)
for name, s in inputs["scenarios"].items():
    fl, tv = pv(s["op_fcf_bn"], D(s["g"]), r)
    ev = (fl + tv) * 1000
    equity = ev + bridge - D(s["cash_misallocation_bn"]) * 1000
    v = per_ads(equity)
    wsum += D(s["prob"]) * v
    out["scenarios"][name] = {"ops_EV_cny_m": ev, "pv_flows_cny_m": fl * 1000, "pv_terminal_cny_m": tv * 1000,
                              "equity_cny_m": equity, "value_usd_per_ads": v, "vs_price_pct": (v / price - 1) * 100}
out["prob_weighted_usd_per_ads"] = wsum
out["prob_weighted_vs_price_pct"] = (wsum / price - 1) * 100
out["sensitivity_r"] = {}
for rate in ["0.07", "0.08", "0.09", "0.10", "0.11"]:
    rr = D(rate); row = {}
    for name, s in inputs["scenarios"].items():
        fl, tv = pv(s["op_fcf_bn"], D(s["g"]), rr)
        row[name] = per_ads((fl + tv) * 1000 + bridge - D(s["cash_misallocation_bn"]) * 1000)
    out["sensitivity_r"][rate] = row
# reverse: perpetual zero-growth operating FCF implied by price
out["reverse"] = {"implied_flat_op_fcf_cny_m_vs_conservative_bridge": (mcap_cny_m - bridge) * r,
                  "implied_flat_op_fcf_cny_m_vs_gross_net_cash": (mcap_cny_m - gross_net_cash) * r,
                  "ttm_op_profit_after_15pct_tax": ttm["op_profit"] * D("0.85")}
# cash-inclusive 10-year IRR (own model): buy at mcap; each year receive op FCF + after-tax cash yield on bridge; exit 2036 = bridge - misallocation + ops TV
def irr(cfs):
    lo, hi = D("-0.9"), D("1.0")
    for _ in range(200):
        mid = (lo + hi) / 2
        npv = sum((c / (1 + mid) ** t for t, c in enumerate(cfs)), D(0))
        lo, hi = (mid, hi) if npv > 0 else (lo, mid)
    return mid
out["ten_year_cash_inclusive_irr_pct"] = {}
cy = D(inputs["cash_yield_after_tax"])
for name, s in inputs["scenarios"].items():
    base_cash = bridge - D(s["cash_misallocation_bn"]) * 1000
    cfs = [-mcap_cny_m]
    for i, c in enumerate(s["op_fcf_bn"]):
        cfs.append(D(c) * 1000 + base_cash * cy)
    g = D(s["g"]); last = D(s["op_fcf_bn"][-1]) * 1000
    cfs[-1] += base_cash + last * (1 + g) / (r - g)
    out["ten_year_cash_inclusive_irr_pct"][name] = irr(cfs) * 100
out["ten_year_cash_returned_3y_irr_pct"] = {}
for name, s in inputs["scenarios"].items():
    base_cash = bridge - D(s["cash_misallocation_bn"]) * 1000
    cfs = [-mcap_cny_m]
    remaining = base_cash
    for i, c in enumerate(s["op_fcf_bn"]):
        pay = base_cash / 3 if i < 3 else D(0)
        cfs.append(D(c) * 1000 + remaining * cy + pay)
        remaining -= pay
    g = D(s["g"]); last = D(s["op_fcf_bn"][-1]) * 1000
    cfs[-1] += last * (1 + g) / (r - g)
    out["ten_year_cash_returned_3y_irr_pct"][name] = irr(cfs) * 100
out["ten_year_cash_returned_3y_irr_pct"]["prob_weighted"] = sum(D(s["prob"]) * out["ten_year_cash_returned_3y_irr_pct"][n] for n, s in inputs["scenarios"].items())
out["ten_year_cash_inclusive_irr_pct"]["prob_weighted"] = sum(D(s["prob"]) * out["ten_year_cash_inclusive_irr_pct"][n] for n, s in inputs["scenarios"].items())
# inputs for terminal_value.py irr (tool-native: exit = profit x PE, cash only via its yield)
out["tool_profit_2036_cny_bn"] = {n: D(s["op_fcf_bn"][-1]) + (bridge / 1000 - D(s["cash_misallocation_bn"])) * cy for n, s in inputs["scenarios"].items()}
acts = {"buy_below": D("17.0"), "watch_upper": D("25.0"), "trim_above": D("26.5")}
out["action_prices_usd_per_ads"] = acts
out["action_prices_hkd_per_share"] = {k: v * D(inputs["usd_hkd"]) / 4 for k, v in acts.items()}
out["buy_below_discount_to_conservative_bridge_pct"] = (acts["buy_below"] / out["per_ads_usd"]["conservative_bridge"] - 1) * 100

P.joinpath("results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str) + "\n")

def run(tool, args):
    z = subprocess.run(["python3", str(ROOT / "tools" / tool), *args], capture_output=True, text=True)
    return f"COMMAND: {tool} {' '.join(args)}\n{z.stdout}{z.stderr}"

q2 = lambda x: str(x.quantize(D("0.0001")))
mc_rep = str((mcap_usd_m * M).quantize(D(1)))
tp = out["tool_profit_2036_cny_bn"]; mc_bn = q2(mcap_cny_m / 1000)
checks = [
    ("financial_rigor.py", ["verify-market-cap", "--price", "20.15", "--shares", str(ads_high), "--reported", mc_rep, "--currency", "USD"]),
    ("financial_rigor.py", ["verify-market-cap", "--price", "20.15", "--shares", "115760000", "--reported", "2330000000", "--currency", "USD"]),
    ("financial_rigor.py", ["cross-validate", "--field", "2026-10-20 ATHM close", "--values", '{"StockAnalysis history": 20.15, "Yahoo chart": 20.16, "HK 2518 parity (10-16)": ' + q2(out["hk_parity_usd_per_ads"]) + '}', "--unit", "USD/ADS"]),
    ("financial_rigor.py", ["cross-validate", "--field", "2025-12-31 ordinary shares outstanding", "--values", '{"20-F F-5": 463038708, "StockAnalysis 115.76M ADS x4": 463040000}', "--unit", "shares"]),
    ("financial_rigor.py", ["cross-validate", "--field", "FY2025 revenue", "--values", '{"20-F F-6": 6452.030, "StockAnalysis": 6452}', "--unit", "CNY million"]),
    ("financial_rigor.py", ["cross-validate", "--field", "FY2025 net income to ordinary shareholders", "--values", '{"20-F F-6": 1385.133, "StockAnalysis": 1385}', "--unit", "CNY million"]),
    ("financial_rigor.py", ["cross-validate", "--field", "FY2025 operating cash flow", "--values", '{"20-F F-7": 889.462, "StockAnalysis": 889.46}', "--unit", "CNY million"]),
    ("financial_rigor.py", ["cross-validate", "--field", "TTM net income to ordinary (Q3-25..Q2-26)", "--values", '{"quarterly releases sum": ' + q2(ttm["ni_ordinary"]) + ', "StockAnalysis TTM": 937.88}', "--unit", "CNY million"]),
    ("financial_rigor.py", ["cross-validate", "--field", "2026-06-30 cash+ST investments", "--values", '{"Q2 release": ' + q2(bs["cash"] + bs["short_term_investments"]) + ', "StockAnalysis": 18155}', "--unit", "CNY million"]),
    ("financial_rigor.py", ["verify-valuation", "--price", "20.15", "--eps", q2(out["ttm_ratios"]["eps_ads_usd_ni_autohome"]), "--fcf-per-share", q2((ttm["cfo"] - D("118.057")) * M / ads_high / fx), "--dividend", "1.86"]),
    ("financial_rigor.py", ["three-scenario", "--price", "20.15", "--eps", q2(out["ttm_ratios"]["eps_ads_usd_ni_autohome"]), "--shares", q2(ads_high / D(10) ** 8),
                             "--growth", "0.05", "-0.05", "-0.20", "--pe", "16", "12", "8", "--years", "3", "--currency", "USD"]),
    ("financial_rigor.py", ["calc", "--expr", "2495.814+15659.096+1209.698-489.821-(200-62.3+43.6)*6.7851-2220.070-1500"]),
    ("terminal_value.py", ["audit", "--currency", "CNY", "--r", "0.09", "--roic", "0.12", "--g", "0,0,0.02", "--rf", "0.017", "--beta", "1.0",
                           "--discrete-risks", "控股股东资金占用或低效投资:情景,VIE与中概退市:尾部档,行业销量继续下滑:情景,AI搜索绕过垂直平台:情景,私有化低溢价:未建模"]),
    ("terminal_value.py", ["pe", "--roic", "0.12", "--g", "0", "--r", "0.10"]),
    ("terminal_value.py", ["pe", "--roic", "0.12", "--g", "0.02", "--r", "0.10"]),
    ("terminal_value.py", ["irr", "--profit", q2(tp["bear"]), "--mcap", mc_bn, "--pe", "10", "--years", "10", "--payout", "0.06"]),
    ("terminal_value.py", ["irr", "--profit", q2(tp["base"]), "--mcap", mc_bn, "--pe", "10", "--years", "10", "--payout", "0.06"]),
    ("terminal_value.py", ["irr", "--profit", q2(tp["bull"]), "--mcap", mc_bn, "--pe", "10.5", "--years", "10", "--payout", "0.06"]),
    ("terminal_value.py", ["flip", "--name", "汽车之家", "--roic", "0.12", "--g", "0,0,0.02", "--p", "0.30,0.50,0.20", "--irr10=-12.47,-0.42,7.85",
                           "--k", "0.06", "--r", "0.09", "--delta", "0.02", "--currency", "CNY", "--g-shift", "0", "--rf", "0.017"]),
    ("terminal_value.py", ["flip", "--name", "汽车之家", "--roic", "0.12", "--g", "0,0,0.02", "--p", "0.30,0.50,0.20", "--irr10=-12.47,-0.42,7.85",
                           "--k", "0.06", "--r", "0.09", "--delta", "0.01", "--currency", "CNY", "--g-shift", "0", "--rf", "0.017"]),
]
logs = [run(t, a) for t, a in checks]
txt = re.sub(r"\x1b\[[0-9;]*m", "", "\n".join(logs))
irrs = re.findall(r"IRR[^\n]*?(-?\d+\.\d+)\s*%", txt)
P.joinpath("financial-rigor.txt").write_text(txt)
print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
