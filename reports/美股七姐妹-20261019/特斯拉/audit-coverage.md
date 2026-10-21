# 数据抽检覆盖说明

随机种子42，15%抽样（最多30项）。没有改变抽样种子来回避差异。

{
  "external_dual_or_derived": 14,
  "model_recalculation_or_assumption": 7,
  "parser_false_positive": 3,
  "single_source_or_derived": 6
}

外部双源包括使用两源输入的派生计算；单源/同发行人重复披露不称独立双源。模型项仅检查假设转写和运算一致性，不意味着预测真实。三项解析误报保留在分类文件而排除数字判决；没有空值冒充通过。原始第三方重分类差异另见validation-log.txt及正文，未被悄悄改为一致。

核心事实收入、净利、现金、股价、股本和FCF另由financial_rigor检查；季度细分毛利成本仍有独立第二来源缺口，不能将本次准出视为全报告审计。
