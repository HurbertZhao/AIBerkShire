#!/usr/bin/env python3
"""Report-specific scenarios. All forecasts are assumptions, not company guidance.

Run from any directory. Output amounts are RMB 100 million unless stated.
No external packages; exact Decimal arithmetic from the shared rigor toolkit.
"""
from pathlib import Path
import importlib.util
import json
from decimal import Decimal, getcontext

getcontext().prec = 36
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
spec = importlib.util.spec_from_file_location("financial_rigor", REPO / "tools/financial_rigor.py")
rigor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rigor)
D = rigor.exact

# Each row: ads, livestreaming, commerce/other EXCLUDING Kling, core net margin,
# external Kling revenue, fully burdened Kling net margin, parent economic share,
# incremental after-tax unallocated costs. Training R&D, SBC and depreciation
# remain expenses. Intercompany revenue is eliminated, and AI ad uplift is in core.
RAW = {
    "bear": {
        2029: [750, 260, 200, ".10", 40, "-.20", ".65", 3],
        2031: [700, 220, 190, ".08", 45, "-.10", ".60", 4],
        2036: [650, 150, 200, ".07", 60, "0", ".50", 3],
    },
    "base": {
        2029: [950, 310, 330, ".14", 70, ".08", ".68", 4],
        2031: [1050, 290, 410, ".15", 120, ".12", ".65", 5],
        2036: [1300, 250, 590, ".16", 300, ".20", ".60", 10],
    },
    "bull": {
        2029: [1100, 360, 400, ".17", 120, ".15", ".68", 5],
        2031: [1300, 370, 530, ".19", 280, ".23", ".65", 8],
        2036: [1800, 400, 900, ".20", 1000, ".28", ".60", 15],
    },
}

# Approximation: 2027 is one discount period after the valuation date; 2036 is ten.
# These are parent-attributable OPERATING free cash flows after all capex,
# working capital, unlevered cash tax, lease payments and economic SBC cost,
# but BEFORE bank/supplier financing interest, principal or new financing.
# Operating value is bridged to equity by cash minus financial debt below.
# They include investment losses and are not reported CFO-minus-capex.
CASH = {
    "bear": {"discount": ".15", "terminal_growth": "0", "flows": [20,20,25,30,35,35,38,40,40,40]},
    "base": {"discount": ".12", "terminal_growth": ".02", "flows": [-20,30,90,120,150,180,210,235,255,275]},
    "bull": {"discount": ".11", "terminal_growth": ".03", "flows": [30,80,160,230,310,380,450,510,570,620]},
}


def scenario(row):
    ad, live, other, margin, kr, km, share, central = map(D, row)
    core_revenue = ad + live + other
    core_profit = core_revenue * margin
    kling_profit = kr * km
    attributable = core_profit + kling_profit * share - central
    return dict(ad_revenue=ad, live_revenue=live, other_ex_kling_revenue=other,
                core_revenue=core_revenue, core_margin=margin, core_profit=core_profit,
                kling_external_revenue=kr, kling_net_margin=km, kling_standalone_profit=kling_profit,
                parent_kling_share=share, kling_parent_profit=kling_profit*share,
                unallocated_after_tax_cost=central, attributable_profit=attributable,
                business_revenue_sum_before_control_assessment=core_revenue+kr)


def dcf(flows, discount, growth, excess_cash, shares_yi, fx):
    r, g = D(discount), D(growth)
    assert r > g
    flows = list(map(D, flows))
    explicit = sum(f/(1+r)**(i+1) for i, f in enumerate(flows))
    terminal = flows[-1]*(1+g)/(r-g)/(1+r)**len(flows)
    equity = explicit + terminal + D(excess_cash)
    return dict(explicit_pv=explicit, terminal_pv=terminal, equity_rmb_yi=equity,
                price_hkd=equity/D(shares_yi)/D(fx), terminal_fraction=terminal/(explicit+terminal))


def main():
    market = json.loads((HERE / "模型市场输入.json").read_text())
    market = {k: D(v) if k not in ("price_date", "shares_date", "fx_note", "source_note") else v for k,v in market.items()}
    scenarios = {name: {str(year): scenario(row) for year,row in years.items()} for name,years in RAW.items()}
    valuations = {name: dcf(c["flows"], c["discount"], c["terminal_growth"], market["excess_cash_yi"], market["shares_yi"], market["rmb_per_hkd"]) for name,c in CASH.items()}
    cap_hkd = market["price_hkd"]*market["shares_yi"]
    cap_rmb = cap_hkd*market["rmb_per_hkd"]
    pe = cap_rmb/market["ttm_parent_profit_yi"]
    sensitivity = {str(r): {str(g): dcf(CASH["base"]["flows"],r,g,market["excess_cash_yi"],market["shares_yi"],market["rmb_per_hkd"])["price_hkd"] for g in ("0", ".02", ".03")} for r in (".10", ".12", ".14")}
    # Simple reverse valuation: flat unlevered attributable cash in perpetuity.
    r = D(".12")
    flat_cash_implied = (cap_rmb-market["excess_cash_yi"])*r
    # 2036 indicative terminal PE valuation, excluding future excess cash and
    # distributions. CAGR is explicitly price-only and assumes unchanged shares/FX.
    terminal = {}
    for name, multiple in (("bear",8),("base",12),("bull",18)):
        p = scenarios[name]["2036"]["attributable_profit"]*D(multiple)/market["shares_yi"]/market["rmb_per_hkd"]
        terminal[name] = {"pe":multiple,"price_hkd":p,"price_only_cagr":(p/market["price_hkd"])**D(".1")-1}
    unit_economics = {
        "illustration_only": True,
        "model_A_delivered_cost": D(2)/D(".4")+D(5)*D(2),
        "model_B_delivered_cost": D(1)/D(".15")+D(12)*D(2),
        "contribution_before": D(100)-D(40)-D(20),
        "contribution_after_gpu_half_price_cut_40pct": D(60)-D(20)-D(20),
    }
    kling_bottom_up = {"direct_seats":3000000, "annual_direct_arpu_rmb":3600,
                       "enterprise_equivalent_accounts":128000, "enterprise_annual_arpu_rmb":150000,
                       "direct_revenue_yi":D(3000000)*D(3600)/D(100000000),
                       "enterprise_revenue_yi":D(128000)*D(150000)/D(100000000)}
    private_entry_rmb_yi = D(180)*D("6.7253")
    private_base_terminal = D(60)*D(25)
    private_hurdle_profit = private_entry_rmb_yi*(1+D(".15"))**10/D(25)
    private_return = {"assumptions":"Same-rights ordinary-equity comparison only; no dilution, no distributions, unchanged FX, 25x 2036 P/E. Not a preferred-stock valuation.",
                      "postmoney_usd_yi":D(180),"postmoney_rmb_yi":private_entry_rmb_yi,
                      "base_terminal_value_rmb_yi":private_base_terminal,
                      "base_10y_price_cagr":(private_base_terminal/private_entry_rmb_yi)**D(".1")-1,
                      "profit_needed_for_15pct_cagr":private_hurdle_profit,
                      "revenue_needed_at_20pct_margin":private_hurdle_profit/D(".20")}
    assert kling_bottom_up["direct_revenue_yi"]+kling_bottom_up["enterprise_revenue_yi"] == scenarios["base"]["2036"]["kling_external_revenue"]
    # Explicit coherence checks: no double-counted revenue or minority interests.
    for series in scenarios.values():
        for s in series.values():
            assert s["attributable_profit"] == s["core_profit"]+s["kling_parent_profit"]-s["unallocated_after_tax_cost"]
            assert s["business_revenue_sum_before_control_assessment"] == s["core_revenue"]+s["kling_external_revenue"]
    cash_bridge = {
        "description":"Illustrative attributable profit to operating cash bridge, rounded inputs; lease cash netted in noncash_addback. Training R&D and SBC remain expensed.",
        "2029":{"net_profit":scenarios["base"]["2029"]["attributable_profit"],"after_tax_finance_addback":D(15),"noncash_addback_net_leases":D(90),"capex":D(200),"working_capital_other_retention":D(37)},
        "2031":{"net_profit":scenarios["base"]["2031"]["attributable_profit"],"after_tax_finance_addback":D(15),"noncash_addback_net_leases":D(105),"capex":D(195),"working_capital_other_retention":D(42)},
        "2036":{"net_profit":scenarios["base"]["2036"]["attributable_profit"],"after_tax_finance_addback":D(15),"noncash_addback_net_leases":D(120),"capex":D(190),"working_capital_other_retention":D(38)},
    }
    for year in ("2029","2031","2036"):
        b=cash_bridge[year]
        b["operating_cash"] = b["net_profit"]+b["after_tax_finance_addback"]+b["noncash_addback_net_leases"]-b["capex"]-b["working_capital_other_retention"]
        assert abs(b["operating_cash"]-D(CASH["base"]["flows"][int(year)-2027])) < D(".5")
    output = dict(disclaimer="All future numbers are conditional assumptions; arithmetic verification is not forecast validation.",
                  units="RMB 100 million unless otherwise labeled", market=market,
                  market_cap_hkd_yi=cap_hkd,market_cap_rmb_yi=cap_rmb,ttm_pe=pe,
                  profit_scenarios=scenarios,dcf_cash_assumptions=CASH,valuations=valuations,
                  sensitivity=sensitivity,second_half_2026_net_cash_change_assumed_yi="0 excluding dividend already deducted; unmodeled funding/operating/investing/buyback changes",
                  price_effect_per_100_yi_net_cash=D(100)/market["shares_yi"]/market["rmb_per_hkd"],
                  reverse_dcf_flat_perpetual_cash_yi=flat_cash_implied,
                  terminal_pe_comparison=terminal,unit_economics=unit_economics,kling_bottom_up=kling_bottom_up,profit_to_cash_bridge=cash_bridge,private_round_hurdle=private_return,
                  core_2036_margin_1pp_profit_effect_yi=scenarios["base"]["2036"]["core_revenue"]*D(".01"),
                  kling_2036_share_10pp_profit_effect_yi=D(60)*D(".10"))
    (HERE / "利润与估值模型.json").write_text(json.dumps(output,ensure_ascii=False,indent=2,default=str)+"\n")
    print(json.dumps({"profits":{k:{y:str(v["attributable_profit"]) for y,v in s.items()} for k,s in scenarios.items()},"values":valuations},ensure_ascii=False,indent=2,default=str))


if __name__ == "__main__":
    main()
