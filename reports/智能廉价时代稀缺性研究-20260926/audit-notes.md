# 审计说明

核验日期：2026-09-26。

## 结果与含义

- 固定种子 42、抽样比例 15%；工具从主报告识别 29 个候选数据点，抽中 5 项，全部核验。
- 扩展检查覆盖 25 个有效候选数据点，并人工补充 13 项正文数字，共 38 项数值比较；结果为 38 项通过、零警告、零失败。
- 另核验两项带“超过”的来源表述：AlphaFold 两亿个结构预测的下界、并网投运时长五年的下界。未把下界改写成精确点估计。
- 识别器的 4 项噪声分别是数据年份、引用编号 S07、报告日期与研究区间；排除原因逐项保存在 audit-results.json。随机抽中的五项没有被排除。
- 对低置信度的十年推断，采用反证与情景边界审读；不以算术 PASS 宣称预测已被证明。

工具的默认百分比容差不是对事实口径的验证。本文同时人工检查了单位、年份、样本、估计与预测、比较对象以及阈值。来源值由本次阅读填入；重新运行数值判决不会重新访问网站。

## 已处理的关键口径

1. 固定能力的使用成本，与前沿能力、每 token 价格、完整成功交付成本分开。
2. 降价千倍是题设；成本占比、弹性和独立错误概率是演示参数，不作为观测事实。
3. 客服研究采用 2024 年修订稿的 5,172 人和 15% 口径。
4. IEA 的 2030 年值属于预测，全部数据中心不等于 AI 专属负荷。
5. Berkeley Lab 的队列为发电与储能项目；没有改写成数据中心接电等待时间或缺电量。
6. 数据库条目是结构预测，不是已验证药物或实验成果。
7. Google 关于 AP2 的材料是公司公告，不证明实际采用率和独占权。
8. C2PA 溯源与内容真伪分开；链接目录和 PDF 自标版本存在差异，已在 sources.md 记录。
9. 中国数据政策原文与官方站点刊载的专家解读分开，不据此认定某家公司权利。
10. 租金现值只估算额外租金部分，不是任何完整企业估值，也没有生成个股买入价。

## 计算复现

从仓库根目录执行：

```bash
python3 reports/智能廉价时代稀缺性研究-20260926/calculations.py
python3 tools/report_audit.py extract --report reports/智能廉价时代稀缺性研究-20260926/README.md --seed 42
```

计算脚本采用 Python Decimal、40 位有效数字；非整数幂在该精度内舍入。它也调用 financial_rigor.py 的 calc 子命令，输出保存在 financial-rigor.txt。

当前 financial_rigor.py 的 calc 内部先计算 Python 原生数值表达式，再转为 Decimal，不能把其命令名当作全程十进制精确运算的保证。因此本报告以 calculations.py 中直接使用 Decimal 的结果为主，仓库工具作为第二次数值对照；未修改共享工具。

完整候选清单、样本编号与主报告 SHA-256 在 audit-extracted.json；来源/公式映射与排除项在 audit-results.json；工具判决在 audit-verdict.txt。

如需重放已填数值的判决：

```python
import json
import subprocess
import sys
from pathlib import Path

p = Path("reports/智能廉价时代稀缺性研究-20260926")
checks = json.loads((p / "audit-results.json").read_text())["checks"]
subprocess.run([
    sys.executable, "tools/report_audit.py", "verdict",
    "--results", json.dumps(checks, ensure_ascii=False),
    "--report", str(p / "README.md"), "--output-json"
], check=True)
```

这只复现比较，不替代再次查证原始资料。没有将两个引用同一底层数据的页面包装成独立双源。

## 审读结论

报告可作为明确题设下的研究发布。它给出可检验的机制、反例与投资筛选方向；没有证明未来会按某一路径发展，没有核验具体公司的当前估值，也没有把哲学上的珍贵直接换算成股票回报。
