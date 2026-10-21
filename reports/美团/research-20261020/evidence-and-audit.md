# 美团研究证据与审计边界

研究日：2026-10-20 Asia/Shanghai，启动时执行 `date` 得到 2026-10-20 01:26:59 CST。正文为独立研究，不复制历史报告。

## 核验文件

| 证据 | 已打开的来源 | 定位与用途 |
|---|---|---|
| 2025年度财务 | https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0424/2026042400179.pdf | p6五年收入、毛利及归母净利；p8、30集团及分部利润；p219现金流 |
| 2026上半年 | https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0929/2026092900007.pdf | p4–7收入与分部；p23–25调整项目；p30–35董事权益；p44不同投票权；p58–59现金与债务；p64–65现金流；p110债务 |
| 2022年度及2021比较期 | https://www1.hkexnews.hk/listedco/listconews/sehk/2023/0424/2023042400042.pdf | p28经营利润；p198现金流及资本开支 |
| 2023年度 | https://www.hkexnews.hk/listedco/listconews/sehk/2024/0429/2024042900115.pdf | 经营利润134.15387亿元 |
| 2025Q3 | https://www1.hkexnews.hk/listedco/listconews/sehk/2025/1128/2025112800483.pdf | p1分部、p12净亏损 |
| 最新股本 | https://www1.hkexnews.hk/listedco/listconews/sehk/2026/1007/2026100700730.pdf | p2 B股5,596,355,247、A股579,152,986，库存股零 |
| 独立财务数据 | https://stockanalysis.com/quote/hkg/3690/financials/ | S&P数据，单位百万元人民币；不可拿statistics页港元财务与人民币直接比较 |
| 独立价格/股本 | https://stockanalysis.com/quote/hkg/3690/history/ ； https://ms.investing.com/equities/meituan-dianping-historical-data ； https://companiesmarketcap.com/meituan-dianping/shares-outstanding/ | 2026-10-16收盘75.70；第三方股本6,174,383,320 |

FinancialFilings中报镜像曾用于检索，最终用HKEX原文逐项对照。镜像与HKEX不是独立双源。AASTOCKS基本面页访问失败，转用其业绩新闻和StockAnalysis；未把失败访问说成核验完成。

## 审计执行与结果

`model.py` 是输入和Decimal计算的单一文件，生成 `model-output.json` 与 `financial-rigor.txt`。市值、收入、归母净利、现金理财与股本运行金融严谨性工具；负PE只能做算术，不应作为有效估值指标。FCFF情景是假设，不能从模型正常运行推断其真实。

`report_audit.py extract --seed 42` 从114个候选点抽18项。人工复核发现1项把2025年份识别为财务值，保留原样并排除。其余17项与已打开原始报表核对；10项同时有独立StockAnalysis展示值，7项仅核到原始披露，未伪造第二源。公式派生的毛利率、季度差额、债务合计，以已核验原始数字复算，不是另一个独立事实来源。

工具verdict对有值项目给出17通过、0警告、0失败；这是**PARTIAL_DUAL_SOURCE / LIMITED_SCOPE**，不能理解为整篇所有数据完成双源准出。工具本身允许单源和跳过项，本记录明确收窄其“可发布”措辞。原始抽样、填值和输出分别保存在audit-extract.txt、audit-results.json、audit-verdict.txt。

尚未解决：季度分部的独立第三方逐项核对；历史2023现金流及部分年度现金理财的精确第二源；逐城订单单位经济；真正可分配现金余额。上述缺口限制结论强度，但不影响报告已明确列示的集团IFRS报表与市场价格事实。管理层持股第三方报道日期与基金会口径不同，报告未称其精确双源一致。

## 需要维护的模型约定

- 港币市值换成人民币：乘0.8525；人民币价值换每股港元：除股数、再除0.8525。
- 金融债务887.01255亿元；租赁作为经营成本，不在FCFF桥重复扣除。
- 300亿元经营现金储备是研究假设，不是已披露事实；不计受限现金。
- 未来FCFF已扣经济SBC，不再另扣同额稀释；回购不额外叠加到DCF。
- 三种情景均为未来十个完整年度期间，不把不完整2026年与完整年度混合；终值占经营价值约六成，预测风险显著。

## 最终模型补充

基准首期与第五期新增损益到FCFF数字桥及Decimal断言：200×75%+60−90−20=100亿元；640×75%+100−110−20=450亿元。EBIT含经济SBC与完整租赁成本，折旧只加回非租赁折旧。均为研究假设，非公司指引，不纳入事实双源PASS。financial_rigor calc小数表达式存在浮点尾差，主模型字符串构造Decimal结果为正文依据；工具输出的精度措辞不代表已证明全部数值没有任何实现限制。
