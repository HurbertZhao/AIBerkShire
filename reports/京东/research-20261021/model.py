"""京东集团（JD / 9618）估值模型：现金桥、分部加总、三年三情景、反向估值、十年压力测试输入。

全部计算用 Decimal。输入在同目录 inputs.json，输出写 results.json。
复跑：python3 reports/京东/research-20261021/model.py

口径约定（避免现金与少数股东权益重复归属）：
1. 上市子公司（京东物流、京东健康、京东工业）一律按"京东持股比例 × 市值"计价；
   它们自身的净现金（100%）先从合并口径净现金里扣掉，避免同一笔现金既在子公司市值里、又在母公司现金里。
2. 核心业务（零售中扣除京东健康与京东工业、新业务、未分配项目）用税后经营利润 × 倍数计价，
   不含利息收入与联营投资收益（这两项分别以现金和投资账面单独计价）。
3. 六月底应付账款受"618"季节性推高，高出 2025 年末的部分视为必须归还的季节性占款，从现金中扣除。
4. 限制性现金不计入可动用现金。
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json

getcontext().prec = 40
P = Path(__file__).resolve().parent
I = json.loads(P.joinpath('inputs.json').read_text())


def d(x):
    return D(str(x))


def q(x, n='0.01'):
    return x.quantize(D(n))


out = {}
mkt = I['market']
bs = I['balance_sheet_20260630_cny_mn']
subs = I['listed_subsidiaries']
fx_usd = d(mkt['usd_cny'])
fx_hkd = d(mkt['hkd_cny'])
shares = d(mkt['shares_outstanding'])    # 普通股流通股数（A+B，2026-06-30，公司6-K）
ads_ratio = d(mkt['ordinary_per_ads'])
hk_price = d(mkt['hk_price_hkd'])        # 主价格：9618.HK 2026-10-20 收盘
ads_price_check = d(mkt['ads_price_usd_check'])  # 交叉核对：JD ADS 2026-10-19 收盘

# ---------- 1. 市值 ----------
mcap_hkd = hk_price * shares
mcap_cny = mcap_hkd * fx_hkd
ads_equiv_usd = hk_price * ads_ratio * fx_hkd / fx_usd
ads_price = ads_equiv_usd                 # 以港股收盘折算的每ADS美元价，作为回报计算基准
out['market_cap'] = {
    'hkd_bn': q(mcap_hkd / D(10)**9),
    'cny_bn': q(mcap_cny / D(10)**9),
    'usd_bn': q(mcap_cny / fx_usd / D(10)**9),
    'ads_equivalent_usd': q(ads_equiv_usd),
    'ads_close_check_usd': q(ads_price_check),
    'ads_vs_hk_gap_pct': q((ads_price_check / ads_equiv_usd - 1) * 100),
    'usd_bn_via_ads_close': q(ads_price_check / ads_ratio * shares / D(10)**9),
}
mcap_bn = mcap_cny / D(10)**9

# ---------- 2. 历史与TTM ----------
h = I['history_cny_mn']
hist = {}
for y in h['revenue']:
    rev = d(h['revenue'][y]); cogs = d(h['cogs'][y]); oi = d(h['operating_income'][y]); ni = d(h['ni_attr'][y])
    hist[y] = {
        'revenue_bn': q(rev / 1000), 'gross_margin_pct': q((rev - cogs) / rev * 100),
        'op_margin_pct': q(oi / rev * 100), 'ni_attr_bn': q(ni / 1000),
        'net_margin_pct': q(ni / rev * 100), 'non_gaap_ni_bn': q(d(h['non_gaap_ni'][y]) / 1000),
        'cfo_bn': q(d(h['cfo'][y]) / 1000), 'company_fcf_bn': q(d(h['company_fcf'][y]) / 1000),
    }
out['history'] = hist
t = I['ttm_components_cny_mn']


def ttm(k):
    a, b, c = (d(x) for x in t[k])
    return a - b + c


ttm_vals = {k: ttm(k) for k in t if not k.startswith('_')}
out['ttm_bn'] = {k: q(v / 1000) for k, v in ttm_vals.items()}
out['ttm_bn']['company_fcf'] = q(d(I['ttm_company_fcf_cny_mn']) / 1000)
out['multiples'] = {
    'pe_ttm_gaap': q(mcap_bn / (ttm_vals['ni_attr'] / 1000)),
    'pe_ttm_non_gaap': q(mcap_bn / (ttm_vals['non_gaap_ni'] / 1000)),
    'pe_fy2025_gaap': q(mcap_bn / (d(h['ni_attr']['2025']) / 1000)),
    'pe_fy2024_gaap': q(mcap_bn / (d(h['ni_attr']['2024']) / 1000)),
    'ps_ttm': q(mcap_bn / (ttm_vals['revenue'] / 1000), '0.001'),
    'fcf_yield_ttm_pct': q(d(I['ttm_company_fcf_cny_mn']) / 1000 / mcap_bn * 100),
    'pb': q(mcap_bn / (d(bs['jd_shareholders_equity']) / 1000)),
}

# ---------- 3. 现金桥 ----------
cash = d(bs['cash']); rcash = d(bs['restricted_cash']); sti = d(bs['short_term_investments'])
debt = d(bs['short_term_debt']) + d(bs['notes_current']) + d(bs['notes_noncurrent']) + d(bs['long_term_debt'])
seasonal_ap = d(bs['accounts_payable']) - d(bs['accounts_payable_20251231'])
gross = cash + rcash + sti
adj_net = gross - rcash - debt - seasonal_ap
sub_value = {}
for k, s in subs.items():
    mc_cny = d(s['price_hkd']) * d(s['shares_total']) * fx_hkd / D(10)**6
    jd_cny = d(s['price_hkd']) * d(s['jd_shares_held']) * fx_hkd / D(10)**6
    net = d(s['cash']) + d(s['term_deposits']) + d(s['fvtpl_current']) - d(s['borrowings'])
    s['net_cash_cny_mn'] = str(net)
    sub_value[k] = {'market_cap_cny_mn': q(mc_cny), 'jd_shares_held': s['jd_shares_held'],
                    'jd_stake_of_sep30_shares_pct': q(d(s['jd_shares_held']) / d(s['shares_total']) * 100),
                    'jd_share_cny_mn': q(jd_cny),
                    'net_cash_100pct_cny_mn': s['net_cash_cny_mn']}
sub_total = sum((v['jd_share_cny_mn'] for v in sub_value.values()), D(0))
sub_netcash = sum((d(s['net_cash_cny_mn']) for s in subs.values()), D(0))
sub_noncurrent = sum((d(s['fvtpl_noncurrent']) for s in subs.values()), D(0))
parent_net = adj_net - sub_netcash
post = sum((d(v) for v in I['post_period_cash_items_cny_mn'].values()), D(0))
parent_net_after = parent_net + post
inv = I['investments_cny_mn']
inv_total = d(inv['equity_investees_book']) + d(inv['noncurrent_securities_book']) - sub_noncurrent
out['cash_bridge_cny_bn'] = {
    'gross_cash_restricted_sti': q(gross / 1000),
    'less_restricted_cash': q(-rcash / 1000),
    'less_interest_bearing_debt': q(-debt / 1000),
    'less_seasonal_payables_above_dec2025': q(-seasonal_ap / 1000),
    'adjusted_consolidated_net_cash': q(adj_net / 1000),
    'less_listed_subsidiaries_net_cash_100pct': q(-sub_netcash / 1000),
    'parent_ex_listed_net_cash': q(parent_net / 1000),
    'post_period_items': q(post / 1000),
    'parent_ex_listed_net_cash_after_post_items': q(parent_net_after / 1000),
    'jd_share_of_listed_subsidiaries_market_value': q(sub_total / 1000),
    'equity_investees_book': q(d(inv['equity_investees_book']) / 1000),
    'noncurrent_securities_and_investments_book': q(d(inv['noncurrent_securities_book']) / 1000),
    'less_listed_subsidiaries_noncurrent_fvtpl': q(-sub_noncurrent / 1000),
    'investments_ex_listed_subsidiaries_book': q(inv_total / 1000),
    'nci_book_value_reference': q(d(bs['nci_book']) / 1000),
}
out['listed_subsidiaries'] = sub_value

# 市场隐含核心价值（基准：投资按 50% 计）
hair = d(I['investment_haircut_base'])
non_core_base = parent_net_after + sub_total + inv_total * hair
implied_core = mcap_cny / D(10)**6 - non_core_base
core_ttm_pre = d(I['core_ttm_pre_tax_operating_cny_mn'])
out['implied_core'] = {
    'non_core_value_cny_bn': q(non_core_base / 1000),
    'non_core_share_of_market_cap_pct': q(non_core_base / (mcap_cny / D(10)**6) * 100),
    'implied_core_value_cny_bn': q(implied_core / 1000),
    'core_ttm_pre_tax_operating_cny_bn': q(core_ttm_pre / 1000),
    'core_retail_ex_listed_ttm_cny_bn': q(d(I['core_retail_ex_listed_ttm_cny_mn']) / 1000),
    'implied_multiple_on_retail_ex_listed_after_tax': q(implied_core / (d(I['core_retail_ex_listed_ttm_cny_mn']) * (1 - d(I['tax_rate'])))),
}

# ---------- 4. 三年三情景（2029 年末，每 ADS，人民币与美元） ----------
r_usd = d(I['hurdle_usd'])
sc_out = {}
for name, s in ((k, v) for k, v in I['scenarios'].items() if not k.startswith('_')):
    retail = d(s['retail_ex_listed_2029']); nb = d(s['new_business_2029']); un = d(s['unallocated_2029'])
    pre = retail + nb + un
    nopat = pre * (1 - d(I['tax_rate'])) if pre > 0 else pre
    core_val = nopat * d(s['exit_pe'])
    subs_val = sub_total * (1 + d(s['subsidiary_value_change']))
    invest = inv_total * d(s['investment_haircut'])
    cum_cash = sum((d(x) for x in s['core_cash_2027_2029']), D(0))
    equity = core_val + subs_val + invest + parent_net_after + cum_cash
    sh2029 = shares * (1 - d(s['net_share_reduction_3y']))
    per_ads_cny = equity * D(10)**6 / sh2029 * ads_ratio
    per_ads_usd = per_ads_cny / fx_usd
    per_share_hkd = equity * D(10)**6 / sh2029 / fx_hkd
    irr = ((per_ads_usd / ads_price) ** (D(1) / D(3)) - 1) * 100
    pv_today = per_ads_usd / (1 + r_usd) ** 3
    sc_out[name] = {
        'core_pre_tax_2029_cny_bn': q(pre / 1000), 'core_nopat_2029_cny_bn': q(nopat / 1000),
        'core_value_cny_bn': q(core_val / 1000), 'subsidiaries_cny_bn': q(subs_val / 1000),
        'investments_cny_bn': q(invest / 1000), 'parent_net_cash_cny_bn': q(parent_net_after / 1000),
        'cum_core_cash_2027_2029_cny_bn': q(cum_cash / 1000), 'equity_2029_cny_bn': q(equity / 1000),
        'shares_2029_mn': q(sh2029 / D(10)**6), 'value_per_ads_2029_usd': q(per_ads_usd),
        'value_per_share_2029_hkd': q(per_share_hkd), 'pv_today_per_share_hkd': q(per_share_hkd / (1 + r_usd) ** 3),
        'annualized_return_pct': q(irr), 'pv_today_at_hurdle_usd': q(pv_today),
        'probability': s['probability'],
    }
out['scenarios'] = sc_out
ev = sum((d(sc_out[k]['pv_today_at_hurdle_usd']) * d(sc_out[k]['probability']) for k in sc_out), D(0))
out['probability_weighted_pv_usd'] = q(ev)
out['buy_below_usd'] = q(ev * (1 - d(I['margin_of_safety'])))
ev_hk = sum((d(sc_out[k]['pv_today_per_share_hkd']) * d(sc_out[k]['probability']) for k in sc_out), D(0))
out['probability_weighted_pv_hkd_per_share'] = q(ev_hk)
out['buy_below_hkd_per_share'] = q(ev_hk * (1 - d(I['margin_of_safety'])))
out['current_vs_weighted_pv_pct'] = q((ads_price / ev - 1) * 100)
out['bear_pv_usd'] = sc_out['bear']['pv_today_at_hurdle_usd']

# ---------- 5. 反向估值：当前价隐含的核心税后利润 ----------
rev_out = {}
for pe in I['reverse_pe_grid']:
    rev_out[str(pe)] = q(implied_core / d(pe) / 1000)
out['reverse_implied_core_nopat_cny_bn_by_pe'] = rev_out
# 永续零增长、按人民币 r 折现：隐含的核心永续税后现金流
rev_dcf = {}
for r in I['reverse_r_grid']:
    rev_dcf[str(r)] = q(implied_core * d(r) / 1000)
out['reverse_flat_perpetuity_core_fcf_cny_bn'] = rev_dcf

# ---------- 6. 十年压力测试输入（利润单位：人民币十亿元） ----------
tv = I['ten_year']
out['ten_year_inputs'] = {
    'market_cap_cny_bn': q(mcap_bn),
    'profit_2036_cny_bn': tv['profit_2036_cny_bn'],
    'note': '终值年利润 = 核心税后经营利润 + 上市子公司归属利润 + 净现金利息（税后）；用 terminal_value.py irr 计算',
}

# ---------- 7. 敏感性：基准情景退出倍数 ±2 ----------
sens = {}
b = I['scenarios']['base']
for dpe in ['-2', '0', '2']:
    pre = d(b['retail_ex_listed_2029']) + d(b['new_business_2029']) + d(b['unallocated_2029'])
    core_val = pre * (1 - d(I['tax_rate'])) * (d(b['exit_pe']) + d(dpe))
    equity = core_val + sub_total + inv_total * d(b['investment_haircut']) + parent_net_after + sum((d(x) for x in b['core_cash_2027_2029']), D(0))
    per_ads_usd = equity * D(10)**6 / (shares * (1 - d(b['net_share_reduction_3y']))) * ads_ratio / fx_usd
    sens[dpe] = q(per_ads_usd / (1 + r_usd) ** 3)
out['base_pe_sensitivity_pv_usd'] = sens
# 新业务亏损敏感性（基准其余不变）
sens2 = {}
for nb in ['-10000', '-18000', '-30000']:
    pre = d(b['retail_ex_listed_2029']) + d(nb) + d(b['unallocated_2029'])
    core_val = pre * (1 - d(I['tax_rate'])) * d(b['exit_pe'])
    equity = core_val + sub_total + inv_total * d(b['investment_haircut']) + parent_net_after + sum((d(x) for x in b['core_cash_2027_2029']), D(0))
    per_ads_usd = equity * D(10)**6 / (shares * (1 - d(b['net_share_reduction_3y']))) * ads_ratio / fx_usd
    sens2[nb] = q(per_ads_usd / (1 + r_usd) ** 3)
out['base_new_business_loss_sensitivity_pv_usd'] = sens2

P.joinpath('results.json').write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str) + '\n')
print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
