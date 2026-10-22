#!/usr/bin/env python3
"""POP MART research snapshot. Amounts: CNY100m except explicit HKD prices.
Run from any directory. Model assumptions are not issuer guidance.
"""
from decimal import Decimal as D, getcontext
from pathlib import Path
import json, subprocess, sys, importlib.util

getcontext().prec = 36
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
logs = []
def run(tool, *args):
    args = list(map(str, args))
    p = subprocess.run([sys.executable, str(ROOT/'tools'/f'{tool}.py'), *args], capture_output=True, text=True)
    logs.append('$ python3 tools/'+tool+'.py '+' '.join(args)+'\n'+p.stdout+p.stderr)
    if p.returncode:
        raise RuntimeError(logs[-1])
    return p.stdout

price, shares, fx = D('129.8'), D('1331779203'), D('.85619')
n = shares/D('100000000')
cap_hkd, cap = price*n, price*n*fx
f = {k:D(v) for k,v in {
 'rev25':'371.20052','profit25':'127.75689','rev25h1':'138.76276',
 'profit25h1':'45.74368','rev26h1':'171.72921','profit26h1':'50.38384',
 'cfo25':'108.65152','cfo25h1':'59.77473','cfo26h1':'36.37324',
 'ppe25':'9.85250','ppe25h1':'3.53623','ppe26h1':'6.73560',
 'int25':'1.86287','int25h1':'.20900','int26h1':'.50579',
 'lease25':'6.08288','lease25h1':'2.63592','lease26h1':'5.02889',
 'cash':'124.42065','shortdeposit':'15.20187','longdeposit':'2.01773',
 'leasedebt':'37.27572','equity':'230.59024',
 'overseas25h1':'55.93464','overseas26h1':'49.72412',
 'overseasop25h1':'24.64510','overseasop26h1':'15.08492',
 'star25h1':'3.89363','star26h1':'26.49969',
 'monsters25h1':'48.14017','monsters26h1':'44.54361',
 'molly25h1':'13.57248','molly26h1':'9.00631',
}.items()}
d = {}
history=[]
for year,cfo,ppe,intang,cashshort in [
    (2021,'7.791','2.875','.4625','52.85'),
    (2022,'8.9102','2.6613','.8149','50.54'),
    (2023,'19.90596','3.24179','.68287','59.72'),
    (2024,'49.54220','3.72668','1.44022','96.32'),
    (2025,'108.65152','9.85250','1.86287','172.35')]:
    cash=D(cfo)-D(ppe)-D(intang)
    history.append({'year':year,'cash_after_ppe_intang_before_leases':cash,
                    'standardized_cash_short_investments':D(cashshort)})
    run('financial_rigor','calc','--expr',f'{cfo}-{ppe}-{intang}')
for key in ('rev','profit','cfo','ppe','int','lease'):
    d[key+'_ttm'] = f[key+'25']-f[key+'25h1']+f[key+'26h1']
d['fcf25'] = f['cfo25']-f['ppe25']-f['int25']-f['lease25']
d['fcf25h1'] = f['cfo25h1']-f['ppe25h1']-f['int25h1']-f['lease25h1']
d['fcf26h1'] = f['cfo26h1']-f['ppe26h1']-f['int26h1']-f['lease26h1']
d['fcf_ttm'] = d['cfo_ttm']-d['ppe_ttm']-d['int_ttm']-d['lease_ttm']
d['cash_deposits'] = f['cash']+f['shortdeposit']+f['longdeposit']
d['netcash_lease_diagnostic'] = d['cash_deposits']-f['leasedebt']
d['excesscash_assumption'] = d['cash_deposits']-D(40)
d['rev_growth_h1'] = (f['rev26h1']/f['rev25h1']-1)*100
d['profit_growth_h1'] = (f['profit26h1']/f['profit25h1']-1)*100
d['star_increment_share'] = (f['star26h1']-f['star25h1'])/(f['rev26h1']-f['rev25h1'])*100
d['exstar_growth'] = ((f['rev26h1']-f['star26h1'])/(f['rev25h1']-f['star25h1'])-1)*100
for key in ('overseas','overseasop','monsters','molly'):
    d[key+'_growth'] = (f[key+'26h1']/f[key+'25h1']-1)*100
d['overseasmargin25h1']=f['overseasop25h1']/f['overseas25h1']*100
d['overseasmargin26h1']=f['overseasop26h1']/f['overseas26h1']*100
d['tax_cash_bridge_pct']=(D('32.19674')-D('11.89626'))/(f['cfo25h1']-f['cfo26h1'])*100
rev25h2=f['rev25']-f['rev25h1']
near={}
for name,gr,margin in [('悲观','-.35','.22'),('基准','-.25','.25'),('乐观','-.15','.28')]:
    h2=rev25h2*(1+D(gr)); profit=f['profit26h1']+h2*D(margin)
    near[name]={'h2_growth':D(gr),'h2_margin':D(margin),'revenue':f['rev26h1']+h2,'profit':profit}
base=near['基准']['profit']
d.update(mcap_hkd=cap_hkd,mcap_cny=cap,price_cny=price*fx,shares_yi=n,
         pe_ttm=cap/d['profit_ttm'],pe25=cap/f['profit25'],pe26=cap/base,
         ps_ttm=cap/d['rev_ttm'],pb=cap/f['equity'],fcf_yield=d['fcf_ttm']/cap*100,
         ev_sales_diagnostic=(cap-d['netcash_lease_diagnostic'])/d['rev_ttm'],
         dividend_yield=D('2.3817')/(price*fx)*100)
run('financial_rigor','verify-market-cap','--price',price,'--shares',shares,'--reported','172856000000','--currency','HKD')
cross=[('股本',{'HKEX月报':1331779203,'证券之星':1331779203},'股'),
       ('10月21日收盘价',{'Investing历史':129.8,'新浪报道':129.8},'HKD'),
       ('2025收入',{'HKEX':371.20052,'S&P':371.20},'亿元CNY'),
       ('2025归母',{'HKEX':127.75689,'S&P':127.76},'亿元CNY'),
       ('2026H1收入',{'HKEX':171.72921,'中国基金报东方财富':171.73},'亿元CNY'),
       ('2026H1归母',{'HKEX':50.38384,'中国基金报东方财富':50.38},'亿元CNY'),
       ('2026H1现金等价物',{'HKEX':124.42065,'观点网':124.42},'亿元CNY'),
       ('2026H1CFO',{'HKEX':36.37324,'新浪雷递':36.37},'亿元CNY')]
for field, vals, unit in cross:
    run('financial_rigor','cross-validate','--field',field,'--values',json.dumps(vals,ensure_ascii=False),'--unit',unit)
run('financial_rigor','verify-valuation','--price',price,'--eps',d['profit_ttm']/n/fx,
    '--bvps',f['equity']/n/fx,'--fcf-per-share',d['fcf_ttm']/n/fx,'--dividend',D('2.3817')/fx)
run('financial_rigor','three-scenario','--price',price,'--eps',base/n/fx,'--shares',n,
    '--growth','.20','.06','-.12','--pe','24','18','12','--years','3','--currency','HKD')
three=[]
for name, gr, pe in [('乐观','.20','24'),('基准','.06','18'),('悲观','-.12','12')]:
    profit=base*(1+D(gr))**3; target=profit*D(pe)/n/fx; pv=target/D('1.08')**3
    three.append(dict(name=name,growth=gr,pe=pe,profit=profit,target_hkd=target,pv_hkd=pv,mos25_hkd=pv*D('.75')))
# Illustrative reverse DCF: recurring equity cash assumed 60, not actual FCFE.
# No separate cash addition. Year1=60; years2..10 grow at x; terminal g=1%.
def dcf(cf, growth, r=D('.08'), g=D('.01')):
    return sum(cf*(1+growth)**(t-1)/(1+r)**t for t in range(1,11))+cf*(1+growth)**9*(1+g)/(r-g)/(1+r)**10
reverse={}
for cf in map(D,['50','60','80']):
    lo,hi=D('-.5'),D('.5')
    for _ in range(180):
        mid=(lo+hi)/2
        if dcf(cf,mid)>cap: hi=mid
        else: lo=mid
    reverse[str(cf)]={'implied_growth_year2_10_pct':(lo+hi)/2*100,'flat_growth_value_hkd':dcf(cf,D(0))/n/fx}
# Terminal PE from perpetuity ONLY; r=10% anchors are mechanical, outside CNY main range.
risks='IP热度衰退:情景,海外需求萎缩:情景,授权终止:未建模,重大产品召回:未建模,跨境监管冲击:未建模'
run('terminal_value','audit','--currency','CNY','--r','.08','--roic','.25','--g','0,.01,.01','--rf','.02','--beta','1','--discrete-risks',risks)
spec=importlib.util.spec_from_file_location('tv',ROOT/'tools/terminal_value.py');tv=importlib.util.module_from_spec(spec);spec.loader.exec_module(tv)
profits=[50,170,320]; gs=[0,.01,.01]; weights=[.3,.5,.2]; k=.015; anchors=[]; terminal=[]
for profit,g in zip(profits,gs):
    for r in [.10,.08]:
        pe=(1-g/.25)/(r-g)
        run('terminal_value','pe','--roic','.25','--g',g,'--r',r)
        run('terminal_value','irr','--profit',profit,'--mcap',cap,'--pe',pe,'--years','10','--payout',k)
    anchors.append(tv.irr_from_terminal(profit,float(cap),(1-g/.25)/(.10-g),10,k)*100)
    pe=(1-g/.25)/(.08-g)
    terminal.append({'profit2036':profit,'g':g,'pe':pe,'irr_pct':tv.irr_from_terminal(profit,float(cap),pe,10,k)*100})
conf={'泡泡玛特':dict(roic=.25,g=gs,p=weights,irr10=anchors,k=k)}
(HERE/'terminal-config.json').write_text(json.dumps(conf,ensure_ascii=False,indent=2)+'\n')
flip=run('terminal_value','flip','--name','泡泡玛特','--config',HERE/'terminal-config.json','--r','.08','--delta','.02','--currency','CNY','--g-shift','0','--rf','.02')
flip1=run('terminal_value','flip','--name','泡泡玛特','--config',HERE/'terminal-config.json','--r','.08','--delta','.01','--currency','CNY','--g-shift','0','--rf','.02')
sensitivity=[]
for r in [.06,.07,.08,.09,.10]:
    vals=[tv.irr_from_terminal(p,float(cap),(1-g/.25)/(r-g),10,k)*100 for p,g in zip(profits,gs)]
    sensitivity.append(dict(r=r,irr_pct=vals,expected_irr_pct=sum(v*w for v,w in zip(vals,weights))))
# Additional decimal computations are mirrored through the mandatory financial tool.
for expr in ['129.8*1331779203/100000000*.85619',
             '36.37324-6.73560-.50579-5.02889',
             '108.65152-59.77473+36.37324',
             '(26.49969-3.89363)/(171.72921-138.76276)*100',
             '(32.19674-11.89626)/(59.77473-36.37324)*100',
             '124.42065+15.20187+2.01773-37.27572']:
    run('financial_rigor','calc','--expr',expr)
output=dict(cutoff='2026-10-22; quote 2026-10-21 close',fx_hkd_cny=fx,facts=f,derived=d,history=history,
            author_2026_scenarios=near,three_year=three,reverse_dcf=reverse,
            terminal=terminal,sensitivity=sensitivity,
            assumptions={'cashflow_currency':'CNY','r':'.08','ROIC':'.25','rf':'.02','ERP':'.06','beta':'1',
                         'terminal_probabilities':weights,'annual_dividend_less_dilution_proxy':k,
                         'reverse_dcf_firstyear_cash':'60 (assumption, not issuer FCFE)',
                         'excesscash_operating_reserve':'40 (not used as DCF addition)'})
(HERE/'model-results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2,default=str)+'\n')
(HERE/'financial-rigor.txt').write_text('\n'.join(logs))
(HERE/'sensitivity.txt').write_text(flip+'\n'+flip1)
print(json.dumps(dict(derived=d,near=near,three=three,reverse=reverse,terminal=terminal,sensitivity=sensitivity),ensure_ascii=False,indent=2,default=str))
