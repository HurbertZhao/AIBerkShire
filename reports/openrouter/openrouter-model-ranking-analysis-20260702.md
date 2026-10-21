# OpenRouter 模型使用量多维度拆解：价格归一化前后的真实排名

> 数据快照：2026年6月23日 | 分析日期：2026年7月2日

## 核心问题

OpenRouter 上的模型使用量排行能反映模型真实好用程度吗？答案是：**不能直接用**。原始 token 使用量基本就是价格的倒数——便宜的模型天然获得不成比例的流量。本文通过多维度分析和价格归一化，试图还原一个更接近"真实好用度"的排名。

## 数据来源

- **CodeSOTA Agent Leaderboard**（主要数据源）：覆盖46个 Agent 应用的30天使用数据，同时提供 token 量、花费、采用 app 数、#1 slot 数
- **DigitalApplied** April/June 2026 报告：周度 token 量、市场份额
- **OpenRouter 官方博客**：开源模型基准测试、定价、吞吐量
- **AICost**：月度 token 排行、中国模型分析

## 方法论

### 五个维度

| 维度 | 权重 | 含义 | 噪声特征 |
|------|:----:|------|----------|
| 收入（Revenue） | 30% | 用钱投票——开发者愿意为这个模型花多少钱 | 偏向有钱的企业用户 |
| 采用广度（Apps） | 25% | 有多少不同应用集成了这个模型 | 最不受价格影响 |
| 使用量（Tokens） | 20% | 原始 token 处理量 | 价格噪声最大 |
| 质量领先（#1 Slots） | 15% | 在多少个应用中被选为首选模型 | 样本小但信号强 |
| 单开发者付费 | 10% | Revenue/Apps——每个开发者愿意花多少 | 过滤掉"便宜才用"的噪声 |

### 为什么不用"token/价格"做归一化

"每美元处理多少 token"本质上就是价格的倒数，无法提供增量信息。真正有意义的价格归一化方法是：**在控制了价格因素后，开发者的行为是否仍然指向这个模型**——即收入、采用广度、#1 slots 这些维度。

---

## 综合排名 Top 20

| 排名 | 模型 | 供应商 | 综合分 | 收入 | 使用量 | 采用 | #1 | 有效价格 |
|:----:|------|--------|:-----:|:----:|:-----:|:----:|:---:|:--------:|
| 1 | Claude Sonnet 4.6 | Anthropic | 96.4 | #1 | #3 | #3 | #2 | $6.35/M |
| 2 | MiniMax M3 | MiniMax | 86.2 | #6 | #2 | #4 | #6 | $0.55/M |
| 3 | DeepSeek V4 Pro | DeepSeek | 85.3 | #8 | #4 | #2 | #3 | $0.56/M |
| 4 | Claude Opus 4.8 | Anthropic | 84.8 | #2 | #7 | #8 | #8 | $10.60/M |
| 5 | DeepSeek V4 Flash | DeepSeek | 78.6 | #13 | #1 | #1 | #1 | $0.12/M |
| 6 | Gemini 3.5 Flash | Google | 73.1 | #7 | #14 | #5 | #11 | $3.59/M |
| 7 | GPT-5.5 | OpenAI | 72.8 | #3 | #13 | #15 | #9 | $12.01/M |
| 8 | Claude Opus 4.6 | Anthropic | 71.9 | #5 | #17 | #9 | #10 | $10.60/M |
| 9 | Claude Opus 4.7 | Anthropic | 68.3 | #4 | #16 | #12 | #16 | $10.59/M |
| 10 | Gemini 3 Flash Preview | Google | 67.2 | #12 | #12 | #10 | #4 | $1.20/M |
| 11 | MiMo-V2.5-Pro | Xiaomi | 62.9 | #14 | #9 | #6 | #13 | $0.56/M |
| 12 | Step 3.7 Flash | StepFun | 61.4 | #9 | #5 | #27 | #7 | $0.47/M |
| 13 | Laguna M.1 | Poolside | 54.0 | #17 | #6 | #19 | #14 | $0.26/M |
| 14 | Kimi K2.6 | MoonshotAI | 48.8 | #15 | #18 | #13 | #18 | $1.43/M |
| 15 | GPT-5.3-Codex | OpenAI | 44.7 | #10 | #22 | #29 | #12 | $5.19/M |
| 16 | GLM 5.2 | Z.ai | 44.1 | #16 | #20 | #17 | #19 | $1.52/M |
| 17 | Gemini 3.1 Flash Lite | Google | 41.4 | #26 | #19 | #11 | #5 | $0.60/M |
| 18 | Nex-N2-Pro | Nex AGI | 39.0 | #20 | #11 | #22 | #22 | $0.46/M |
| 19 | Claude Fable 5 | Anthropic | 36.4 | #11 | #29 | #28 | #17 | $21.21/M |
| 20 | Claude Sonnet 4.5 | Anthropic | 35.9 | #18 | #26 | #18 | #20 | $6.36/M |

---

## 各维度排名对比

### 维度一：原始使用量（Token Volume）

价格噪声最大的维度。前10全部是 $1/M 以下的低价模型（Claude Sonnet 4.6 除外）。

| 排名 | 模型 | Token 量 | 有效价格 |
|:----:|------|:--------:|:--------:|
| 1 | DeepSeek V4 Flash | 6,420B | $0.12/M |
| 2 | MiniMax M3 | 4,530B | $0.55/M |
| 3 | Claude Sonnet 4.6 | 3,290B | $6.35/M |
| 4 | DeepSeek V4 Pro | 2,880B | $0.56/M |
| 5 | Step 3.7 Flash | 2,880B | $0.47/M |
| 6 | Laguna M.1 | 2,130B | $0.26/M |
| 7 | Claude Opus 4.8 | 1,540B | $10.60/M |
| 8 | Nemotron 3 Super | 1,470B | $0.19/M |
| 9 | MiMo-V2.5-Pro | 1,270B | $0.56/M |
| 10 | MiMo-V2.5 | 857B | $0.18/M |

**Claude Sonnet 4.6 是唯一一个以高价（$6.35/M）挤进 token 量 Top 3 的模型**——这本身就是极强的质量信号。

### 维度二：收入（Revenue = 用钱投票）

收入是最强的质量信号。愿意花真金白银，说明模型在生产环境中不可替代。

| 排名 | 模型 | 月收入 | Token 量 |
|:----:|------|:------:|:--------:|
| 1 | Claude Sonnet 4.6 | $20.9M | 3,290B |
| 2 | Claude Opus 4.8 | $16.3M | 1,540B |
| 3 | GPT-5.5 | $7.9M | 661B |
| 4 | Claude Opus 4.7 | $5.9M | 554B |
| 5 | Claude Opus 4.6 | $5.7M | 536B |
| 6 | MiniMax M3 | $2.5M | 4,530B |
| 7 | Gemini 3.5 Flash | $2.2M | 599B |
| 8 | DeepSeek V4 Pro | $1.6M | 2,880B |
| 9 | Step 3.7 Flash | $1.3M | 2,880B |
| 10 | GPT-5.3-Codex | $1.3M | 247B |

**Anthropic 前5占了4席，总月收入 $50.1M，占全市场的 66%。** 尽管 token 量只占约 15%。

### 维度三：开发者采用广度（Apps Count）

最不受价格影响的维度——开发者花时间集成一个模型，不仅仅因为便宜。

| 排名 | 模型 | Apps 数 | 有效价格 |
|:----:|------|:-------:|:--------:|
| 1 | DeepSeek V4 Flash | 36 | $0.12/M |
| 2 | DeepSeek V4 Pro | 34 | $0.56/M |
| 3 | Claude Sonnet 4.6 | 29 | $6.35/M |
| 4 | MiniMax M3 | 28 | $0.55/M |
| 5 | Gemini 3.5 Flash | 26 | $3.59/M |
| 6 | MiMo-V2.5-Pro | 26 | $0.56/M |
| 7 | MiMo-V2.5 | 25 | $0.18/M |
| 8 | Claude Opus 4.8 | 24 | $10.60/M |
| 9 | Claude Opus 4.6 | 21 | $10.60/M |
| 10 | Gemini 3 Flash Preview | 21 | $1.20/M |

**DeepSeek V4 Flash 在采用广度上排第一，说明它的流行不仅仅是价格驱动。** 36个不同 app 选择集成它，开发者用脚投票。

### 维度四：质量领先（#1 Slots）

在多少个应用中被选为首选模型——这是最纯粹的质量信号。

| 排名 | 模型 | #1 数 | 总采用 |
|:----:|------|:-----:|:------:|
| 1 | DeepSeek V4 Flash | 6 | 36 apps |
| 2 | Claude Sonnet 4.6 | 5 | 29 apps |
| 3 | DeepSeek V4 Pro | 3 | 34 apps |
| 4 | Gemini 3 Flash Preview | 3 | 21 apps |
| 5 | Gemini 3.1 Flash Lite | 3 | 21 apps |
| 6 | MiniMax M3 | 2 | 28 apps |
| 7 | Step 3.7 Flash | 2 | 7 apps |

**只有15个模型拿到过至少一个 #1 slot。** 能在至少一个场景中成为最优选择，本身就是很高的门槛。

### 维度五：单开发者付费（Revenue / App）

每个集成该模型的开发者平均花多少钱——过滤掉"因为免费所以用"的噪声。

| 排名 | 模型 | 每 App 收入 | Apps 数 |
|:----:|------|:----------:|:-------:|
| 1 | Claude Sonnet 4.6 | $721K | 29 |
| 2 | Claude Opus 4.8 | $680K | 24 |
| 3 | GPT-5.5 | $496K | 16 |
| 4 | Claude Opus 4.7 | $294K | 20 |
| 5 | Claude Opus 4.6 | $270K | 21 |
| 6 | GPT-5.3-Codex | $256K | 5 |
| 7 | Step 3.7 Flash | $191K | 7 |
| 8 | Claude Fable 5 | $149K | 6 |
| 9 | MiniMax M3 | $89K | 28 |
| 10 | Gemini 3.5 Flash | $83K | 26 |

**Claude Sonnet 4.6 不仅采用广（29 apps），每个 app 还平均花 $721K/月**——既广又深。

---

## 价格归一化核心发现

对比"原始 token 排名"和"综合排名"的位差，就能看出价格在多大程度上扭曲了使用量数据。

### 被价格虚高膨胀的模型

这些模型的 token 使用量排名远高于综合排名——说明使用量主要由低价驱动，而非质量。

| 模型 | Token排名 | 综合排名 | 下降 | 有效价格 | 诊断 |
|------|:---------:|:-------:|:----:|:--------:|------|
| Nemotron 3 Super | #8 | #25 | ↓17 | $0.19/M | 10个 app，0个 #1。纯粹靠便宜跑批量 |
| MiMo-V2.5 | #10 | #21 | ↓11 | $0.18/M | 25个 app 但0个 #1，没人觉得它最好 |
| MiniMax M2.7 | #15 | #24 | ↓9 | $0.44/M | 被 M3 取代后仍靠老用户惯性 |
| Nemotron 3 Ultra | #21 | #29 | ↓8 | $0.98/M | benchmark 不错（AA 48）但实际采用很低 |
| Step 3.7 Flash | #5 | #12 | ↓7 | $0.47/M | 只有7个 app，极度集中使用 |
| Laguna M.1 | #6 | #13 | ↓7 | $0.26/M | 2.13T token 但只有12个 app |

### 被价格压制的模型

这些模型的 token 使用量排名远低于综合排名——因为贵，使用量被抑制了，但收入和采用度说明质量确实好。

| 模型 | Token排名 | 综合排名 | 上升 | 有效价格 | 诊断 |
|------|:---------:|:-------:|:----:|:--------:|------|
| Claude Fable 5 | #29 | #19 | ↑10 | $21.21/M | 全场最贵，42B token，但月入 $891K |
| Claude Opus 4.6 | #17 | #8 | ↑9 | $10.60/M | 21个 app 愿意以 $10.60/M 持续用 |
| Gemini 3.5 Flash | #14 | #6 | ↑8 | $3.59/M | 26个 app，价格适中但采用极广 |
| Claude Opus 4.7 | #16 | #9 | ↑7 | $10.59/M | 20个 app，$5.87M 月收入 |
| GPT-5.3-Codex | #22 | #15 | ↑7 | $5.19/M | 只有5个 app 但月入 $1.28M，极度垂直 |
| GPT-5.5 | #13 | #7 | ↑6 | $12.01/M | $7.94M 月收入，收入排第三 |

---

## 关键洞察

### 1. Token 使用量 ≈ 价格的倒数

DeepSeek V4 Flash 处理了 6.42T token（第一），但收入只有 $739K（第十三）。Claude Sonnet 4.6 的 token 量只有它的一半，但收入是它的 **28倍**。如果只看 token 排行榜，你会以为 DeepSeek V4 Flash 是市场上最好的模型——但它更多是"最便宜的够用模型"。

### 2. 收入是最强但有偏差的质量信号

Anthropic 6个模型拿走了 $50.1M 月收入（占全市场66%），但 token 只占15%。这说明企业用户真的认为 Anthropic 的模型更好，愿意为此付出 10-20 倍的价格溢价。但这也意味着收入排行偏向"有预算的企业选什么"，不代表"最佳性价比"。

### 3. 采用广度是最干净的信号

开发者花时间集成一个模型，成本远高于切换价格——这意味着 apps 数量相对不受价格影响。在这个维度上，DeepSeek V4 Flash（36 apps）和 DeepSeek V4 Pro（34 apps）排在前两位，说明它们的流行不仅仅是价格效应。

### 4. 四个维度都靠前的才是"真正好用"

- **Claude Sonnet 4.6**：四个维度全部 Top 3，唯一一个。绝对统治力。
- **MiniMax M3**、**DeepSeek V4 Pro**：便宜但采用和领先度都强，不只是靠价格。
- **GPT-5.5**：收入第三但采用只有16个 app，主要靠少数高付费用户。

### 5. 中国模型：token 占51%，收入占7%

中国模型（MiniMax、DeepSeek、Xiaomi、Moonshot、Z.ai、Qwen）在 token 量上已经超过一半，但收入贡献不到十分之一。这个差距的核心解释是价格策略——中国模型普遍以 1/10 到 1/100 的价格竞争。例外是 MiniMax M3，在采用和质量领先维度都表现突出，不只是靠便宜。

### 6. 对投资者的启示

如果你在评估 AI 模型/公司的竞争力：
- **不要看 token 使用量排行榜**——它基本就是价格的倒数
- **看收入 + 采用广度的交叉**——Claude Sonnet 4.6 在两个维度都是 Top 3，这才是真正的护城河
- **注意"价格膨胀型"模型**——Nemotron 3 Super 的 token 量看起来很大，但下降17位后才是它的真实位置
- **关注价格弹性**——如果一个模型涨价后使用量骤降，说明用户忠诚度低；如果维持住了（如 Claude Opus 系列），说明切换成本高

---

## 供应商分布（Top 20）

| 供应商 | 模型数 | 总收入 | 总 Token | 平均价格 |
|--------|:------:|:------:|:--------:|:--------:|
| Anthropic | 6 | $50.1M | 6.0T | $8.35/M |
| OpenAI | 2 | $9.2M | 0.9T | $10.22/M |
| Google | 3 | $3.2M | 1.7T | $1.88/M |
| MiniMax | 1 | $2.5M | 4.5T | $0.55/M |
| DeepSeek | 2 | $2.3M | 9.3T | $0.25/M |
| StepFun | 1 | $1.3M | 2.9T | $0.47/M |
| Xiaomi | 1 | $0.7M | 1.3T | $0.56/M |
| MoonshotAI | 1 | $0.6M | 0.5T | $1.43/M |
| Z.ai | 1 | $0.6M | 0.4T | $1.52/M |
| Poolside | 1 | $0.5M | 2.1T | $0.26/M |
| Nex AGI | 1 | $0.4M | 0.8T | $0.46/M |

---

## 数据来源

- [CodeSOTA Agent Leaderboard](https://www.codesota.com/agentic/openrouter-models)（主数据源，46个 Agent 应用30天快照）
- [OpenRouter Rankings April 2026 - DigitalApplied](https://www.digitalapplied.com/blog/openrouter-rankings-april-2026-top-ai-models-data)
- [OpenRouter June 2026 Roundup - DigitalApplied](https://www.digitalapplied.com/blog/openrouter-new-models-june-2026-roundup-pricing-rankings)
- [OpenRouter: The Open Weight Models That Matter June 2026](https://openrouter.ai/blog/insights/the-open-weight-models-that-matter-june-2026/)
- [AICost: Chinese Models Dominate](https://aicost.org/blog/openrouter-monthly-token-usage-ranking-2026-chinese-models-dominate)
- [OpenRouter Data Page](https://openrouter.ai/data)
