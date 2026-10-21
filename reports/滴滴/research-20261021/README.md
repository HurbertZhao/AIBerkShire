# 滴滴研究附件

研究日期：2026-10-21；正文：[`../滴滴研究报告-20261021.md`](../滴滴研究报告-20261021.md)。

- `model.py`、`inputs.json`、`results.json`：Decimal 计算的市值（法定/经济两种股本口径）、历史比率、现金桥（3 月末一手快照与 6 月末二手快照两版）、分部三情景折现、折现率敏感性、国际亏损压力测试、反向估值、三年三情景、十年 IRR。运行 `python3 reports/滴滴/research-20261021/model.py`，会重写三个 JSON/文本文件。
- `financial-rigor.txt`：model.py 调用 `tools/financial_rigor.py`（verify-market-cap ×2、cross-validate ×6、verify-valuation、three-scenario、calc ×2）与 `tools/terminal_value.py`（audit 准出、pe、irr ×3、flip ±2pp 与 ±1pp）的实际输出。
- `audit-extract.txt`：`python3 tools/report_audit.py extract --report reports/滴滴/滴滴研究报告-20261021.md --seed 42` 的输出。
- `audit.py`、`audit-classified.json`、`audit-verdict.txt`：抽中 28 点，其中 9 点为情景假设、模型输出或行动条件，单独归类不进判决；19 个事实或事实推算点进入 verdict，结果【准出】。运行 `python3 reports/滴滴/research-20261021/audit.py`。
- `sources.md`：来源 URL、访问日期、定位与缺口。

## 核验边界

- 19 个判决点中 7 个有第二来源（StockAnalysis 或公司另一期公告），其余为一手原件单一来源或由原件推算。第二来源 StockAnalysis 是数据库，不是独立审计；同一公司不同期公告也不是独立来源。
- 2026Q2 数字全部是二手来源（路透、财新、Quartr、StockAnalysis），分部数字只有亿元精度；其他业务分部 Q2 缺失。
- 2021、2022 年为美国会计准则，2023 年起为 IFRS，五年表只能看方向。
- 股本：法定股本 1,126,879,059 股为 2026-03-20 单一来源（20-F），与 StockAnalysis 的 4.51 亿份 ADS 等价数一致；经济股本 1,165,462,746 股为 2026Q1 基本加权股数，单一来源。
- 现金桥用 2026-03-31 一手快照，未扣现金结算股份激励负债（金额未披露）；用 6 月末二手快照会使净余量从 193.62 亿元降到 122.15 亿元、每 ADS 价值下调约 0.23 美元。
- 情景现金流、终值增速、ROIC、股息减稀释率、经营缓冲、非核心投资折扣都是研究假设，PASS 只说明模型复算一致，不说明假设正确。
- 未修改其他公司目录、未提交、未推送、未更新索引。
