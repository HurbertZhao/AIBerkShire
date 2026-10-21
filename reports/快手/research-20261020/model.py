from decimal import Decimal as D, getcontext
from pathlib import Path
import json, subprocess, re
getcontext().prec=38
P=Path(__file__).resolve().parent
inputs={"price_hkd":"29.30","price_date":"2026-10-16","shares":"4304151598","share_date":"2026-09-30","hkd_cny":"0.8525","fx_type":"2026-10-16 market reference, not executable quote","cash_current_pool_bn":"80.407","excluded_equity_bn":"0.719","bank_debt_bn":"27.362","supplier_finance_bn":"25.253","dividend_payable_bn":"2.584","operating_buffer_bn":"15","kling_economic_stake":"0.6833","wacc":"0.105","scenarios":{"bear":{"main":[7,7,7,6,6,5,5,4,4,4],"kling":[-4,-4,-3,-2,-1,0,0,0,0,0],"g":"0"},"base":{"main":[8,9,10,11,12,13,14,15,16,17],"kling":[-3,-2,-1,0,1,2,3,4,5,6],"g":"0.02"},"bull":{"main":[10,12,14,16,18,20,22,24,26,28],"kling":[-3,-1,1,3,5,7,10,13,16,20],"g":"0.025"}},"definition":"Forecast nominal CNY billion 2027-2036 unlevered operating free cash flow: cash tax, SBC economic compensation, capex incl prepayment, WC and lease cash deducted; exclude finance income/expense. Main and Kling separated without adding financing valuation. All bank and supplier finance debt assigned to main; Kling modeled debt-free. Current post-June financing proceeds excluded as unverified. Hypothetical future fully diluted Kling stake is not current settled ownership. Main case assumes financing investors bear negative operating funding pro rata, not a verified contractual duty. Stress case allocates all Kling negative cash to parent but only 68.33 percent positive cash. Base operating bridge explicitly deducts economic SBC and cash lease, excludes net finance/investment and assumes no material minority in main; depreciation is PPE only."}
P.joinpath('inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n')
price=D(inputs['price_hkd']);shares=D(inputs['shares']);fx=D(inputs['hkd_cny']);stake=D(inputs['kling_economic_stake']);r=D(inputs['wacc']);bn=D(10)**9
bridge=D('80.407')-D('.719')-D('27.362')-D('25.253')-D('2.584')-D('15')
def pv(cf,g):
 flows=sum((D(c)/(1+r)**(i+1) for i,c in enumerate(cf)),D(0)); terminal=D(cf[-1])*(1+g)/(r-g)/(1+r)**len(cf)
 return flows+terminal,terminal
out={'market_cap_hkd_bn':price*shares/bn,'market_cap_cny_bn':price*shares*fx/bn,'TTM_revenue_bn':D('142.776')-D('67.654')+D('69.251'),'TTM_net_income_bn':D('18.617')-D('8.900')+D('6.049'),'TTM_CFO_bn':D('26.716')-D('11.781')+D('9.044'),'TTM_capex_bn':D('14.942')-D('7.075')+D('17.941'),'TTM_lease_bn':D('3.823')-D('1.733')+D('1.919'),'bridge_bn':bridge,'scenarios':{}}
out['TTM_simple_FCF_bn']=out['TTM_CFO_bn']-out['TTM_capex_bn'];out['TTM_after_lease_FCF_bn']=out['TTM_simple_FCF_bn']-out['TTM_lease_bn'];out['PE_TTM']=out['market_cap_cny_bn']/out['TTM_net_income_bn'];out['PS_TTM']=out['market_cap_cny_bn']/out['TTM_revenue_bn'];out['PE_2025']=out['market_cap_cny_bn']/D('18.617');out['reverse_flat_FCFF_bn']=(out['market_cap_cny_bn']-bridge)*r;out['reverse_g2_FCFF_year1_bn']=(out['market_cap_cny_bn']-bridge)*(r-D('.02'))
for name,s in inputs['scenarios'].items():
 a,at=pv(s['main'],D(s['g']));b,bt=pv(s['kling'],D(s['g']));equity=a+stake*b+bridge; target=equity*bn/fx/shares
 out['scenarios'][name]={'main_EV_bn':a,'kling_EV_100pct_bn':b,'equity_bn':equity,'value_per_share_hkd':target,'upside_pct':(target/price-1)*100,'terminal_share_operating_value_pct':(at+stake*bt)/(a+stake*b)*100,'parent_2036_FCFF_bn':D(s['main'][-1])+stake*D(s['kling'][-1])}
out['base_operating_bridge_bn']={}
bridges={'2027_main':['145','17.5','3.5','10','14','2'],'2027_kling':['8','-2.5','0','1','1','.5'],'2036_main':['220','27.5','5.5','10','13','2'],'2036_kling':['60','18.75','3.75','8','15','2']}
inputs['base_operating_bridge_inputs_bn']=bridges
for key,vals in bridges.items():
 revenue,ebit,tax,da,capex,wc=map(D,vals);nopat=ebit-tax;cf=nopat+da-capex-wc
 out['base_operating_bridge_bn'][key]={'revenue':revenue,'EBIT_after_economic_SBC_and_cash_lease':ebit,'cash_tax':tax,'NOPAT_equals_normalized_NI_no_net_finance_or_investment':nopat,'PPE_depreciation':da,'cash_capex_including_prepayments':capex,'additional_working_capital':wc,'FCFF':cf,'EBIT_margin':ebit/revenue}
assert out['base_operating_bridge_bn']['2027_main']['FCFF']==D('8')
assert out['base_operating_bridge_bn']['2027_kling']['FCFF']==D('-3')
assert out['base_operating_bridge_bn']['2036_main']['FCFF']==D('17')
assert out['base_operating_bridge_bn']['2036_kling']['FCFF']==D('6')
out['kling_negative_cash_full_parent_stress']={}
for name,sc in inputs['scenarios'].items():
 extra=sum(((1-stake)*min(D(c),D(0))/(1+D(inputs['wacc']))**(i+1) for i,c in enumerate(sc['kling'])),D(0))
 per_share=extra*bn/fx/shares
 out['kling_negative_cash_full_parent_stress'][name]={'additional_parent_negative_cash_PV_bn':extra,'per_share_change_hkd':per_share,'stressed_value_hkd':out['scenarios'][name]['value_per_share_hkd']+per_share}
out['base_observe_75pct_hkd']=out['scenarios']['base']['value_per_share_hkd']*D('.75')
out['shares_secondary_error_pct']=abs(shares-D('4304000000'))/shares*100
out['RSU_grant_pct']=D('13293362')/shares*100
out['scenario_2036_net_profit_bn']={'bear':D('8'),'base':D('22')+D('15')*stake,'bull':D('35')+D('40')*stake}
out['sensitivity']={}
for rate in ['.09','.105','.12']:
 r=D(rate);a,_=pv(inputs['scenarios']['base']['main'],D('.02'));b,_=pv(inputs['scenarios']['base']['kling'],D('.02'));out['sensitivity'][rate]=(a+stake*b+bridge)*bn/fx/shares
P.joinpath('inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n')
P.joinpath('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str)+'\n')
checks=[['verify-market-cap','--price','29.30','--shares','4304151598','--reported','126112000000','--currency','HKD'],['cross-validate','--field','2025 revenue','--values','{"HKEX":142776,"StockAnalysis":142776}','--unit','CNY million'],['cross-validate','--field','2025 attributable net income','--values','{"HKEX":18617,"StockAnalysis":18617}','--unit','CNY million'],['cross-validate','--field','2026H1 cash equivalents','--values','{"HKEX":11696,"StockAnalysis":11696}','--unit','CNY million'],['cross-validate','--field','current shares rounded secondary','--values','{"Stockstar monthly transcription":4304151598,"Futu":4304000000}','--unit','shares'],['cross-validate','--field','2026-10-16 close','--values','{"Investing":29.30,"StockAnalysis":29.30}','--unit','HKD'],['calc','--expr','26.716-11.781+9.044-(14.942-7.075+17.941)']]
logs=[]
root=Path(__file__).resolve().parents[3]
for c in checks:
 z=subprocess.run(['python3',str(root/'tools/financial_rigor.py'),*c],capture_output=True,text=True);logs.append('COMMAND: financial_rigor.py '+' '.join(c)+'\n'+z.stdout+z.stderr)
P.joinpath('financial-rigor.txt').write_text(re.sub(r'\x1b\[[0-9;]*m','', '\n'.join(logs)))
print(json.dumps(out,ensure_ascii=False,indent=2,default=str))
