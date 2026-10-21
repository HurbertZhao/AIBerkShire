"""Reproduce research assumptions and valuations with Decimal; no network access.

All amounts are USD millions unless stated. Forecasts are analyst assumptions,
not company guidance. Historical StockAnalysis input is preserved unmodified.
Run from any directory with Python 3.9+.
"""
import json
from decimal import Decimal as D, getcontext
from pathlib import Path

getcontext().prec = 36
HERE = Path(__file__).resolve().parent
RAW = json.loads((HERE / 'financial-inputs-stockanalysis.json').read_text())
ORDER = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA']

def scenario(g1, g2, margins, terminal):
    return dict(growth_1_5=str(g1), growth_6_10=str(g2),
                economic_cash_margins=[str(x) for x in margins], terminal_growth=str(terminal))

CONFIG = {
 'AAPL': dict(name='苹果', shares='14594.180000', model_shares='14594.180000', debt='84344', premium='.035',
    leases='0', lease_note='融资租赁本金未在所取数据中单列；此处0是未作额外调整，并非确认无租赁。',
    bear=scenario(.02,.01,[.22]*5,.02), base=scenario(.07,.04,[.25]*5,.025), bull=scenario(.10,.05,[.27]*5,.03),
    eps_growth=['.12','.07','.02'], exit_pe=['30','25','18']),
 'MSFT': dict(name='微软', shares='7425.545491', model_shares='7425.545491', debt='40294', premium='.035',
    leases='3101', lease_note='FY2026融资租赁本金；前瞻租赁付款在现金率中承担，不再扣融资租赁负债。',
    bear=scenario(.10,.05,[.09,.10,.12,.14,.16],.02), base=scenario(.16,.08,[.12,.16,.20,.24,.27],.03), bull=scenario(.20,.10,[.16,.21,.26,.29,.31],.03),
    eps_growth=['.20','.15','.08'], exit_pe=['30','25','18']),
 'GOOGL': dict(name='谷歌', shares='12230', model_shares='12285', debt='100164', premium='.04',
    leases='0', lease_note='融资租赁本金未单列，0不代表没有租赁；经营租赁已进入CFO。',
    preferred_dividend='1203.125',
    bear=scenario(.08,.03,[.00,.01,.03,.06,.09],.02), base=scenario(.18,.08,[.03,.07,.12,.17,.20],.03), bull=scenario(.24,.10,[.06,.12,.19,.25,.29],.03),
    eps_growth=['.22','.15','.05'], exit_pe=['28','22','16']),
 'AMZN': dict(name='亚马逊', shares='10786.313572', model_shares='10786.313572', debt='132549', premium='.045',
    leases='1599', other_financing='308', lease_note='以下为百万美元：TTM融资租赁本金1599、融资义务本金308；资产处置/激励4021未冲减本表毛资本开支。',
    bear=scenario(.08,.04,[-.04,-.02,.00,.02,.04],.02), base=scenario(.14,.08,[-.03,.00,.03,.06,.09],.03), bull=scenario(.18,.10,[.00,.03,.07,.11,.14],.03),
    eps_growth=['.22','.16','.05'], exit_pe=['32','25','18']),
 'META': dict(name='Meta', shares='2547.506225', model_shares='2547.506225', debt='83664', premium='.045',
    leases='3104', lease_note='以下为百万美元：TTM融资租赁本金=2524+1805−1225=3104。',
    bear=scenario(.10,.04,[-.06,-.02,.02,.06,.10],.02), base=scenario(.18,.08,[-.03,.03,.10,.17,.23],.03), bull=scenario(.22,.10,[.01,.08,.16,.24,.28],.03),
    eps_growth=['.22','.16','.05'], exit_pe=['28','22','16']),
 'NVDA': dict(name='英伟达', shares='24147', model_shares='24147', debt='33366', premium='.05',
    leases='0', other_financing='120', lease_note='TTM设备和无形资产融资本金为101+92−73=120百万美元，已扣除；未来云采购及租赁支出由现金率承担，附条件担保另设压力。',
    bear=scenario(.10,.02,[.30,.29,.28,.28,.28],.02), base=scenario(.25,.06,[.42,.43,.44,.43,.42],.03), bull=scenario(.32,.08,[.44,.46,.48,.47,.46],.03),
    eps_growth=['.30','.22','.05'], exit_pe=['28','22','15']),
 'TSLA': dict(name='特斯拉', shares='3949.547394', model_shares='3949.547394', debt='9061', premium='.06',
    leases='74', lease_note='以下为百万美元：TTM融资租赁本金=104+37−67=74；市值股数使用含已发行受限股的封面总数。',
    bear=scenario(.05,.03,[-.05,-.03,-.01,.01,.03],.02), base=scenario(.14,.10,[-.03,-.01,.02,.05,.08],.025), bull=scenario(.35,.12,[-.01,.03,.08,.15,.23],.03),
    eps_growth=['.60','.25','.00'], exit_pe=['60','30','15']),
}

# Assets are kept separate from operating DCF. Historical vendor cash fields
# sometimes combine cash, traded equity, and duplicated maturity categories.
# Non-operating asset marks are not recurring operating earnings.
CONFIG['NVDA']['cash_override']='56586'
CONFIG['GOOGL']['cash_override']='155411'
CONFIG['AAPL']['cash_override']='145423'
CONFIG['MSFT']['cash_override']='73043'
CONFIG['META']['cash_override']='86717'
CONFIG['TSLA']['cash_override']='43238'
CONFIG['AMZN']['cash_override']='118301'
CONFIG['GOOGL']['book_equity_override']='622457'  # remove preferred carrying equity 18023
CONFIG['TSLA']['book_equity_override']='86858'
CONFIG['AAPL']['investment_asset_book']='1094'
CONFIG['MSFT']['investment_asset_book']='28848'  # equity & other 36348 less restricted securities 7500; mixed upper bound
CONFIG['GOOGL']['investment_asset_book']='232650'  # listed 101189 + nonmarketable 131461
CONFIG['AMZN']['investment_asset_book']='229582'  # private 122300 + notes 97900 + warrants 4300 + equity method 395 + listed 4687
CONFIG['META']['investment_asset_book']='33700'  # listed 3543 + nonmarketable 30157
CONFIG['NVDA']['investment_asset_book']='98897'  # listed 47740 + nonmarketable 51157
CONFIG['TSLA']['investment_asset_book']='3681'  # SpaceX 3007 + digital assets 674, latest balance marks
CONFIG['TSLA']['minority_interest']='661'  # noncontrolling 607 + redeemable noncontrolling 54
CONFIG['TSLA']['model_shares']='3525.847394'  # exclude 423.7m conditional 2025 performance award in base/bear
CONFIG['TSLA']['bull_model_shares']='3949.547394'
BASE_OPERATING={
 'AAPL':(['.32']*5,'.32','.03'),
 'MSFT':(['.47','.48','.49','.49','.49'],'.49','.12'),
 'GOOGL':(['.33','.34','.35','.35','.35'],'.35','.10'),
 'AMZN':(['.12','.13','.14','.15','.15'],'.15','.09'),
 'META':(['.36','.37','.38','.39','.40'],'.40','.13'),
 'NVDA':(['.60','.60','.60','.59','.58'],'.46','.02'),
 'TSLA':(['.05','.07','.10','.12','.15'],'.15','.07')}
for case,margin in [('bear','.20'),('base','.32'),('bull','.38')]:
    CONFIG['NVDA'][case]['margin_year10']=margin

def dcf(ticker, case='base', rate=None, terminal=None, growth=None):
    raw, cfg = RAW[ticker], CONFIG[ticker]
    s = cfg[case]
    r = D(rate) if rate is not None else D('.0509') + D(cfg['premium'])
    g = D(terminal) if terminal is not None else D(s['terminal_growth'])
    rev = D(raw['revenue'][0]); pv = D(0); rows = []
    for year in range(1,11):
        gr = (D(growth) if growth is not None else D(s['growth_1_5'])) if year <= 5 else D(s['growth_6_10'])
        rev *= 1 + gr
        margin = D(s['economic_cash_margins'][min(year,5)-1])
        if year>5 and 'margin_year10' in s:
            margin += (D(s['margin_year10'])-margin)*D(year-5)/5
        core_cf = rev * margin
        preferred = D(cfg.get('preferred_dividend','0')) if year <= 3 else D(0)
        guarantee = D('20000') if ticker=='NVDA' and case=='bear' and year==4 else D('10000') if ticker=='NVDA' and case=='bear' and year==5 else D(0)
        cf = core_cf - preferred - guarantee
        discounted = cf / (1+r)**year
        pv += discounted
        rows.append(dict(year=year,revenue=rev,margin=margin,core_cash=core_cf,preferred=preferred,guarantee=guarantee,cash=cf,pv=discounted))
    tv = core_cf * (1+g) / (r-g)
    tv_pv = tv/(1+r)**10
    net_cash = D(cfg.get('cash_override',raw['cash'][0]))-D(cfg['debt'])-D(cfg.get('minority_interest','0'))
    equity = pv + tv_pv + net_cash
    return dict(rate=r, terminal_growth=g, pv_explicit=pv, terminal_pv=tv_pv,
        terminal_weight=tv_pv/(pv+tv_pv), net_cash=net_cash, equity=equity,
        per_share=equity/D(cfg.get(case+'_model_shares',cfg['model_shares'])),rows=rows)

def operating_bridge(ticker):
    """Explicit forward assumptions, not sourced historical CFO components.
    Operating margin treats leases as rent and includes regular employee pay.
    D&A excludes leased assets. Residual investment includes necessary customer
    ecosystem funding; working-capital intensity is assumed neutral here.
    """
    op5,op10,da=BASE_OPERATING[ticker]; rows=dcf(ticker)['rows']; out=[]
    for n in [1,5,10]:
        op=D(op5[n-1]) if n<=5 else D(op10)
        nopat=op*D('.8'); margin=rows[n-1]['margin']; investment=nopat+D(da)-margin
        out.append(dict(year=n,revenue=rows[n-1]['revenue'],operating_margin=op,tax_rate=D('.20'),
          nopat_margin=nopat,da_margin=D(da),working_capital_margin=D(0),
          cash_reinvestment_margin=investment,economic_cash_margin=margin))
    terminal_reinvestment=out[-1]['nopat_margin']-out[-1]['economic_cash_margin']
    return dict(rows=out, implied_terminal_incremental_roic=D(CONFIG[ticker]['base']['terminal_growth'])*out[-1]['nopat_margin']/terminal_reinvestment if terminal_reinvestment>0 else None)

def reverse_growth(ticker):
    price=D(RAW[ticker]['price']); lo=D('-.50'); hi=D('1.50')
    if dcf(ticker,growth=lo)['per_share']>price or dcf(ticker,growth=hi)['per_share']<price:
        return None
    for _ in range(160):
        mid=(lo+hi)/2
        if dcf(ticker,growth=mid)['per_share']<price: lo=mid
        else: hi=mid
    return (lo+hi)/2

def calculate(ticker):
    x,c=RAW[ticker],CONFIG[ticker]; shares=D(c['shares']); price=D(x['price'])
    revenue=D(x['revenue'][0]); op=D(x['operating_income'][0]); ni=D('3804') if ticker=='TSLA' else D(x['net_income'][0])
    cap=shares*price; cfo=D(x['cfo'][0]); capex=-D(x['capex'][0]); sbc=D(x['sbc'][0]); fcf=cfo-capex
    econ=fcf-D(c['leases'])-D(c.get('other_financing','0'))-sbc
    fiscal_i=1
    annual_ni=D('3794') if ticker=='TSLA' else D(x['net_income'][fiscal_i])
    avg_eq=(D('82137')+D('72913'))/2 if ticker=='TSLA' else (D(x['equity'][fiscal_i])+D(x['equity'][fiscal_i+1]))/2
    avg_assets=(D(x['assets'][fiscal_i])+D(x['assets'][fiscal_i+1]))/2
    eps_proxy=op*D('.8')/D(c['model_shares'])
    scenarios={s:dcf(ticker,s) for s in ['bear','base','bull']}
    r=scenarios['base']['rate']
    return dict(ticker=ticker, price=price, shares=shares, cap=cap, revenue=revenue, op=op, ni=ni,
      cfo=cfo,capex=capex,sbc=sbc,fcf=fcf,economic_cash=econ,
      pe=price/D(x['eps'][0]), aggregate_pe=cap/ni, ps=cap/revenue, pb=cap/D(c.get('book_equity_override',x['equity'][0])),
      p_fcf=cap/fcf if fcf>0 else None,p_economic_cash=cap/econ if econ>0 else None,
      gross_margin=D(x['gross_profit'][0])/revenue,op_margin=op/revenue,net_margin=ni/revenue,
      roe=annual_ni/avg_eq,roa=annual_ni/avg_assets,debt_to_assets=(D(x['assets'][0])-D(x['equity'][0]))/D(x['assets'][0]),
      current_ratio=D(x['current_assets'][0])/D(x['current_liabilities'][0]),
      capex_cfo=capex/cfo,sbc_revenue=sbc/revenue,eps_proxy=eps_proxy,
      reverse_growth=reverse_growth(ticker),scenarios=scenarios,
      operating_bridge=operating_bridge(ticker),
      sensitivity=[dict(rate=rr,growth=gg,price=dcf(ticker,rate=rr,terminal=gg)['per_share']) for rr in [r-D('.01'),r,r+D('.01')] for gg in [D('.02'),D('.03'),D('.04')]],
      investment_book_per_share=D(c['investment_asset_book'])/D(c['model_shares']),
      five_year=[dict(name=name,growth=D(growth),exit_ev_nopat=D(pe),nopat_per_share=op*D('.8')*(1+D(growth))**5/D(c.get(name+'_model_shares',c['model_shares'])),
        future_price=(op*D('.8')*(1+D(growth))**5*D(pe)+scenarios['base']['net_cash'])/D(c.get(name+'_model_shares',c['model_shares'])),
        price_cagr=(((op*D('.8')*(1+D(growth))**5*D(pe)+scenarios['base']['net_cash'])/D(c.get(name+'_model_shares',c['model_shares'])))/price)**(D(1)/5)-1)
        for name,growth,pe in zip(['bull','base','bear'],c['eps_growth'],c['exit_pe'])])

def encode(obj):
    if isinstance(obj,D): return str(obj)
    raise TypeError(type(obj))

if __name__=='__main__':
    out={t:calculate(t) for t in ORDER}
    (HERE/'valuation-assumptions.json').write_text(json.dumps(CONFIG,ensure_ascii=False,indent=2)+'\n')
    (HERE/'valuation-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=encode)+'\n')
    for t,x in out.items():
        print(t, 'price',x['price'],'DCF bear/base/bull',*[round(x['scenarios'][s]['per_share'],2) for s in ['bear','base','bull']], 'reverse growth',round(x['reverse_growth']*100,2),'terminal weight',round(x['scenarios']['base']['terminal_weight']*100,2))
