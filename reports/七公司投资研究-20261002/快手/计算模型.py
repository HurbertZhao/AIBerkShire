"""Research assumptions, not forecasts. Amounts CNY million; shares million.
Run from any cwd. Decimal exact arithmetic; no external packages.
The sibling Meituan model uses the same transparent structure.
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json
getcontext().prec = 38

def dcf(flows, r, g, assets, shares):
    flows = list(map(lambda x: D(str(x)), flows)); r=D(str(r));g=D(str(g))
    explicit = sum(c / (1+r)**i for i,c in enumerate(flows,1))
    terminal = flows[-1]*(1+g)/(r-g)/(1+r)**10
    return dict(explicit=explicit,terminal=terminal,equity=explicit+terminal+D(str(assets)),price=(explicit+terminal+D(str(assets)))/D(str(shares))/FX)

def run(name, price, shares, scenarios, annual):
    price=D(price);shares=D(shares); out={'company':name,'date':'2026-10-02','unit':'CNY million; shares million','HKD_to_CNY':FX,'market_price_HKD':price,'shares_m':shares,'market_cap_HKD_m':price*shares,'market_cap_CNY_m':price*shares*FX,'scenarios':{},'annual':[]}
    for label,p in scenarios.items():
        f=list(map(lambda x:D(str(x)),p['flows']));r=D(p['r']);g=D(p['g']);a=D(p['assets']);div=D(p['div_HKD']);v=dcf(f,r,g,a,shares)
        remaining=sum(c/(1+r)**(i-3) for i,c in enumerate(f,1) if i>3)+f[-1]*(1+g)/(r-g)/(1+r)**7
        retained=sum(f[:3])-div*FX*shares*3
        endprice=(remaining+a+retained)/shares/FX
        total=endprice+div*3
        v.update({'flows':f,'r':r,'g':g,'assets':a,'annual_dividend_HKD':div,'year3_price_HKD':endprice,'year3_total_wealth_HKD':total,'year3_discounted_wealth_HKD':endprice/(1+r)**3+sum(div/(1+r)**t for t in range(1,4)),'three_year_total_return':total/price-1,'three_year_annual_return':(total/price)**(D(1)/3)-1,'year3_price_1pct_dilution_HKD':endprice/D('1.01')**3})
        out['scenarios'][label]=v
    p=scenarios['base'];b=out['scenarios']['base'];r=D(p['r']);f=list(map(lambda x:D(str(x)),p['flows']));first2=f[0]/(1+r)+f[1]/(1+r)**2
    scale=(price*shares*FX-D(p['assets'])-first2)/(b['explicit']+b['terminal']-first2)
    out['reverse_DCF']={'tail_scale_after_year2':scale,'implied_year3_FCF_m':f[2]*scale,'implied_year10_FCF_m':f[-1]*scale,'fixed_year1_2':f[:2],'r':r,'g':p['g']}
    out['sensitivity']=[{'r':r,'g':g,'price':dcf(p['flows'],r,g,p['assets'],shares)['price']} for r in ['0.09','0.11','0.13'] for g in (['0.01','0.02','0.03'] if name=='快手' else ['0.015','0.025','0.035'])]
    for year,rev,profit,cfo,capex in annual:
        rev,profit,cfo,capex=map(lambda x:D(str(x)),(rev,profit,cfo,capex));fcf=cfo-capex
        out['annual'].append(dict(year=year,revenue=rev,profit=profit,cfo=cfo,capex=capex,fcf=fcf,cfo_profit=cfo/profit,fcf_profit=fcf/profit,netmargin=profit/rev))
    return out

FX=D('0.85842') # 2026-09-30 SAFE fixing, not executable spot.
SCENARIOS={
 'bear':{'flows':[-6000,-2000,1000,3000,4000,4000,4000,4000,4000,4000],'r':'0.13','g':'0','assets':'5000','div_HKD':'0'},
 'base':{'flows':[0,5000,8000,9000,10000,10300,10609,10927,11255,11593],'r':'0.11','g':'0.02','assets':'12797','div_HKD':'0.69'},
 'bull':{'flows':[2000,8000,12000,15000,18000,19440,20995,22675,24489,26448],'r':'0.10','g':'0.03','assets':'20000','div_HKD':'0.90'}}
ANNUAL=[(2021,81082,-78074,-5519,7764),(2022,94183,-13690,795,5100),(2023,113470,6396,20781,4897),(2024,126898,15335,29787,8063),(2025,142776,18617,26716,14942)]
if __name__=='__main__':
    out=run('快手','29.58','4327.034194',SCENARIOS,ANNUAL)
    out['cash_bridge']={'liquid':D('80407'),'loans':D('27362'),'supplier_financing':D('25248'),'net_before_lease':D('27797'),'lease_liabilities':D('11672'),'net_including_lease':D('16125'),'operating_reserve_assumption':D('15000'),'excess_used':D('12797')}
    out['H126']={'CFO':D('9044'),'capex':D('17941'),'simple_FCF':D('9044')-D('17941'),'lease_payments':D('1919'),'postlease_FCF':D('9044')-D('17941')-D('1919'),'attributable_profit':D('6049'),'CFO_profit':D('9044')/D('6049'),'FCF_profit':(D('9044')-D('17941'))/D('6049')}
    out['TTM']={'revenue':D('144373'),'profit':D('15766'),'CFO':D('23979'),'capex':D('14942')+D('17941')-D('7075'),'FCF':D('23979')-(D('14942')+D('17941')-D('7075'))}
    out['multiples']={'PE':out['market_cap_CNY_m']/D('15766'),'PS':out['market_cap_CNY_m']/D('144373'),'EV_revenue_conservative_cash':(out['market_cap_CNY_m']-D('27797'))/D('144373'),'FY25_FCF_yield':D('11774')/out['market_cap_CNY_m'],'TTM_FCF_yield':D('-1829')/out['market_cap_CNY_m']}
    Path(__file__).with_name('计算结果.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str)+'\n')
