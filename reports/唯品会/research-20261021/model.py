"""唯品会（VIPS）估值模型：Decimal 精确计算。
运行：python3 reports/唯品会/research-20261021/model.py
单位：除特别注明外，人民币百万元；每 ADS = 0.2 股 A 类普通股。
输出 inputs.json / results.json / financial-rigor.txt（调用 tools/financial_rigor.py 与 tools/terminal_value.py）。
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json, subprocess, re

getcontext().prec = 38
P = Path(__file__).resolve().parent
ROOT = P.parents[2]

inputs = {
    "price_usd_per_ads": "12.80", "price_date": "2026-10-19 (NYSE close; Nasdaq & StockAnalysis)",
    "usd_cny": "6.6807", "fx_date": "2026-10-19 ECB reference via frankfurter.dev; Fed H.10 2026-10-16 = 6.6861",
    "ordinary_shares_outstanding_m": "95.1", "shares_date": "2026-06-30 (Q2 2026 balance sheet note, rounded to 0.1m)",
    "ordinary_shares_20f_m": "96.054108", "shares_20f_date": "2026-03-31 (20-F Item 6.E)",
    "diluted_weighted_ordinary_q2_m": "97.619760", "ads_per_ordinary": "5",
    "fy": {  # SEC XBRL (20-F) 原值，百万元
        "revenue": {"2021": "117059.7", "2022": "103152.5", "2023": "112856.0", "2024": "108420.8", "2025": "105919.5"},
        "gross_profit": {"2021": "23106.6", "2022": "21616.1", "2023": "25720.9", "2024": "25469.7", "2025": "24490.3"},
        "op_income": {"2021": "5582.4", "2022": "6197.4", "2023": "9104.1", "2024": "9173.3", "2025": "8135.9"},
        "ni_attr": {"2021": "4681.1", "2022": "6298.8", "2023": "8116.6", "2024": "7739.9", "2025": "7242.5"},
        "cfo": {"2021": "6744.6", "2022": "10519.7", "2023": "14414.5", "2024": "9129.0", "2025": "7454.2"},
        "capex_ppe": {"2021": "2732.4", "2022": "2430.8", "2023": "2167.2", "2024": "2723.2", "2025": "1985.8"},
        "buyback": {"2021": "1938.8", "2022": "6257.7", "2023": "5106.9", "2024": "3865.8", "2025": "4940.8"},
        "sbc": {"2021": "1010.0", "2022": "1207.6", "2023": "1509.8", "2024": "1537.7", "2025": "1731.1"},
    },
    "quarters": {  # 季度新闻稿 6-K，千元转百万元
        "Q3_2025": {"rev": "21370.865", "gp": "4908.911", "op": "1262.400", "ni": "1220.677", "nongaap": "1501.489", "sbc": "346.352"},
        "Q4_2025": {"rev": "32473.779", "gp": "7444.199", "op": "2898.846", "ni": "2589.219", "nongaap": "2858.031", "sbc": "336.254"},
        "Q1_2026": {"rev": "26574.509", "gp": "6495.150", "op": "2497.769", "ni": "2206.308", "nongaap": "2305.623", "sbc": "220.645"},
        "Q2_2026": {"rev": "24707.149", "gp": "5754.692", "op": "1519.657", "ni": "4306.193", "nongaap": "392.213", "sbc": "486.514"},
    },
    "one_offs_q2_2026": {"reit_gain_pre_tax": "5790", "reit_gain_tax": "1630", "withholding_tax_accrual": "1560"},
    "ttm_company_fcf_jun26": "7201.751", "ttm_cfo_jun26": "8766.247", "ttm_capex_jun26": "1512.848",
    "fy2025_interest_income": "801.587", "fy2025_interest_expense": "90.037", "tax_rate_on_interest": "0.25",
    "bridge_jun26": {"cash": "29246.429", "restricted_cash": "604.940", "short_term_investments": "3618.481",
                      "short_term_loans": "10968.130", "accounts_payable": "10350.342", "inventories": "4327.466",
                      "equity_method_investees": "7616.184", "other_investments": "4980.862", "htm_securities": "806.443"},
    "assumption_unpaid_tax": "3190 = REIT tax 1630 + withholding 1560, assumed unpaid at 2026-06-30 (conservative; not verified)",
    "scenarios_3y": {
        "bear": {"core_ni_growth": "-0.08", "pe_ex_cash": "5", "bridge": "conservative"},
        "base": {"core_ni_growth": "0", "pe_ex_cash": "7", "bridge": "base"},
        "bull": {"core_ni_growth": "0.04", "pe_ex_cash": "9", "bridge": "bull"},
    },
    "dcf": {"r_base": "0.08", "r_sensitivity": ["0.08", "0.10", "0.12"],
             "owner_fcf_2027_bn": {"bear": "3.5", "base": "4.5", "bull": "5.5"},
             "growth_2027_2036": {"bear": "-0.08", "base": "0", "bull": "0.03"},
             "terminal_g": {"bear": "0", "base": "0.01", "bull": "0.02"},
             "tail": {"probability": "0.10", "value": "50% of conservative cash bridge only"},
             "probabilities": {"bear": "0.30", "base": "0.50", "bull": "0.20"},
             "definition": "Owner FCF = company-defined FCF (CFO + internet-finance adj - capex incl. land use rights) minus SBC minus after-tax net interest income, CNY bn; cash bridge added separately so interest is not double counted. Calibration: FY2024 ~3.5, FY2025 ~3.1, TTM Jun-26 ~5.3"},
    "ten_year": {"roic": "0.15", "profit_2036_m": {"bear": "3500", "base": "6700", "bull": "9000"},
                  "k": "0.03", "k_note": "dividend yield 4.84% minus estimated gross SBC dilution ~1.8%; buybacks excluded (conservative)"},
}

price = D(inputs["price_usd_per_ads"]); fx = D(inputs["usd_cny"])
ads_basic = D(inputs["ordinary_shares_outstanding_m"]) * 5
ads_dil = D(inputs["diluted_weighted_ordinary_q2_m"]) * 5
out = {}
out["ads_basic_m"] = ads_basic; out["ads_diluted_m"] = ads_dil
out["mcap_usd_m"] = price * ads_basic
out["mcap_cny_m"] = out["mcap_usd_m"] * fx
out["mcap_usd_m_20f_shares"] = price * D(inputs["ordinary_shares_20f_m"]) * 5

fy = {k: {y: D(v) for y, v in s.items()} for k, s in inputs["fy"].items()}
hist = {}
for y in ["2021", "2022", "2023", "2024", "2025"]:
    hist[y] = {"gross_margin_pct": fy["gross_profit"][y] / fy["revenue"][y] * 100,
               "op_margin_pct": fy["op_income"][y] / fy["revenue"][y] * 100,
               "net_margin_pct": fy["ni_attr"][y] / fy["revenue"][y] * 100,
               "simple_fcf": fy["cfo"][y] - fy["capex_ppe"][y],
               "simple_fcf_minus_sbc": fy["cfo"][y] - fy["capex_ppe"][y] - fy["sbc"][y],
               "buyback_over_ni_pct": fy["buyback"][y] / fy["ni_attr"][y] * 100}
out["history"] = hist
out["revenue_cagr_2021_2025_pct"] = ((fy["revenue"]["2025"] / fy["revenue"]["2021"]) ** (D(1) / 4) - 1) * 100

q = {k: {kk: D(vv) for kk, vv in v.items()} for k, v in inputs["quarters"].items()}
ttm = {f: sum(q[k][f] for k in q) for f in ["rev", "gp", "op", "ni", "nongaap", "sbc"]}
oo = {k: D(v) for k, v in inputs["one_offs_q2_2026"].items()}
ttm["ni_ex_oneoffs"] = ttm["ni"] - (oo["reit_gain_pre_tax"] - oo["reit_gain_tax"]) + oo["withholding_tax_accrual"]
ttm["nongaap_ex_wht"] = ttm["nongaap"] + oo["withholding_tax_accrual"]
ttm["gross_margin_pct"] = ttm["gp"] / ttm["rev"] * 100
ttm["op_margin_pct"] = ttm["op"] / ttm["rev"] * 100
for k in q:
    q[k]["gm_pct"] = q[k]["gp"] / q[k]["rev"] * 100
    q[k]["om_pct"] = q[k]["op"] / q[k]["rev"] * 100
out["quarters"] = q; out["ttm"] = ttm
out["q2_2026_nongaap_ex_wht"] = q["Q2_2026"]["nongaap"] + oo["withholding_tax_accrual"]

# 估值倍数
mc = out["mcap_cny_m"]
out["pe_fy2025_gaap"] = mc / fy["ni_attr"]["2025"]
out["pe_ttm_gaap"] = mc / ttm["ni"]
out["pe_ttm_ex_oneoffs"] = mc / ttm["ni_ex_oneoffs"]
out["ps_ttm"] = mc / ttm["rev"]
out["fcf_yield_ttm_pct"] = D(inputs["ttm_company_fcf_jun26"]) / mc * 100
out["eps_fy2025_cny_per_current_diluted_ads"] = fy["ni_attr"]["2025"] / ads_dil
out["eps_fy2025_usd_per_current_diluted_ads"] = out["eps_fy2025_cny_per_current_diluted_ads"] / fx
out["bvps_usd_jun26"] = D("44987.634") / ads_basic / fx
out["dividend_yield_pct"] = D("0.62") / price * 100
out["shareholder_return_2025_over_mcap_pct"] = D("944.1") / out["mcap_usd_m"] * 100

# 现金桥
b = {k: D(v) for k, v in inputs["bridge_jun26"].items()}
gross_cash = b["cash"] + b["restricted_cash"] + b["short_term_investments"]
net_cash = gross_cash - b["short_term_loans"]
unpaid_tax = oo["reit_gain_tax"] + oo["withholding_tax_accrual"]
supplier_float = b["accounts_payable"] - b["inventories"]
lt_inv = b["equity_method_investees"] + b["other_investments"] + b["htm_securities"]
bridges = {"accounting_net_cash": net_cash,
           "base": net_cash - unpaid_tax,
           "conservative": net_cash - unpaid_tax - supplier_float,
           "bull": net_cash + lt_inv * D("0.5")}
out["cash_bridge"] = {"gross_cash": gross_cash, "net_cash": net_cash, "unpaid_tax_assumed": unpaid_tax,
                      "supplier_float_net_of_inventory": supplier_float, "long_term_investments_book": lt_inv, **bridges}
out["net_cash_per_ads_usd"] = net_cash / ads_dil / fx
out["ev_cny_m_base"] = mc - bridges["base"]

# 核心利润（剔除税后净利息）
after_tax_interest = (D(inputs["fy2025_interest_income"]) - D(inputs["fy2025_interest_expense"])) * (1 - D(inputs["tax_rate_on_interest"]))
core_ni = fy["ni_attr"]["2025"] - after_tax_interest
out["after_tax_net_interest_2025"] = after_tax_interest
out["core_ni_2025_ex_interest"] = core_ni
out["ev_over_core_ni"] = out["ev_cny_m_base"] / core_ni

# 三年三情景（分部加总：核心利润×PE + 现金桥）
sc3 = {}
for name, s in inputs["scenarios_3y"].items():
    ni3 = core_ni * (1 + D(s["core_ni_growth"])) ** 3
    eq = ni3 * D(s["pe_ex_cash"]) + bridges[s["bridge"]]
    v = eq / ads_dil / fx
    sc3[name] = {"core_ni_2028": ni3, "equity_cny_m": eq, "value_usd_per_ads": v, "vs_price_pct": (v / price - 1) * 100}
out["three_year_sotp"] = sc3

# 反向估值：当前 EV 隐含的永续增速
owner_fcf_now = (D(inputs["ttm_company_fcf_jun26"]) - ttm["sbc"] - after_tax_interest)
out["owner_fcf_ttm_ex_interest"] = owner_fcf_now
rev = {}
for r in ["0.08", "0.10", "0.12"]:
    rr = D(r)
    rev[r] = {"implied_g_pct_using_owner_fcf_ttm": (rr - owner_fcf_now * (1 + D(0)) / out["ev_cny_m_base"]) * 100,
              "implied_g_pct_using_core_ni_2025": (rr - core_ni / out["ev_cny_m_base"]) * 100}
out["reverse_dcf"] = rev

# 十年现金流折现
def dcf(name, r):
    d = inputs["dcf"]; f0 = D(d["owner_fcf_2027_bn"][name]) * 1000; gr = D(d["growth_2027_2036"][name]); g = D(d["terminal_g"][name])
    flows = [f0 * (1 + gr) ** i for i in range(10)]
    pv = sum(f / (1 + r) ** (i + 1) for i, f in enumerate(flows))
    tv = flows[-1] * (1 + g) / (r - g) / (1 + r) ** 10
    eq = pv + tv + bridges["base" if name != "bear" else "conservative"]
    return {"pv_flows": pv, "pv_terminal": tv, "equity": eq, "value_usd_per_ads": eq / ads_dil / fx,
            "terminal_share_pct": tv / (pv + tv) * 100, "fcf_2036": flows[-1]}
out["dcf"] = {}
for r in inputs["dcf"]["r_sensitivity"]:
    rr = D(r); res = {n: dcf(n, rr) for n in ["bear", "base", "bull"]}
    tail = bridges["conservative"] * D("0.5") / ads_dil / fx
    pr = {k: D(v) for k, v in inputs["dcf"]["probabilities"].items()}; pt = D(inputs["dcf"]["tail"]["probability"])
    weighted = (1 - pt) * sum(pr[n] * res[n]["value_usd_per_ads"] for n in res) + pt * tail
    out["dcf"][r] = {**res, "tail_value_usd_per_ads": tail, "probability_weighted_usd_per_ads": weighted}

# 行动区间（以 r=10% 概率加权值为锚）
anchor = out["dcf"]["0.10"]["probability_weighted_usd_per_ads"]
out["action"] = {"anchor_r10_weighted": anchor, "buy_below_70pct": anchor * D("0.7"), "fair_low_90pct": anchor * D("0.9"),
                  "trim_above_120pct": anchor * D("1.2")}

# 十年 IRR 输入（terminal_value.py）
tv_in = inputs["ten_year"]
out["ten_year_pe"] = {}
for r in ["0.08", "0.10"]:
    out["ten_year_pe"][r] = {n: (1 - D(inputs["dcf"]["terminal_g"][n]) / D(tv_in["roic"])) / (D(r) - D(inputs["dcf"]["terminal_g"][n])) for n in ["bear", "base", "bull"]}

P.joinpath("inputs.json").write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + "\n")

def q2(x):
    if isinstance(x, D): return str(x.quantize(D("0.0001")))
    if isinstance(x, dict): return {k: q2(v) for k, v in x.items()}
    if isinstance(x, list): return [q2(v) for v in x]
    return x
P.joinpath("results.json").write_text(json.dumps(q2(out), ensure_ascii=False, indent=2) + "\n")

# ---- 工具核验 ----
def tool(script, args):
    z = subprocess.run(["python3", str(ROOT / "tools" / script), *args], capture_output=True, text=True)
    return "COMMAND: " + script + " " + " ".join(args) + "\n" + z.stdout + z.stderr + f"[exit {z.returncode}]\n"

eps_usd = out["eps_fy2025_usd_per_current_diluted_ads"].quantize(D("0.0001"))
irr10 = {}
logs = [
    tool("financial_rigor.py", ["verify-market-cap", "--price", "12.80", "--shares", str(ads_basic * 10**6), "--reported", str((price * ads_basic * 10**6).quantize(D(1))), "--currency", "USD"]),
    tool("financial_rigor.py", ["verify-market-cap", "--price", "12.80", "--shares", "480270540", "--reported", "6133054796", "--currency", "USD"]),
    tool("financial_rigor.py", ["cross-validate", "--field", "ADS outstanding (m)", "--values", json.dumps({"Q2 2026 balance sheet 95.1m x5": float(ads_basic), "20-F 2026-03-31 96.054108m x5 (Nasdaq implied)": 480.27054}), "--unit", "m ADS"]),
    tool("financial_rigor.py", ["cross-validate", "--field", "2026-10-19 close", "--values", '{"Nasdaq": 12.80, "StockAnalysis": 12.80}', "--unit", "USD"]),
    tool("financial_rigor.py", ["cross-validate", "--field", "USD/CNY", "--values", '{"ECB ref 10-19": 6.6807, "Fed H.10 10-16": 6.6861}', "--unit", "CNY"]),
    tool("financial_rigor.py", ["cross-validate", "--field", "FY2025 revenue", "--values", '{"20-F/XBRL": 105919.5, "StockAnalysis": 105920}', "--unit", "CNY m"]),
    tool("financial_rigor.py", ["cross-validate", "--field", "FY2025 net income attributable", "--values", '{"20-F/XBRL": 7242.5, "StockAnalysis": 7242}', "--unit", "CNY m"]),
    tool("financial_rigor.py", ["cross-validate", "--field", "TTM revenue Jun-26", "--values", json.dumps({"6-K sum": float(ttm["rev"]), "StockAnalysis TTM": 105126}), "--unit", "CNY m"]),
    tool("financial_rigor.py", ["cross-validate", "--field", "TTM GAAP NI Jun-26", "--values", json.dumps({"6-K sum": float(ttm["ni"]), "StockAnalysis TTM": 10322}), "--unit", "CNY m"]),
    tool("financial_rigor.py", ["cross-validate", "--field", "Cash+ST inv Jun-26 (ex restricted)", "--values", json.dumps({"6-K": float(b["cash"] + b["short_term_investments"]), "StockAnalysis": 32865}), "--unit", "CNY m"]),
    tool("financial_rigor.py", ["cross-validate", "--field", "FY2025 CFO", "--values", '{"20-F/XBRL": 7454.2, "StockAnalysis": 7454}', "--unit", "CNY m"]),
    tool("financial_rigor.py", ["verify-valuation", "--price", "12.80", "--eps", str(eps_usd), "--bvps", str(out["bvps_usd_jun26"].quantize(D("0.0001"))), "--fcf-per-share", str((D(inputs["ttm_company_fcf_jun26"]) / ads_dil / fx).quantize(D("0.0001"))), "--dividend", "0.62"]),
    tool("financial_rigor.py", ["three-scenario", "--price", "12.80", "--eps", str(eps_usd), "--shares", str((ads_dil / 100).quantize(D("0.0001"))), "--growth", "0.04", "0", "-0.08", "--pe", "9", "7", "5", "--years", "3", "--currency", "USD"]),
    tool("terminal_value.py", ["audit", "--currency", "CNY", "--r", "0.08", "--roic", tv_in["roic"], "--g", "0,0.01,0.02", "--beta", "1.0",
                               "--discrete-risks", "ADR退市:尾部档,VIE结构失效:尾部档,股息预提税与资金出境:情景,控股股东投票权滥用:情景,平台竞争份额流失:情景,美国对华投资限制:未建模"]),
]
for n in ["bear", "base", "bull"]:
    logs.append(tool("terminal_value.py", ["pe", "--roic", tv_in["roic"], "--g", inputs["dcf"]["terminal_g"][n], "--r", "0.08"]))
for r in ["0.08", "0.10"]:
    irr10[r] = {}
    for n in ["bear", "base", "bull"]:
        pe = out["ten_year_pe"][r][n].quantize(D("0.0001"))
        s = tool("terminal_value.py", ["irr", "--profit", tv_in["profit_2036_m"][n], "--mcap", str(mc.quantize(D("0.01"))), "--pe", str(pe), "--years", "10", "--payout", tv_in["k"]])
        logs.append(s)
        m = re.findall(r"IRR[^\n]*?(-?\d+\.\d+)%", s)
        irr10[r][n] = m[-1] if m else None
logs.append(tool("terminal_value.py", ["flip", "--name", "唯品会", "--roic", tv_in["roic"], "--g", "0,0.01,0.02", "--p", "0.30,0.50,0.20",
                                        "--irr10=" + ",".join(str(irr10["0.10"][n]) for n in ["bear", "base", "bull"]), "--k", tv_in["k"],
                                        "--r", "0.08", "--delta", "0.02", "--currency", "CNY"]))
logs.append(tool("terminal_value.py", ["flip", "--name", "唯品会", "--roic", tv_in["roic"], "--g", "0,0.01,0.02", "--p", "0.30,0.50,0.20",
                                        "--irr10=" + ",".join(str(irr10["0.10"][n]) for n in ["bear", "base", "bull"]), "--k", tv_in["k"],
                                        "--r", "0.08", "--delta", "0.01", "--currency", "CNY"]))
out["irr10_parsed"] = irr10
P.joinpath("results.json").write_text(json.dumps(q2(out), ensure_ascii=False, indent=2) + "\n")
P.joinpath("financial-rigor.txt").write_text(re.sub(r"\x1b\[[0-9;]*m", "", "\n".join(logs)))
print(json.dumps(q2(out), ensure_ascii=False, indent=2))
