# 来源与事实核验账本

访问日期均为北京时间 2026-10-20。以下原始文档及网页在本轮通过 web 打开读取，不把旧报告当作本轮证据。价格、财务第三方数据能独立检查发行人抄录错误，但同一份公告在 IR 和 HKEX 的副本不算两个独立来源。

| 来源 | 核验内容及定位 | 使用边界 |
|---|---|---|
| [2025 年报](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0422/2026042202118.pdf) | p4 四年摘要；p7—12 管理讨论；p101 损益、p106—107 现金流；IPO 日期；收入确认 | 原始来源；2025收入79.038m、净损失1871.617m、调整后损失250.856m；公允价值损失不能当现金烧损 |
| [招股书](https://www1.hkexnews.hk/listedco/listconews/sehk/2025/1231/2025123100025.pdf) | 财务摘要、附录I现金流；2022—2024；2022设备0.256m、2023 0.697m、2024 0.759m | 2021未取得系统披露，不编数 |
| [2026 中期报告](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0930/2026093002173.pdf) | p6损益；p7收入；p12控制权；p34资产负债；p38—39现金流；p41单一分部；p44诉讼 | H126收入116.573m、GP20.813m、CFO-318.106m、设备购买187.626m；非审计中期数据；没有Q3完整报表 |
| [S&P 财务](https://stockanalysis.com/quote/hkg/0100/financials/) | 收入、GP、净利、TTM、历史财务 | 2023 GP-.85m，2024 3.74m；2025 NI-1872m；四舍五入；分产品TTM合计不一致，拒用 |
| [S&P 现金流](https://stockanalysis.com/quote/hkg/0100/financials/cash-flow-statement/) | 历史CFO、capex、SBC、FCF | 2025 CFO-279.64m、SBC24.03m；TTM FCF-617.37m；只表示标准化简单FCF |
| [S&P 资产负债](https://stockanalysis.com/quote/hkg/0100/financials/balance-sheet/) | 现金930.91m等；流动资金池约1223m | 上市前优先股负债不能都称银行借款；设备字段可能含ROU，本文直接采用原表PPE74.913m |
| [九月月报](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/1002/2026100200077.pdf) | A271377649+B81102534=352480183，库存股0 | 原件已读取；数据库349.24m滞后0.919%，尚非精确二源一致 |
| [StockAnalysis 历史价](https://stockanalysis.com/quote/hkg/0100/history/) | Oct16 Close182.10 | 正规历史收盘 |
| [Investing 历史价](https://hk.investing.com/equities/minimax-group-inc-historical-data) | Oct16 Close182.10 | 独立行情源，与上项一致 |
| [港交所假期通告](https://www.hkex.com.hk/-/media/HKEX-Market/Services/Circulars-and-Notices/Participant-and-Members-Circulars/SEHK/2025/ce_SEHK_CT_075_2025.pdf) | 2026-10-19重阳翌日无交易 | 因而Oct16是最近收盘 |
| [Investing USDHKD](https://ca.investing.com/currencies/usd-hkd-historical-data) | Oct16 7.8478 | 市场参考，不是实时可成交 |
| [YCharts USDHKD](https://ycharts.com/indicators/us_dollar_to_hong_kong_dollar_exchange_rate) | 搜索摘要Oct16 7.848 | 完整页未返回历史表，第二来源强度有限，工具容差通过不等于无缺口 |
| [七月融资完成](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0716/2026071601147.pdf) | 配售净9443.71mHKD、CB净6433.3mHKD | 加六月现金只得历史备考，不是Oct余额 |
| [七月融资条款](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0710/2026071000027.pdf) | CB本金6500mHKD，初始转股335，赎回102.75% | 偿还及转股择一；零息不等于无资金成本 |
| [阿里云关联交易](https://www.hkexnews.hk/listedco/listconews/sehk/2026/0826/2026082601949.pdf) | 年度上限2026 300mUSD、2027 400m、2028 500m；融资用途预算 | 上限≠实际费用或最低支出；不能机械外推早期轻资产 |
| [九月奖励授予](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0929/2026092901775.pdf) | 2092198份，未来新股，未设业绩目标 | 不能直接加为九月末已发行；潜在约.594% |
| [M3.1 Flash](https://www.minimax.io/blog/minimax-m31f) | 10月19正式发布；API/MPlan/Code可用；权重和Pro稍后；输入.15输出.60缓存.015美元/百万token | 性能、速度、成本改善系公司主张，非本研究独立实测；全文只有限引用 |
| [M3模型卡](https://huggingface.co/MiniMaxAI/MiniMax-M3) | 模型架构、上下文与开放材料 | 技术说明不证明客户留存或利润 |
| [M3许可](https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/main/LICENSE)、[H3许可](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE) | 当前公开许可 | 未将开放权重误写为无条件MIT；不代替部署时逐条检查 |
| [管理团队](https://ir.minimax.io/corporate-information/management) | 创始及技术团队履历 | 页面部分职位可能滞后，职务以较新法定报告为准；履历不证明资本纪律 |

## 抽样事实人工回看

固定种子42取14点，其中6点有独立财务数据库对照：2023/2024毛利、2023/2025归母损益、2024简单FCF、2025 SBC。另4点为公司原始单源：2022/2025调整后损益、2025H1收入、2026H1毛利。四个模型点为2036悲观净利、悲观权益保留、悲观折现价格和乐观IRR，只复算，不填外部事实值。

原始股数、治理、融资合同、关联交易与新产品发布属于原始披露事实；无法取得同日精确独立二源的项目已在正文限制结论。没有把“将来如何赚钱”盖成事实验证PASS。完整最新诉讼卷宗、产品留存与分产品毛利、Oct现金余额仍缺失。
