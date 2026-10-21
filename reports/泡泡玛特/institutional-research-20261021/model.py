#!/usr/bin/env python3
"""Reproducible operating scenarios, not broker consensus or price targets.
Money unit: CNY 100 million. Facts: HKEX FY2025 and H1 2026 releases.
Decimal calculates the model; the repository financial_rigor CLI cross-checks it.
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json
import subprocess
import sys

getcontext().prec = 36
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def pct(new, old):
    return (new / old - 1) * 100

def cagr(new, old, years):
    return ((new / old) ** (D(1) / D(years)) - 1) * 100

facts = {
    'fy2025_revenue': D('371.20052'),
    'fy2025_attributable_profit': D('127.75689'),
    'h1_2025_revenue': D('138.76276'),
    'h1_2026_revenue': D('171.72921'),
    'h1_2025_attributable_profit': D('45.74368'),
    'h1_2026_attributable_profit': D('50.38384'),
    'h1_2026_group_profit': D('51.00310'),
    'h1_2026_adjusted_profit': D('51.55777'),
    'h1_2026_china_revenue': D('122.00509'),
    'h1_2025_china_revenue': D('82.82812'),
    'h1_2026_overseas_revenue': D('49.72412'),
    'h1_2025_overseas_revenue': D('55.93464'),
    'h1_2026_overseas_segment_profit': D('15.08492'),
    'h1_2025_overseas_segment_profit': D('24.64510'),
    'h1_2026_gross_profit': D('119.65740'),
    'h1_2026_cfo': D('36.37324'),
    'h1_2026_ppe_capex': D('6.73560'),
    'h1_2026_intangible_capex': D('.50579'),
    'h1_2026_lease_payments': D('5.02889'),
    'h1_2026_star_revenue': D('26.49969'),
    'h1_2025_star_revenue': D('3.89363'),
}
f = facts
derived = {
    'h1_revenue_growth_pct': pct(f['h1_2026_revenue'], f['h1_2025_revenue']),
    'h1_attributable_profit_growth_pct': pct(f['h1_2026_attributable_profit'], f['h1_2025_attributable_profit']),
    'h1_china_growth_pct': pct(f['h1_2026_china_revenue'], f['h1_2025_china_revenue']),
    'h1_overseas_growth_pct': pct(f['h1_2026_overseas_revenue'], f['h1_2025_overseas_revenue']),
    'h1_net_margin_pct': f['h1_2026_attributable_profit']/f['h1_2026_revenue']*100,
    'h1_gross_margin_pct': f['h1_2026_gross_profit']/f['h1_2026_revenue']*100,
    'h1_overseas_segment_margin_pct': f['h1_2026_overseas_segment_profit']/f['h1_2026_overseas_revenue']*100,
    'h1_2025_overseas_segment_margin_pct': f['h1_2025_overseas_segment_profit']/f['h1_2025_overseas_revenue']*100,
    'h1_overseas_segment_profit_growth_pct': pct(f['h1_2026_overseas_segment_profit'],f['h1_2025_overseas_segment_profit']),
    'h1_cfo_to_group_profit_pct': f['h1_2026_cfo']/f['h1_2026_group_profit']*100,
    'h1_post_capex_lease_cash': f['h1_2026_cfo']-f['h1_2026_ppe_capex']-f['h1_2026_intangible_capex']-f['h1_2026_lease_payments'],
    'star_share_of_group_increment_pct': (f['h1_2026_star_revenue']-f['h1_2025_star_revenue'])/(f['h1_2026_revenue']-f['h1_2025_revenue'])*100,
    'ex_star_revenue_growth_pct': pct(f['h1_2026_revenue']-f['h1_2026_star_revenue'],f['h1_2025_revenue']-f['h1_2025_star_revenue']),
    'fy2025_h2_revenue': f['fy2025_revenue']-f['h1_2025_revenue'],
}
near = {}
for name,g,m in [('bear','-.35','.22'),('base','-.25','.25'),('bull','-.15','.28')]:
    h2=derived['fy2025_h2_revenue']*(1+D(g))
    rev=f['h1_2026_revenue']+h2
    profit=f['h1_2026_attributable_profit']+h2*D(m)
    near[name]={'h2_revenue_growth_assumption_pct':D(g)*100,'h2_attributable_margin_assumption_pct':D(m)*100,'h2_revenue':h2,'fy2026_revenue':rev,'fy2026_attributable_profit':profit,'fy2026_revenue_growth_pct':pct(rev,f['fy2025_revenue']),'fy2026_profit_growth_pct':pct(profit,f['fy2025_attributable_profit'])}
long = {}
for name,rev,profit in [('bear','350','70'),('base','650','170'),('bull','1000','320'),('strong_execution_crosscheck','900','225')]:
    rev=D(rev);profit=D(profit)
    long[name]={'fy2036_revenue_assumption':rev,'fy2036_attributable_profit_assumption':profit,'net_margin_pct':profit/rev*100,'revenue_cagr_from_2026_base_pct':cagr(rev,near['base']['fy2026_revenue'],10),'profit_cagr_from_2026_base_pct':cagr(profit,near['base']['fy2026_attributable_profit'],10),'profit_cagr_from_actual_2025_pct':cagr(profit,f['fy2025_attributable_profit'],11)}
geography = {
    'note':'Author assumptions; China includes Hong Kong, Macau and Taiwan. No separate addition of category/IP revenue.',
    '2026_base_china_revenue_assumption':D('240'),
    '2026_base_overseas_revenue_assumption':near['base']['fy2026_revenue']-D('240'),
    '2036_base_china_revenue_assumption':D('350'),
    '2036_base_overseas_revenue_assumption':D('300'),
    'china_cagr_pct':cagr(D('350'),D('240'),10),
    'overseas_cagr_pct':cagr(D('300'),near['base']['fy2026_revenue']-D('240'),10),
}
out={'cutoff':'2026-10-21 Asia/Shanghai','unit':'CNY 100 million','facts':facts,'derived':derived,'author_2026_scenarios':near,'author_2036_scenarios':long,'geography_crosscheck':geography,'forecast_warning':'All future operating scenarios are author assumptions, not issuer guidance, not broker consensus, and not probability intervals.'}
(HERE/'model-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str)+'\n')
expressions=[
    '371.20052-138.76276',
    '371.20052*0.93',
    '171.72921+(371.20052-138.76276)*0.75',
    '50.38384+(371.20052-138.76276)*0.75*0.25',
    '(26.49969-3.89363)/(171.72921-138.76276)*100',
    '((171.72921-26.49969)/(138.76276-3.89363)-1)*100',
    '15.08492/49.72412*100',
    '(15.08492/24.64510-1)*100',
    '36.37324-6.73560-0.50579-5.02889',
    '(650/346.0575300)**(1/10)*100-100',
    '(170/93.965920000)**(1/10)*100-100',
    '900*0.25',
]
logs=[]
for expr in expressions:
    run=subprocess.run([sys.executable,str(ROOT/'tools/financial_rigor.py'),'calc','--expr',expr],capture_output=True,text=True,check=True)
    logs.append(run.stdout)
(HERE/'financial-rigor.txt').write_text('\n'.join(logs))
print(json.dumps({'derived':derived,'2026':near,'2036':long,'geography':geography},ensure_ascii=False,indent=2,default=str))
