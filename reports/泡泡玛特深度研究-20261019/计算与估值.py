#!/usr/bin/env python3
"""Decimal reproduction. All financial model amounts are CNY 100 million.
Forecasts are assumptions, not facts. Run from any working directory.
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json
import subprocess
import sys

getcontext().prec = 40
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TOOL = ROOT / 'tools/financial_rigor.py'
price, shares, fx = D('142.2'), D('1331779203'), D('0.8520')
share_yi = shares / D('1e8')
cap_hkd = price * share_yi
cap_cny = cap_hkd * fx
raw = {
    'revenue_25': '371.20052', 'revenue_25h1': '138.76276', 'revenue_26h1': '171.72921',
    'net_25': '127.75689', 'net_25h1': '45.74368', 'net_26h1': '50.38384',
    'cfo_25': '108.65152', 'cfo_25h1': '59.77473', 'cfo_26h1': '36.37324',
    'ppe_25': '9.85250', 'ppe_25h1': '3.53623', 'ppe_26h1': '6.73560',
    'intang_25': '1.86287', 'intang_25h1': '.20900', 'intang_26h1': '.50579',
    'leasepaid_25': '6.08288', 'leasepaid_25h1': '2.63592', 'leasepaid_26h1': '5.02889',
    'cash': '124.42065', 'short_deposit': '15.20187', 'lease_debt': '37.27572',
    'operating_reserve_assumption': '40', 'equity': '230.59024',
}
x = {k: D(v) for k, v in raw.items()}
def ttm(key):
    return x[key+'_25'] - x[key+'_25h1'] + x[key+'_26h1']
ttm_rev, ttm_net, ttm_cfo = ttm('revenue'), ttm('net'), ttm('cfo')
simple_fcf = ttm_cfo - ttm('ppe')
lease_fcf = simple_fcf - ttm('intang') - ttm('leasepaid')
excess = x['cash'] + x['short_deposit'] - x['operating_reserve_assumption']
metrics = {
    'cap_hkd_yi': cap_hkd, 'cap_cny_yi': cap_cny, 'TTM_revenue': ttm_rev,
    'TTM_net': ttm_net, 'TTM_CFO': ttm_cfo, 'TTM_simple_FCF': simple_fcf,
    'TTM_after_intang_lease': lease_fcf, 'PE': cap_cny/ttm_net,
    'PS': cap_cny/ttm_rev, 'PB': cap_cny/x['equity'],
    'simple_FCF_yield_pct': simple_fcf/cap_cny*100,
    'after_intang_lease_yield_pct': lease_fcf/cap_cny*100,
    'cash_minus_lease': x['cash']+x['short_deposit']-x['lease_debt'],
    'excess_cash_assumption': excess,
    'H1_CFO_decline_pct': (x['cfo_26h1']/x['cfo_25h1']-1)*100,
    'H1_cash_after_ppe_intang_lease': x['cfo_26h1']-x['ppe_26h1']-x['intang_26h1']-x['leasepaid_26h1'],
    'H1_cash_after_ppe_intang_lease_2025': x['cfo_25h1']-x['ppe_25h1']-x['intang_25h1']-x['leasepaid_25h1'],
    'cash_before_tax_change_pct': (D('67.64282')/D('69.75420')-1)*100,
    'tax_cash_increase': D('32.19674')-D('11.89626'),
    'tax_share_of_CFO_decline_pct': (D('32.19674')-D('11.89626'))/(x['cfo_25h1']-x['cfo_26h1'])*100,
    'op_ex_fx_26h1': D('67.24746')+D('7.20270'),
    'op_ex_fx_25h1': D('60.43741')-D('1.20130'),
    'op_ex_fx_growth_pct': ((D('67.24746')+D('7.20270'))/(D('60.43741')-D('1.20130'))-1)*100,
    'core_op_26h1': D('119.65740')-D('39.31123')-D('9.26526'),
    'core_op_25h1': D('97.61064')-D('31.92590')-D('7.70405'),
    'monsters_growth_pct': (D('44.54361')/D('48.14017')-1)*100,
    'molly_growth_pct': (D('9.00631')/D('13.57248')-1)*100,
    'twinkle_growth_contribution_pct': (D('26.49969')-D('3.89363'))/(x['revenue_26h1']-x['revenue_25h1'])*100,
    'excluding_twinkle_growth_pct': ((x['revenue_26h1']-D('26.49969'))/(x['revenue_25h1']-D('3.89363'))-1)*100,
    'overseas_growth_pct': (D('49.72412')/D('55.93464')-1)*100,
    'plush_share_pct': D('98.25')/x['revenue_26h1']*100,
    'annual_retention_10yr_80pct': D('.8')**10*100,
    'cash_recovery_85pct_value_hkd': (D('85')-lease_fcf)/share_yi/fx,
}
metrics['core_op_growth_pct'] = (metrics['core_op_26h1']/metrics['core_op_25h1']-1)*100

# Year 1 is the next complete 12 months from research date. Year 10 ends in 2036.
# Revenues grow at a constant rate BETWEEN year 1 and year 10 (nine intervals).
# Margin and conversion linearly interpolate between endpoints. All are assumptions.
params = {
    'bear': ['340', '250', '.20', '.12', '.85', '.85', '0'],
    'base': ['400', '700', '.25', '.22', '.85', '.90', '.02'],
    'bull': ['440', '1200', '.28', '.25', '.85', '.95', '.03'],
}
def model(values, rate=D('.11')):
    rev1, rev10, margin1, margin10, conv1, conv10, g = map(D, values)
    growth = (rev10/rev1)**(D(1)/9)-1
    rows = []
    for y in range(1, 11):
        t = D(y-1)/9
        rev = rev1*(1+growth)**(y-1)
        margin = margin1+(margin10-margin1)*t
        conv = conv1+(conv10-conv1)*t
        profit = rev*margin
        cf = profit*conv
        rows.append({'year': y, 'revenue': rev, 'margin': margin, 'profit': profit,
                     'conversion': conv, 'cashflow': cf, 'PV': cf/(1+rate)**y})
    terminal_pv = rows[-1]['cashflow']*(1+g)/(rate-g)/(1+rate)**10
    flows_pv = sum(z['PV'] for z in rows)
    return {'rows': rows, 'growth_year1_to_10': growth, 'discount_rate': rate,
            'terminal_growth': g, 'PV_flows': flows_pv, 'PV_terminal': terminal_pv,
            'terminal_share_operating_pct': terminal_pv/(flows_pv+terminal_pv)*100,
            'equity_value_cny_yi': flows_pv+terminal_pv+excess,
            'price_hkd': (flows_pv+terminal_pv+excess)/share_yi/fx}
models = {k: model(v) for k,v in params.items()}
sens = {str(rate): model(params['base'], rate)['price_hkd'] for rate in [D('.09'), D('.11'), D('.13')]}
lo, hi = D('400'), D('1600')
for _ in range(160):
    middle = (lo+hi)/2
    vals = list(params['base']); vals[1] = str(middle)
    if model(vals)['price_hkd'] < price: lo=middle
    else: hi=middle
reverse_rev = (lo+hi)/2
summary = {'raw_inputs':raw, 'price_hkd':price,'shares':shares,'cny_per_hkd':fx,
           'metrics':metrics,'assumptions':params,'models':models,
           'base_rate_sensitivity':sens,'reverse_2036_revenue':reverse_rev,
           'reverse_2036_operating_net':reverse_rev*D('.22'),
           'reverse_2036_cash':reverse_rev*D('.22')*D('.9')}
HERE.joinpath('计算结果.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str)+'\n')
commands = [
    ['verify-market-cap','--price',str(price),'--shares',str(shares),'--reported','189379000000','--currency','HKD'],
    ['cross-validate','--field','2025收入','--values','{"HKEX":37120.052,"StockAnalysis":37120}','--unit','百万元人民币'],
    ['cross-validate','--field','2025归母利润','--values','{"HKEX":12775.689,"StockAnalysis":12776}','--unit','百万元人民币'],
    ['cross-validate','--field','2026H1收入','--values','{"HKEX":17172.921,"东方财富":17173}','--unit','百万元人民币'],
    ['cross-validate','--field','2026H1归母利润','--values','{"HKEX":5038.384,"东方财富":5038}','--unit','百万元人民币'],
    ['cross-validate','--field','股本','--values','{"HKEX_9月月报":1331779203,"Webb":1331779203}','--unit','股'],
    ['verify-valuation','--price',str(price),'--eps',str(ttm_net/share_yi/fx),
     '--bvps',str(x['equity']/share_yi/fx),'--fcf-per-share',str(lease_fcf/share_yi/fx)],
]
for k,z in models.items():
    expr = '+'.join(f'({r["cashflow"]}/(1.11**{r["year"]}))' for r in z['rows'])
    expr += f'+({z["rows"][-1]["cashflow"]}*(1+{z["terminal_growth"]})/(0.11-{z["terminal_growth"]})/(1.11**10))+{excess}'
    commands.append(['calc','--expr',f'({expr})/{share_yi}/{fx}'])
logs = []
for args in commands:
    r = subprocess.run([sys.executable,str(TOOL),*args], text=True,capture_output=True,check=True)
    logs.append('COMMAND '+ ' '.join(args)+'\n'+r.stdout)
HERE.joinpath('financial-rigor.txt').write_text('\n'.join(logs))
print(json.dumps({'metrics': metrics,'scenario_values':{k:v['price_hkd'] for k,v in models.items()},
                  'rate_sensitivity':sens,'reverse_2036_revenue':reverse_rev,
                  'reverse_2036_profit': reverse_rev*D('.22')},ensure_ascii=False,indent=2,default=str))
