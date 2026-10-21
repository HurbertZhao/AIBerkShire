import pathlib,subprocess,json
from decimal import Decimal as D
base=pathlib.Path(__file__).resolve().parent.parent
commands={
'腾讯':[
['verify-market-cap','--price','421.2','--shares','9092605595','--reported','3880000000000','--currency','HKD'],
['cross-validate','--field','2025收入','--values','{"公司原报":751766,"StockAnalysis":751766}','--unit','百万元'],
['cross-validate','--field','2025归母利润','--values','{"公司原报":224842,"StockAnalysis":224842}','--unit','百万元'],
['cross-validate','--field','2025经营利润_口径差异采用原报','--values','{"公司原报":241562,"StockAnalysis标准化":245628}','--unit','百万元'],
['cross-validate','--field','股份数_日期口径有差异采用9月30日披露','--values','{"9月30日股份变动表":9092605595,"StockAnalysis":9000000000}','--unit','股'],
['cross-validate','--field','现金口径不可混同_不能判双源一致','--values','{"公司广义现金2026H1":511154,"StockAnalysis现金短投":458904}','--unit','百万元'],
['cross-validate','--field','2025经营现金流','--values','{"年报":303052,"StockAnalysis":303052}','--unit','百万元'],
['calc','--expr','206930+304224-298942-154021'],
['calc','--expr','154061-95615-11547-3636-6408'],
['verify-valuation','--price','421.2','--eps',str(D('25.45')/D('.85842')),'--fcf-per-share',str(D('168.309')/D('9.092605595')/D('.85842')),'--dividend','5.3'],
['three-scenario','--price','421.2','--eps',str(D('24.153')/D('.85842')),'--shares','90.92605595','--growth','.13','.07','-.03','--pe','23','18','13','--years','3','--currency','HKD']],
'拼多多':[
['verify-market-cap','--price','76.5','--shares','1423396462','--reported','108890000000','--currency','USD'],
['cross-validate','--field','2025收入','--values','{"公司公告":431845.7,"StockAnalysis":431846}','--unit','百万元'],
['cross-validate','--field','2025归母利润','--values','{"2025年报":97842.539,"StockAnalysis":97843}','--unit','百万元'],
['cross-validate','--field','2026H1现金加短投','--values','{"公司公告":456414,"StockAnalysis":456414}','--unit','百万元'],
['cross-validate','--field','ADS等价股本_时点差异','--values','{"2026年3月18日20F披露换算":1423396462,"StockAnalysis四舍五入":1420000000}','--unit','ADS'],
['cross-validate','--field','2025经营现金流','--values','{"年报":106938.690,"StockAnalysis":106939}','--unit','百万元'],
['calc','--expr','128918+327496-2455-2389'],
['calc','--expr','106938.690-1145.077'],
['verify-valuation','--price','76.5','--eps',str(D('62.26')/D('6.7351')),'--fcf-per-share',str(D('105793.613')/D('1423.396462')/D('6.7351')),'--dividend','0'],
['three-scenario','--price','76.5','--eps',str(D('92076')/D('1480')/D('6.7351')),'--shares','14.8','--growth','.12','.05','-.10','--pe','15','11','7','--years','3','--currency','USD']]
}
for co,cmds in commands.items():
 if co != pathlib.Path(__file__).resolve().parent.name: continue
 out=[]
 for args in cmds:
  p=subprocess.run(['python3','tools/financial_rigor.py']+args,capture_output=True,text=True)
  out.append('$ python3 tools/financial_rigor.py '+' '.join(args)+'\n'+p.stdout+p.stderr)
 (base/co/'financial-rigor.txt').write_text('\n\n'.join(out))
 print(co,len(cmds),'checks written')
