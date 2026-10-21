# 美股七姐妹财务口径独立复核

复核日与信息截止：2026-10-19（Asia/Shanghai）。股票价格截面：2026-10-16 美国正常交易时段收盘，单位 USD/股。此文件是行业研究员的独立交叉检查，不替代主财务报告。

**结论：指定七个收盘价均一致；美国财政部 10 年 5.09%、30 年 5.43% 均准确。七家公司下一次财报均尚未发生。需特别校正 META 为 10 月 21 日、NVDA 为 11 月 17 日；Apple 11 月 2 日已在官方动态页面直接核实。**

## 价格截面

| 股票 | 待核价格 | 本次核实 | 两个公开行情入口 |
|---|---:|---|---|
| AAPL | 343.46 | 一致 | [Chartexchange 日线](https://chartexchange.com/symbol/nasdaq-aapl/historical/)；[JPMorgan/IDC](https://idc.chase.com/stockspublic/historicalquotes?symbol=AAPL) |
| MSFT | 529.05 | 一致 | [Yahoo 历史行情](https://finance.yahoo.com/quote/MSFT/history/?ltr=1)；[Chartexchange 日线](https://chartexchange.com/symbol/nasdaq-msft/historical/) |
| GOOGL | 340.59 | 一致，Class A | [Stock Analysis 历史行情](https://stockanalysis.com/stocks/googl/history/)；[Google Finance](https://www.google.com/finance/beta/quote/GOOGL%3ANASDAQ?window=6M) |
| AMZN | 250.00 | 一致 | [Yahoo 历史行情](https://finance.yahoo.com/quote/AMZN/history/?p=AMZN)；[Investing 日线](https://ca.investing.com/equities/amazon-com-inc-historical-data) |
| META | 709.33 | 一致 | [Yahoo 历史行情](https://finance.yahoo.com/quote/META/history/)；[Stock Analysis 历史行情](https://stockanalysis.com/stocks/meta/history/) |
| NVDA | 214.13 | 一致 | [Chartexchange 日线](https://chartexchange.com/symbol/nasdaq-nvda/historical/)；[Google Finance](https://www.google.com/finance/quote/NVDA%3ANASDAQ?window=5D) |
| TSLA | 354.72 | 一致 | [Yahoo 历史行情](https://finance.yahoo.com/quote/TSLA/history/)；[Investing 日线](https://www.investing.com/equities/tesla-motors-historical-data) |

七组已调用 `tools/financial_rigor.py cross-validate`，容差设为 0%，均返回偏差 0.00%。此检查只确认录入值一致，不验证底层数据源是否完全独立。

价格边界与易错点：

- 以上是多个行情商公开页面的交叉检查，未取得交易所签发的原始收盘数据文件。Nasdaq 历史页本次未返回可用日线。因此可表述为“多行情源核实的正常收盘价”，不应写成“交易所原始数据已核验”。不同入口可能共享底层供应商。
- Chartexchange 页头最后一笔显示 AAPL 343.42、MSFT 528.99、NVDA 214.12，而 10 月 16 日日线 Close 为表内数值；TSLA 页头 16:00:08 为 354.91，日线 Close 为 354.72。不可用页头秒级快照替换日线正常收盘。
- 盘后价格另列，例如 Yahoo 的 MSFT 526.83、META 705.32、TSLA 352.46，均不进入本次估值价格截面。GOOGL 与 GOOG 为不同股份类别，也不能混用报价。
- 以上核实不证明市值分母正确；市值还须按各公司对应时点实际流通/发行股数及股份类别重新核对，不能直接使用 EPS 的加权平均稀释股数。

## 美国财政部收益率

[U.S. Treasury Daily Treasury Par Yield Curve Rates，2026 年表](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=2026&type=daily_treasury_yield_curve) 的 **10/16/2026** 一行明确列示：10 年 **5.09%**，20 年 **5.47%**，30 年 **5.43%**。两个待核数字正确，勿把 20 年列误当 30 年列。

口径是美元名义国债的 par/CMT 曲线估计。财政部说明其依据约纽约时间下午 3:30 的指示性买方报价，并非实际成交价；它不是零息即期利率，也不是任意具体债券的到期收益率。不能把该值直接称为股票资本成本：风险现金流与折现率必须匹配；若使用无风险折现率，现金流须采用一致的确定性等价处理。上述利率只是当前可核验的美元长期无风险参照。

## 下一次财报：均在截止日之后

日期按美国当地日历；“电话会”时间不自动等同于新闻稿精确发布时间。下面只列原始来源可支持的精度。

| 公司 | 下一次报告/电话会 | 已核实时间与期间 | 原始来源和证据日期 |
|---|---|---|---|
| AAPL | **2026-11-02** | FY26Q4 电话会 14:00 PT / 17:00 ET；该页未给新闻稿精确发布时间 | [Apple IR](https://investor.apple.com/investor-relations/default.aspx)，2026-10-19 浏览器实际渲染页直接读取 “FY 26 Fourth Quarter Results”；未标公告发布日期 |
| MSFT | **2026-10-28** | FY27Q1；本次直接读取的主 IR 页确认日期，未列时分 | [Microsoft IR](https://www.microsoft.com/en-us/investor/default?DocType=Current&SortOrder=Date+Ascending)，2026-10-19 页面标为 Upcoming，并明确 next earnings release 日期 |
| GOOGL | **2026-10-28** | 2026Q3 电话会 13:30 PT / 16:30 ET | [Alphabet 官方活动页](https://abc.xyz/investor/events/event-details/2026/2026-Q3-Earnings-Call-2026-Ujou16CTw9/default.aspx)，2026-10-19 浏览器直接读取；公司日期公告为 2026-10-06，另见[公司公告原文转载](https://www.marketscreener.com/news/alphabet-announces-date-of-third-quarter-2026-financial-results-conference-call-ce785dd9dc89f62d) |
| AMZN | **2026-10-29** | 2026Q3 电话会 14:00 PT / 17:00 ET | [Amazon 官方公告](https://press.aboutamazon.com/2026/10/amazon-com-to-webcast-third-quarter-2026-financial-results-conference-call)，2026-10-15 发布 |
| META | **2026-10-21** | 2026Q3 正常收盘后发布；电话会 13:30 PT / 16:30 ET | [Meta 官方公告](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-to-Announce-Third-Quarter-2026-Results/default.aspx)，2026-10-12 发布 |
| NVDA | **2026-11-17** | FY27Q3；已核实下一次电话会日期，未给精确时间 | [NVIDIA 官方托管 FY27Q2 电话会全文](https://investor.nvidia.com/files/content_files/TRANSCRIPT_-NVIDIA-Corp-NVDA-US-Q2-2027-Earnings-Call-26-August-2026-5_00-PM-ET.pdf)，2026-08-26，第 15 页，IR 负责人结束语明确下一次为 November 17；该文本由 FactSet 整理并托管于公司 IR |
| TSLA | **2026-10-21** | 2026Q3 正常收盘后发布；电话会 16:30 Central / 17:30 ET | [Tesla 官方交付公告](https://ir.tesla.com/press-release/tesla-third-quarter-2026-production-deliveries-and-deployments)，2026-10-02 发布 |

需要带回总报告的差异与证据边界：

1. **META 不可套用月底惯例，NVDA 不可沿用 11 月 19 日等历史日期。** 当前读到的公司来源分别支持 10 月 21 日和 11 月 17 日；NVDA 的证据日期较早，若公司后来更新应以最新公告为准。
2. **Apple 的 11 月 2 日已经公司官方确认。** 部分第三方页面仍标 Estimated，另有第三方把季度错写为 Q3；本次官方动态页明确 FY26Q4，电话会为 17:00 ET，不能使用第三方 16:30 ET 说法。
3. **截至 10 月 19 日，七家的上述财报结果都还不能作为已发生事实。** Tesla 已在 10 月 2 日披露 Q3 交付与储能装机，但尚未披露 Q3 利润、现金流；Apple FY26 已结束也不等于 FY26 年报已发布。财年标签不同：Microsoft FY27Q1、NVIDIA FY27Q3 不等于自然年 2027 已发生。
4. Apple、Alphabet 的静态网页抓取未显示活动内容，但浏览器渲染页可以读取，故不能把抓取空白解读为公司尚未公告。所有日期是已公布安排，仍可能在截止日以后变更。
