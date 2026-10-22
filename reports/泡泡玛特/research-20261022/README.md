# 泡泡玛特研究（2026-10-22）

主报告：[泡泡玛特投资研究报告](泡泡玛特投资研究报告-20261022.md)。完整保留既有日期报告。

结论：空仓观望，小仓有条件持有；基准价值约140港元，25%安全边际价约105港元。价格、盈利、汇率及风险假设见正文，不把模型区间当作确定回报。

本目录包含可复算模型、五年财务图、双源校对日志、随机及定向抽检、终值约束和敏感性输出。统一报价为10/21收盘129.8港元。

从项目根目录重算：

```bash
python3 reports/泡泡玛特/research-20261022/model.py
python3 reports/泡泡玛特/research-20261022/audit.py
```

- [模型结果](model-results.json)
- [验证原始输出](financial-rigor.txt)
- [来源与限制](sources.md)
- [随机抽样清单](audit-extract.txt)
- [抽检分类](audit-dispositions.json)
- [抽检判决](audit-verdict.txt)
- [十年敏感性](sensitivity.txt)
- [最终终值审计](terminal-final-audit.txt)

抽检覆盖财报摘录、假设录入与计算，分类披露；工具通过不等于所有明细均获独立双源核查，更不等于未来预测获验证。Q3样本、机构预测和官方实绩的区别尤其重要。
