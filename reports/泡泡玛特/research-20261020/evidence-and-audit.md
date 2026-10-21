# 泡泡玛特研究证据与审计范围

研究开始日期由 `date` 实测：2026-10-20 01:35:45 CST。股价固定2026-10-16收盘，10月19日港股休市。网页可能后来展示10月20日行情，本报告不使用晚于研究时刻的行情替换已核实的统一价格。

## 已打开并用于取数的证据

| 材料 | URL | 定位与内容 |
|---|---|---|
| 2025年报 | https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0421/2026042100394.pdf | p6五年收益；p19地区；p27–29 IP与形态；p34完整capex；p225–226现金流；p342 SBC |
| 2024年报 | https://www1.hkexnews.hk/listedco/listconews/sehk/2025/0423/2025042300687.pdf | p195–196核对2023与2024现金流、PPE与无形资产购买 |
| 2026中报 | https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0924/2026092400544.pdf | p16地区；p25 IP；p31调整项目；p32库存与资金；p45股权穿透；p63–70损益/余额/现金流；p83–84分部 |
| 2026Q1业务更新 | https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0512/2026051200579.pdf | p1同比区间，不含完整单季财务 |
| 2026年9月股本 | https://www1.hkexnews.hk/listedco/listconews/sehk/2026/1006/2026100601443.pdf | p2已发行1,331,779,203、库藏股零；授权股数5bn不可用于市值 |
| 最近奖励计划 | https://www1.hkexnews.hk/listedco/listconews/sehk/2026/1015/2026101501003.pdf | 已授奖励不等于已新增发行 |
| 独立财务数据 | https://stockanalysis.com/quote/hkg/9992/financials/ | S&P，单位RMB million；经营利润有重分类，不能强行双源配对 |
| 独立现金流表 | https://stockanalysis.com/quote/hkg/9992/financials/cash-flow-statement/ | 其FCF仅减PPE，缺无形资产；TTM SBC栏仍显示年度数，采用原件重构TTM |
| 价格 | https://stockanalysis.com/quote/hkg/9992/history/ 和 https://br.investing.com/equities/pop-mart-international-group-historical-data | 10月16日142.20港元，开盘145.90，收盘价双入口一致 |
| 独立报道 | https://companies.caixin.com/2026-08-20/102476226.html | 收入171.73亿、归母50.38亿、国内+47.3%、海外-11.1%、亚太-9.7%、美洲-16.5%；管理层解释不是独立事实证明 |
| 股本再传播 | https://www.itiger.com/hans/news/1132172554 | 与月报一致，但其来自同一披露，不冒充独立登记验证 |

HKEX和公司IR是同一披露来源。Caibao镜像只帮助检索，最终回到HKEX原件，不计独立第二来源。AASTOCKS指定财务入口与Macrotrends入口访问失败。部分新闻页面只能取到导航，未把导航页算作核验完成。

## 计算约定与检查

`model.py` 内嵌事实输入和明确假设，所有主模型计算使用字符串构造Decimal，生成 `model-output.json`。金额用人民币十亿元，股本用十亿股；展示亿元时乘10。`financial-rigor.txt`保存规定工具执行。

工具边界需注意：financial_rigor的cross-validate默认对中位数且宽容差，不能替代本研究独立两源的直接差异检查。1.331779203bn对供应商舍入1.31bn直接差约1.66%，因此仍是未解决股本口径差；本报告使用官方总发行股数，未把工具绿色输出宣传成双源PASS。工具calc对小数表达式出现6.052085999999999的浮点尾差，主模型Decimal的6.052086是正文依据。本次没有修改共享工具。

FCFE已扣税、完整租赁、完整capex、营运资本、经济SBC和少数股东归属；非经营现金利息排除后才加剩余现金。现金桥139.71914亿减经营现金30亿及少数权益代理2.29451亿，得107.42463亿；后两项不是公开事实的精确可分配余额。半年末至研究日余额缺口明确披露。未来回购、股息不另叠加DCF。十年利润、现金桥、折现率与安全边际均为假设。

基准第1/5期归母经营利润→FCFE分别110+8−18−30=70亿、150+10−20−20=120亿，Decimal断言勾稽；不是预测真实度测试。

## 随机抽检与判决解释

最终 `report_audit.py extract` 默认15%随机抽样，从131个候选抽20项，原始清单保存在audit-extract.txt。13项为事实或基于披露的算术，其中7项有独立第二发布者、6项仅单发布者；13项实际取数后偏差均低于1%。另1项是2025年份误提取，保留记录并排除；6项为估值算术或模型假设，仅复算并在audit-dispositions.json记录，没有给它们填同值伪造事实通过。

`audit-verdict.txt`工具显示13通过、0警告、0失败，其“可发布”通用措辞仅适用于已填事实项目。本研究状态为 **PARTIAL_DUAL_SOURCE / LIMITED_SCOPE**。这不是全部131项独立双源审计，更不是对护城河或未来利润的审计背书。

未解决项目：股本供应商口径；2021–2022 CFO及早期流动资产细项的完整独立双源；IP合约全文与受益信托条款；季度完整利润/现金报表；海外同店、库龄及用户队列；6月底至研究时现金变动。报告据此采用条件结论，未用旧报告填补当前证据。
