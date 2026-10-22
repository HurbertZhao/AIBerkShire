from decimal import Decimal as D
from pathlib import Path
import subprocess,json,sys,importlib.util
ROOT=Path('/workspace/AIBerkShire'); W=Path('/workspace/work')
def make(c):
 out=W/c['work'];out.mkdir(exist_ok=True,parents=True);logs=[]; data={}
 def run(tool,*args):
  args=[str(x) for x in args];p=subprocess.run([sys.executable,str(ROOT/'tools'/f'{tool}.py'),*args],capture_output=True,text=True)
  logs.append('$ python3 tools/'+tool+'.py '+' '.join(args)+'\n'+p.stdout+p.stderr)
  if p.returncode: raise RuntimeError(logs[-1])
  return p.stdout
 price=D(c['price']);shares=D(c['shares']);n=shares/D(10)**8;mcap=price*n
 data['shares_yi']=str(n);data['mcap_yi']=str(mcap)
 run('financial_rigor','verify-market-cap','--price',price,'--shares',shares,'--reported',c['reported_mcap'],'--currency','CNY')
 for x in c['cross']:
  run('financial_rigor','cross-validate','--field',x['field'],'--values',json.dumps(x['values'],ensure_ascii=False),'--unit',x['unit'])
 eps=D(c['profit26'])/n
 run('financial_rigor','three-scenario','--price',price,'--eps',eps,'--shares',n,'--growth',*c['growth'],'--pe',*c['pe'],'--years','3','--currency','CNY')
 data['scenarios']=[]
 for name,g,pe in zip(['乐观','基准','悲观'],c['growth'],c['pe']):
  profit=D(c['profit26'])*(1+D(g))**3;target=profit*D(pe)/n;pv=target/(D('1.08')**3)
  data['scenarios'].append(dict(name=name,profit=str(profit),price=str(target),pv=str(pv),safety75=str(pv*D('.75'))))
 run('financial_rigor','verify-valuation','--price',price,'--eps',D(c['ttm_profit'])/n,'--bvps',D(c['equity'])/n)
 data['pe_ttm']=str(mcap/D(c['ttm_profit']));data['pe26']=str(mcap/D(c['profit26']));data['pb']=str(mcap/D(c['equity']))
 for label,expr in c.get('exprs',{}).items():
  data[label]=run('financial_rigor','calc','--expr',expr)
 risks=c['risks'];roic=float(c['roic']);gs=[float(x) for x in c['g']];k=float(c['k'])
 run('terminal_value','audit','--currency','CNY','--r','.08','--roic',roic,'--g',','.join(c['g']),'--rf','.02','--beta','1','--discrete-risks',risks)
 spec=importlib.util.spec_from_file_location('tv',ROOT/'tools/terminal_value.py');tv=importlib.util.module_from_spec(spec);spec.loader.exec_module(tv)
 irs=[];data['terminal']=[]
 for profit,g in zip(c['profits36'],gs):
  pe10=(1-g/roic)/(.10-g);pe8=(1-g/roic)/(.08-g)
  for r,pe in [(.10,pe10),(.08,pe8)]:
   run('terminal_value','pe','--roic',roic,'--g',g,'--r',r)
   run('terminal_value','irr','--profit',profit,'--mcap',mcap,'--pe',pe,'--years',10,'--payout',k)
  irs.append(tv.irr_from_terminal(float(profit),float(mcap),pe10,10,k)*100)
  data['terminal'].append(dict(profit=profit,pe=pe8,irr=tv.irr_from_terminal(float(profit),float(mcap),pe8,10,k)*100))
 conf={c['name']:dict(roic=roic,g=gs,p=c['p'],irr10=irs,k=k)}
 (out/'model.json').write_text(json.dumps(conf,ensure_ascii=False,indent=2))
 data['flip']=run('terminal_value','flip','--name',c['name'],'--config',out/'model.json','--r','.08','--delta','.02','--currency','CNY','--g-shift','0','--rf','.02')
 (out/'verification.txt').write_text('\n'.join(logs));(out/'calculations.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));(out/'inputs.json').write_text(json.dumps(c,ensure_ascii=False,indent=2))
 print(json.dumps(data,ensure_ascii=False,indent=2))
if __name__=='__main__':make(json.loads(Path(sys.argv[1]).read_text()))
