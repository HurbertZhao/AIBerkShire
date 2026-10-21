"""Reproduce conditional valuation; Decimal arithmetic is not forecast validation."""
from decimal import Decimal as D, getcontext
import json, pathlib, subprocess, sys
getcontext().prec=36
P=pathlib.Path(__file__).resolve().parent
root=P.parents[2]
inputs={'price_hkd':'417.80','shares':'9092644829','hkd_cny':'0.8525','revenue_2025_bn':'751.766','profit_2025_bn':'224.842','revenue_ttm_bn':'788.483','profit_ttm_bn':'235.508','company_fcf_2025_bn':'182.6','net_cash_bn':'58.191','cash_bn':'511.154','borrowings_notes_bn':'452.963','listed_investments_bn':'487.2','unlisted_book_bn':'387.9','scenarios':{'bear':{'fcff':'120','g1':'.01','g2':'.01','gt':'.01','assets':'450'},'base':{'fcff':'160','g1':'.08','g2':'.04','gt':'.025','assets':'709.341'},'bull':{'fcff':'200','g1':'.12','g2':'.06','gt':'.03','assets':'900'}}}
(P/'inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n')
shares=D(inputs['shares'])/D(10)**9;fx=D(inputs['hkd_cny']);price=D(inputs['price_hkd']);market=price*shares*fx

def dcf(s,r=D('.09'),g1=None):
 c=D(s['fcff']); pv=D(0);flows=[]
 for y in range(1,11):
  c*=1+((D(s['g1']) if g1 is None else g1) if y<=5 else D(s['g2']));pv+=c/(1+r)**y;flows.append(c)
 terminal=c*(1+D(s['gt']))/(r-D(s['gt']))/(1+r)**10
 return {'equity_bn':pv+terminal+D(s['assets']),'hkd':(pv+terminal+D(s['assets']))/shares/fx,'fcff_year3':flows[2],'fcff_year5':flows[4],'fcff_year10':flows[9],'terminal_share_operating':terminal/(pv+terminal)}
out={'market_hkd_bn':price*shares,'market_cny_bn':market,'pe2025':market/D('224.842'),'pettm':market/D('235.508'),'psttm':market/D('788.483'),'ev_sales_ex_investment_adjustment':(market-D('58.191'))/D('788.483'),'fcf_yield_2025':D('182.6')/market,'dividend_yield':D('5.3')/price,'price_share_gap_pct':(shares/D('9')-1)*100,'fx_gap_pct':(D('.8525')/D('.8520')-1)*100,'scenarios':{k:dcf(s) for k,s in inputs['scenarios'].items()},'sensitivity':{str(r):dcf(inputs['scenarios']['base'],r)['hkd'] for r in map(D,['.08','.09','.10'])}}
lo,hi=D('-.3'),D('.5')
for _ in range(180):
 mid=(lo+hi)/2
 if dcf(inputs['scenarios']['base'],g1=mid)['equity_bn']>market:hi=mid
 else:lo=mid
out['reverse_first5_growth']=(lo+hi)/2
out['annual']={}
for y,rev,gross,op,profit,cfo,capex in [(2021,'560.118','245.944','124.656','224.822','175.186','29.302'),(2022,'554.552','238.746','110.827','188.243','146.091','22.679'),(2023,'609.015','293.109','160.074','115.216','221.962','21.008'),(2024,'660.257','349.246','208.099','194.073','258.521','62.927'),(2025,'751.766','422.593','241.562','224.842','303.052','87.482')]:
 out['annual'][y]={'revenue':rev,'net_income':profit,'gross_margin_pct':D(gross)/D(rev)*100,'op_margin_pct':D(op)/D(rev)*100,'aggregator_cfo_minus_capex':D(cfo)-D(capex)}
out['normalized_fcff_bridge']=(D('305')-D('25'))*(1-D('.20'))+D('45')-D('94')-D('10')-D('5')
out['three_year_eps_scenarios']={name:(D('235.508')/shares/fx)*(1+D(g))**3*D(pe) for name,g,pe in [('bull','.12','20'),('base','.07','16'),('bear','0','10')]}
out['three_year_dividend_assumption']=D('5.30')*3
out['strict_1pct_pairwise_checks']={'shares':abs(D('9092644829')/D('9000000000')-1)<=D('.01'),'cash':abs(D('511154')/D('458904')-1)<=D('.01')}
(P/'outputs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str)+'\n')
commands=[['verify-market-cap','--price','417.8','--shares','9092644829','--reported','3760000000000','--currency','HKD'],['cross-validate','--field','2025 revenue','--values','{"annual_report":751766,"StockAnalysis":751766}','--unit','CNY_million'],['cross-validate','--field','2025 net_income','--values','{"annual_report":224842,"StockAnalysis":224842}','--unit','CNY_million'],['cross-validate','--field','cash_definition_DIFFERENCE','--values','{"company_total_cash":511154,"StockAnalysis_cash_investments":458904}','--unit','CNY_million'],['cross-validate','--field','shares_definition_DIFFERENCE','--values','{"issued_20261015":9092644829,"StockAnalysis_rounded_outstanding":9000000000}','--unit','shares'],['cross-validate','--field','20261016_close','--values','{"StockAnalysis":417.8,"Investing":417.8}','--unit','HKD'],['verify-valuation','--price','417.8','--eps',str(D('235.508')/shares/fx),'--fcf-per-share',str(D('182.6')/shares/fx),'--dividend','5.3'],['three-scenario','--price','417.8','--eps',str(D('235.508')/shares/fx),'--shares',str(shares*10),'--growth','.12','.07','0','--pe','20','16','10','--years','3','--currency','HKD']]
log=[]
for args in commands:
 p=subprocess.run([sys.executable,str(root/'tools/financial_rigor.py'),*args],capture_output=True,text=True)
 log.append('COMMAND '+ ' '.join(args)+'\n'+p.stdout+p.stderr)
(P/'financial-rigor.txt').write_text('\n'.join(log))
print(json.dumps(out,ensure_ascii=False,indent=2,default=str))
