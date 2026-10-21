# 阿里巴巴研究附件（2026-10-20）

[完整报告](../阿里巴巴研究报告-20261020.md)；金额单位人民币亿元、价格港元，最新财务为六月季报，股本为九月月报，股价为十月十六日收盘。

在仓库根目录复跑：

```bash
python3 reports/Alibaba/research-20261020/model.py
python3 tools/report_audit.py extract --report reports/Alibaba/阿里巴巴研究报告-20261020.md --ratio .15 --seed 42
python3 reports/Alibaba/research-20261020/audit.py
```

`model.py`使用Decimal，并调用`tools/financial_rigor.py`检查市值、关键数据差异、估值与情景。`model-results.json`记录输入、年度财务、FCFF路径、资产桥、反向估值和敏感性。所有前瞻数据均为条件假设，不表示概率分布。

`audit-results.json`是21个抽样点的来源/公式复核，13项有独立第二来源。部分为假设转录或公式，只验证其与模型一致。详见[audit-notes.md](audit-notes.md)，不应将工具PASS理解为全部数字双源、预测正确或投资结论有保证。
