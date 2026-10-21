# 汽车之家研究附件

研究日期：2026-10-21；正文：`../汽车之家研究报告-20261021.md`。

## 文件说明

- `model.py`、`inputs.json`、`results.json`：Decimal 计算的股本估计、市值、净现金桥、TTM 指标、三情景经营现金流折现、折现率敏感性、反向测算、两种现金处理方式下的十年 IRR、行动价格。运行 `python3 reports/汽车之家/research-20261021/model.py` 会重写 inputs/results 并重新生成 `financial-rigor.txt`。
- `financial-rigor.txt`：`tools/financial_rigor.py`（verify-market-cap、cross-validate、verify-valuation、three-scenario、calc）与 `tools/terminal_value.py`（audit、pe、irr、flip ±2pp 与 ±1pp）的实际输出。
- `audit-extract.txt`：`report_audit.py extract --seed 42` 输出，136 个可提取点抽 21 点。
- `audit.py`、`audit-classified.json`、`audit-facts.json`、`audit-verdict.txt`：13 个事实或原件推算点进入判决，全部通过，判决【准出】；3 个模型假设或输出点、5 个抽取噪声点（日期、年份、文件编号）单独分类，不进判决。运行 `python3 reports/汽车之家/research-20261021/audit.py`。
- `sources.md`：来源链接、访问日期、页码定位与缺口。

## 核验边界

- 进入判决的 13 点中，4 点有两个独立来源（股价两点、2025 年收入、2025 年媒体服务收入），其余 9 点为 SEC 原件单一来源或由原件数字推算。准出说明正文数字与来源一致，不等于每个数字都有双源。
- **单一来源项：** 美元兑人民币汇率（Yahoo）；当前股本（本文由 20-F 股本与 6-K 回购数推算的上限估计，不是公司披露值）；乘联分会数据（媒体转载）；海尔收购资金结构（13D）。
- 6 月 30 日后的回购现金按上限扣除，天天拍车可赎回优先股全额扣除，15 亿元经营备用金为本文假设，三者都使净现金桥偏保守。
- 情景现金流、概率、折现率、ROIC 都是假设，`results.json` 中的估值是情景结果，不是价格预测。
- 未修改其他公司目录、索引与配置文件，未提交或推送。
