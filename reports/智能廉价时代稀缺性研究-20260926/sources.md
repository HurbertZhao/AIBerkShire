# 来源与证据边界

检索与访问日期：2026-09-26，北京时间。这里只保存研究使用的事实与口径，不复制来源全文。

正文编号指向下列资料。统计、研究估计、机构预测、公司公告、政策与研究者推断分别处理；同一机构不同页面不算独立双源。

## S01 · 固定能力成本

- 来源：Luke Emberson、David Roodman，Epoch AI，[The plunging price of thought](https://epoch.ai/publications/the-plunging-price-of-thought)，2026-09-22。
- 使用事实：作者对自 2023 年以来给定测试表现的成本估计，约每季度下降 47%、每年降低至此前约十三分之一。正文只使用约每年 13 倍。
- 口径：模型与推理预算所形成的最低费用—表现边界；主要涵盖五组数学、科学与博弈测试。
- 限制：这不是所有企业实际支付价格指数，更不是完整现实交付成本。基准优化、数据缺口、模型切换成本和不同任务差异均有限制。作者自己讨论这些限制。
- 证据类型：研究估计；成本千倍下降是用户设定，不由该研究“验证”。

## S02 · 可靠性与任务时长

- 来源：Thomas Kwa，METR，[Clarifying limitations of time horizon](https://metr.org/notes/2026-01-22-time-horizon-limitations/)，2026-01-22。
- 使用事实：任务时长指标用人类基准所需时间标定任务，不是 AI 实际可以自主运行多久；一定成功率上的时长也不能直接等同于可委托的工作范围。
- 限制：具体模型时长变化很快，本文不沿用该说明中的旧模型排行与具体小时数。
- 证据类型：原研究团队方法说明。

## S03 · 能力分布不均

- 来源：Stanford HAI，[The 2026 AI Index Report](https://hai.stanford.edu/ai-index/2026-ai-index-report)，2026 版。
- 使用事实：技术进步在不同任务之间仍存在明显差异，研究报告用多个测试说明这一点。
- 限制：本文不将其组织采用率、消费者福利估计或单项分数外推至 2036 年。页面是研究汇编入口，具体测试仍有各自样本和口径。
- 证据类型：学术机构年度汇编。

## S04 · 数据中心用电及供给响应

- 来源：IEA，[Key Questions on Energy and AI](https://www.iea.org/reports/key-questions-on-energy-and-ai)，2026-04-16；使用其[执行摘要](https://www.iea.org/reports/key-questions-on-energy-and-ai/executive-summary)。
- 使用数字：2025 年全球数据中心用电约 485 TWh；2030 年约 950 TWh 是该报告更新预测。
- 口径：全部数据中心，不是只统计生成式 AI。2025 数值为机构对历史用电的估计；2030 是条件预测。
- 定性证据：机构同时讨论基础设施约束与 AI 改善能源系统效率的可能性。
- 限制：不外推 2036 年总量，不由此推荐整个能源板块；电力、接入、资本回报必须分别分析。
- 证据类型：国际机构估计与预测。同机构主题页重复该数字，不算第二独立来源。

## S05 · 发电与储能并网

- 来源：Lawrence Berkeley National Laboratory，[Queued Up，2026 Edition](https://emp.lbl.gov/queues)，页面说明 PDF 于 2026 年 6 月发布，数据截至 2025 年底。
- 使用数字：发电 1,312 GW 加储能约 749 GW，合计约 2,061 GW；正文保守表述为超过 2,060 GW。对有数据地区，2025 年建成项目从申请并网到商业投运的中位时长超过五年。
- 口径：发电与储能申请接入输电网；排队项目多数未必建成。这既不是即时缺电量，也不是数据中心负荷申请接电时长。
- 版本差异：2026 年 7 月新闻稿与当前项目页对“已签或草签并网协议但未投运”的容量数字有差异，本文未使用该字段。正文只使用两者不冲突的总队列规模及项目页的投运时长。
- 证据类型：实验室汇编的观测数据。有选择偏差的投运项目时长，不代表所有申请项目。

## S06 · 工作场景的生产率改善

- 来源：Erik Brynjolfsson、Danielle Li、Lindsey Raymond，[Generative AI at Work，arXiv v2](https://arxiv.org/abs/2304.11771v2)，修订日期 2024-11-06。
- 使用数字：5,172 名客服人员样本；每小时解决问题数平均提高 15%。
- 口径：分阶段引入 AI 助手的客服场景，群体之间效果不同。本文用修订稿的样本与数字，不混入较早稿件的其他数字。
- 限制：不是随机代表整个经济的样本；不推算工资、就业或 GDP。
- 证据类型：作者原论文。

## S07 · 职业暴露

- 来源：ILO–NASK，[Generative AI and jobs: A 2025 update](https://www.ilo.org/publications/generative-ai-and-jobs-2025-update)，2025-05-20。
- 使用数字：约四分之一全球就业位于具有某种生成式 AI 暴露的职业。
- 口径：任务与职业暴露的估计，不是已经发生的岗位损失，不是十年后模型能力假设下的失业预测。
- 限制：本文不与其他机构不同定义的 AI 暴露比例平均或混用。
- 证据类型：国际组织研究估计。

## S08 · 结构预测与真实结果

- 来源：EMBL-EBI，[New AlphaFold Database entry pages](https://www.ebi.ac.uk/about/news/updates-from-data-resources/new-alphafold-database-entry-pages/)，2025-08-07。
- 使用数字：该机构说明数据库提供超过两亿个蛋白结构预测。
- 口径：预测，不是两亿项新实验，也不是药物数量。正文保留这个区别。
- 限制：用来说明可规模化数字预测的供给，不用来估计某家药企的利润或临床成功率。
- 证据类型：数据库运营机构披露。

## S09 · 专业能力扩散

- 来源：David Autor，[Applying AI to Rebuild Middle Class Jobs](https://www.nber.org/papers/w32140)，NBER Working Paper 32140，2024-02。
- 使用观点：AI 可能扩大具备互补知识的劳动者能够从事的专业任务范围。
- 限制：是一条有理论和经验讨论支持的可能路径，不是劳动收入必然上升的结论。
- 证据类型：经济学研究与政策讨论。正文明确这是研究者观点。

## S10 · 临床研究需要什么证据

- 来源：FDA，[Step 3: Clinical Research](https://www.fda.gov/patients/drug-development-process/step-3-clinical-research)，访问于截止日。
- 使用事实：临床研究分阶段积累安全性、有效性与不良反应证据。
- 限制：未引用页面上的阶段成功比例与典型时长，也不把当前美国监管流程当作所有国家或 2036 年的统一规则。
- 证据类型：监管机构流程说明，不提供个案法律或医疗意见。

## S11 · 配套组织投资

- 来源：Erik Brynjolfsson、Daniel Rock、Chad Syverson，[The Productivity J-Curve: How Intangibles Complement General Purpose Technologies](https://www.nber.org/papers/w25148)，2018 年工作论文，2020 年修订，2021 年发表。
- 使用机制：通用技术常需配套流程、商业模式与人力资本投入，部分无形投资与收益存在测量和时间差。
- 限制：未引用论文中的历史 TFP 数字；不能用该机制免除项目回报核验。
- 证据类型：理论与历史经验研究。

## S12 · 代理交易的授权层

- 来源：Google，[We’re donating Agent Payments Protocol to the FIDO Alliance…](https://blog.google/products-and-platforms/platforms/google-pay/agent-payments-protocol-fido-alliance/)，2026-04-28。
- 使用事实：Google 宣布向 FIDO Alliance 移交 AP2，并介绍基于预先授权的自主交易更新。
- 限制：产品与治理公告证明该议题正在形成标准，不证明普及率、实际收入、无风险执行，或某家公司将垄断入口。移交的治理完成度未另外核验，正文用“宣布”表述。
- 证据类型：公司一手公告，有商业宣传动机。

## S13 · 溯源不是事实真伪的完整证明

- 来源：C2PA，[C2PA and Content Credentials Explainer](https://spec.c2pa.org/specifications/specifications/2.3/explainer/_attachments/Explainer.pdf)；[FAQ](https://c2pa.org/faqs/)用于交叉理解技术范围。链接目录标为 2.3，实际 PDF 封面自标 2.2、2025-12-11；本文引用 PDF 第 7.2.2 节的原则说明，不据目录名声称版本。
- 使用事实：来源、历史与完整性信息本身不能断定内容真实、准确或符合事实。
- 限制：不声称该标准能防止所有伪造，也不声称数字签名本身保证现实陈述为真。两个文档来自同一标准组织，不计为独立来源。
- 证据类型：标准制定组织技术说明。

## S14 · 数据权利的分置

- 来源：中共中央、国务院，[关于构建数据基础制度更好发挥数据要素作用的意见](https://app.www.gov.cn/govdata/gov/202212/19/495422/article.html)，2022-12-19 公布。
- 使用事实：提出数据资源持有、加工使用、产品经营等权利分置的运行机制。
- 限制：政策原则不直接证明某项数据的具体权属或排他性。个别公司的权利要查合同、来源、用途与适用规则。
- 证据类型：政策原文。

## S15 · 数据权利的解释边界

- 来源：张新宝，[深入贯彻落实数据产权制度 依法保障各方主体合法权益](https://www.nda.gov.cn/sjj/zwgk/zjjd/0315/20260315130425237481780_pc.html)，国家数据局刊载，2026-03-15。
- 使用观点：区分持有、使用和经营等权利，讨论数据非排他性与流转。
- 限制：官方站点刊载的专家解读，不冒充具体法条、司法判决或新设所有权。
- 证据类型：专家解释，证据地位低于直接适用的法律和裁判。

## S16 · 从任务到宏观

- 来源：Daron Acemoglu，[The Simple Macroeconomics of AI](https://www.nber.org/papers/w32487)，NBER Working Paper 32487，2024-05，后发表于 Economic Policy。
- 使用机制：宏观生产率效应应考虑受影响任务范围、任务成本节约和互补关系。
- 限制：本文未采用该论文的十年 TFP 数值作为本题预测，更未把它当作任何未来技术的上限。
- 证据类型：任务框架下的条件模型。

## 本报告自己的假设与推断

以下内容没有冒充外部事实：

1. 千倍降价是用户给定前提；年度降幅是数学换算。
2. 成本占比、需求弹性、独立错误概率与租金现值都是演示参数。
3. 对客户授权、可信交付、真实反馈的排序是研究判断。
4. 三个 2036 年情景不分配概率，也不是已发生的事实。
5. 人的健康时间、真实关系和自主性的重要性含有价值判断，不能用单一市场价格证明。
6. 商业模式观察表不包含任何已核验的个股投资建议。

主报告链接保持集中且就近；复核者可据本文件追溯口径。未将旧仓库文章的具体预测与数字当作本次证据。
