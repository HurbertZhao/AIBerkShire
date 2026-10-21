"""理想汽车（LI / 2015.HK）研究模型，2026-10-21。
全部用 Decimal 计算；金额单位除注明外为人民币亿元。
运行：python3 reports/理想汽车/research-20261021/model.py
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json

getcontext().prec = 40
P = Path(__file__).resolve().parent
YI = D(10) ** 8  # 1亿

inputs = {
    "price_hkd": "45.64", "price_hkd_date": "2026-10-20 港股收盘（10-19 重阳节翌日休市）",
    "ads_usd": "11.29", "ads_usd_date": "2026-10-19 纳斯达克收盘（10-20 美股盘中，未收盘不用）",
    "ads_ratio": "2",
    "class_a_ex_treasury": "1716030157", "class_b": "345199159", "treasury_a": "102294952",
    "share_date": "2026-09-30 港交所 FF301 月报表",
    "ceo_award_shares": "108557400",
    "hkd_cny": "0.8526", "usd_cny": "6.6909", "fx_date": "2026-10-16 收盘参考价（Yahoo），不是可成交报价",
    "bs_date": "2026-06-30",
    "cash_k": "40117782", "restricted_k": "14782", "td_sti_k": "45474274",
    "st_borrow_k": "286205", "lt_borrow_k": "6863999",
    "payables_k": "38756080", "inventory_k": "8333701", "receivable_k": "206592",
    "equity_attr_k": "65428704",
    "buyback_post_june_usd": "169729422.44", "buyback_post_june_hkd": "493287499.62",
    "q": {  # 人民币百万元：Q3'25, Q4'25, Q1'26, Q2'26
        "revenue": ["27364.7", "28775.4", "22982.9", "25666.9"],
        "ni_attr": ["-624.976", "6.519", "-2289.531", "-1704.181"],
        "cfo": ["-7395.6", "3521.4", "-6091.0", "15.0"],
        "capex": ["1516.607", "1053.769", "1297.326", "1315.790"],
        "interest_inv_income": ["475.435", "430.733", "394.020", "455.033"],
    },
    "fy": {  # 人民币百万元
        "revenue": {"2021": "27009.779", "2022": "45286.816", "2023": "123851.332", "2024": "144459.946", "2025": "112312.511"},
        "gross_profit": {"2021": "5761.454", "2022": "8790.456", "2023": "27496.751", "2024": "29656.138", "2025": "20985.058"},
        "op_income": {"2021": "-1017.320", "2022": "-3654.877", "2023": "7406.877", "2024": "7019.114", "2025": "-521.117"},
        "ni_attr": {"2021": "-321.455", "2022": "-2012.215", "2023": "11704.133", "2024": "8032.350", "2025": "1124.438"},
        "cfo": {"2021": "8340.385", "2022": "7380.266", "2023": "50693.521", "2024": "15933.160", "2025": "-8611.397"},
        "capex": {"2021": "3444.573", "2022": "5127.899", "2023": "6507.190", "2024": "7730.022", "2025": "4205.517"},
        "rnd": {"2025": "11314.949"},
    },
    "deliveries_q3_2026": ["30468", "37679", "31817"],
    "operating_buffer_bn": "200",
    "three_year": {
        "definition": "截至2028年末。经营价值=2028年经营税后利润（不含利息收入）×PE；悲观档经营亏损，改用EV/收入残值。净现金=2026-06净金融现金-7至9月回购+2026H2至2028累计自由现金流（含利息收入）-经营缓冲200亿。",
        "discount_r": "0.10", "years_to_end_2028": "2.2",
        "bear": {"p": "0.35", "revenue": "950", "nopat": "-40", "ev_sales": "0.10", "cum_fcf": "-250"},
        "base": {"p": "0.45", "revenue": "1200", "nopat": "30", "pe": "15", "cum_fcf": "-40"},
        "bull": {"p": "0.20", "revenue": "1500", "nopat": "95", "pe": "15", "cum_fcf": "150"},
    },
    "ten_year": {
        "definition": "2036年末股东价值=2036经营税后利润（不含利息）×永续增长PE+2036年净现金（不扣回购，含累计利息）；对比今日人民币市值。",
        "roic": "0.12", "r_base": "0.08", "r_grid": ["0.06", "0.07", "0.08", "0.09", "0.10"],
        "bear": {"p": "0.35", "op": "15", "cash": "450", "g": "0"},
        "base": {"p": "0.45", "op": "70", "cash": "950", "g": "0.015"},
        "bull": {"p": "0.20", "op": "160", "cash": "1500", "g": "0.02"},
    },
}
P.joinpath("inputs.json").write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + "\n")

I = inputs
k = lambda x: D(I[x]) * 1000 / YI      # 千元 -> 亿元
m = lambda x: D(x) * 10**6 / YI        # 百万元 -> 亿元
price, ads, hkd, usd = D(I["price_hkd"]), D(I["ads_usd"]), D(I["hkd_cny"]), D(I["usd_cny"])
shares = D(I["class_a_ex_treasury"]) + D(I["class_b"])
o = {}
o["shares"] = shares
o["mcap_hkd_bn"] = price * shares / YI
o["mcap_cny_bn"] = o["mcap_hkd_bn"] * hkd
o["mcap_cny_via_ads_bn"] = ads * shares / D(I["ads_ratio"]) * usd / YI
o["ads_implied_hkd_per_share"] = ads / 2 * usd / hkd
# TTM
for key in ["revenue", "ni_attr", "cfo", "capex", "interest_inv_income"]:
    o[f"ttm_{key}_bn"] = sum(m(x) for x in I["q"][key])
o["ttm_fcf_bn"] = o["ttm_cfo_bn"] - o["ttm_capex_bn"]
o["ps_ttm"] = o["mcap_cny_bn"] / o["ttm_revenue_bn"]
o["pb"] = o["mcap_cny_bn"] / k("equity_attr_k")
o["pe_fy2025"] = o["mcap_cny_bn"] / m(I["fy"]["ni_attr"]["2025"])
o["fy_gross_margin_pct"] = {y: D(I["fy"]["gross_profit"][y]) / D(I["fy"]["revenue"][y]) * 100 for y in I["fy"]["revenue"]}
o["fy_op_margin_pct"] = {y: D(I["fy"]["op_income"][y]) / D(I["fy"]["revenue"][y]) * 100 for y in I["fy"]["revenue"]}
o["fy_fcf_bn"] = {y: m(I["fy"]["cfo"][y]) - m(I["fy"]["capex"][y]) for y in I["fy"]["cfo"]}
o["rnd_ratio_2025_pct"] = D(I["fy"]["rnd"]["2025"]) / D(I["fy"]["revenue"]["2025"]) * 100
o["mid_cycle_ni_2023_2025_bn"] = sum(m(I["fy"]["ni_attr"][y]) for y in ["2023", "2024", "2025"]) / 3
o["q3_2026_deliveries"] = sum(D(x) for x in I["deliveries_q3_2026"])
# 现金桥
o["gross_cash_bn"] = k("cash_k") + k("restricted_k") + k("td_sti_k")
o["borrowings_bn"] = k("st_borrow_k") + k("lt_borrow_k")
o["net_fin_cash_bn"] = o["gross_cash_bn"] - o["borrowings_bn"]
o["buyback_post_june_bn"] = (D(I["buyback_post_june_usd"]) * usd + D(I["buyback_post_june_hkd"]) * hkd) / YI
o["net_cash_after_buyback_bn"] = o["net_fin_cash_bn"] - o["buyback_post_june_bn"]
o["operating_float_bn"] = k("payables_k") - k("inventory_k") - k("receivable_k")
o["net_cash_after_float_bn"] = o["net_fin_cash_bn"] - o["operating_float_bn"]
buf = D(I["operating_buffer_bn"])
o["deployable_cash_bn"] = o["net_cash_after_buyback_bn"] - buf
o["net_cash_per_share_hkd"] = o["net_cash_after_buyback_bn"] * YI / shares / hkd
# 反向估值
o["implied_operating_value_bn"] = o["mcap_cny_bn"] - o["deployable_cash_bn"]
o["implied_perpetual_nopat_r8_bn"] = o["implied_operating_value_bn"] * D("0.08")
o["implied_perpetual_nopat_r10_bn"] = o["implied_operating_value_bn"] * D("0.10")
o["implied_ev_bn"] = o["mcap_cny_bn"] - o["net_fin_cash_bn"]
# 三年三情景
T = I["three_year"]
r3, yrs = D(T["discount_r"]), D(T["years_to_end_2028"])
disc = (1 + r3) ** int(2) * (1 + r3 * (yrs - 2))  # 2.2年：两年复利+0.2年单利近似
sc = {}
exp = D(0)
for name in ["bear", "base", "bull"]:
    s = T[name]
    opv = D(s["revenue"]) * D(s["ev_sales"]) if name == "bear" else D(s["nopat"]) * D(s["pe"])
    cash = o["net_cash_after_buyback_bn"] + D(s["cum_fcf"]) - buf
    eq = opv + cash
    ps_cny = eq * YI / shares
    ps_hkd = ps_cny / hkd
    sc[name] = {"operating_value_bn": opv, "cash_2028_after_buffer_bn": cash, "equity_bn": eq,
                "per_share_hkd_2028": ps_hkd, "per_ads_usd_2028": ps_cny * 2 / usd,
                "per_share_hkd_pv": ps_hkd / disc, "per_ads_usd_pv": ps_cny * 2 / usd / disc,
                "vs_price_pct": (ps_hkd / price - 1) * 100}
    exp += D(s["p"]) * ps_hkd
o["three_year"] = sc
o["three_year_expected_hkd_2028"] = exp
o["three_year_expected_hkd_pv"] = exp / disc
o["discount_factor_2_2y"] = disc
o["buy_below_hkd"] = (sc["base"]["per_share_hkd_pv"] * D("0.8"))
o["buy_below_ads_usd"] = o["buy_below_hkd"] * hkd * 2 / usd
# 十年压力测试
Tn = I["ten_year"]
def pe(roic, g, r): return (1 - g / roic) / (r - g)
ten = {}
for rkey in ["0.06", "0.07", "0.08", "0.09", "0.10"]:
    r = D(rkey); ex = D(0); rows = {}
    for name in ["bear", "base", "bull"]:
        s = Tn[name]; g = D(s["g"])
        p_ = pe(D(Tn["roic"]), g, r)
        term = D(s["op"]) * p_ + D(s["cash"])
        x = (term / o["mcap_cny_bn"]) ** (D(1) / 10) - 1
        rows[name] = {"exit_pe": p_, "terminal_equity_bn": term, "irr_pct": x * 100, "r_minus_g_pct": (r - g) * 100,
                      "equivalent_profit_for_tool_bn": term / p_}
        ex += D(s["p"]) * x * 100
    rows["expected_irr_pct"] = ex
    rows["covers_r"] = ex >= r * 100
    ten["r=" + rkey] = rows
o["ten_year"] = ten
o["ten_year_note"] = "直接法：净现金不随r重估；flip工具把全部终值当作PE×利润随r换算，会高估低r下的IRR，故以本表为准"

def ser(x):
    if isinstance(x, D): return str(x.quantize(D("0.0001")))
    if isinstance(x, dict): return {kk: ser(v) for kk, v in x.items()}
    return x
P.joinpath("results.json").write_text(json.dumps(ser(o), ensure_ascii=False, indent=2) + "\n")
print(json.dumps(ser(o), ensure_ascii=False, indent=2))
