# 京东研究附件

研究日期：2026-10-21；正文：[../京东研究报告-20261021.md](../京东研究报告-20261021.md)。

| 文件 | 内容 |
|---|---|
| `model.py` | Decimal 模型：市值、五年历史与滚动十二月、现金桥（季节性应付款、上市子公司净现金与非流动金融资产去重）、市场隐含核心价值、三年三情景、反向估值、敏感性。运行 `python3 reports/京东/research-20261021/model.py` |
| `inputs.json` | 全部输入，单位人民币百万元（另注者除外）；情景假设与事实输入分开 |
| `results.json` | 模型输出 |
| `financial-rigor.txt` | `tools/financial_rigor.py` 的 calc / verify-market-cap / cross-validate / verify-valuation / three-scenario 实际输出 |
| `terminal-value.txt` | `tools/terminal_value.py` 的 audit（【准出】）/ pe / irr / flip（±2pp 与 ±1pp）实际输出 |
| `audit-extract.txt` | `python3 tools/report_audit.py extract --report reports/京东/京东研究报告-20261021.md --seed 42` 的输出（160 点抽 24 点） |
| `audit.py`、`audit-classified.json`、`audit-verdict.txt` | 16 个事实或事实推算点进入判决，全部通过，判决【准出】；5 个模型假设/输出点、3 个提取噪声点（股票代码、年份）单独分类不进判决。运行 `python3 reports/京东/research-20261021/audit.py` |
| `sources.md` | 来源链接、访问日期、定位与缺口 |

## 核验边界

- 双来源：股价（stockanalysis 与 Yahoo）、流通股（公司 6-K 与 stockanalysis 的 ADS 口径，偏差 0.15%）、2021-2025 收入/归母净利润/经营现金流、2026-06-30 现金加短期投资（公司公告/SEC XBRL 与 stockanalysis 一致）。
- 单一来源：公司口径自由现金流、分部数据、收入分类、员工数、控制权比例（只有公司原件）；三家上市子公司的现金、借款、持股数（只有各自港交所公告）；同业市值（stockanalysis，部分为盘中）；国家统计局数据；Ceconomy 交割进度（新闻报道，未见官方交割公告）。
- 推算项：滚动十二月数据、核心零售利润（用子公司国际财务报告准则净利润近似扣除，偏保守）、子公司非流动金融资产去重（会计口径不同，近似）。
- 抽检 PASS 只说明正文数字与原件或复算一致，不说明情景假设正确。

## 口径要点

1. 上市子公司按"京东持有股数 × 2026-10-20 收盘价"计价，其净现金（100%）和非流动金融资产先从合并口径扣除，避免同一笔现金被计两次。
2. 六月底应付账款高于 2025 年末的 405.82 亿元视为季节性占款，从现金中扣除；限制性现金不计。
3. 未计入：7 月后回购、Ceconomy 交割对价与并表债务、京东科技等权益法投资的市场价值（按账面 50% 计入基准）。
4. 未做 git 提交、未修改索引与其他公司目录。
