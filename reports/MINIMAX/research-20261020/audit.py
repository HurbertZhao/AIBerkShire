from pathlib import Path
import json,sys,subprocess,re
from decimal import Decimal as D
P=Path(__file__).resolve().parent;root=P.parents[2]
sys.path.insert(0,str(root/'tools'));import report_audit
report=P.parent/'MiniMax研究报告-20261020.md';pts=report_audit.sample_points(report_audit.extract_data_points(report.read_text()),ratio=.15,seed=42)
a='https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0422/2026042202118.pdf';b='https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0930/2026093002173.pdf';p='https://www1.hkexnews.hk/listedco/listconews/sehk/2025/1231/2025123100025.pdf';s='https://stockanalysis.com/quote/hkg/0100/financials/'
verified={4:(-.854,p+' financial summary',-.85,s),5:(3.738,a+' financial summary',3.74,s),14:(-1871.617,a+' financial summary',-1872,s),12:(-269.246,p+' financial summary',-269.25,s),15:(-12.150,a+' four-year financial summary',None,''),18:(-250.856,a+' non-IFRS reconciliation',None,''),29:(float(D('-258.483')-D('.759')),p+' I-14 cash flow CFO minus purchases',-259.24,s+'cash-flow-statement/'),32:(30.429,b+' p6',None,''),36:(20.813,b+' p6',None,''),55:(24.031,a+' cash flow and non-IFRS reconciliation',24.03,s+'cash-flow-statement/')}
model_ids={70,76,82,87};facts=[];classes=[];outputs=json.loads(P.joinpath('results.json').read_text())
model_expected={70:D(outputs['scenarios']['bear']['NI_2036_bn']),76:D('50'),82:D(outputs['scenarios']['bear']['value_per_share_hkd']),87:D(outputs['scenarios']['bull']['conditional_IRR_at_current_price'])*100}
for x in pts:
 if x['id'] in model_ids:
  v=model_expected[x['id']];assert abs(D(str(x['reported_value']))-v)<D('.0051')
  x.update(classification='MODEL_ASSUMPTION_OR_DERIVATION',external_fact_verification=False,fetched_value=None,model_recomputed_value=str(v),note='Inputs and Decimal outputs consistent; not an externally verified fact');classes.append(x);continue
 v,src,v2,src2=verified[x['id']];x.update(fetched_value=v,fetched_source=src,fetched_value2=v2,fetched_source2=src2,classification='FACT_DUAL_SOURCE' if v2 is not None else 'FACT_SINGLE_SOURCE');facts.append(x);classes.append(x)
P.joinpath('audit-classified.json').write_text(json.dumps(classes,ensure_ascii=False,indent=2)+'\n');P.joinpath('audit-facts.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
z=subprocess.run(['python3',str(root/'tools/report_audit.py'),'verdict','--results',json.dumps(facts,ensure_ascii=False),'--report',report.name,'--output-json'],capture_output=True,text=True);P.joinpath('audit-verdict.txt').write_text(re.sub(r'\x1b\[[0-9;]*m','',z.stdout+z.stderr));print(z.returncode,z.stdout[-1300:])
