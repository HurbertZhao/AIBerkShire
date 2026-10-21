# -*- coding: utf-8 -*-
"""Recompute scenario arithmetic without importing any company model.

Inputs remain researcher assumptions. This checks arithmetic, not forecasts.
"""
from pathlib import Path
from decimal import Decimal as D, getcontext
import json

getcontext().prec = 45
P = Path(__file__).resolve().parent
checks = []

def load(name):
    file = 'model-results.json' if name == '茅台' else '计算结果.json'
    return json.loads((P / name / file).read_text())

def check(name, scenario, kind, actual, reported):
    difference = abs(actual-D(str(reported)))
    assert difference < D('0.000001'), (name, scenario, kind, actual, reported)
    checks.append(dict(company=name, scenario=scenario, type=kind,
                       recomputed=str(actual), reported=str(reported),
                       absolute_difference=str(difference), status='ARITHMETIC_PASS'))

def pv_cash(flows, r, g, adjustment):
    return (sum((f/(1+r)**y for y, f in enumerate(flows, 1)), D(0))
            + flows[-1]*(1+g)/(r-g)/(1+r)**len(flows) + adjustment)

for name in ['腾讯', '拼多多']:
    data = load(name)
    inputs = data['assumptions']
    shares, fx = D(inputs['shares']), D(inputs['fx'])
    for label, start, first, second, rate, terminal, adjustment in inputs['scenarios']:
        start, first, second, rate, terminal, adjustment = map(lambda v: D(str(v)),
            [start, first, second, rate, terminal, adjustment])
        flows = [start*(1+first)**min(y, 5)*(1+second)**max(y-5, 0) for y in range(1, 11)]
        value = pv_cash(flows, rate, terminal, adjustment)/shares*fx
        check(name, label, 'DCF', value, data['dcf'][label]['price'])
    for case in data['three_year']:
        r = D(inputs['r'])
        end = D(inputs['eps'])*fx*(1+D(case['growth']))**3*D(case['pe'])
        dividends = [D(inputs['div'])*(1+D(inputs['divgrowth']))**y for y in range(1, 4)]
        value = end/(1+r)**3 + sum(x/(1+r)**y for y, x in enumerate(dividends, 1))
        check(name, case['scenario'], 'THREE_YEAR_PV', value, case['present_value'])

for name in ['快手', '美团']:
    data = load(name)
    for label, case in data['scenarios'].items():
        flows = list(map(D, case['flows']))
        r, g, adjustment, shares, fx = map(D, [case['r'], case['g'], case['assets'], data['shares_m'], data['HKD_to_CNY']])
        value = pv_cash(flows, r, g, adjustment)/shares/fx
        check(name, label, 'DCF', value, case['price'])
        remaining = sum(f/(1+r)**(y-3) for y, f in enumerate(flows, 1) if y > 3)
        remaining += flows[-1]*(1+g)/(r-g)/(1+r)**7
        div = D(case['annual_dividend_HKD'])
        end = (remaining+adjustment+sum(flows[:3])-div*fx*shares*3)/shares/fx
        value = end/(1+r)**3 + sum(div/(1+r)**y for y in range(1, 4))
        check(name, label, 'THREE_YEAR_PV', value, case['year3_discounted_wealth_HKD'])

data = load('茅台')
for label, case in data['DCF'].items():
    start, g, r, terminal, adj = map(D, [case['oe0_100m'], case['growth'], case['discount'], case['terminal_g'], case['excess_cash_100m']])
    flows = [start*(1+g)**y for y in range(1, 11)]
    value = pv_cash(flows, r, terminal, adj)*D('1e8')/D(data['shares'])
    check('茅台', label, 'DCF', value, case['price'])
for label, case in data['three_year'].items():
    eps, g, pe = D(data['TTM_profit'])/D(data['shares']), D(case['growth']), D(case['pe'])
    value = eps*(1+g)**3*pe/D('1.1')**3 + sum(eps*(1+g)**y*D('.75')/D('1.1')**y for y in range(1,4))
    check('茅台', label, 'THREE_YEAR_PV', value, case['present_value'])

data = load('泡泡玛特')
settings = {'bear': ('6', '0', '0', '.13', '.01', '5'),
            'base': ('8.5', '.07', '.04', '.11', '.025', data['excesscash_bn']),
            'bull': ('10.5', '.12', '.06', '.10', '.03', '10')}
for label, cfg in settings.items():
    start, g1, g2, r, terminal, adj = map(D, cfg)
    flows = [start*(1+g1)**min(y,5)*(1+g2)**max(y-5,0) for y in range(1,11)]
    value = pv_cash(flows, r, terminal, adj)*D('1e9')/D(data['shares'])/D(data['cny_per_hkd'])
    check('泡泡玛特', label, 'DCF', value, data['dcf'][label]['price'])
for label, case in data['three_year'].items():
    eps = D('10.5e9')/D(data['shares'])/D(data['cny_per_hkd'])
    g, pe = D(case['profit_growth']), D(case['pe'])
    value = eps*(1+g)**3*pe/D('1.11')**3 + sum(eps*(1+g)**y*D('.25')/D('1.11')**y for y in range(1,4))
    check('泡泡玛特', label, 'THREE_YEAR_PV', value, case['pv'])

data = load('MiniMax')
for label, case in data['dcf'].items():
    r, g, dilution = map(D, [case['discount'], case['terminal_growth'], case['annual_share_dilution']])
    shares, fx = D(data['shares']), D(data['hkd_per_usd'])
    flows = list(map(D, case['fcf_usd_bn']))
    operations = sum(f*D('1e9')/(shares*(1+dilution)**y)/(1+r)**y for y,f in enumerate(flows,1))
    terminal = flows[-1]*D('1e9')*(1+g)/(r-g)/(shares*(1+dilution)**10)/(1+r)**10
    cash = D(data['estimated_start_netcash_bn'])*D('1e9')/(shares*(1+dilution)**10)
    value = max(D(0), (operations+terminal+cash)*fx)
    check('MiniMax', label, 'DCF', value, case['price_hkd'])
for label, case in data['three_year'].items():
    value = D(case['year3_revenue_usd_bn'])*D('1e9')*D(case['equity_ps'])*D(data['hkd_per_usd'])/D(case['shares'])/D('1.15')**3
    check('MiniMax', label, 'THREE_YEAR_PV', value, case['pv'])

assert len(checks) == 42
(P/'独立复算.json').write_text(json.dumps({'scope':'Arithmetic only; assumptions are not validated', 'checks':checks}, ensure_ascii=False, indent=2))
print('42 arithmetic checks passed: 21 DCF and 21 three-year present values.')
