# 快手+可灵 2036 年利润推演（三情景）。输入全部来自一手原件：
# 2025 年报、2026 中期业绩公告、2026-07-02 可灵增资公告、港交所 2026-10-07 月报表。
# 这是推演不是预测，用于把"护城河判断"翻译成数字，检验内部一致性。
import json

# ---------- 一手输入（人民币亿元） ----------
rev_2025 = 1427.76          # 2025 总收入
adj_np_2025 = 206.47        # 2025 经调整净利润
kling_rev_2025 = 11.0       # 可灵 2025 收入（增资公告"约 11 亿"）
kling_loss_2025 = 19.0      # 可灵 2025 净亏（增资公告未审计数）
adj_np_h1_2026 = 72.87      # 2026H1 经调整净利润
adj_np_q2_2026 = 39.13      # 2026Q2 经调整净利润
kling_rev_q1 = 6.5; kling_rev_q2 = 8.5
capex_2024, capex_2025, capex_h1_2026 = 80.63, 149.42, 180.0
usable_cash = 1213.0        # 2026-06-30 可利用资金（公司口径）
borrowings = 273.62; lease = 116.72
shares = 43.0415            # 亿股，2026-09-30
price_hkd = 29.30; hkd_cny = 0.8542
usd_cny_deal = 138.236/20.282   # 增资公告隐含汇率 6.816
kling_post_usd = 180.0; ks_stake = 0.6833

# ---------- 现状 ----------
mkt_cap_cny = shares*price_hkd*hkd_cny
net_cash = usable_cash - borrowings            # 不扣租赁
net_cash_strict = net_cash - lease
main_adj_2025 = adj_np_2025 + kling_loss_2025   # 主业（剔除可灵亏损）2025 经调整净利
# 2026 运行率：Q2 经调整 39 亿年化；可灵亏损假设与 2025 持平（H1 约 10 亿），主业年化约 170 亿
main_run_2026 = adj_np_q2_2026*4 + 19.0
kling_stake_cny = kling_post_usd*usd_cny_deal*ks_stake

# ---------- 2036 三情景 ----------
# 主业：2026 运行率为基数，年复合增速 g；可灵：2026 收入约 38 亿（Q1 6.5+Q2 8.5+下半年按季度 +12% 推）为基数
kling_rev_2026 = kling_rev_q1 + kling_rev_q2 + kling_rev_q2*1.12 + kling_rev_q2*1.12**2
scen = {
 "悲观(直播继续萎缩/广告低增/可灵被价格战吃掉)": dict(g_main=-0.03, kling_cagr=0.05, kling_margin=0.0, p=0.30),
 "中性(主业横盘/可灵成中等规模工具公司)":          dict(g_main=0.015, kling_cagr=0.20, kling_margin=0.15, p=0.50),
 "乐观(生成式推荐抬高广告/可灵留在寡头)":          dict(g_main=0.04,  kling_cagr=0.30, kling_margin=0.20, p=0.20),
}
out = {}
for k,s in scen.items():
    main_2036 = main_run_2026*(1+s["g_main"])**10
    kling_rev_2036 = kling_rev_2026*(1+s["kling_cagr"])**10
    kling_np_2036 = kling_rev_2036*s["kling_margin"]
    total = main_2036 + kling_np_2036*ks_stake
    out[k] = dict(主业2036=round(main_2036), 可灵收入2036=round(kling_rev_2036), 可灵净利2036=round(kling_np_2036),
                  归母合计2036=round(total), 概率=s["p"])
ev = sum(v["归母合计2036"]*v["概率"] for v in out.values())

res = dict(
  现状=dict(市值亿元=round(mkt_cap_cny), 净现金不扣租赁=round(net_cash), 净现金扣租赁=round(net_cash_strict),
           市值减净现金=round(mkt_cap_cny-net_cash), 可灵权益按投后=round(kling_stake_cny),
           主业2025经调整剔可灵=round(main_adj_2025), 主业2026运行率=round(main_run_2026),
           可灵2026收入推算=round(kling_rev_2026,1), 市值减净现金_对_主业运行率倍数=round((mkt_cap_cny-net_cash)/main_run_2026,2)),
  情景2036=out, 概率加权2036=round(ev),
  与2025比=dict(悲观=round(out[list(out)[0]]["归母合计2036"]/adj_np_2025,2), 中性=round(out[list(out)[1]]["归母合计2036"]/adj_np_2025,2), 乐观=round(out[list(out)[2]]["归母合计2036"]/adj_np_2025,2)))
json.dump(res, open("model-results.json","w"), ensure_ascii=False, indent=2)
print(json.dumps(res, ensure_ascii=False, indent=2))
