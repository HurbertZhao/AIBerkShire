# 瓶颈猎手信号扫描 — 2026-06-20 10:00（第247轮）

## 新信号

| 环节 | 信号描述 | 来源 | 是否有可投资标的 | 下一步 |
|------|---------|------|----------------|-------|
| InP衬底/EML激光器（Layer 3/2） | Nvidia于2026年3月以$40亿锁定Lumentum+Coherent EML产能；全球月需求700-800K units vs 月供给仅400K；EML良率仅15-50%放大基板需求；AXT已将部分客户涨价近70%；800G+光模块出货量2025→2026预计跳增2.6倍（24M→63M units） | [TechTimes 2026-05-27](https://www.techtimes.com/articles/317281/20260527/ai-data-center-optical-component-shortage-nvidias-4b-laser-lockup-pushes-rivals-past-2027.htm) · [SDxCentral](https://www.sdxcentral.com/news/nvidias-aggressive-laser-procurement-spurs-supply-chain-fears/) · [TrendForce 2025-12](https://www.trendforce.com/presscenter/news/20251208-12823.html) | ⚠️ AXT (AXTI) 最纯正InP标的但估值★★封顶（PS 72x，双重红灯）；暂无通过估值检查的可投标的 | 搜索日本供应商（住友电工、三菱电机）是否有可触达标的 |
| HALEU铀燃料（Layer 3/SMR供应链） | 美国国内唯一HALEU生产商Centrus Energy (LEU)；Phase III DOE合同延续（$1.1亿年延期，2026年6月）；DOE承诺100亿美元10年期扩产计划；俄罗斯Tenex已被禁（2024年5月）；美国已生产~1公吨但2030年代需求>40公吨 | [Yahoo Finance - Centrus DOE](https://finance.yahoo.com/news/centrus-energy-secures-110m-haleu-041451652.html) · [ANS Nuclear News](https://www.ans.org/news/2025-06-25/article-7134/doe-extends-centruss-haleu-production-contract-by-one-year/) · [World Nuclear Assoc](https://world-nuclear.org/information-library/nuclear-fuel-cycle/conversion-enrichment-and-fabrication/high-assay-low-enriched-uranium-haleu) | 🆕 Centrus Energy (LEU) 建议加入观察名单★★；PS ~8.6x（绿灯）但HALEU业务占收入<5%，不满足纯正度初筛（>30%）；属战略期权型 | 跟踪SMR项目时间线，监察HALEU业务收入占比提升节点 |

---

## InP衬底/EML激光器 — 详细分析

### 瓶颈定位

**Layer 3 → Layer 2 链路**：InP（磷化铟）衬底 → EML激光器芯片 → 光模块收发器 → AI数据中心互联

瓶颈评级：**S级**（供给端结构性短缺，需求端加速扩张，两者在2026年形成最大缺口）

| 瓶颈标准 | 评分 | 说明 |
|---------|------|------|
| 供给集中度 | 🔴 | 全球InP衬底主要供应商：AXT、Wafer Technology、Sumitomo（3家以内）；EML生产商<5家（Lumentum、Coherent、三菱、住友、博通） |
| 扩产周期 | 🔴 | InP外延设备（MOCVD）交期18-24个月；即使今天下单扩产，2027年底才有新产能 |
| 替代难度 | 🔴 | EML技术路线暂无法被VCSEL或硅光子100%替代（硅光子需要外置光源，仍需InP激光器） |
| 产能利用率 | 🔴 | 月需求700-800K vs 月供给400K → 供给缺口约40-50% |
| 需求增速 | 🔴 | 800G+光模块出货量预计同比增长160%；AI数据中心互联带宽需求持续加速 |
| 客户验证周期 | 🔴 | 光模块客户（如Nvidia）对激光器供应商验证周期>1年 |

**结论：6/6标准全红，S级瓶颈确认。**

### Nvidia $4B锁定事件（关键催化剂）

2026年3月2日，Nvidia向Lumentum和Coherent各投入$20亿（共$40亿），另外投资Scintil Photonics和Ayar Labs，锁定优先产能访问权。这一举措：

1. 直接导致竞争对手（AMD、Google、Microsoft）找不到EML货源，被迫等到2027年以后
2. 剩余EML供应商（MACOM、住友、博通）产能迅速被其他AI芯片厂商抢占
3. InP衬底需求因此进一步集中，AXT等基板厂商进入配给状态

### 相关标的估值检查

#### AXT Inc（AXTI）— InP衬底最纯正标的

| 指标 | 数据 | 来源 |
|------|------|------|
| 市值 | **~$64亿 USD** | companiesmarketcap.com, 2026年6月 |
| TTM收入 | $88.3M | SEC 10-Q / StockAnalysis |
| PS | **~72x** | $6.4B ÷ $88.3M |
| PE | **亏损（TTM净亏$21.3M）** | SEC 10-Q |
| Q1 2026收入增速 | +39% YoY | semiconductor-today.com |
| InP业务占比 | 约60-70%（估计） | 主营为InP+GaAs+Ge衬底 |
| 扩产计划 | 2026年底前将InP产能翻倍 | 公司公告 |

**估值红灯检查（必填）**：

| 红灯条件 | 结果 |
|---------|------|
| 市值 > TAM的20%？（InP晶圆TAM ~$2亿/年，20%阈值=$4,000万） | 🚨 $64亿 >> $4,000万，**严重触发**（即使用更大口径TAM也触发） |
| PS > 30x 且增速 < 100%？ | 🚨 PS=72x，增速39%（远低于100%豁免线），**触发** |
| 市值 > 5年乐观预测10倍？（乐观年收入翻倍到$200M×5年=$10亿，×10=$100亿） | ⚠️ $64亿 < $100亿，边界（依赖极乐观假设） |

**双重红灯触发。信号强度封顶 ★★，标注"⚠️ 估值严重透支"。**

10年25xPE退出法：以$64亿市值买入，10年后若净利润达$100M（从亏损到盈利，再到$100M需要极大假设），25xPE退出=$25亿，比买入市值低75%，**无安全边际**。即使极乐观情景（净利$300M，对应收入$1.2B），25xPE=$75亿，10年年化仅1.6%。**当前价格完全不具备安全边际。**

**结论：InP/EML瓶颈是真实的S级瓶颈，但AXT已被充分乃至严重透支定价。最高评级★★（估值红灯）。**

---

## HALEU铀燃料信号 — 战略期权信号

### 背景

SMR（小型模块化反应堆）大多数设计需要HALEU（高丰度低浓缩铀，5-20%丰度），而传统核电站使用3-5%LEU。美国：
- 俄罗斯Tenex（此前唯一商业供应商）已被禁（2024年5月）
- Centrus Energy（LEU）是目前唯一运营HALEU生产设施的美国公司
- 已生产约920公斤；2030年代SMR商业化后年需求可能>40公吨 → 供给缺口极大

### Centrus Energy（LEU）估值检查

| 指标 | 数据 | 来源 |
|------|------|------|
| 市值 | **~$40.7亿** | companiesmarketcap.com, May 2026 |
| 2026年收入指引 | $450-500M | 公司指引 |
| PS | **~8.6x** | $4.07B ÷ $475M（中值估计） |
| PE | ~62x（估，2025数据） | 黄灯，需2026最新数据确认 |
| HALEU业务占收入 | **<5%（估计）** | HALEU合同$1.1亿/年 vs 总收入$475M |
| 通过"瓶颈业务>30%收入"初筛 | ❌ **未通过**，主业为LEU核燃料供应 |

**估值灯：PS ~8.6x绿灯，但初筛不通过（瓶颈纯正度不足）。**

**结论：Centrus是HALEU的战略期权，但不是当前的瓶颈纯正标的。SMR商业化仍需3-5年，HALEU业务占比届时才可能突破30%阈值。加入观察名单★★，跟踪条件：HALEU业务占收入比例触及20%+时重新评估。**

---

## 观察名单状态变化

| 标的 | 代码 | 变化 | 理由 |
|------|------|------|------|
| Centrus Energy | LEU | 🆕 **新增 ★★（战略期权）** | 美国唯一HALEU生产商，DOE Phase III合同延续，SMR供应链前置布局 |
| AXT Inc | AXTI | 🆕 **★★（估值红灯）** | InP衬底S级瓶颈确认，但PS 72x双重红灯封顶，不可买入；监察估值回调至PS<10x |
| HEX.L | HEX.L | **无变化** | 14:00轮次已升至★★★★，无新增信号 |
| 所有其他标的 | — | 无变化 | — |

---

## 下一步研究方向

1. **InP/EML日本替代标的**：住友电工（5802.T）、三菱电机（6503.T）的EML业务占比和估值检查——如果EML业务占比超过30%且估值合理，可能是更好的投资切入点
2. **AXT估值回调监察**：触发价格：PS<15x（约$20/股），PS<10x（约$13/股）；当前$88.59不具备安全边际
3. **HALEU合同规模追踪**：下一个DOE大合同（$27亿10年期）的具体分配，是否有更多HALEU纯正标的出现（如Urenco、Orano在美建厂）

---

*信源：[TechTimes EML Shortage](https://www.techtimes.com/articles/317281/20260527/ai-data-center-optical-component-shortage-nvidias-4b-laser-lockup-pushes-rivals-past-2027.htm) · [SDxCentral Nvidia Laser](https://www.sdxcentral.com/news/nvidias-aggressive-laser-procurement-spurs-supply-chain-fears/) · [TrendForce Dec 2025](https://www.trendforce.com/presscenter/news/20251208-12823.html) · [StockAnalysis AXTI Market Cap](https://stockanalysis.com/stocks/axti/market-cap/) · [SEC AXTI 10-Q 2026](https://www.sec.gov/Archives/edgar/data/0001051627/000143774926017054/axti20260331_10q.htm) · [Yahoo Finance Centrus DOE](https://finance.yahoo.com/news/centrus-energy-secures-110m-haleu-041451652.html) · [ANS Nuclear Centrus](https://www.ans.org/news/2025-06-25/article-7134/doe-extends-centruss-haleu-production-contract-by-one-year/) · [InP Bottleneck Substack](https://yianisz.substack.com/p/indium-phosphide-inp-the-quiet-bottleneck)*
