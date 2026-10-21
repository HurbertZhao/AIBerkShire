# 瓶颈猎手信号扫描 — 2026-06-11 17:07
**第二百零七轮扫描**

---

## 执行摘要

本轮（16:09→17:07）发现 **3个新信号（含1个重大状态变化）**：

1. **🔄 ALM — $7亿可转债清算（Phase 2 FID落地），股价-23%，稀释被市场过度定价**：6月9日$700M可转债交割，实际最大稀释9%（只有当股价>$27.40时才会稀释），但市场卖出23%（$20.68→$15.75）。分析师对FY2026收入预测从CAD 297M（AGP）到CAD 670M（BofA）严重分歧，估值不确定性极高。Russell 1000指数纳入18天后（6/29），机械性买盘支撑。**维持★★★，需专项深入分析才能判断是否升级。**

2. **🆕 IQE ADR程序（4月17日已生效）——此前未记录**：IQE plc向SEC提交F-6EF注册，每1个ADR代表25股普通股，摩根大通为存托银行，注册日期2026年4月17日。美国机构可直接通过NYSE/OTC交易IQE，是IQE在美国知名度和流动性的重要正催化剂。IQE今日股价51p，YTD+914%，但今日-8.44%（近期有所回调）。**维持★★★，ADR记录为正催化剂。**

3. **📋 ICL CFO交接（6/15，4天后）**：Asaf Alperovitz（前SolarEdge CFO）6月15日正式接任，原任CFO Aviram Lahav退休。监控信号——新CFO资本分配偏好尚未明确，对ICL短期无实质影响。**维持★★★★，不改变估值判断。**

---

## 新信号详情

### 1. Almonty Industries (ALM) — Phase 2 FID实质落地，但估值极度不确定

**触发事件（2026年6月4-9日）**：

| 事件 | 数据 | 来源 |
|------|------|------|
| 可转债公告 | 2026年6月4日公告$700M 2.25%可转债 | PR Newswire / StockTitan |
| 可转债交割 | 2026年6月9日完成交割（超额认购）| SEC 6-K |
| 转换价格 | $27.40/股（$20.68 × 1.325溢价）| 公告 |
| 封顶期权（Capped Call）上限 | $20.68/股（阻止$27.40以下转换稀释）| 公告 |
| 附加购买权 | 承销商可追加$1亿（总计$800M上限）| 公告 |
| 股价（公告前，6/4）| $20.68 | StockTitan |
| 股价（6/11，今）| $15.75 | MacroTrends / CNBC |
| 市值（6/11）| **$4.34B** | MacroTrends |
| 跌幅 | -23.8%（$20.68→$15.75）| 计算 |

**稀释分析（关键：市场可能过度反应）**

| 情景 | 条件 | 稀释规模 | 实际稀释率 |
|------|------|---------|----------|
| 无稀释 | 股价≤$20.68（capped call保护）| 0股 | 0% |
| 部分稀释 | $20.68 < 股价 < $27.40 | 0股（capped call覆盖）| 0% |
| 最大稀释 | 股价 > $27.40 | $700M ÷ $27.40 ≈ 25.5M股 | ~9%（基于275M股基数）|

**结论**：当前股价$15.75远低于转换价格$27.40（需再涨74%才触发稀释），市场对稀释的恐慌被放大。$700M可转债本质上是：**当前是纯粹债务（2.25%利息=$15.75M/年），只有在牛市充分兑现后才转股**。

**这实际上是 Phase 2 FID 的资金落地**（上一轮报告标注"等Phase 2 FID"）：Sangdong Phase 2计划2027年完工，将双倍产能至1.2M吨/年矿石。

**估值检查（困难：分析师分歧极大）**

| 分析师/来源 | FY2026E收入（CAD）| FY2026E EBITDA（CAD）| 数据来源 |
|-----------|------------|--------------|------|
| Alliance Global Partners（保守）| CAD 297M（~$218M USD）| N/A | 3月2026研报 |
| BofA（激进）| CAD 670M（~$490M USD）| CAD 597M（~$438M USD）| 2026研报 |
| 实际Q1 2026（已知）| CAD 25.4M（年化×4 = CAD 102M）| EBITDA CAD 6.1M | ALM财报 |

⚠️ **注意**：Q1年化推算（CAD 102M）远低于两家分析师预测，说明Sangdong矿仍处于产能爬坡阶段，分析师预测反映的是H2-FY2027的全产能情景而非Q1线性外推。

| 估值指标 | 保守（AGP） | 激进（BofA） | 判断 |
|---------|-----------|-----------|------|
| PS（FY2026E）| $4.34B/$218M = **19.9x** | $4.34B/$490M = **8.9x** | 🟡黄灯 / 🟢绿灯 |
| PE（FY2026E）| $4.34B/（$43M净利）= **~101x** | $4.34B/（BofA净利约$300M）= **~14x** | 🔴红灯 / 🟢绿灯 |
| 市值 vs TAM 20% | 全球非中国钨市场约$20B×20%=$4B；$4.34B轻微超线 | — | ⚠️ 边界 |

**估值安全边际（10年25xPE退出法——两种情景）**

| 情景 | 净利基础 | CAGR | 10年净利 | 退出市值 | 年化回报 |
|------|---------|------|--------|---------|---------|
| BofA激进（FY2026净利$300M） | $300M | 10% | $778M | $19.4B | **16.3%** ✅ |
| AGP保守（FY2026净利$43M，FY2028净利$200M起计）| $200M（延迟2年）| 10% | $519M | $13.0B | **11.6%** ✅ |
| 悲观（矿产爬坡不及预期，FY2027净利$80M起）| $80M（延迟3年）| 10% | $207M | $5.2B | **1.8%** ❌ |

**结论**：

- 极端分歧的分析师预测（2x收入差距）反映Sangdong矿的爬坡不确定性
- 市场可能对稀释过度反应（仅9%最大稀释 vs 23%跌幅），但估值本质上依赖BofA的激进情景
- Russell 1000纳入（6/29，18天后）产生机械买盘，短期催化剂成立
- $700M转债利息支出$15.75M/年对现金流有压力，需Sangdong收入快速提升

**看多逻辑**：
1. **Phase 2 FID资金落地**：$700M过额认购（机构投资者覆盖），说明大资金认可Sangdong的长期价值
2. **稀释被市场过度定价**：当前股价$15.75距转换价$27.40有74%距离，短期无实质稀释；23%下跌创造了更好入场价
3. **Russell 1000机械买盘**：6/29，被动指数基金强制买入，规模取决于ALM的指数权重

**看空逻辑**：
1. **爬坡不确定性**：Q1实际年化CAD 102M vs BofA预测CAD 670M——差距5.6倍，即使BofA是FY2027展望，爬坡路径上的任何延误都会造成巨大估值压力
2. **市值 vs TAM边界警告**：$4.34B市值已接近全球非中国钨市场×20%的红线，说明市场已提前定价了部分成功
3. **债务负担**：$700M可转债 + 原有建设债务，总负债可能达$1B+，对现金流要求极高

**建议**：★★★（维持），不升级。数据分歧过大，需执行 `/investment-research` 深度研究以确认Sangdong的实际爬坡曲线和收入模型，才能判断是否升至★★★★。**在Russell 1000纳入后（6/29）观察买盘支撑情况是辅助参考节点。**

---

### 2. IQE plc — ADR程序已于4月17日生效（此前未记录）

| 项目 | 内容 | 来源 |
|------|------|------|
| 生效日期 | 2026年4月17日 | SEC F-6EF |
| ADR结构 | 1 ADR = 25 IQE普通股 | SEC F-6EF |
| 存托银行 | JPMorgan Chase Bank, N.A. | SEC F-6EF |
| 意义 | 美国机构可直接通过美股账户交易IQE，无需UK经纪商 | 分析 |

**影响评估**：
- **正面**：扩大美国投资者基础，AI光通信叙事在美国市场更易传播；JPMorgan背书提升机构知名度
- **中性**：不改变IQE的基本面；ADR结构不会影响UK主板交易
- **注意**：IQE今日（6/11）股价51p，-8.44%（YTD +914%）。大幅涨后回调属正常技术整理

**对估值的影响**：ADR不改变IQE的PS/PE计算（仍然£448M市值 / FY2026E £116.8M收入 = PS 3.84x，维持绿灯）。但提高了可被发现的概率，是长期正催化剂。

**建议**：★★★（维持），ADR催化剂记录在案。等8月中期报告EBITDA转正确认后升至★★★★。

---

### 3. ICL Group — CFO交接（6月15日，4天后）监控信号

| 项目 | 内容 |
|------|------|
| 新任CFO | Asaf Alperovitz |
| 前任职务 | SolarEdge Technologies CFO |
| 其他经历 | Delta Galil Industries CFO、Syneron Candela CFO |
| 生效日期 | 2026年6月15日 |
| 离任 | Aviram Lahav 退休 |
| 公告日期 | 2026年3月10日（Business Wire）|

**影响评估**：
- **正面**：来自高成长科技公司（SolarEdge）的CFO背景，可能对资本市场更敏感，IR水平提升
- **中性**：ICL是大型特矿公司，CFO变动不影响溴化物定价或Hormuz局势
- **风险**：新CFO上任后可能重新审视资本结构（如是否增加股东回报或调整杠杆），短期存在不确定性，但可能性低
- **注意**：Q2财报（8月5日）将是新CFO首次重要电话会，值得关注新CFO的表达风格和前瞻指引策略

**建议**：★★★★（维持），CFO交接记录为监控项，不影响投资论证。

---

## 存量信号状态确认

### 4047.T（Kanto Denka）— 无新信号，7/1倒计时19天

| 项目 | 状态 |
|------|------|
| WF6涨价70-90%通知 | 已向三星/SK Hynix/DB HiTek发出（多方确认）|
| 7/1 Showa Denko Kanto + Central Glass永久退出 | 倒计时19天，无新变化 |
| NF3（Mitsui 2026年退出）| 已生效，Kanto Denka NF3垄断进一步强化 |
| 火灾（2025年8月，10个月前）| 1条生产线部分受损，10个月后应已恢复，需确认 |
| 市值 | ¥240.3B（~$1.54B USD）|
| 追踪PE | >63x |

**注意**：Mitsui Chemicals已于2026年退出NF3市场（验证），Kanto Denka在日本NF3市场份额进一步扩大，强化其NF3垄断地位。与WF6独占相叠加，7/1后Kanto Denka在两个关键半导体气体上均具有更强定价权。**维持★★★★★。**

### LEU（Centrus Energy）— Phase IV窗口10天，$9亿商业级任务单已落定

| 项目 | 状态 |
|------|------|
| $900M商业级HALEU任务单 | 2026年1月5日已公告（DOE授权美国离心运营公司）|
| 合同总价 | $900M基础 + $170M选项 = $1.07B上限 |
| Piketon扩建首期产能 | 预计2029年上线 |
| Phase III合同 | 2026年6月30日到期 |
| Phase IV（2年延期）决定 | 6/30前待决定（倒计时19天）|
| 6/18年会 | Section 382 NOL保护续期投票（确认）|
| HALEU产量 | 超额完成920kg |

**若Phase IV被执行（概率偏高）**：LEU持续HALEU生产至2028年，同时商业级$900M扩建进行中，形成"短期合同续期+长期产能建设"双轮驱动。**维持★★★★。**

---

## 观察名单状态

| 公司 | 代码 | 上轮（16:09）评级 | 本轮变化 | 最新评级 |
|------|------|---------|---------|---------|
| **Kanto Denka** | **4047.T** | ★★★★★ | Mitsui NF3退出确认→NF3垄断进一步强化；7/1倒计时19天 | **★★★★★（维持）** |
| **ICL Group** | **ICL** | ★★★★ | CFO交接6/15，4天后；不影响投资论证 | **★★★★（维持）** |
| **IQE plc** | **IQE.L** | ★★★ | 🆕 ADR程序4月17日生效（此前未记录）；今日-8.44%至51p（YTD+914%正常技术回调）| **★★★（维持，正催化剂记录）** |
| **Centrus LEU** | **LEU** | ★★★★ | $900M商业级任务单背景补充；Phase IV决定6/30（倒计时19天）| **★★★★（维持）** |
| **Almonty Industries** | **ALM** | ★★★ | 🔄 $700M可转债6/9交割（Phase 2 FID落地）；股价-23%至$15.75；最大稀释仅9%（需股价>$27.40）；市值$4.34B；Russell 1000+18天 | **★★★（维持，需/investment-research深入研究）** |
| **TOK** | **4186.T** | ★★★⚠️ | 无新信号 | **★★★⚠️（维持）** |
| **AXTI** | **AXTI** | ★★ | 无新信号 | **★★（维持）** |
| **Powell Industries** | **POWL** | ★★★ | 无新信号 | **★★★（维持）** |

---

## 关键节点（更新）

| 日期 | 事件 | 优先级 | 状态 |
|------|------|--------|------|
| **6/11 持续** | 霍尔木兹交火持续；EIA $105/桶有效 | 🚨🚨 | ICL最大尾部风险 |
| **6/15（4天）** | **ICL新CFO Alperovitz上任** | ★★★ | 监控资本配置信号 |
| **6/18（7天）** | **LEU年会 Section 382 NOL保护投票** | ★★★★ | 10AM ET虚拟会议 |
| **6/29（18天）** | **ALM加入Russell 1000/3000指数** | ★★★ | 被动买盘，辅助催化剂 |
| **6/30（19天）** | **LEU DOE Phase IV两年延期选项决定** | ★★★★★ | HALEU超额920kg，概率偏高 |
| **7/1（20天）** | **Showa Denko Kanto + Central Glass永久停止WF6** | 🔴🔴 | 4047.T定价权临界点 |
| **7/1（20天）** | Nittobo（3110.T）5:1拆股生效 | ★★★★ | 已公告确认 |
| **7月底** | AXTI Q2 2026财报 | ★★★ | 等FY2026E>$200M→PS降至<28x |
| **8/5** | **ICL Q2 2026财报** | ★★★★★ | 溴化物价格兑现；新CFO首次财报会 |
| **8月初** | **POWL Q3 FY2026财报** | ★★★ | 收入加速确认节点 |
| **8月** | **IQE FY2026中期报告** | ★★★★ | EBITDA转正+ADR美国投资者加入 |
| **8/12** | **Kanto Denka Q1 FY2027财报** | ★★★★★ | WF6+NF3双垄断定价权首个季度验证 |

---

## 核心结论

**本轮最重要更新：ALM $7亿可转债——Phase 2 FID落地，但市场解读存在分歧**

表面看是"稀释冲击"（股价-23%），实质上是Sangdong Phase 2的资金落地，且实际稀释幅度仅9%（需股价涨74%才触发）。市场对稀释的恐惧与实际稀释幅度不成比例。

但问题的核心是估值：ALM的投资价值完全依赖Sangdong矿能否在FY2026-2027按BofA预测快速爬坡（年收入达CAD 670M vs Q1年化CAD 102M）。这个差距（5.6倍）超出了本轮扫描的验证能力。**在执行 `/investment-research` 专项研究验证Sangdong爬坡曲线之前，维持★★★，不升级。**

**次要：IQE ADR是低调但重要的正催化剂**

4月17日的F-6EF注册此前未被记录。JPMorgan为存托银行的IQE ADR项目使美国AI基础设施投资者能够直接持有IQE，显著扩大了潜在投资者基础。这对IQE的估值重估有长期正面意义，但短期不改变PS 3.84x / 等EBITDA转正的基本投资逻辑。

---

## 信源

- [Centrus Energy Secures $110M HALEU Extension from DOE — Yahoo Finance](https://finance.yahoo.com/news/centrus-energy-secures-110m-haleu-041451652.html)
- [Centrus Awarded $900 Million to Expand Uranium Enrichment in Ohio — PR Newswire](https://www.prnewswire.com/news-releases/centrus-awarded-900-million-to-expand-uranium-enrichment-in-ohio-302654299.html)
- [Centrus Energy Annual Meeting DEF 14A — SEC](https://www.sec.gov/Archives/edgar/data/0001065059/000162828026027241/leu-20260424.htm)
- [Almonty Industries Announces $700M Convertible Senior Notes — StockTitan](https://www.stocktitan.net/news/ALM/almonty-industries-announces-proposed-convertible-senior-notes-gjphjtmaixky.html)
- [Almonty Industries Prices $700M 2.25% Convert — StockTitan](https://www.stocktitan.net/news/ALM/almonty-industries-prices-oversubscribed-us-700-million-convertible-zjhfqft1du4p.html)
- [Almonty's Sangdong Mine Starts Commercial Production as Tungsten Prices Triple — Ad-Hoc News](https://www.ad-hoc-news.de/boerse/news/ueberblick/almonty-s-sangdong-mine-starts-commercial-production-as-tungsten-prices/)
- [Almonty Turns Cash Flow Positive as Sangdong Mine Ramps — Ad-Hoc News](https://www.ad-hoc-news.de/boerse/news/ueberblick/almonty-turns-cash-flow-positive-as-sangdong-mine-ramps-up-production/69314500)
- [Almonty Industries Set to Join Large-Cap Russell 1000 Index — Morningstar](https://www.morningstar.com/news/business-wire/20260528919556/almonty-industries-set-to-join-large-cap-russell-1000-index-and-broad-market-russell-3000-index)
- [Almonty's Revenue Surge and Russell 1000 Entry — Ad-Hoc News](https://www.ad-hoc-news.de/boerse/news/ueberblick/almonty-s-revenue-surge-and-russell-1000-entry-a-defining-quarter-for/69469394)
- [IQE PLC ADR Form F-6EF — SEC](https://www.sec.gov/Archives/edgar/data/1550405/000119380526000476/e665377_f6ef-iqe.htm)
- [ICL Announces CFO Transition — Business Wire](https://www.businesswire.com/news/home/20260310113162/en/ICL-Announces-Chief-Financial-Officer-Transition)
- [ICL Appoints Asaf Alperovitz as New CFO — GuruFocus](https://www.gurufocus.com/news/8695776/icl-appoints-asaf-alperovitz-as-new-cfo-starting-june-2026)
- [WF6 Sourcing Crisis 2026 — LDeepAI](https://www.ldeepai.com/tech-hub/wf6-sourcing-crisis-market-analysis-semiconductor-supply-chain-risks-2026/)
- [Supply Tightening Expected for Specialty Electronic Gases — Semiconductor Digest](https://www.semiconductor-digest.com/supply-tightening-expected-for-specialty-electronic-gases/)
