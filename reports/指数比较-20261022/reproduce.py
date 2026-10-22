"""Reproduce the dated research snapshot; all forecasts are explicit assumptions."""
from decimal import Decimal as D, getcontext
import json
from pathlib import Path
import subprocess
import sys

getcontext().prec = 40
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import terminal_value as tv

DATA = {
 '沪深300': dict(code='000300', price='4036.30', ref='4357.62', pe='13.15', pb='1.36', div='2.49', roic=.10, k=.02,
   closes='4036.30 4111.93 4152.11 4174.53 4170.61 4166.01 4217.68 4275.68 4287.98 4317.25 4310.28 4357.62 4345.21 4340.75 4439.14 4517.28 4544.59 4539.57 4507.39 4460.16',
   growth3=['.08','.04','-.03'], pe3=['15','13','10'], growth10=['0','.04','.08'], low='4022.87', valband=['11','12.5']),
 '创业板指': dict(code='399006', price='2576.90', ref='3135.28', pe='31.28', pb='5.2', div=None, roic=.15, k=.005,
   closes='2576.90 2694.71 2739.20 2746.29 2772.38 2783.17 2866.76 2958.34 2963.82 3043.33 3036.66 3135.28 3142.56 3139.82 3288.95 3379.61 3399.93 3399.59 3372.68 3298.31',
   growth3=['.15','.08','-.05'], pe3=['35','28','20'], growth10=['-.02','.09','.15'], low='2576.90', valband=['22','28']),
 '科创50': dict(code='000688', price='1305.87', ref='1530.01', pe='71.37', pb='7.82', div='.27', roic=.15, k=.001,
   closes='1305.87 1343.28 1342.42 1329.19 1358.65 1359.52 1380.26 1427.18 1426.72 1457.27 1456.32 1530.01 1569.34 1555.98 1621.87 1660.85 1665.04 1657.48 1652.63 1606.29',
   growth3=['.25','.15','0'], pe3=['60','45','30'], growth10=['0','.15','.23'], low='1302.39', valband=['40','50']),
}
log=[]
def run(tool, *args):
    p=subprocess.run([sys.executable,str(ROOT/'tools'/tool),*map(str,args)],capture_output=True,encoding='utf-8')
    log.append('$ '+tool+' '+' '.join(map(str,args))+'\n'+p.stdout+p.stderr)
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    return p.stdout

out={}
cfg={}
for name,s in DATA.items():
    p,ref,pe,pb=map(D,[s['price'],s['ref'],s['pe'],s['pb']])
    ratio=p/ref
    eps=ref/pe
    values=list(map(D,s['closes'].split()))
    v=dict(price=str(p),ref=str(ref),eps_proxy=str(eps),pe_proxy=str(pe*ratio),pb_proxy=str(pb*ratio),
           since_ref_pct=str((ratio-1)*100),ma={str(n):str(sum(values[:n])/D(n)) for n in (5,10,20)},
           valuation_band=[str(eps*D(x)) for x in s['valband']],scenarios3=[],terminal=[])
    run('financial_rigor.py','cross-validate','--field',name+'收盘2026-10-22','--values',json.dumps({'ETF.run':s['price'],'Investing':s['price']}),'--unit','点','--tolerance','1')
    run('financial_rigor.py','verify-valuation','--price',p,'--eps',eps,'--bvps',ref/pb)
    run('financial_rigor.py','three-scenario','--price',p,'--eps',eps,'--shares','1','--growth',*s['growth3'],'--pe',*s['pe3'],'--years','3','--currency','指数点位（非货币股价）')
    for growth,exitpe in zip(s['growth3'],s['pe3']):
        target=eps*(1+D(growth))**3*D(exitpe)
        v['scenarios3'].append(dict(growth=growth,pe=exitpe,target=str(target),change_pct=str((target/p-1)*100)))
    run('terminal_value.py','audit','--currency','CNY','--r','.08','--roic',s['roic'],'--g','0,.01,.01','--rf','.02','--beta','1','--discrete-risks','出口限制:情景,信用冲击:情景,极端流动性冻结:未建模')
    anchors=[]
    for growth,g in zip(s['growth10'],[0,.01,.01]):
        profit=eps*(1+D(growth))**10
        for r in (.08,.10):
            ep=tv.exit_pe(s['roic'],g,r)[0]
            run('terminal_value.py','pe','--roic',s['roic'],'--g',g,'--r',r)
            run('terminal_value.py','irr','--profit',profit,'--mcap',p,'--pe',ep,'--years','10','--payout',s['k'])
            irr=tv.irr_from_terminal(float(profit),float(p),ep,10,s['k'])*100
            if r==.10: anchors.append(irr)
            else: v['terminal'].append(dict(growth=growth,g=g,pe=ep,approx_annual_return_pct=irr))
    cfg[name]=dict(roic=s['roic'],g=[0,.01,.01],p=[.3,.5,.2],irr10=anchors,k=s['k'])
    run('terminal_value.py','flip','--name',name,'--roic',s['roic'],'--g','0,.01,.01','--p','.3,.5,.2','--irr10='+','.join(map(str,anchors)),'--k',s['k'],'--r','.08','--delta','.02','--currency','CNY','--rf','.02')
    for r in (.06,.08,.10):
        ev=tv.evaluate(cfg[name],r)
        v.setdefault('sensitivity',{})[str(r)]={'mean_pct':ev['mean']*100} if 'mean' in ev else ev
    out[name]=v

run('financial_rigor.py','cross-validate','--field','沪深300官方9月PE','--values',json.dumps({'中证单张':13.15,'中证上证报联合月报（同源复核）':13.15}),'--unit','倍','--tolerance','1')
run('financial_rigor.py','calc','--expr','13.92+12.82+8.88')
run('financial_rigor.py','calc','--expr','28.61+27.82+25.97')
(HERE/'snapshot.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'calculations.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'terminal-config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'validation.txt').write_text('\n\n'.join(log),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
