"""Run the shared financial_rigor CLI and preserve its exact output.
Primary values were transcribed/TTM-bridged from the cited filings; do not
interpret successful arithmetic as validation of forecast assumptions.
"""
import json, re, subprocess, sys
from pathlib import Path
from decimal import Decimal as D
from build_model import RAW, CONFIG, ORDER, calculate

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIMARY={
 'AAPL':['466823','154859','128930','146724','10041'],
 'MSFT':['331839','155237','133749','182935','115948'],
 'GOOGL':['445866','147628','244119','185675','132402'],
 'AMZN':['775680','93712','135281','161403','173028'],
 'META':['228248','86926','68098','130301','89325'],
 'NVDA':['302970','197579','192880','134360','7354'],
 'TSLA':['103619','4278','3804','18685','12923']}
MACRO_REVENUE={
 'AAPL':['416161','391035','383285'], 'MSFT':['331839','281724','245122'],
 'GOOGL':['402836','350018','307394'], 'AMZN':['716924','637959','574785'],
 'META':['200966','164501','134902'], 'NVDA':['215938','130497','60922'],
 'TSLA':['94827','97690','96773']}
MACRO_NI={
 'AAPL':['112010','93736','96995'], 'MSFT':['133749','101832','88136'],
 'GOOGL':['132170','100118','73795'], 'AMZN':['77670','59248','30425'],
 'META':['60458','62360','39098'], 'NVDA':['120067','72880','29760'],
 'TSLA':['3794','7091','14997']}
MARKET_CAP={'AAPL':'5014000','MSFT':'3902000','GOOGL':'4157000','AMZN':'2689000','META':'1791000','NVDA':'5161000','TSLA':'1388000'}

def run(args):
    cmd=[sys.executable,str(ROOT/'tools/financial_rigor.py')]+[str(a) for a in args]
    p=subprocess.run(cmd,capture_output=True,text=True,check=True)
    clean=re.sub(r'\x1b\[[0-9;]*m','',p.stdout)
    return '\n'.join(line.rstrip() for line in clean.splitlines())+'\n', cmd

if __name__=='__main__':
    manifest={}
    for t in ORDER:
        x=calculate(t); c=CONFIG[t]; raw=RAW[t]; commands=[]; blocks=[]
        tests=[['verify-market-cap','--price',x['price'],'--shares',x['shares']*1000000,'--reported',D(MARKET_CAP[t])*1000000,'--currency','USD'],
          ['verify-valuation','--price',x['price'],'--eps',raw['eps'][0],'--bvps',D(c.get('book_equity_override',raw['equity'][0]))/x['shares'],'--revenue-per-share',x['revenue']/x['shares']]]
        if x['fcf']>0: tests[-1]+=['--fcf-per-share',x['fcf']/x['shares']]
        for k,primary in zip(['revenue','operating_income','net_income','cfo','capex'],PRIMARY[t]):
            vendor=abs(D(raw[k][0])) if k=='capex' else D(raw[k][0])
            tests.append(['cross-validate','--field',f'{t} TTM {k}','--values',json.dumps({'primary_or_TTM_bridge':float(D(primary)),'StockAnalysis':float(vendor)}),'--unit','百万美元','--tolerance','1'])
        for k,series in [('revenue',MACRO_REVENUE[t]),('net_income',MACRO_NI[t])]:
            for j,m in enumerate(series,1):
                tests.append(['cross-validate','--field',f'{t} {raw["periods"][j]} {k}','--values',json.dumps({'Macrotrends':float(D(m)),'StockAnalysis':float(D(raw[k][j]))}),'--unit','百万美元','--tolerance','1'])
        # This CLI calls its input EPS and its multiple PE. Here they are a
        # synthetic NOPAT/share and EV/NOPAT; only multiplication is reused.
        tests.append(['three-scenario','--price',x['price'],'--eps',x['eps_proxy'],'--shares',x['shares']/100,'--growth',*c['eps_growth'],'--pe',*c['exit_pe'],'--years','5','--currency','USD'])
        tests.append(['calc','--expr',f"{x['cfo']} - {x['capex']} - {c['leases']} - {c.get('other_financing','0')} - {x['sbc']}"])
        for args in tests:
            output,command=run(args)
            display=['python3','tools/financial_rigor.py']+[str(a) for a in args]
            commands.append(display); blocks.append('$ '+' '.join(display)+'\n'+output)
        (HERE/f'{t}-financial-rigor.txt').write_text('\n'.join(blocks))
        manifest[t]={'primary_ttm':dict(zip(['revenue','operating_income','net_income','cfo','capex'],PRIMARY[t])),
          'macrotrends_annual_revenue':MACRO_REVENUE[t],'macrotrends_annual_net_income':MACRO_NI[t],
          'commands':commands,'boundary':'Source discrepancies are disclosed in the report. CLI output is arithmetic validation, not an investment verdict. Three-scenario output is synthetic EV/share, not GAAP EPS equity valuation.'}
    (HERE/'financial-verification.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('Wrote seven financial-rigor logs and financial-verification.json')
