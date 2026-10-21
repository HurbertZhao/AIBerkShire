from pathlib import Path
import json,importlib.util,contextlib,io,re
from decimal import Decimal as D
p=Path('reports/快手/快手可灵深度研究-20261016')
spec=importlib.util.spec_from_file_location('audit','tools/report_audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
report=p/'快手与可灵深度研究报告-20261016.md'
points=a.extract_data_points(report.read_text());samples=a.sample_points(points,ratio=.15,seed=20261016)
f=json.loads((p/'financial_facts.json').read_text());m=json.loads((p/'利润与估值模型.json').read_text());S=f['sources']
model='利润与估值模型.py / 利润与估值模型.json；假设与算式，不是外部事实验证'
mapping={
1:('fact','692.51',S['interim_2026']+' p57',None,'','半年收入公司原件；未强称独立第二源'),
14:('fact','58.78','https://ir.kuaishou.com/news-releases/news-release-details/kuaishou-technology-announces-third-quarter-2025-unaudited',None,'','季度细分单源'),
16:('fact','55.81','https://ir.kuaishou.com/node/11461/pdf',None,'','季度细分单源'),
106:('fact','116.96',S['interim_2026']+' p59','116.96',S['secondary_balance'],'现金等价物'),
35:('assumption','40',model,None,'','演示成功率，非实测'),
60:('calculation',D(1050)+D(290)+D(410),model,None,'','2031主业收入加总'),
69:('assumption','120',model,None,'','2031可灵收入假设'),
76:('calculation',D(300)*D('.2'),model,None,'','可灵独立利润'),
83:('assumption','4',model,None,'','集团增量费用假设'),
86:('calculation',D(1590)*D('.14')+D(70)*D('.08')*D('.68')-D(4),model,None,'','2029归母独立Decimal复算'),
92:('assumption','60',model,None,'','悲观2036可灵收入假设'),
105:('calculation',D(3100)*D('.2')+D(1000)*D('.28')*D('.6')-D(15),model,None,'','乐观2036归母复算'),
114:('assumption','-150','模型市场输入.json',None,'','研究缓冲而非法定受限资金'),
121:('assumption','15',model,None,'','2036融资成本加回假设'),
122:('assumption','90',model,None,'','2029非现金净加回假设'),
132:('calculation',(D('266.86')+D(15)+D(105)-D(195)-D(42)).quantize(D(1)),model,None,'','2031现金桥梁取整'),
135:('assumption','15',model,None,'','悲观折现率假设'),
136:('calculation',m['valuations']['bear']['price_hkd'],model,None,'','模型DCF输出并经独立审读'),
141:('assumption','11',model,None,'','乐观折现率假设')}
excluded={144:'年份误提取，非财务数',26:'7月2日月份误提取；任职已于治理证据核验',43:'Seedance版本号；已于技术证据核验',45:'Wan版本号；已核实预览边界'}
rows=[]
for s in samples:
 x=dict(s)
 if s['id'] in excluded:x.update(kind='nonfinancial_extraction',fetched_value=None,fetched_source='',note=excluded[s['id']])
 else:
  k,v,src,v2,src2,n=mapping[s['id']]
  x.update(kind=k,fetched_value=float(v),fetched_source=src,fetched_value2=float(v2) if v2 is not None else None,fetched_source2=src2,note=n)
 rows.append(x)
assert len(rows)==23 and len(mapping)+len(excluded)==23
(p/'抽检分类与核验.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
crit=[]
def add(label,rv,fv,src,v2=None,src2='',note=''):
 crit.append(dict(id=1000+len(crit),label=label,reported_value=float(rv),unit='亿元或注明单位',fetched_value=float(fv),fetched_source=src,fetched_value2=float(v2) if v2 is not None else None,fetched_source2=src2,note=note,kind='critical_fact_or_calculation'))
for label,v in [('2025收入','1427.76'),('2025归母','186.17')]:add(label,v,v,S['annual_2025'],v,S['secondary_income'])
for label,v in [('2025CFO','267.16'),('2025资本支出','149.42')]:add(label,v,v,S['annual_2025'],v,S['secondary_cashflow'])
add('2026H1资本支出','179.41',D(f['interim_and_ttm'][1]['capex'])/100,S['interim_2026']+' p63',note='单一原件，未制造双源一致')
add('TTM归母','157.66',D('186.17')-D('89')+D('60.49'),S['annual_2025']+' + '+S['interim_2026'],note='滚动计算')
add('TTM简单FCF','-18.29',D('267.16')-D('117.81')+D('90.44')-(D('149.42')-D('70.75')+D('179.41')),S['annual_2025']+' + '+S['interim_2026'],note='拒绝数据库陈旧资本支出')
add('2026H1供应商融资总负债','252.53',D(f['balance_2026_06_30']['supplier_arrangement_total_liability'])/100,S['interim_2026']+' p100',note='单一原始注释')
add('收盘价HKD','28.58','28.58',S['price_1'],'28.58',S['price_2'])
add('已发行股本_股','4304151598',D('3644802646')+D('659348952'),S['share_return'],'4330000000','S&P/StockAnalysis舍入股数',note='采用较新HKEX月报，不取平均')
add('HKDCNY','.85702',D('85.702')/100,S['fx_primary'],'.85702',S['fx_secondary'])
add('市值_亿港元','1230.13',D('28.58')*D('43.04151598'),S['price_1']+' + '+S['share_return'],'1236.6',S['price_2'],note='第三方股数滞后约0.53%，容差内仍采用原件')
add('保守净资金模型_非实时现金','102.08',D('116.96')+D('123.58')+D('563.53')-D('273.62')-D('252.53')-D('25.84')-D('150'),S['interim_2026']+' + 模型150亿元缓冲',note='事实+假设计算，非公司披露可分配现金')
(p/'重点复核.json').write_text(json.dumps(crit,ensure_ascii=False,indent=2)+'\n')
verdicts={};outputs=[]
for name,items in [('随机抽样事实',[x for x in rows if x['kind']=='fact']),('假设和算式一致性',[x for x in rows if x['kind'] in ('assumption','calculation')]),('重点事实与桥梁',crit)]:
 b=io.StringIO()
 with contextlib.redirect_stdout(b):v=a.render_verdict(items,report.name+' / '+name)
 assert v['fail_count']==0 and v['warn_count']==0
 verdicts[name]=v;outputs.append(re.sub(r'\x1b\[[0-9;]*m','',b.getvalue()))
(p/'审计判决.txt').write_text('\n'.join(line.rstrip() for line in '\n'.join(outputs).splitlines())+'\n')
(p/'审计判决.json').write_text(json.dumps({'sample_total':len(rows),'excluded_nonfinancial':len(excluded),'scopes':verdicts,'warning':'PASS only within declared fact/formula scopes; not prediction validation; single-source gaps remain'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'points':len(points),'sampled':len(rows),'verdicts':verdicts},ensure_ascii=False))
