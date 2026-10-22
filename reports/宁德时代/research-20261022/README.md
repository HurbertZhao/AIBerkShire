# 宁德时代研究归档

主报告：[宁德时代投资研究报告](宁德时代投资研究报告-20261022.md)。

- 研究日2026-10-22；财务更新至2026Q3；行情参考2026-10-21。
- 主报告以A股定价，A股等价市值不等于实际AH合计市值。
- inputs.json保存财务输入及情景假设；model.json保存十年敏感性参数。
- verification.txt为计算原始输出，flip-1pp.txt揭示7%至9%区间内仓位测试翻转。
- audit-facts-verdict.txt是事实样本核验，audit-assumptions.json单列未验证预测，audit-calculations-verdict.txt为模型复算。
- terminal-audit.txt为最终终值参数复检。财务图英文轴CNY 100 million指人民币亿元。

从项目根目录复算：
```bash
python3 tools/terminal_value.py flip --name 宁德时代 --config reports/宁德时代/research-20261022/model.json --r .08 --delta .01 --currency CNY --g-shift 0 --rf .02
```

原研究脚本含/workspace/work临时路径，迁移后需修改输出路径。旧港股召回池报告保留，本报告说明为何不沿用其旧买价与现金流判断。
