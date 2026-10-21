from pathlib import Path
from decimal import Decimal as D
import importlib.util,json
p=Path(__file__).parent.parent/'快手'/'计算模型.py'
s=importlib.util.spec_from_file_location('common',p);c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
SCENARIOS={
 'bear':{'flows':[-10000,-5000,0,5000,8000,10000,10000,10000,10000,10000],'r':'0.13','g':'0.01','assets':'40000','div_HKD':'0'},
 'base':{'flows':[5000,15000,22000,25000,27500,28600,29744,30934,32171,33458],'r':'0.11','g':'0.025','assets':'74612.915','div_HKD':'0'},
 'bull':{'flows':[15000,30000,42000,50000,57500,60950,64607,68483,72592,76947],'r':'0.10','g':'0.03','assets':'90000','div_HKD':'0'}}
ANNUAL=[(2021,179127.997,-23538.379,-4011,9010),(2022,219954.948,-6686.110,11411,5731),(2023,276744.954,13855.828,40521.850,6879.551),(2024,337591.576,35807.179,57146.784,10999.490),(2025,364854.746,-23355.015,-13815.001,13270.708)]
out=c.run('美团','70.20','6175.4848',SCENARIOS,ANNUAL)
out['cash_bridge']={'cash':D('104716.797'),'shortterm':D('63597.373'),'loans':D('42138.301'),'notes':D('46562.954'),'leases':D('7116.047'),'net_before_leases':D('79612.915'),'net_with_leases':D('72496.868'),'reserve_assumption':D('35000'),'excess_cash':D('44612.915'),'investment_realization_assumption':D('30000'),'assets_used':D('74612.915')}
out['H126']={'CFO':D('2719.085'),'capex':D('6584.447'),'FCF':D('2719.085')-D('6584.447'),'lease_payments':D('1606.666'),'postlease_FCF':D('2719.085')-D('6584.447')-D('1606.666'),'paid_finance_cost':D('1414.617'),'postlease_interest_FCF':D('2719.085')-D('6584.447')-D('1606.666')-D('1414.617'),'profit':D('-4672.487')}
out['TTM']={'revenue':D('382840.334'),'profit':D('-38449.146'),'CFO':D('-26000.486'),'capex':D('13270.708')+D('6584.447')-D('5554.202'),'FCF':D('-26000.486')-(D('13270.708')+D('6584.447')-D('5554.202'))}
out['multiples']={'PS':out['market_cap_CNY_m']/D('382840.334'),'EV_revenue_excluding_lease_cash':(out['market_cap_CNY_m']-D('79612.915'))/D('382840.334'),'TTM_FCF_yield':out['TTM']['FCF']/out['market_cap_CNY_m']}
out['governance']={'Wang_family_economic_pct_June30':D('515871422')/D('6174765962')*100,'Wang_deemed_including_charity_pct_June30':D('563215264')/D('6174765962')*100,'Wang_voting_pct_including_deemed_B_June30':(D('515869783')*10+D('47345481'))/(D('579152986')*10+D('5595612976'))*100}
Path(__file__).with_name('计算结果.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str)+'\n')
