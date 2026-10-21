# 唯品会研究附件

研究日期：2026-10-21；正文：`../唯品会研究报告-20261021.md`。

- `model.py`、`inputs.json`、`results.json`：Decimal 计算的市值、滚动四季、一次性项目剔除、四档现金桥、反向现金流估值、三年三情景（核心利润×除现金市盈率+现金桥）、十年现金流折现（r=8%/10%/12%，含10%尾部档）、十年退出市盈率与IRR。运行 `python3 reports/唯品会/research-20261021/model.py`，会同时重写 `financial-rigor.txt`。
- `financial-rigor.txt`：`financial_rigor.py` 的 verify-market-cap（两种股本）、cross-validate（股价、汇率、股本、FY2025收入/归母/经营现金流、TTM收入/归母、现金）、verify-valuation、three-scenario 实际输出；`terminal_value.py` 的 audit（【准出】，1条未建模警告）、pe、irr、flip（±2pp 与 ±1pp）输出。
- `audit-extract.txt`：`report_audit.py extract --seed 42` 输出，194个可提取点抽30个。
- `audit.py`、`audit-classified.json`、`audit-facts.json`、`audit-verdict.txt`：18个事实或事实衍生项进入判决，全部通过，判决【准出】；11个情景假设、模型输出与行动条件单独归类不进判决；1个元数据（日期）。运行 `python3 reports/唯品会/research-20261021/audit.py`。
- `sources.md`：来源、访问日期、定位与缺口。

## 核验边界

- 18个判决项中13个有第二来源（StockAnalysis），其余为一手原件单一来源或由原件推算（Q1经营利润、Q3非GAAP利润、研发人数、市盈率、派息年度）。原件与XBRL属同一来源的两种形式，不算独立双源。
- 单一来源项：活跃用户、订单、GMV、SVIP人数（公司口径）；2021—2022年财务（XBRL+StockAnalysis，未重开当年20-F）；同行市盈率（盘中第三方快照）。
- 股本用2026-06-30附注9,510万股（四舍五入到0.1百万股）；与20-F的2026-03-31股本相差约1%，差异来自第二季度回购。StockAnalysis股本数据错误，未采用。
- 现金桥的税款扣减（REIT所得税16.3亿元、预提税15.6亿元）是保守假设，未核实是否已缴纳。供应商净占款扣减、长期投资半价计入均为情景假设。
- 十年IRR不含回购与净现金，系统性偏低；未建模风险为美国对华投资限制。
- 模型PASS只说明输入与输出可复算、抽检事实与原件一致，不代表情景假设经过外部验证。未修改其他公司目录、未改索引、未提交或推送。
