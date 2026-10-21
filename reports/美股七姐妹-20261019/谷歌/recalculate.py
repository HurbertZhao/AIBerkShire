#!/usr/bin/env python3
"""Offline reproducible Alphabet models; all amounts USD millions unless named billion.
Source facts are manually transcribed from links in report, never inferred from this model.
"""
import json, math, subprocess, sys
from decimal import Decimal as D
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
d=json.loads((HERE/'research-data.json').read_text())
b=d['balance_million']; a=d['assumptions']; t=d['ttm']; sh=sum(d['shares_million'].values())
market_class=D(str(d['price_a']))*D(d['shares_million']['A']+d['shares_million']['B'])+D(str(d['price_c']))*D(d['shares_million']['C'])
market_proxy=D(str(d['price_a']))*D(sh)
core_profit=t['op']*(1-a['tax'])
eps=core_profit/sh
strict_cash=b['cash']+b['marketable']-b['marketable_equity_current']-b['debt_exleases']
financial_assets=strict_cash-b['preferred']+0.7*(b['marketable_equity_current']+b['marketable_equity_noncurrent'])+0.5*b['nonmarketable']
asset_ps=financial_assets/sh
out={'shares_million':sh,'market_cap_class_million':str(market_class),'market_cap_a_proxy_million':str(market_proxy),'core_profit_million':core_profit,'core_eps':eps,'strict_net_cash_million':strict_cash,'financial_assets_haircut_million':financial_assets,'financial_assets_per_share':asset_ps,'normalized_pe':float(market_proxy)/core_profit,'gaap_pe':d['price_a']/t['eps_gaap'],'ps':float(market_proxy)/t['revenue'],'fcf_yield':t['fcf']/float(market_proxy),'ev_sales_exleases':(float(market_proxy)+b['debt_exleases']+b['preferred']-b['cash']-(b['marketable']-b['marketable_equity_current']))/t['revenue']}
out['annual_ratios']={y:{'gross_margin':v['gross']/v['revenue']*100,'op_margin':v['op']/v['revenue']*100,'fcf':v['ocf']-v['capex']} for y,v in d['annual'].items()}
out['quarter_ratios']={q:{'services_growth':v['services']/v['services_prior']*100-100,'cloud_growth':v['cloud']/v['cloud_prior']*100-100,'services_margin':v['services_op']/v['services']*100,'cloud_margin':v['cloud_op']/v['cloud']*100} for q,v in d['quarters'].items()}
out['three_year']=[{'name':n,'growth':h,'pe':pe,'eps3':eps*(1+h)**3,'target_core':eps*(1+h)**3*pe,'fair_today_core':eps*(1+h)**3*pe/1.1**3,'fair_today_with_assets':eps*(1+h)**3*pe/1.1**3+asset_ps,'price_only_annual_return':((eps*(1+h)**3*pe+asset_ps)/d['price_a'])**(1/3)-1} for n,h,pe in zip(['bull','base','bear'],a['growth3'],a['pe3'])]
irs=[]; out['ten_year']=[]
for name,g,pr,p in zip(['bear','base','bull'],a['g'],a['profit_2036_billion'],a['p']):
    pe=(1-g/a['roic'])/(a['r']-g)
    irr=((pr*1000*pe)/float(market_proxy))**.1-1+a['k']
    irs.append(irr*100)
    out['ten_year'].append({'name':name,'g':g,'pe':pe,'profit_billion':pr,'probability':p,'irr_percent':irr*100,'denominator':a['r']-g})
out['weighted_irr_percent']=sum(p*i for p,i in zip(a['p'],irs))
# Reverse cash-flow DCF: OCF-capex is an after-interest equity cash-flow proxy,
# not unlevered FCFF. Compare its PV directly with common-equity market value.
# Do NOT add the operating-valuation financial-asset bridge: financial income
# has not been stripped from OCF. This proxy is not exact distributable FCFE.
# End terminal = FCF10 * (1+g)/(r-g); no separately added assets or debt.
def pv(f0,h,r=.10,g=.03):
    return sum(f0*(1+h)**yr/(1+r)**yr for yr in range(1,11))+f0*(1+h)**10*(1+g)/(r-g)/(1+r)**10
def implied_growth(f0,r):
    lo,hi=-.2,.8
    for _ in range(160):
        mid=(lo+hi)/2
        if pv(f0,mid,r)<float(market_proxy):lo=mid
        else:hi=mid
    return {'growth':(lo+hi)/2,'value_million':pv(f0,(lo+hi)/2,r)}
out['reverse_dcf_basis']={'cash_flow':'OCF minus capex; after-interest equity cash-flow proxy, not exact FCFE','target':'A-price proxy for all A/B/C common equity','target_million':float(market_proxy),'financial_asset_addition_million':0,'terminal_growth':.03,'years':10}
out['reverse_dcf']={str(f0):implied_growth(f0,.10) for f0 in [t['fcf'],100000]}
out['reverse_dcf_sensitivity']={str(r):{str(f0):implied_growth(f0,r) for f0 in [t['fcf'],100000]} for r in [.09,.10,.11]}
out['sensitivity']={str(r):{'irr_percent':[(((pr*1000*(1-g/a['roic'])/(r-g))/float(market_proxy))**.1-1)*100 for pr,g in zip(a['profit_2036_billion'],a['g'])]} for r in [.08,.09,.10,.11,.12]}
for r,row in out['sensitivity'].items(): row['expected_irr_percent']=sum(p*i for p,i in zip(a['p'],row['irr_percent']))
(HERE/'model-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
config={'Alphabet':{'roic':a['roic'],'g':a['g'],'p':a['p'],'irr10':irs,'k':a['k']}}
(HERE/'terminal-config.json').write_text(json.dumps(config,indent=2))
log=[]
def run(tool,*args):
    command=[sys.executable,str(ROOT/'tools'/tool),*map(str,args)]
    r=subprocess.run(command,text=True,capture_output=True)
    log.append('$ '+' '.join(command)+'\n'+r.stdout+r.stderr+'\nexit='+str(r.returncode)+'\n')
    if r.returncode: raise RuntimeError(r.stdout+r.stderr)
run('financial_rigor.py','verify-market-cap','--price',d['price_a'],'--shares',sh*1000000,'--reported',4170000000000,'--currency','USD')
for field,v1,v2,v3 in [('FY2025 revenue',402836,402836,402836),('FY2025 net income',132170,132170,132170),('FY2025 cash investments',126843,126843,126843)]:
    run('financial_rigor.py','cross-validate','--field',field,'--values',json.dumps({'SEC':v1,'StockAnalysis':v2,'Macrotrends_search_excerpt':v3}),'--unit','USD_million')
run('financial_rigor.py','cross-validate','--field','all_class_shares_20260715','--values',json.dumps({'SEC_10Q':12230,'StockAnalysis':12230}),'--unit','million_shares')
run('financial_rigor.py','cross-validate','--field','20261016_GOOGL_close','--values',json.dumps({'StockAnalysis':340.59,'Investing':340.59}),'--unit','USD')
run('financial_rigor.py','cross-validate','--field','2026Q2_cash_and_securities_NOT_all_cash','--values',json.dumps({'SEC_10Q':242474,'StockAnalysis':242474}),'--unit','USD_million')
run('financial_rigor.py','verify-valuation','--price',d['price_a'],'--eps',eps,'--bvps',(b['equity_total']-b['preferred'])/sh,'--fcf-per-share',t['fcf']/sh,'--dividend',.88,'--revenue-per-share',t['revenue']/sh)
run('financial_rigor.py','three-scenario','--price',d['price_a'],'--eps',eps,'--shares',sh/100,'--growth',*a['growth3'],'--pe',*a['pe3'],'--years',3,'--currency','USD')
audit=['audit','--currency','USD','--r',a['r'],'--roic',a['roic'],'--g',','.join(map(str,a['g'])),'--rf',a['rf'],'--beta',1,'--discrete-risks','search_disruption:情景,antitrust:情景,AI_overinvestment:情景,catastrophic_cyber_event:未建模']
run('terminal_value.py',*audit)
for row in out['ten_year']:
    run('terminal_value.py','pe','--roic',a['roic'],'--g',row['g'],'--r',a['r'])
    run('terminal_value.py','irr','--profit',row['profit_billion'],'--mcap',float(market_proxy)/1000,'--pe',row['pe'],'--years',10,'--payout',a['k'])
for delta in [.02,.01]:
    run('terminal_value.py','flip','--config',HERE/'terminal-config.json','--name','Alphabet','--r',a['r'],'--delta',delta,'--currency','USD','--g-shift',0,'--rf',a['rf'])
run('terminal_value.py',*audit)
(HERE/'financial-validation.log').write_text('\n'.join(log))
print(json.dumps(out,ensure_ascii=False,indent=2))
