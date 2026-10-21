#!/usr/bin/env python3
"""Reproduce disclosed-data arithmetic and explicitly hypothetical FCFF valuations.
No network; monetary model inputs in RMB billion, shares in billion.
FCFF deducts economic SBC and full operating lease cost; financial debt excludes leases.
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json, subprocess, sys
getcontext().prec=40
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def encode(x):
    if isinstance(x,D): return str(x)
    raise TypeError()
p=D('75.70'); shares=D('6.175508233'); fx=D('0.8525')
cash=D('104.716797'); st=D('63.597373'); debt=sum(map(D,['35.304527','6.833774','46.060011','0.502943']))
leases=D('4.263557')+D('2.852490')
buffer=D('30'); bridge=cash+st-debt-buffer
annual={
 '2021':['179.127997','42.474128','-23.538379','-23.127199','-4.011457','9.010455','116.795'],
 '2022':['219.954948','61.752979','-6.686110','-5.820448','11.411448','5.731304','112.032'],
 '2023':['276.744954','97.191161','13.855828','13.415387','40.522','6.880','145.160'],
 '2024':['337.591576','129.784594','35.807179','36.844956','57.146784','10.999490','168.243'],
 '2025':['364.854746','111.008626','-23.355015','-25.041137','-13.815001','13.270708','166.833704']}
out={'cutoff':'2026-10-20 Asia/Shanghai','price_date':'2026-10-16','price_hkd':p,'shares_bn':shares,'cny_per_hkd':fx,'market_cap_hkd_bn':p*shares,'market_cap_cny_bn':p*shares*fx,'cash_short_term_bn':cash+st,'financial_debt_bn':debt,'lease_debt_bn':leases,'net_cash_excluding_leases_bn':cash+st-debt,'net_cash_including_leases_bn':cash+st-debt-leases,'operating_cash_buffer_assumption_bn':buffer,'bridge_bn':bridge,'annual':{}}
for year,row in annual.items():
    rev,gp,np,op,cfo,capex,liquid=map(D,row)
    out['annual'][year]={'revenue_bn':rev,'gross_profit_bn':gp,'net_income_bn':np,'operating_profit_bn':op,'gross_margin_pct':gp/rev*100,'operating_margin_pct':op/rev*100,'cfo_bn':cfo,'capex_bn':capex,'simple_fcf_bn':cfo-capex,'cash_shortterm_bn':liquid}
out['h1_2026']={'simple_fcf_bn':D('2.719085')-D('6.584447'),'cash_after_capex_leases_finance_bn':D('2.719085')-D('6.584447')-D('1.606666')-D('1.414617'),'sbc_bn':D('3.301589'),'q2_op_ex_other_gains_bn':D('2.691166')-D('3.493946'),'q2_op_ex_other_and_fairvalue_bn':D('2.691166')-D('3.493946')-D('0.054814')}
out['ttm']={'revenue_bn':D('364.854746')+D('195.681950')-D('177.696362'),'cfo_bn':D('-13.815001')+D('2.719085')-D('14.904570'),'capex_bn':D('13.270708')+D('6.584447')-D('5.554202')}
out['ttm']['fcf_bn']=out['ttm']['cfo_bn']-out['ttm']['capex_bn']
out['ps_ttm']=p*shares*fx/out['ttm']['revenue_bn']
out['ev_sales_ttm_ex_operating_cash']= (p*shares*fx-(cash+st-debt))/out['ttm']['revenue_bn']
out['historical_2024_pe_at_current_price']=p*shares*fx/D('35.807179')
out['wang_economic_pct_without_charity']=D('515871222')/D('6174765962')*100
out['wang_sfo_deemed_pct_with_charity_spouse']=D('563215264')/D('6174765962')*100
cases={'bear':(['-5','5','10','15','20'],'0.03','0.02'),'base':(['10','20','30','38','45'],'0.06','0.03'),'bull':(['20','35','50','60','70'],'0.08','0.03')}
def valuation(case,r=D('.10'),scale=D('1')):
    first,growth,g=cases[case]; g=D(g); growth=D(growth)
    cfs=[D(v)*scale for v in first]
    for _ in range(5): cfs.append(cfs[-1]*(1+growth))
    pv=sum(cf/(1+r)**(i+1) for i,cf in enumerate(cfs))
    tv=cfs[-1]*(1+g)/(r-g)/(1+r)**10
    equity=pv+tv+bridge
    return {'fcff_bn':cfs,'terminal_growth':g,'discount_rate':r,'pv_explicit_bn':pv,'pv_terminal_bn':tv,'terminal_share_of_operating_value_pct':tv/(pv+tv)*100,'equity_cny_bn':equity,'fair_hkd':equity/shares/fx,'upside_pct':(equity/(p*shares*fx)-1)*100}
out['scenarios']={k:valuation(k) for k in cases}
out['rate_sensitivity']={str(r):valuation('base',r)['fair_hkd'] for r in map(D,['.09','.10','.11'])}
opbase=out['scenarios']['base']['pv_explicit_bn']+out['scenarios']['base']['pv_terminal_bn']
scale=(p*shares*fx-bridge)/opbase
out['reverse_dcf']={'base_path_scale':scale,'implied_year5_fcff_bn':D('45')*scale,'implied_year10_fcff_bn':out['scenarios']['base']['fcff_bn'][-1]*scale}
out['action_lines']={'seventy_pct_base':out['scenarios']['base']['fair_hkd']*D('.7'),'eightyfive_pct_base':out['scenarios']['base']['fair_hkd']*D('.85')}
out['base_cash_bridges_assumptions']={}
for period,raw in [('year1',['20','.25','6','9','2','10']),('year5',['64','.25','10','11','2','45'])]:
    ebit,tax,da,capex,nwc,expected=map(D,raw)
    fcff=ebit*(1-tax)+da-capex-nwc
    assert fcff==expected
    out['base_cash_bridges_assumptions'][period]={'normalized_ebit_after_economic_sbc_and_full_rent_bn':ebit,'tax_rate':tax,'nonlease_depreciation_bn':da,'full_capex_bn':capex,'working_capital_increase_bn':nwc,'fcff_bn':fcff}
(HERE/'model-output.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=encode)+'\n')
checks=[['verify-market-cap','--price',str(p),'--shares','6175508233','--reported','467210000000','--currency','HKD'],['cross-validate','--field','FY2025 revenue','--values',json.dumps({'HKEX':364854.746,'StockAnalysis':364855}),'--unit','RMB million'],['cross-validate','--field','FY2025 net income attributable','--values',json.dumps({'HKEX':-23355.015,'StockAnalysis':-23355}),'--unit','RMB million'],['cross-validate','--field','H1 cash and ST investments','--values',json.dumps({'HKEX':168314.170,'StockAnalysis':168314}),'--unit','RMB million'],['cross-validate','--field','Shares','--values',json.dumps({'HKEX September':6175508233,'CompaniesMarketCap':6174383320}),'--unit','shares'],['verify-valuation','--price',str(p),'--eps',str(D('-6.35')/fx),'--bvps',str(D('169.2')/shares/fx),'--fcf-per-share',str(out['ttm']['fcf_bn']/shares/fx)],['calc','--expr','2.691166-3.493946'],['calc','--expr=-13.815001+2.719085-14.904570-(13.270708+6.584447-5.554202)']]
logs=[]
for args in checks:
    run=subprocess.run([sys.executable,str(ROOT/'tools/financial_rigor.py')]+args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
    logs.append('$ financial_rigor.py '+' '.join(args)+'\n'+run.stdout)
    if run.returncode: raise RuntimeError(run.stdout)
(HERE/'financial-rigor.txt').write_text('\n'.join(logs))
print(json.dumps({k:out[k] for k in ['market_cap_hkd_bn','market_cap_cny_bn','bridge_bn','scenarios','reverse_dcf','action_lines']},ensure_ascii=False,indent=2,default=encode))
