"""Reproduce conditional examples; these are not forecasts or company valuations."""
from decimal import Decimal, getcontext
from pathlib import Path
import json
import subprocess
import sys

getcontext().prec = 40
D = Decimal
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def text(value):
    return format(value, "f")


cost_rows = []
for share in ("0.1", "0.5", "0.9", "0.99", "0.999"):
    s = D(share)
    ratio = 1 - s + s / 1000
    cost_rows.append({"ai_cost_share_pct": text(s * 100),
                      "new_total_cost_pct": text(ratio * 100),
                      "cost_reduction_pct": text((1 - ratio) * 100),
                      "purchasing_power_multiple": text(1 / ratio)})

demand_rows = []
for elasticity in ("0.5", "1", "1.5"):
    e = D(elasticity)
    q = D(1000) ** e
    demand_rows.append({"elasticity": elasticity, "quantity_multiple": text(q),
                        "revenue_multiple": text(q / 1000)})

reliability = [{"per_step_success_pct": text(D(p) * 100),
                "all_100_steps_success_pct": text(D(p) ** 100 * 100)}
               for p in ("0.99", "0.999", "0.9999")]
pv5 = sum(D(10) / D("1.1") ** t for t in range(1, 6))
pv10 = sum(D(10) / D("1.1") ** t for t in range(1, 11))

result = {
    "scope": "Conditional arithmetic only. Inputs are user premise or illustrative assumptions.",
    "precision": "Python Decimal, 40 significant digits; powers may be rounded at that precision.",
    "ten_year_price_ratio": "0.001",
    "annual_price_decline_pct": text((1 - D("0.001") ** D("0.1")) * 100),
    "annual_efficiency_multiple": text(D(1000) ** D("0.1")),
    "total_cost": cost_rows,
    "demand": demand_rows,
    "energy_example": {"tasks_multiple": "1000", "energy_per_task_reduction_factor": "100", "total_energy_multiple": "10"},
    "serial_reliability": reliability,
    "independent_retry_example": {"success_per_attempt": "0.9", "attempts": 5,
                                  "at_least_one_success_pct": text((1 - D("0.1") ** 5) * 100),
                                  "limitation": "Requires independent errors and a reliable verifier to select the correct result."},
    "scarcity_rent_pv": {"year_end_annual_extra_cashflow": "10", "discount_rate_pct": "10",
                         "terminal_rent": "0", "five_years": text(pv5), "ten_years": text(pv10),
                         "value_loss_if_five_years_instead_of_ten_pct": text((1 - pv5 / pv10) * 100)}
}
(HERE / "calculations.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")

# Repository-required calculator is a second arithmetic check. Its current CLI
# evaluates native Python numeric expressions before converting to Decimal;
# Decimal above is the primary reproducible precision calculation.
expressions = ["(1-(1/1000)**(1/10))*100", "(1-0.9+0.9/1000)*100",
               "1000**0.5", "1000**1.5/1000", "0.99**100*100",
               "0.999**100*100", "0.9999**100*100", "(1-0.1**5)*100",
               "10*(1-(1.1)**(-5))/0.1", "10*(1-(1.1)**(-10))/0.1",
               "1000/100"]
logs = []
for expr in expressions:
    run = subprocess.run([sys.executable, str(ROOT / "tools/financial_rigor.py"),
                          "calc", "--expr", expr], check=True, capture_output=True, text=True)
    logs.append(run.stdout)
(HERE / "financial-rigor.txt").write_text("\n".join(logs))
print(json.dumps(result, ensure_ascii=False, indent=2))
