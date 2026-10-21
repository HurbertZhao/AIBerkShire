# 理想汽车研究附件

研究日期：2026-10-21；正文：[../理想汽车研究报告-20261021.md](../理想汽车研究报告-20261021.md)。

| 文件 | 内容 |
|---|---|
| `model.py` | Decimal 计算：市值、滚动四季指标、现金桥、反向估值、三年三情景（2028年末）、十年压力测试（r=6%至10%网格）。运行 `python3 reports/理想汽车/research-20261021/model.py` 会重写 `inputs.json` 与 `results.json` |
| `inputs.json` | 全部输入及单位、日期；情景参数逐项列明（均为研究假设） |
| `results.json` | 模型输出（金额单位人民币亿元，每股价值单位港元/美元） |
| `financial-rigor.txt` | `financial_rigor.py` 的 verify-market-cap / cross-validate / calc / verify-valuation / three-scenario 输出，以及 `terminal_value.py` 的 audit / pe / irr / flip 输出与口径说明 |
| `audit-extract.txt` | `report_audit.py extract --seed 42` 原始输出：163个可提取点抽25个 |
| `audit.py` | 复现同一抽样，填入核验值与来源，模型假设类单独归类，调用 `report_audit.py verdict` |
| `audit-classified.json` | 25个抽样点的逐项分类与来源 |
| `audit-verdict.txt` | 判决：进入判决18项全部通过，【准出】 |
| `sources.md` | 来源 URL、访问日期、定位与缺口 |

## 核验边界

- 抽检25点中，18个事实项进入判决（17项双来源、1项单一第三方来源：小鹏市销率），6个模型假设或行动条件、1个年份误识别单独归类，不作外部事实核验。
- 双来源里多数是“公司原件 + StockAnalysis 或 SEC XBRL 结构化数据”。XBRL 来自同一份20-F，严格说与原件不是完全独立；技能规范的主数据源 macrotrends 本轮返回403，未能访问。
- 2025年四季度自由现金流用两份公司公告互核，StockAnalysis 该季资本开支（25.70亿元）与公司公告（10.54亿元）不符，未采用；StockAnalysis 2026年二季度车辆销售收入也填错，正文已提示。
- 十年压力测试以 `model.py` 直接法为准；`flip` 工具因把净现金当作随 r 重估的利润，在低 r 时高估回报，差异记录在 `financial-rigor.txt` 末尾。

## 单一来源与缺口

- 行业数据（乘联会9月及1至9月零售）、同行9月交付、同行市销率：单一第三方来源。
- 中债10年期收益率1.68%（10月10日）：单一转载来源，仅用于 audit 的币种匹配检查。
- 汇率为 Yahoo 10月16日收盘参考价，不是可成交报价。
- 第三季度现金流未公布；6月末之后只扣除了按港交所月报表逐笔加总的回购。
- B类股4月和7月两次转换为A类的原因，本轮读取的原件未披露。
- 海外收入、分车型毛利、芯片子公司财务无单独披露。

本轮未读取或引用仓库内旧的理想汽车报告；未修改其他目录；未做任何 git 操作。
