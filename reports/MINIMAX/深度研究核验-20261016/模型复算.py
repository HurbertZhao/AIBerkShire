#!/usr/bin/env python3
"""MiniMax 2026-10-16 research assumptions; Decimal arithmetic, not a forecast validator.

Run from any directory. Inputs use USD billion unless explicitly specified.
No network access is required. The output separates observed facts from assumptions.
"""
import json
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 40
D = Decimal
HERE = Path(__file__).resolve().parent

facts = {
    "price_hkd_20261015": D("179.50"),
    "shares_20260930": D("352480183"),
    "revenue_2025_musd": D("79.038"),
    "revenue_h12025_musd": D("30.429"),
    "revenue_h12026_musd": D("116.573"),
    "platform_h12026_musd": D("73.929"),
    "native_h12026_musd": D("42.644"),
    "gross_profit_h12026_musd": D("20.813"),
    "rd_h12026_musd": D("296.870"),
    "sales_h12026_musd": D("26.973"),
    "admin_h12026_musd": D("30.230"),
    "loss_h12026_musd": D("-357.997"),
    "adjusted_loss_h12026_musd": D("-293.031"),
    "cfo_h12026_musd": D("-318.106"),
    "ppe_purchase_h12026_musd": D("187.626"),
    "cash_equivalents_h12026_musd": D("930.905"),
    "time_deposits_h12026_musd": D("14.038"),
    "current_fvtpl_h12026_musd": D("278.347"),
    "bank_debt_h12026_musd": D("133.555"),
    "july_placement_net_mhkd": D("9443.71"),
    "july_cb_net_mhkd": D("6433.3"),
    "cb_principal_mhkd": D("6500"),
    "cb_redemption_factor": D("1.0275"),
    "cb_conversion_hkd": D("335"),
}
fx = {"hkd_per_usd_model_only": D("7.8"), "rmb_per_usd_model_only": D("7")}
market_cap_hkd = facts["price_hkd_20261015"] * facts["shares_20260930"]
market_cap_busd = market_cap_hkd / fx["hkd_per_usd_model_only"] / D("1e9")
ttm_musd = facts["revenue_2025_musd"] + facts["revenue_h12026_musd"] - facts["revenue_h12025_musd"]

# Customer counts are average paying account equivalents, net external revenue only.
segments = [
    ("external_api", "100000", "20000", ".40"),
    ("enterprise_agent", "40000", "60000", ".65"),
    ("professional_creation", "8000000", "300", ".60"),
    ("consumer_entertainment", "20000000", "60", ".50"),
]
segment_outputs = []
for name, count, annual_net_arpu, gm in segments:
    revenue = D(count) * D(annual_net_arpu) / D("1e9")
    segment_outputs.append({"segment": name, "paying_accounts": D(count),
                            "annual_net_revenue_usd": D(annual_net_arpu),
                            "revenue_busd": revenue, "gross_margin": D(gm),
                            "gross_profit_busd": revenue * D(gm)})
assert sum(x["revenue_busd"] for x in segment_outputs) == D("8")
assert sum(x["gross_profit_busd"] for x in segment_outputs) == D("4.4")

# Every row is an illustrative full-year path, not company guidance.
# Revenue, gross margin, R&D (including SBC economic cost), SG&A/revenue,
# capital expenditure, D&A, incremental operating working capital.
path_inputs = [
    (2026, ".35", ".25", ".85", ".20", ".35", ".02", ".05"),
    (2027, ".65", ".30", "1.50", ".17", ".30", ".05", ".03"),
    (2028, "1.05", ".36", "1.55", ".16", ".25", ".07", ".04"),
    (2029, "1.50", ".42", "1.50", ".15", ".20", ".09", ".04"),
    (2030, "2.10", ".46", "1.50", ".14", ".20", ".11", ".05"),
    (2031, "2.80", ".49", "1.50", ".13", ".22", ".14", ".06"),
    (2032, "3.60", ".51", "1.55", ".13", ".25", ".18", ".06"),
    (2033, "4.50", ".53", "1.60", ".13", ".28", ".22", ".07"),
    (2034, "5.60", ".54", "1.66", ".13", ".32", ".26", ".08"),
    (2035, "6.80", ".55", "1.70", ".13", ".37", ".30", ".09"),
    (2036, "8.00", ".55", "1.76", ".13", ".40", ".32", ".08"),
]
path = []
for year, revenue, gm, rd, sga, capex, da, dwc in path_inputs:
    revenue, gm, rd, sga, capex, da, dwc = map(D, (revenue, gm, rd, sga, capex, da, dwc))
    ebit = revenue * (gm - sga) - rd
    tax = max(ebit, D("0")) * D(".20")
    normalized_profit = ebit - tax  # no net financial income/debt cost assumed in normalized case
    owner_fcf = normalized_profit + da - capex - dwc
    path.append({"year": year, "revenue_busd": revenue, "gross_margin": gm,
                 "rd_busd": rd, "sga_rate": sga, "ebit_busd": ebit,
                 "normalized_net_profit_busd": normalized_profit,
                 "capex_busd": capex, "da_busd": da, "dwc_busd": dwc,
                 "owner_fcf_busd": owner_fcf})

scenarios = [
    {"name": "exit_or_failure", "probability": D(".25"), "revenue": D("0"), "gm": D("0"), "rd": D("0"), "sales": D("0"), "admin": D("0"), "pe": D("0"), "retained": D("0")},
    {"name": "commoditized_specialist", "probability": D(".25"), "revenue": D("2"), "gm": D(".35"), "rd": D(".18"), "sales": D(".07"), "admin": D(".04"), "pe": D("15"), "retained": D(".60")},
    {"name": "base_professional_platform", "probability": D(".40"), "revenue": D("8"), "gm": D(".55"), "rd": D(".22"), "sales": D(".08"), "admin": D(".05"), "pe": D("25"), "retained": D(".70")},
    {"name": "global_platform", "probability": D(".10"), "revenue": D("20"), "gm": D(".65"), "rd": D(".16"), "sales": D(".07"), "admin": D(".045"), "pe": D("30"), "retained": D(".80")},
]
hurdle = D(".20")
for s in scenarios:
    s["ebit_margin"] = s["gm"] - s["rd"] - s["sales"] - s["admin"]
    s["net_margin"] = s["ebit_margin"] * D(".8")
    s["profit_busd"] = s["revenue"] * s["net_margin"]
    s["profit_rmb_100m"] = s["profit_busd"] * D("70")
    s["terminal_equity_busd"] = s["profit_busd"] * s["pe"]
    s["current_holders_terminal_busd"] = s["terminal_equity_busd"] * s["retained"]
    s["hurdle_present_value_busd"] = s["current_holders_terminal_busd"] / ((1+hurdle) ** 10)
    s["price_equivalent_hkd"] = s["hurdle_present_value_busd"] * D("1e9") * fx["hkd_per_usd_model_only"] / facts["shares_20260930"]
    s["irr_at_reference_market_cap"] = ((s["current_holders_terminal_busd"] / market_cap_busd) ** (D("1")/10) - 1) if s["current_holders_terminal_busd"] else D("-1")
assert sum(s["probability"] for s in scenarios) == 1

base = scenarios[2]
checks = {
    "market_cap_hkd": market_cap_hkd,
    "market_cap_busd_model_fx": market_cap_busd,
    "ttm_revenue_musd": ttm_musd,
    "price_to_ttm_sales": market_cap_busd * 1000 / ttm_musd,
    "h12026_revenue_yoy_pct": (facts["revenue_h12026_musd"] / facts["revenue_h12025_musd"] - 1) * 100,
    "h12026_platform_share_pct": facts["platform_h12026_musd"] / facts["revenue_h12026_musd"] * 100,
    "h12026_gm_pct": facts["gross_profit_h12026_musd"] / facts["revenue_h12026_musd"] * 100,
    "h12026_rd_revenue_multiple": facts["rd_h12026_musd"] / facts["revenue_h12026_musd"],
    "h12026_gross_profit_covers_rd_pct": facts["gross_profit_h12026_musd"] / facts["rd_h12026_musd"] * 100,
    "h12026_simple_fcf_musd": facts["cfo_h12026_musd"] - facts["ppe_purchase_h12026_musd"],
    "h12026_ppe_to_sales_pct": facts["ppe_purchase_h12026_musd"] / facts["revenue_h12026_musd"] * 100,
    "h12026_current_liquid_assets_musd": sum(facts[x] for x in ("cash_equivalents_h12026_musd", "time_deposits_h12026_musd", "current_fvtpl_h12026_musd")),
    "cb_redemption_mhkd": facts["cb_principal_mhkd"] * facts["cb_redemption_factor"],
    "cb_conversion_shares": facts["cb_principal_mhkd"] * D("1e6") / facts["cb_conversion_hkd"],
    "cb_extra_shares_vs_current_pct": facts["cb_principal_mhkd"] * D("1e6") / facts["cb_conversion_hkd"] / facts["shares_20260930"] * 100,
    "rd_h12026_from_vendor_ttm_musd": D("425.31") - D("252.77") + D("124.333"),
    "cfo_h12026_from_vendor_ttm_musd": D("-429.21") - D("-279.64") + D("-168.538"),
    "capex_h12026_from_vendor_ttm_musd": D("188.16") - D(".92") + D(".383"),
    "base_revenue_2026_2036_cagr": (D("8") / D(".35")) ** D(".1") - 1,
    "base_revenue_2025_2036_cagr": (D("8000") / facts["revenue_2025_musd"]) ** (D("1")/11) - 1,
    "base_revenue_2029_2036_cagr": (D("8") / D("1.5")) ** (D("1")/7) - 1,
    "base_revenue_2031_2036_cagr": (D("8") / D("2.8")) ** (D("1")/5) - 1,
    "base_economic_funding_consumption_2027_2032_busd": -sum(p["owner_fcf_busd"] for p in path if 2027 <= p["year"] <= 2032),
    "base_break_even_profit_year": next(p["year"] for p in path if p["normalized_net_profit_busd"] > 0),
    "base_break_even_fcf_year": next(p["year"] for p in path if p["owner_fcf_busd"] > 0),
    "subjective_weighted_profit_busd": sum(s["probability"] * s["profit_busd"] for s in scenarios),
    "subjective_weighted_value_busd": sum(s["probability"] * s["hurdle_present_value_busd"] for s in scenarios),
    "base_profit_required_for_20pct_irr_busd": market_cap_busd * (D("1.2") ** 10) / (D("25") * D(".7")),
    "base_revenue_required_at_16pct_margin_busd": market_cap_busd * (D("1.2") ** 10) / (D("25") * D(".7") * D(".16")),
}
sensitivity = []
for gross in (D(".45"), D(".55"), D(".65")):
    for rd in (D(".18"), D(".22"), D(".30")):
        sensitivity.append({"gm": gross, "rd": rd, "profit_busd": D("8") * (gross-rd-D(".13")) * D(".8")})
valuation_sensitivity = []
for rate in (D(".15"), D(".20"), D(".25")):
    for retained in (D(".5"), D(".7"), D("1")):
        valuation_sensitivity.append({"hurdle": rate, "retained": retained, "base_value_busd": D("32") * retained / ((1+rate)**10)})
out = {"cutoff": "2026-10-16 Asia/Shanghai", "reference_price_date": "2026-10-15", "facts": facts,
       "model_fx_not_spot_quotes": fx, "segments_2036_assumptions": segment_outputs,
       "base_path_assumptions": path, "scenarios_assumptions": scenarios,
       "derived_checks": checks, "profit_sensitivity_assumptions": sensitivity,
       "valuation_sensitivity_assumptions": valuation_sensitivity,
       "boundary": "Arithmetic only. SBC economic cost is not added back: owner_fcf and cumulative consumption are economic proxies, not actual funding requirements. The 70% retained share is a separate financing assumption. No forecast, fair value, probability or moat has been empirically validated."}
(HERE / "计算结果.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str)+"\n", encoding="utf-8")
print(json.dumps(checks, ensure_ascii=False, indent=2, default=str))
