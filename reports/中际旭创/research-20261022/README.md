# 中际旭创研究归档

主报告：[中际旭创投资研究报告](中际旭创投资研究报告-20261022.md)。

- 财务数据最新至2026H1，行情2026-10-21，研究日2026-10-22。
- inputs.json包含来源取数及分析假设，calculations.json包含推演结果，model.json供terminal_value.py复算。
- verification.txt保留财务交叉核对及估值输出；terminal-audit.txt为最终参数检查。
- audit-facts-verdict.txt仅确认样本数值，不能验证预测或合同履约。
- financial-trends.png为财务图表，英文轴使用CNY 100 million即人民币亿元。

从项目根目录复算：
```bash
python3 tools/terminal_value.py flip --name 中际旭创 --config reports/中际旭创/research-20261022/model.json --r .08 --delta .02 --currency CNY --g-shift 0 --rf .02
```

原研究脚本含/workspace/work临时路径，迁移后应先修改输出路径；原始计算记录仅供追溯，不依赖临时文件阅读主报告。
