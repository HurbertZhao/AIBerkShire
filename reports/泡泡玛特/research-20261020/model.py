#!/usr/bin/env python3
"""Public-data arithmetic and conditional valuation. Money: CNY billion.
FCFE excludes non-operating interest, includes SBC, all leases, taxes, full capex,
working capital and minority attribution. Cost of equity 10%; no financial debt.
Inputs are research facts or clearly identified assumptions, not live quotes.
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
price=D('142.20'); shares=D('1.331779203'); fx=D('0.8525')
cash=D('12.442065'); deposits=D('1.520187'); liquidinvest=D('0.009662')
buffer=D('3'); nci_proxy=D('.229451')
liquid=cash+deposits+liquidinvest
bridge=liquid-buffer-nci_proxy
cap=price*shares*fx
annual={
 '2021':['4.490651','2.758624','1.149812','.854339','.7791','.2875','5.285','6.818182'],
 '2022':['4.617324','2.654543','.583380','.475660','.89102','.26613','5.054','6.963288'],
 '2023':['6.301002','3.864071','1.230646','1.082344','1.990596','.324179','5.972','7.769927'],
 '2024':['13.037749','8.707765','4.154272','3.125473','4.954220','.372668','9.632','10.683505'],
 '2025':['37.120052','26.764916','16.890474','12.775689','10.865152','.985250','17.235','22.277735']}
out={'cutoff':'2026-10-20 01:35:45 Asia/Shanghai','price_date':'2026-10-16','price_hkd':price,'shares_bn':shares,'shares_date':'2026-09-30','cny_per_hkd':fx,'market_cap_hkd_bn':price*shares,'market_cap_cny_bn':cap,'liquid_assets_bn':liquid,'operating_cash_buffer_assumption_bn':buffer,'minority_cash_deduction_proxy_bn':nci_proxy,'surplus_common_cash_proxy_bn':bridge,'lease_debt_bn':D('.665736')+D('3.061836'),'annual':{}}
prev_equity=None
for y,row in annual.items():
    rev,gp,op,np,cfo,ppe,liq,eq=map(D,row)
    out['annual'][y]={'revenue_bn':rev,'gross_margin_pct':gp/rev*100,'operating_profit_bn':op,'operating_margin_pct':op/rev*100,'attributable_profit_bn':np,'cfo_bn':cfo,'ppe_capex_bn':ppe,'fcf_ppe_only_not_owner_cash_bn':cfo-ppe,'liquid_assets_rounded_bn':liq,'equity_bn':eq,'roe_average_equity_pct':np/((eq+prev_equity)/2)*100 if prev_equity else None}
    prev_equity=eq
out['full_capex']={'2023':D('.324179')+D('.068287'),'2024':D('.372668')+D('.144022'),'2025':D('.985250')+D('.186287'),'h1_2025':D('.353623')+D('.020900'),'h1_2026':D('.673560')+D('.050579')}
out['h1']={'revenue_growth_pct':(D('17.172921')/D('13.876276')-1)*100,'net_profit_growth_pct':(D('5.038384')/D('4.574368')-1)*100,'gross_margin_pct':D('11.965740')/D('17.172921')*100,'net_margin_pct':D('5.038384')/D('17.172921')*100,'domestic_margin_pct':D('6.471322')/D('12.200509')*100,'overseas_margin_pct':D('1.508492')/D('4.972412')*100,'overseas_margin_prior_pct':D('2.464510')/D('5.593464')*100,'overseas_growth_pct':(D('4.972412')/D('5.593464')-1)*100,'after_full_capex_lease_bn':D('3.637324')-out['full_capex']['h1_2026']-D('.502889')}
out['h1']['after_sbc_bn']=out['h1']['after_full_capex_lease_bn']-D('.055467')
out['h1']['cash_to_attributable_profit_pct']=out['h1']['after_sbc_bn']/D('5.038384')*100
out['ttm']={'revenue_bn':D('37.120052')+D('17.172921')-D('13.876276'),'attributable_profit_bn':D('12.775689')+D('5.038384')-D('4.574368'),'cfo_bn':D('10.865152')+D('3.637324')-D('5.977473'),'capex_bn':out['full_capex']['2025']+out['full_capex']['h1_2026']-out['full_capex']['h1_2025'],'leases_bn':D('.608288')+D('.502889')-D('.263592'),'sbc_bn':D('.076629')+D('.055467')-D('.027917'),'interest_received_bn':D('.237628')+D('.092716')-D('.191679'),'minority_dividend_bn':D('.044974')+D('.184823')-D('.044974')}
t=out['ttm'];t['fcf_full_capex_bn']=t['cfo_bn']-t['capex_bn'];t['post_lease_cash_bn']=t['fcf_full_capex_bn']-t['leases_bn'];t['post_sbc_cash_bn']=t['post_lease_cash_bn']-t['sbc_bn'];t['attributable_operating_cash_proxy_bn']=t['post_sbc_cash_bn']-t['interest_received_bn']-t['minority_dividend_bn']
out['multiples']={'pe_ttm':cap/t['attributable_profit_bn'],'pe_2025':cap/D('12.775689'),'ps_ttm':cap/t['revenue_bn'],'pb':cap/D('23.059024'),'ev_revenue_exleases':(cap-liquid)/t['revenue_bn'],'price_owner_cash_proxy':cap/t['attributable_operating_cash_proxy_bn'],'cash_yield_pct':t['attributable_operating_cash_proxy_bn']/cap*100,'last_dividend_yield_pct':D('2.3817')/fx/price*100}
out['ownership']={'sfo_deemed_pct':D('654381407')/D('1331723150')*100,'economic_lookthrough_estimate_pct':(D('561131960')+D('31196420')+D('62053027')*D('.4096'))/D('1331723150')*100}
out['buyback_average_hkd']=D('1744493320')/D('11220000')
cases={'bear':(['5','4.5','4','4','4'],'0','0','35','7'),'base':(['7','8','9','10','12'],'.04','.025','65','17'),'bull':(['10','12','15','18','20'],'.07','.03','100','32')}
def val(case,r=D('.10'),scale=D('1')):
    first,growth,g,rev10,profit10=cases[case];growth=D(growth);g=D(g)
    cfs=[D(x)*scale for x in first]
    for _ in range(5):cfs.append(cfs[-1]*(1+growth))
    pv=sum(cf/(1+r)**(i+1) for i,cf in enumerate(cfs));terminal=cfs[-1]*(1+g)/(r-g)
    tv=terminal/(1+r)**10;eq=pv+tv+bridge
    year5=sum(cfs[i]/(1+r)**(i-4) for i in range(5,10))+terminal/(1+r)**5+bridge
    wealth=(year5+sum(cfs[:5]))/cap
    return {'fcfe_bn':cfs,'r':r,'g':g,'growth_year6_10':growth,'pv_explicit_bn':pv,'pv_terminal_bn':tv,'terminal_share_pct':tv/(pv+tv)*100,'equity_cny_bn':eq,'fair_hkd':eq/shares/fx,'upside_pct':(eq/cap-1)*100,'year10_revenue_assumption_bn':D(rev10),'year10_profit_assumption_bn':D(profit10),'year10_net_margin_assumption_pct':D(profit10)/D(rev10)*100,'year10_cash_conversion_pct':cfs[-1]/D(profit10)*100,'year5_stock_value_plus_surplus_cash_bn':year5,'fiveyear_cash_distributed_assumption_bn':sum(cfs[:5]),'fiveyear_wealth_multiple':wealth,'fiveyear_annualized_return_pct':(wealth**(D(1)/D(5))-1)*100}
out['scenarios']={k:val(k) for k in cases}
out['sensitivity']={str(r):val('base',r)['fair_hkd'] for r in map(D,['.09','.10','.11'])}
base=out['scenarios']['base'];scale=(cap-bridge)/(base['pv_explicit_bn']+base['pv_terminal_bn'])
out['reverse_dcf']={'base_path_scale':scale,'year5_fcfe_bn':D('12')*scale,'year10_fcfe_bn':base['fcfe_bn'][-1]*scale}
out['action_lines']={'70pct_base':base['fair_hkd']*D('.7'),'85pct_base':base['fair_hkd']*D('.85')}
out['share_source_discrepancy_pct']=(shares/D('1.31')-1)*100
out['base_cash_bridges_assumptions']={}
for period,raw in [('year1',['45','11','.8','1.8','3','7']),('year5',['60','15','1','2','2','12'])]:
    revenue,profit,da,capex,nwc,expected=map(D,raw)
    fcfe=profit+da-capex-nwc
    assert fcfe==expected
    out['base_cash_bridges_assumptions'][period]={'revenue_bn':revenue,'normalized_attributable_profit_after_tax_sbc_full_rent_ex_nonoperating_interest_bn':profit,'nonlease_depreciation_bn':da,'full_capex_bn':capex,'working_capital_increase_bn':nwc,'fcfe_bn':fcfe}
(HERE/'model-output.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=encode)+'\n')
checks=[['verify-market-cap','--price',str(price),'--shares','1331779203','--reported','186680000000','--currency','HKD'],['cross-validate','--field','FY2025 revenue','--values','{"HKEX":37120.052,"StockAnalysis":37120}','--unit','RMB million'],['cross-validate','--field','FY2025 attributable profit','--values','{"HKEX":12775.689,"StockAnalysis":12776}','--unit','RMB million'],['cross-validate','--field','H1 2026 revenue','--values','{"HKEX":17172.921,"Caixin":17173}','--unit','RMB million'],['cross-validate','--field','H1 2026 attributable profit','--values','{"HKEX":5038.384,"Caixin":5038}','--unit','RMB million'],['cross-validate','--field','TTM CFO','--values','{"HKEX arithmetic":8525.003,"StockAnalysis":8525}','--unit','RMB million'],['cross-validate','--field','Shares unresolved gross vs vendor','--values','{"HKEX September":1331779203,"StockAnalysis rounded":1310000000}','--unit','shares'],['verify-valuation','--price',str(price),'--eps',str(t['attributable_profit_bn']/shares/fx),'--bvps',str(D('23.059024')/shares/fx),'--fcf-per-share',str(t['attributable_operating_cash_proxy_bn']/shares/fx)],['calc','--expr','10.865152+3.637324-5.977473-(1.171537+0.724139-0.374523)-(0.608288+0.502889-0.263592)-(0.076629+0.055467-0.027917)']]
logs=[]
for args in checks:
    run=subprocess.run([sys.executable,str(ROOT/'tools/financial_rigor.py')]+args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
    logs.append('$ financial_rigor.py '+' '.join(args)+'\n'+run.stdout+'\nexit='+str(run.returncode))
(HERE/'financial-rigor.txt').write_text('\n'.join(logs)+'\n')
print(json.dumps({k:out[k] for k in ['market_cap_hkd_bn','market_cap_cny_bn','multiples','ownership','scenarios','reverse_dcf','action_lines','sensitivity']},ensure_ascii=False,indent=2,default=encode))
