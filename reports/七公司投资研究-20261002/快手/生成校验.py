"""Reproducible tables and financial_rigor logs for both reports. No network."""
from pathlib import Path
from decimal import Decimal as D
import json,subprocess,shutil
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).parent.parent
FX=D('0.85842')
def number(v,places=2):return f'{D(str(v)):,.{places}f}'
for company,code,bank in [('快手','1024',[45457,35620,49018,51640,62256]),('美团','3690',[116795,112032,145160,168243,166834])]:
    p=BASE/company;d=json.loads((p/'计算结果.json').read_text());report=p/f'{company}研究报告-20261002.md';text=report.read_text()
    a='| 年度 | 收入 | 归母净利润 | CFO | 资本支出 | 简单FCF | CFO/归母 | FCF/归母 | 现金及短期投资 |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|'
    for row,cash in zip(d['annual'],bank):
        vals=[number(D(row[k])/100) for k in ['revenue','profit','cfo','capex','fcf']]
        a+='\n| '+str(row['year'])+' | '+' | '.join(vals)+f" | {number(row['cfo_profit'])} | {number(row['fcf_profit'])} | {number(D(cash)/100)} |"
    t='| 情景 | 今日DCF现值，港元 | 三年后价格，港元 | 三年累计股息，港元 | 三年总回报 | 简单年化 | 三年财富折回今日，港元 |\n|---|---:|---:|---:|---:|---:|---:|'
    for key,cn in [('bear','悲观'),('base','基准'),('bull','乐观')]:
        s=d['scenarios'][key]
        t+=f"\n| {cn} | {number(s['price'])} | {number(s['year3_price_HKD'])} | {number(D(s['annual_dividend_HKD'])*3)} | {D(s['three_year_total_return'])*100:+.2f}% | {D(s['three_year_annual_return'])*100:+.2f}% | {number(s['year3_discounted_wealth_HKD'])} |"
    text=text.replace('{{ANNUAL}}',a).replace('{{SCENARIOS}}',t)
    text=text.replace('模型为股权现金DCF','模型为归属经营现金DCF').replace('模型对股权可分配现金折现','模型对归属经营现金折现')
    text=text.replace('现金流已在税、利息、租赁付款、必要资本开支和股权薪酬经济成本之后','现金流为税后、金融借款利息前，已扣租赁付款、必要资本开支和股权薪酬经济成本')
    text=text.replace('现金在税、利息、租赁付款、维持与增长资本开支、股权薪酬经济成本之后','现金流为税后、金融借款利息前，已扣租赁付款、维持与增长资本开支和股权薪酬经济成本')
    text=text.replace('归母可分配现金','归属经营现金').replace('可分配现金要求','归属经营现金要求')
    if '金融债务本金在资产桥扣除一次' not in text: text=text.replace('折现率11%，永续增长2%。','经营资本折现率11%，永续增长2%。金融债务本金在资产桥扣除一次；未来现金流不再扣其利息，避免把企业与股权现金模型混用。历史CFO与租赁、利息后现金余量仅作质量检查，非未经调整的预测起点。')
    if '金融债务本金在资产桥扣一次' not in text: text=text.replace('r为11%。','经营资本折现率r为11%。金融债务本金在资产桥扣一次，预测现金不重复扣金融利息；历史CFO与租赁、利息后现金余量用于质量检查，不直接等于预测现金口径。')
    text=text.replace('三年总回报”含股息、未再投资，不含税费。','三年总回报”含股息、未再投资，不含税费；简单年化为期末财富倍数换算，不是IRR。')
    text=text.replace('三年财富折回今天与完整DCF略有差异','股息按第一、二、三年逐笔折现，期末股价按第三年折现；三年财富折回今天与完整DCF略有差异')
    report.write_text(text)
    evidence=p/'证据';evidence.mkdir(exist_ok=True)
    shutil.copyfile('/tmp/km-quote-20261002.txt',evidence/'腾讯行情-20261002-GB18030.txt')
    commands=[]
    def add(*args):
        args=list(args)
        if args[0]=='calc' and args[1]=='--expr': args=['calc','--expr='+args[2]]
        commands.append(['python3',str(ROOT/'tools/financial_rigor.py'),*args])
    price=d['market_price_HKD'];shares=D(d['shares_m'])*1000000
    add('verify-market-cap','--price',price,'--shares',str(shares),'--reported','127316770000' if code=='1024' else '433519030000','--currency','HKD')
    values=[('股价',{'腾讯行情':float(price),'StockAnalysis':float(price)},'HKD'),('总股本',{'披露汇总与采用值':float(shares),'腾讯行情':4304150498 if code=='1024' else 6175484800},'股')]
    if code=='1024':
        values += [('2025收入',{'公司年报':142776,'StockAnalysis':142776},'CNY百万'),('2025归母',{'公司年报':18617,'StockAnalysis':18617},'CNY百万'),('2025现金及短期投资',{'公司表内同口径重建':62256,'StockAnalysis':62256},'CNY百万'),('2026H1现金及等价物',{'公司中报':11696,'ETnet':11696},'CNY百万'),('苏华经济权益',{'公司中报':9.88,'Infocast':9.88},'%'),('程一笑经济权益',{'公司中报':8.84,'Infocast':8.84},'%')]
        eps=D('15766')/D(d['shares_m'])/FX;fcf=D('-1829')/D(d['shares_m'])/FX
    else:
        values += [('2025收入',{'公司年报':364854.746,'StockAnalysis':364855},'CNY百万'),('2025归母',{'公司年报':-23355.015,'StockAnalysis':-23355},'CNY百万'),('2026H1现金及短期理财',{'公司中报':168314.170,'新浪财务报道':168314.170},'CNY百万'),('2026H1经营现金',{'公司中报':2719.085,'IT之家':2719},'CNY百万')]
        eps=D('-38449.146')/D(d['shares_m'])/FX;fcf=D(d['TTM']['FCF'])/D(d['shares_m'])/FX
    for label,vals,unit in values:add('cross-validate','--field',label,'--values',json.dumps(vals,ensure_ascii=False),'--unit',unit)
    add('verify-valuation','--price',price,'--eps',str(eps),'--fcf-per-share',str(fcf),'--dividend','0.69' if code=='1024' else '0')
    b=d['scenarios']['base'];add('calc','--expr',f"({b['explicit']} + {b['terminal']} + {b['assets']}) / {d['shares_m']} / 0.85842")
    if code=='1024':
        for expr in ['9044-17941','14942+17941-7075','23979-(14942+17941-7075)','80407-27362-25248-15000','32.49+33.34','9.88+8.84','20639/19765-1','8690/10044-1','6206/5237-1']:add('calc','--expr',expr)
    else:
        for expr in ['2719.085-6584.447','2719.085-6584.447-1606.666-1414.617','13270.708+6584.447-5554.202','-26000.486-(13270.708+6584.447-5554.202)','104716.797+63597.373-42138.301-46562.954-35000+30000','30000/6175.4848/0.85842','5668.275/71530.555','515871422/6174765962*100','563215264/6174765962*100']:add('calc','--expr',expr)
    log=[]
    for cmd in commands:
        result=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT)
        log.append('ARGUMENTS '+json.dumps(cmd[2:],ensure_ascii=False)+'\n'+result.stdout+result.stderr+'\nExit '+str(result.returncode))
    (p/'financial_rigor验证.txt').write_text('\n\n'.join(log))
    (evidence/'事实与限制.json').write_text(json.dumps({'date':'2026-10-02','price_timestamp':'2026-10-02 16:08 HKT delayed after close','key_cross_checks':values,'fx_CNY_per_HKD':'0.85842','fx_date':'2026-09-30','not_fully_independent':['原始公告与官网转载是同一源','新闻引述财报不是独立财务审计','管理层投票权只有公司原表加算术核验','DCF与反向DCF全部为假设的数学结果'],'cashflow_warning':'数据库部分现金流TTM列滞后，最新中报优先','share_warning':'快手腾讯行情股数与9月披露汇总相差0.53%，采用较高分母；美团两源一致','model_convention':'税后金融利息前、租赁/SBC/资本开支后归属经营现金；金融债务在现金资产桥扣一次；不另加内含AI业务估值'},ensure_ascii=False,indent=2)+'\n')
    if company=='美团':
        shutil.copyfile('/tmp/meituan-h126.txt',evidence/'美团2026中报-官方下载文本.txt')
    else:shutil.copyfile('/tmp/kuaishou-release-h126.txt',evidence/'快手2026中期业绩-官方下载文本.txt')
