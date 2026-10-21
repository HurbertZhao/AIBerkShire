"""Reproduce illustrative models; assumptions are NOT observed industry averages.

Run from any directory. Decimal is authoritative; repository CLI outputs are
retained as an additional arithmetic check, not as external verification.
"""
from decimal import Decimal, getcontext
from pathlib import Path
import json
import subprocess
import sys

getcontext().prec = 40
D = Decimal
BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
OUT = BASE / "audit"
OUT.mkdir(exist_ok=True)

def fmt(value):
    return str(value.quantize(D("0.000001")))

costs = []
for name, gross, ads, production in [
    ("original", "100", "55", "15"),
    ("ai_static", "100", "55", "4.5"),
    ("ai_competition", "90", "60", "4.5"),
]:
    revenue, acquisition, prod = map(D, (gross, ads, production))
    channel = revenue * D("0.15")
    profit = revenue - channel - acquisition - prod - D("10")
    costs.append(dict(name=name, gross=fmt(revenue), channel=fmt(channel),
                      acquisition=fmt(acquisition), production=fmt(prod),
                      other="10", pretax_profit=fmt(profit)))

scenarios = []
for name, reach, hours, monetization, ai_output, ai_view in [
    ("bear", "1.25", "1.20", "0.90", "0.50", "0.20"),
    ("base", "1.60", "1.35", "1.00", "0.75", "0.45"),
    ("bull", "2.00", "1.60", "1.10", "0.90", "0.70"),
]:
    mult = D(reach) * D(hours) * D(monetization)
    cagr = mult ** (D(1) / D(10)) - D(1)
    scenarios.append(dict(name=name, reach_factor=reach, hours_factor=hours,
        revenue_per_hour_factor=monetization, revenue_factor=fmt(mult),
        cagr=fmt(cagr), year2036_usd_bn=fmt(D("14") * mult),
        ai_output_share=ai_output, ai_watch_time_share=ai_view))

result = {
    "cutoff": "2026-10-19 Asia/Shanghai",
    "model_status": "Illustrative assumptions, not predictions or observations",
    "unit_economics_per_original_100_cash_spend": costs,
    "production_cost_decline_pct": fmt((D(15)-D("4.5"))/D(15)*100),
    "total_cost_decline_pct": fmt((D(95)-D("84.5"))/D(95)*100),
    "iaa_monthly_revenue_rmb": fmt(D(6)*30*D("0.8")*20/1000),
    "iaa_monthly_revenue_rmb_low_ecpm": fmt(D(6)*30*D("0.8")*10/1000),
    "generation_rmb_per_finished_minute_p25": fmt(60*D(1)/D("0.25")),
    "generation_rmb_per_finished_minute_p10": fmt(60*D(1)/D("0.10")),
    "global_scenarios": scenarios,
    "scenario_anchor_note": "USD14bn is Omdia's 2026 forecast, not actual full-year revenue. Scenarios do not validate the anchor.",
    "incremental_value_thresholds_rmb_100m": [
        {"valuation_premium": str(v), "required_annual_owner_fcf_at_20x": fmt(D(v)/20),
         "required_revenue_at_15pct_cash_margin": fmt(D(v)/20/D("0.15"))}
        for v in (10, 30, 100)
    ],
    "employment_output_5x_labor_down80pct": fmt(D(5)*D("0.2")),
    "employment_output_2x_labor_down80pct": fmt(D(2)*D("0.2")),
    "derived_company_metrics_pct": {
        "ireader_2026h1_gross_margin": fmt((D("1783793670.53")-D("613002054.27"))/D("1783793670.53")*100),
        "ireader_2026h1_selling_ratio": fmt(D("1108896945.96")/D("1783793670.53")*100),
        "ireader_2026h1_gross_less_selling_ratio": fmt((D("1783793670.53")-D("613002054.27")-D("1108896945.96"))/D("1783793670.53")*100),
        "ireader_2026h1_derivatives_ratio_rounded_inputs": fmt(D("11.8510")/D("17.8379")*100),
    },
}
(OUT / "model-results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")

expressions = [
    "100-100*0.15-55-15-10", "100-100*0.15-55-4.5-10",
    "90-90*0.15-60-4.5-10", "(95-84.5)/95*100",
    "6*30*0.8*20/1000", "60/0.25", "60/0.1",
    "14*1.25*1.2*0.9", "14*1.6*1.35", "14*2*1.6*1.1",
    "(1.35**(1/10)-1)*100", "(2.16**(1/10)-1)*100",
    "(3.52**(1/10)-1)*100", "100/20/0.15",
    "(1783793670.53-613002054.27)/1783793670.53*100",
    "1108896945.96/1783793670.53*100",
    "(1783793670.53-613002054.27-1108896945.96)/1783793670.53*100",
    "11.8510/17.8379*100",
]
logs = ["Decimal model-results.json is authoritative. CLI calc uses its existing implementation.\n"]
for expression in expressions:
    completed = subprocess.run([sys.executable, str(REPO/"tools/financial_rigor.py"),
        "calc", "--expr", expression], check=True, capture_output=True, text=True)
    logs.append(completed.stdout)
(OUT / "financial-rigor.txt").write_text("\n".join(logs))
print(json.dumps(result, ensure_ascii=False, indent=2))
