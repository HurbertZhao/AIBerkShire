"""Audit observed facts separately from arithmetic and subjective assumptions."""
from decimal import Decimal as D
from pathlib import Path
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import report_audit as ra
import terminal_value as tv

report=HERE/'沪深300创业板指科创50研究报告-20261022.md'
sample=ra.sample_points(ra.extract_data_points(report.read_text(encoding='utf-8')),ratio=.15,seed=42)
calc=json.loads((HERE/'calculations.json').read_text(encoding='utf-8'))
cfg=json.loads((HERE/'terminal-config.json').read_text(encoding='utf-8'))
U={
 'csi':'https://cn.investing.com/indices/csi300-historical-data',
 'cyb':'https://cn.investing.com/indices/chinext-price-historical-data',
 'star':'https://cn.investing.com/indices/sse-star-50-historical-data',
 'choice':'https://fund.eastmoney.com/a/202610223904049940.html',
 'quarter':'https://finance.eastmoney.com/a/202609303887802159.html',
 'cnipdf':'https://www.cnindex.com.cn/html2pdf/preview/jj_399006.pdf',
 'csipdf':'https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/zh_CN/000688factsheet.pdf',
}
verification={
4:(4036.30,U['csi'],4036.30,'https://www.etf.run/index/SSE/000300','观测值双页'),
5:(2576.90,U['choice'],2576.90,U['cyb'],'观测值双页'),
12:(1530.01,U['quarter'],1530.01,U['star'],'观测值双页'),
15:((D('1305.87')/D('1530.01')-1)*100,'基于已读取两日期行情重新计算；'+U['star'],None,'','算术复核'),
14:((D('2576.90')/D('3135.28')-1)*100,'基于已读取两日期行情重新计算；'+U['cyb'],None,'','算术复核'),
18:(sum(map(D,['1305.87','1343.28','1342.42','1329.19','1358.65']))/5,'五日行情重新求均值；'+U['star'],None,'','算术复核'),
29:(5.2,U['cnipdf'],None,'未取得独立同口径二源','一手值；二源缺口'),
32:(.27,U['csipdf'],None,'未取得独立同口径二源','一手值；二源缺口'),
36:(D('1.36')*D('4036.30')/D('4357.62'),'官方月末PB与行情代入粗略外推公式',None,'','算术复核；非当日真实估值验证'),
55:(15,'研究者基准假设；仅核对参数抄录',None,'','假设参数，非事实数据'),
70:(sum(v['irr']*p for v,p in zip(tv.evaluate(cfg['创业板指'],.06),[.3,.5,.2])),'terminal-config.json与terminal_value.py独立重新调用',None,'','条件模型算术，非未来收益验证'),
76:(4111.93,'前日收盘取整构造观察位；'+U['csi'],None,'','价位规则构造，非支撑有效性验证'),
82:(1343.28,'前日收盘取整构造观察位；'+U['star'],None,'','价位规则构造，非支撑有效性验证'),
}
for item in sample:
    a,b,c,d,e=verification[item['id']]
    item.update(fetched_value=float(a),fetched_source=b,fetched_value2=c,fetched_source2=d,verification_scope=e)
(HERE/'audit-results.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2),encoding='utf-8')
p=subprocess.run([sys.executable,str(ROOT/'tools/report_audit.py'),'verdict','--results',json.dumps(sample,ensure_ascii=False),'--report',report.name],capture_output=True,encoding='utf-8')
(HERE/'audit-verdict.txt').write_text(p.stdout+'\nSCOPE: Two official metrics still lack independent second sources; assumptions and calculated outputs are only transcription/arithmetic checks, not external validation.\n',encoding='utf-8')
print(p.stdout)
for name,s in cfg.items():
    args=[sys.executable,str(ROOT/'tools/terminal_value.py'),'audit','--currency','CNY','--r','.08','--roic',str(s['roic']),'--g','0,.01,.01','--rf','.02','--beta','1','--discrete-risks','出口限制:情景,信用冲击:情景,极端流动性冻结:未建模']
    q=subprocess.run(args,capture_output=True,encoding='utf-8')
    with (HERE/'audit-verdict.txt').open('a',encoding='utf-8') as f: f.write('\nFINAL PARAMETER AUDIT '+name+'\n'+q.stdout)
    if q.returncode: raise RuntimeError(q.stdout)
if p.returncode: raise RuntimeError(p.stdout)
