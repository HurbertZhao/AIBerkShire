"""Conditional PDD valuation, Decimal only. Model assumptions are not independent facts."""
from decimal import Decimal as D, getcontext
import json, pathlib, subprocess, sys
getcontext().prec=36
P=pathlib.Path(__file__).resolve().parent; root=P.parents[2]
inputs={'price_usd':'80.97','legal_ordinary_shares_20260318':'5693585848','ordinary_per_ads':'4','usd_cny':'6.6905','revenue_2025_bn':'431.845713','net_income_2025_bn':'97.842539','operating_profit_2025_bn':'93.102131','cfo_2025_bn':'106.938690','capex_2025_bn':'1.145077','sbc_2025_bn':'7.936971','revenue_h1_2026_bn':'218.587','revenue_h1_2025_bn':'199.657','profit_h1_2026_bn':'39.729','profit_h1_2025_bn':'45.496','cash_and_short_investments_bn':'456.414','restricted_cash_bn':'77.274','lease_liability_bn':'4.844','scenarios':{'bear':{'fcff':'45','g1':'-.03','g2':'-.02','gt':'0','assets':'200'},'base':{'fcff':'70','g1':'.03','g2':'.02','gt':'.02','assets':'300'},'bull':{'fcff':'95','g1':'.08','g2':'.04','gt':'.025','assets':'380'}}}
shares=D(inputs['legal_ordinary_shares_20260318'])/D(4)/D(10)**9;fx=D(inputs['usd_cny']);price=D(inputs['price_usd']);market=price*shares*fx

def dcf(s,r=D('.09'),g1=None,assets=None,fcff=None):
 c=D(s['fcff']) if fcff is None else fcff;pv=D(0);flows=[]
 for y in range(1,11):
  c*=1+((D(s['g1']) if g1 is None else g1) if y<=5 else D(s['g2']));pv+=c/(1+r)**y;flows.append(c)
 terminal=c*(1+D(s['gt']))/(r-D(s['gt']))/(1+r)**10
 equity=pv+terminal+(D(s['assets']) if assets is None else assets)
 return {'equity_bn':equity,'usd':equity/shares/fx,'fcff_y3':flows[2],'fcff_y5':flows[4],'fcff_y10':flows[9],'terminal_share':terminal/(pv+terminal)}
revttm=D(inputs['revenue_2025_bn'])+D('218.587')-D('199.657');nttm=D('97.842539')+D('39.729')-D('45.496');opttm=D('93.102131')+D('47.330')-D('41.879')
fcf=D('106.938690')-D('1.145077');ownerproxy=fcf-D('7.936971')
out={'ads_bn':shares,'market_usd_bn':price*shares,'market_cny_bn':market,'revenue_ttm_bn':revttm,'profit_ttm_bn':nttm,'operating_profit_ttm_bn':opttm,'pe2025':market/D('97.842539'),'pettm':market/nttm,'ps_ttm':market/revttm,'ev_sales_cash_all':(market-D('456.414'))/revttm,'ev_sales_excess300':(market-D('300'))/revttm,'cash_per_ads_usd':D('456.414')/shares/fx,'surplus300_per_ads_usd':D('300')/shares/fx,'reported_fcf2025':fcf,'sbc_adjusted_cfo_capex_proxy':ownerproxy,'reported_fcf_yield':fcf/market,'sbc_adjusted_proxy_yield':ownerproxy/market,'normalized_fcf_yield':D('70')/market,'normalized_bridge':D('95')*(1-D('.20'))+1-5-2,'usd_cny_source_gap_pct':(D('6.6905')/D('6.6863')-1)*100,'shares_source_gap_pct':(shares/D('1.42')-1)*100,'marketcap_source_gap_pct':((price*shares)/D('115.25')-1)*100,'scenarios':{k:dcf(s) for k,s in inputs['scenarios'].items()},'sensitivity':{str(r):dcf(inputs['scenarios']['base'],r)['usd'] for r in map(D,['.08','.09','.10'])},'cash_zero_base':dcf(inputs['scenarios']['base'],assets=D(0))['usd'],'base_diluted_proxy_usd':dcf(inputs['scenarios']['base'])['equity_bn']/D('1.4735')/fx,'current_price_against_base_pct':price/dcf(inputs['scenarios']['base'])['usd']-1,'three_year_eps_scenarios':{}}
lo,hi=D('-.4'),D('.4')
for _ in range(180):
 mid=(lo+hi)/2
 if dcf(inputs['scenarios']['base'],g1=mid)['equity_bn']>market:hi=mid
 else:lo=mid
out['reverse_first5_growth']=(lo+hi)/2
out['steady_no_growth_fcf_required']=(market-D('300'))*D('.09')
for name,g,pe in [('bull','.08','14'),('base','.02','10'),('bear','-.10','7')]:
 eps=nttm/shares/fx;target=eps*(1+D(g))**3*D(pe)
 out['three_year_eps_scenarios'][name]={'target':target,'annual_return':(target/price)**(D(1)/D(3))-1}
out['annual']={}
for y,rev,gp,op,net,cfo,capex,cash in [(2021,'93.949939','62.231846','6.896762','7.768670','28.783011','3.287232','92.943'),(2022,'130.557589','99.095291','30.401921','31.538062','48.507860','.635716','149.439'),(2023,'247.639205','155.915628','58.698762','60.026544','94.162531','.583879','217.210'),(2024,'393.836097','239.935723','108.422862','112.434512','121.929292','.967137','331.560'),(2025,'431.845713','243.043960','93.102131','97.842539','106.938690','1.145077','422.308')]:
 out['annual'][y]={'revenue':rev,'gross_margin_pct':D(gp)/D(rev)*100,'op_margin_pct':D(op)/D(rev)*100,'net_income':net,'cfo':cfo,'capex':capex,'fcf':D(cfo)-D(capex),'cash_investments':cash}
out['quarter_metrics']={}
for q,r,c,o,n in [('2025Q3','108.276512','46.840159','25.025924','29.328184'),('2025Q4_unaudited','123.912194','55.155561','27.719675','24.540999'),('2026Q1','106.229','46.893','19.566','12.547'),('2026Q2','112.358','48.017','27.764','27.182')]:
 out['quarter_metrics'][q]={'gross_margin_pct':(D(r)-D(c))/D(r)*100,'op_margin_pct':D(o)/D(r)*100,'revenue':r,'net_income':n}
out['year10_profit_bridge']={'base_after_tax_operating':out['scenarios']['base']['fcff_y10']+D('6'),'base_operating_before_tax':(out['scenarios']['base']['fcff_y10']+D('6'))/D('.8')}
out['audit_revision_gap_pct']=(D('99.364469')/D('97.842539')-1)*100
out['strict_1pct_pairwise_checks']={
 'revenue':abs(D('431846')/D('431845.713')-1)<=D('.01'),
 'net_income':abs(D('97843')/D('97842.539')-1)<=D('.01'),
 'shares_with_date_gap':abs(D('1420000000')/D('1423396462')-1)<=D('.01'),
 'unaudited_vs_audited_profit':abs(D('99.364469')/D('97.842539')-1)<=D('.01')}
(P/'inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n');(P/'outputs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str)+'\n')
commands=[['verify-market-cap','--price','80.97','--shares',str(shares*D(10)**9),'--reported','115250000000','--currency','USD'],['cross-validate','--field','2025 revenue','--values','{"20F":431845.713,"StockAnalysis":431846}','--unit','CNY_million'],['cross-validate','--field','2025 net_income','--values','{"20F":97842.539,"StockAnalysis":97843}','--unit','CNY_million'],['cross-validate','--field','2026Q2 cash_short_investment','--values','{"company":456414,"StockAnalysis":456414}','--unit','CNY_million'],['cross-validate','--field','ADS_shares_date_and_rounding_gap','--values','{"20F_March18":1423396462,"StockAnalysis_rounded_current":1420000000}','--unit','ADS'],['cross-validate','--field','20261016_close','--values','{"StockAnalysis":80.97,"MarketBeat":80.97}','--unit','USD'],['cross-validate','--field','2025_profit_unaudited_vs_audited_DIFFERENCE','--values','{"20F":97842.539,"March_announcement":99364.469}','--unit','CNY_million'],['verify-valuation','--price','80.97','--eps',str(nttm/shares/fx),'--bvps',str(D('447.787')/shares/fx),'--fcf-per-share',str(ownerproxy/shares/fx),'--dividend','0'],['three-scenario','--price','80.97','--eps',str(nttm/shares/fx),'--shares',str(shares*10),'--growth','.08','.02','-.10','--pe','14','10','7','--years','3','--currency','USD']]
log=[]
for args in commands:
 p=subprocess.run([sys.executable,str(root/'tools/financial_rigor.py'),*args],capture_output=True,text=True);log.append('COMMAND '+' '.join(args)+'\n'+p.stdout+p.stderr)
(P/'financial-rigor.txt').write_text('\n'.join(log)); print(json.dumps(out,ensure_ascii=False,indent=2,default=str))
