# 网易研究附件

研究日期：2026-10-21；正文：`../网易研究报告-20261021.md`。

| 文件 | 内容 |
|---|---|
| `model.py` | Decimal 计算：市值与港美股折算、滚动十二个月、净现金重算与可动用净现金、正常化利润、估值指标、历史年末市盈率、反向折现、三年三情景、十年折现四情景（含尾部）、十年 IRR（工具口径与显式现金口径）、敏感性；并实跑 `tools/financial_rigor.py` 与 `tools/terminal_value.py`。运行：`python3 reports/网易/research-20261021/model.py` |
| `inputs.json` / `results.json` | 全部输入（含口径说明与情景假设）与输出；金额单位为人民币十亿元，每 ADS 价值为美元 |
| `financial-rigor.txt` | 工具实跑原始输出：verify-market-cap、cross-validate（股价、股本、汇率、收入、归母、滚动收入/归母/经营现金流、净现金、创始人持股）、verify-valuation、three-scenario，以及 terminal_value 的 audit / pe / irr / flip（±2pp 与 ±1pp） |
| `audit-extract.txt` | `python3 tools/report_audit.py extract --report reports/网易/网易研究报告-20261021.md --seed 42` 的输出：204 个可提取点中抽 30 个 |
| `audit.py` | 把抽中点逐一填入取数值与来源后调用 `report_audit.py verdict`；运行：`python3 reports/网易/research-20261021/audit.py` |
| `audit-classified.json` / `audit-facts.json` | 30 个抽中点的分类；进入判决的 16 个事实项 |
| `audit-verdict.txt` | 判决结果：【准出】16/16 通过；另附模型项复算核对 |
| `sources.md` | 来源 URL、访问日期、页码定位与缺口 |

## 抽检分类

- 进入判决的 16 项：7 项填了两个来源，但真正独立的只有 2 项（汇率：欧洲央行与 Yahoo；滚动十二个月经营利润：原件推算与 StockAnalysis）；其余 5 项的第二来源是同一公司的 20-F 或同一份公告的报表重算。9 项为单一原件、单一数据库或由原件数字推算。
- 不进判决的 14 项：11 项为模型假设或模型输出（只与 `results.json` 复算一致，不是外部事实）；3 项为非数据（日期、星级）。

## 核验边界

- PASS 只说明报告数字与原件或数据库一致，不说明情景假设正确。
- 9999.HK 10-20 收盘价只有 StockAnalysis 一个来源（Yahoo 当日为空），用美股价折算核对，偏差 0.72%。
- 2021 年全部财务数据、2021—2022 年经营利润与固定资产开支为 StockAnalysis 单一来源。
- 公司口径净现金 1675 亿元已按资产负债表逐项重算一致；但境内外现金分布未披露，汇出预提税未建模。
- 净现金与资产负债表为 2026-06-30 快照，不是 10 月实时余额。
- 未编辑旧报告、未提交、未推送。
