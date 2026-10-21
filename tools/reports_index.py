#!/usr/bin/env python3
"""扫描 reports/ 中已纳入 Git 的报告，生成研究索引。

产出两份文件：
  reports/index.json  —— 机器可读清单，供脚本/网页消费
  reports/README.md   —— 人读索引，GitHub 上的报告入口

元数据来源优先级：文件自带 YAML front-matter > 文件名 > 正文 > git 提交时间。
不修改任何报告文件本身。
新报告需先 git add；未跟踪、被忽略或仅 intent-to-add 的文件不进入公开索引。

用法：
  python3 tools/reports_index.py            # 生成索引
  python3 tools/reports_index.py --check     # 只检查是否需要更新（CI 用，不写盘）
"""
import json
import os
import re
import subprocess
import sys
from collections import defaultdict, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports")
CONFIG = os.path.join(REPORTS, "_index", "config.json")

DATE_IN_NAME = re.compile(r"(20[2-3]\d)(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])")
DATE_IN_BODY = re.compile(r"(20[2-3]\d)[-/年](\d{1,2})[-/月](\d{1,2})")
H1 = re.compile(r"^#\s+(.+?)\s*$")

# 报告类型：按顺序匹配，先命中先算
TYPE_RULES = [
    ("底稿", ["研究底稿", "核验", "评审", "verify", "底稿", "对账"]),  # 审计/复核类成品报告不在此列，中间产物由 is_draft 识别
    ("财报", ["earnings", "财报", "中报", "年报", "季报", "业绩", "电话会", "q1", "q2", "q3", "q4"]),
    ("公众号", ["公众号", "wechat", "推文"]),
    ("深度系列", ["看懂", "深度研究", "deep-dive", "深度投研"]),
    ("横评对比", ["横评", "对比", "vs", "对决", "pk", "换仓", "轮动"]),
    ("组织管理", ["7s", "管理层", "组织", "management"]),
    ("估值仓位", ["估值", "赔率", "凯利", "仓位", "valuation", "fair_value", "终值"]),
    ("筛选", ["funnel", "筛选", "召回", "screen", "候选池"]),
]


def load_config():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def git_report_paths():
    """Git 暂存区里的路径；不把尚未加入提交的本地稿件发布到索引。"""
    try:
        raw = subprocess.check_output(
            ["git", "ls-files", "--cached", "-z", "--", "reports/"],
            cwd=ROOT, stderr=subprocess.DEVNULL)
        # git add -N 会出现在 ls-files 中，但实际内容不会进入下一次提交。
        intent = subprocess.check_output(
            ["git", "diff", "--name-only", "--diff-filter=A", "-z", "--", "reports/"],
            cwd=ROOT, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("无法读取 Git 暂存区，已停止生成，避免发布未提交的本地文件") from exc
    paths = {os.fsdecode(p) for p in raw.split(b"\0") if p}
    return paths - {os.fsdecode(p) for p in intent.split(b"\0") if p}


def git_dates():
    """一次遍历拿到每个文件的最近提交日期。"""
    out = {}
    try:
        raw = subprocess.check_output(
            ["git", "-c", "core.quotePath=false", "log",
             "--pretty=format:__D__%ad", "--date=short", "--name-only"],
            cwd=ROOT, stderr=subprocess.DEVNULL,
        ).decode("utf-8", "replace")
    except Exception:
        return out
    cur = None
    for line in raw.splitlines():
        if line.startswith("__D__"):
            cur = line[5:].strip()
        elif line.strip() and cur and line not in out:
            out[line] = cur
    return out


def parse_front_matter(lines):
    """极简 YAML front-matter 解析，只认首行 --- 到次个 --- 之间的 key: value。"""
    if not lines or lines[0].strip() != "---":
        return {}, 0
    meta = {}
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return meta, i + 1
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip().strip("\"'")
    return {}, 0


def read_head(path, n=40):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return [next(f).rstrip("\n") for _ in range(n)]
    except StopIteration:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read().splitlines()
    except Exception:
        return []


def guess_type(name, relpath):
    hay = (name + " " + relpath).lower()
    for label, keys in TYPE_RULES:
        for k in keys:
            if k in hay:
                return label
    return "研究"


def is_draft(relr, cfg):
    """中间产物判定：证据、审计、复算、底稿等不进人读索引。规则见 config.json 的 drafts。"""
    rules = cfg.get("drafts") or {}
    parts = relr.split("/")
    stem = re.sub(r"\.md$", "", parts[-1])
    if "公众号" in stem:
        return False
    dirs = [d.lower() for d in parts[:-1]]
    draft_dirs = {d.lower() for d in rules.get("dirs", [])}
    if any(d in draft_dirs for d in dirs):
        return True
    for d in parts[:-1]:
        base = display_name(d)
        if any(base.endswith(suf) for suf in rules.get("dir_suffixes", [])):
            return True
    stem = display_name(stem).lower()
    return any(re.search(pat, stem) for pat in rules.get("file_patterns", []))


def guess_date(meta, filename, parent, head, gitmap, relpath):
    if meta.get("date"):
        d = meta["date"].replace("/", "-")
        if re.match(r"^20\d\d-\d\d-\d\d$", d):
            return d, "front-matter"
    for src in (filename, parent):
        m = DATE_IN_NAME.search(src)
        if m:
            return "%s-%s-%s" % m.groups(), "文件名"
    for line in head[:15]:
        m = DATE_IN_BODY.search(line)
        if m:
            y, mo, dy = m.groups()
            return "%s-%02d-%02d" % (y, int(mo), int(dy)), "正文"
    if relpath in gitmap:
        return gitmap[relpath], "git"
    return "", "缺失"


def bucket_of(top, cfg):
    top = cfg["aliases"].get(top, top)
    if top in cfg["screens"]:
        return "筛选池", top
    if top in cfg["themes"]:
        return "专题", top
    if top in cfg["masters"]:
        return "大师研究", top
    if top in cfg["other"]:
        return "其他", top
    return "公司", top


def collect(cfg, gitmap):
    items = []
    unknown_dirs = set()
    tracked = git_report_paths()
    excluded = []
    known = (set(cfg["themes"]) | set(cfg["masters"]) | set(cfg["screens"])
             | set(cfg["other"]) | set(cfg.get("companies", [])))
    for dirpath, dirnames, filenames in os.walk(REPORTS):
        dirnames[:] = [d for d in dirnames if d not in cfg["skip_dirs"]]
        for fn in filenames:
            if not fn.endswith(".md") or fn in cfg["skip_files"]:
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            if rel not in tracked:
                excluded.append(rel)
                continue
            relr = os.path.relpath(full, REPORTS).replace(os.sep, "/")
            parts = relr.split("/")
            top = parts[0] if len(parts) > 1 else ""
            head = read_head(full)
            meta, _ = parse_front_matter(head)
            title = meta.get("title", "")
            if not title:
                for line in head:
                    m = H1.match(line)
                    if m:
                        title = m.group(1)
                        break
            if not title:
                title = re.sub(r"-?\d{8}$", "", fn[:-3])
            title = re.sub(r"[*`]", "", title).strip()

            if top:
                bucket, group = bucket_of(top, cfg)
                if bucket == "公司" and top not in known and top not in cfg["aliases"]:
                    unknown_dirs.add(top)
            else:
                bucket, group = "专题", "综合与横评"

            date, dsrc = guess_date(meta, fn, parts[-2] if len(parts) > 1 else "", head, gitmap, rel)
            series = parts[1] if len(parts) > 2 else ""
            rtype = meta.get("type") or ("底稿" if is_draft(relr, cfg) else guess_type(fn, relr))
            items.append(OrderedDict([
                ("title", title),
                ("path", rel),
                ("bucket", bucket),
                ("group", group),
                ("series", series),
                ("type", rtype),
                ("date", date),
                ("date_source", dsrc),
                ("ticker", cfg["tickers"].get(group, "")),
            ]))
    items.sort(key=lambda x: (x["date"], x["path"]), reverse=True)
    return items, sorted(unknown_dirs), sorted(excluded)


def display_name(name):
    return re.sub(r"-20[2-3]\d[01]\d[0-3]\d$", "", name) or name


UNSAFE = {"%": "%25", " ": "%20", "(": "%28", ")": "%29", "#": "%23", "?": "%3F",
          "[": "%5B", "]": "%5D", "<": "%3C", ">": "%3E", '"': "%22"}


def url_path(path):
    """只转义会破坏 Markdown 链接的字符，中文保持原样以便肉眼核对。"""
    return "".join(UNSAFE.get(c, c) for c in path)


def md_link(text, path):
    text = text.replace("[", "〔").replace("]", "〕").replace("|", "丨")
    return "[%s](%s)" % (text, url_path(path.replace("reports/", "", 1)))


def published(items):
    """人读索引只收成品报告；底稿、证据、审计等中间产物只留在 index.json。"""
    return [i for i in items if i["type"] != "底稿"]


def render(items, cfg):
    items = published(items)
    by_bucket = defaultdict(lambda: defaultdict(list))
    for it in items:
        by_bucket[it["bucket"]][it["group"]].append(it)

    latest = max((i["date"] for i in items if i["date"]), default="")
    L = []
    L.append("# 研究报告索引")
    L.append("")
    L.append("> 本文件由 `tools/reports_index.py` 自动生成，请勿手工编辑。")
    L.append("> 新增报告先 `git add`，再运行 `python3 tools/reports_index.py`，将报告与索引一并提交。")
    L.append("> 只收录成品报告；证据、审计、复算、底稿等中间产物不在此列，完整清单见 `index.json`。")
    L.append("")
    L.append("**%d 份报告** · **%d 家公司** · **%d 个专题** · 最近更新 %s" % (
        len(items), len(by_bucket["公司"]), len(by_bucket["专题"]), latest or "—"))
    L.append("")
    L.append("[最近更新](#最近更新) · [按公司](#按公司) · [专题研究](#专题研究) · "
             "[大师研究](#大师研究) · [筛选池](#筛选池)")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## 最近更新")
    L.append("")
    L.append("| 日期 | 报告 | 归属 | 类型 |")
    L.append("|------|------|------|------|")
    seen = defaultdict(int)
    shown = []
    for it in items:
        if it["bucket"] == "筛选池":
            continue
        key = it["group"] + "/" + (it["series"] or "")
        if seen[key] >= 3:
            continue
        seen[key] += 1
        shown.append(it)
        if len(shown) >= 40:
            break
    for it in shown:
        L.append("| %s | %s | %s | %s |" % (
            it["date"] or "—", md_link(it["title"], it["path"]),
            display_name(it["group"]), it["type"]))
    L.append("")
    L.append("---")
    L.append("")

    def section(title, bucket, anchor_note=""):
        groups = by_bucket.get(bucket, {})
        if not groups:
            return
        L.append("## %s" % title)
        L.append("")
        if anchor_note:
            L.append(anchor_note)
            L.append("")
        order = sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        for name, lst in order:
            lst = sorted(lst, key=lambda x: (x["date"], x["title"]), reverse=True)
            last = lst[0]["date"] or "—"
            L.append("<details>")
            L.append("<summary><b>%s</b> · %d 份 · 最近 %s</summary>" % (
                display_name(name), len(lst), last))
            L.append("")
            cur_series = None
            for it in lst:
                if it["series"] and it["series"] != cur_series:
                    cur_series = it["series"]
                    L.append("")
                    L.append("*%s*" % display_name(cur_series))
                    L.append("")
                elif not it["series"] and cur_series is not None:
                    cur_series = None
                    L.append("")
                L.append("- `%s` %s — %s" % (it["date"] or "  —  ", md_link(it["title"], it["path"]), it["type"]))
            L.append("")
            L.append("</details>")
            L.append("")
        L.append("---")
        L.append("")

    section("按公司", "公司")
    section("专题研究", "专题")
    section("大师研究", "大师研究")

    screens = by_bucket.get("筛选池", {})
    if screens:
        L.append("## 筛选池")
        L.append("")
        L.append("> 以下是筛选与推演的**中间产物**，不是成品报告，供复现与追溯用。")
        L.append("")
        L.append("| 池子 | 文件数 | 最近更新 |")
        L.append("|------|--------|----------|")
        for name, lst in sorted(screens.items(), key=lambda kv: -len(kv[1])):
            last = max((x["date"] for x in lst if x["date"]), default="—")
            L.append("| [%s](%s) | %d | %s |" % (
                display_name(name), url_path(name), len(lst), last))
        L.append("")
    return "\n".join(L) + "\n"


ROOT_README = os.path.join(ROOT, "README.md")
MARK_START = "<!-- REPORTS-INDEX:START 由 tools/reports_index.py 自动更新，勿手改 -->"
MARK_END = "<!-- REPORTS-INDEX:END -->"
BANNER_START = "<!-- REPORTS-BANNER:START 由 tools/reports_index.py 自动更新，勿手改 -->"
BANNER_END = "<!-- REPORTS-BANNER:END -->"


def index_stats(items):
    items = published(items)
    groups = defaultdict(set)
    for it in items:
        if it["bucket"] != "筛选池":
            groups[it["bucket"]].add(it["group"])
    latest = max((i["date"] for i in items if i["date"]), default="—")
    return len(items), len(groups["公司"]), len(groups["专题"]), latest


def root_banner_block(items):
    """首屏横幅：仓库日更内容的入口，位置在标题区，不在正文深处。"""
    total, companies, themes, latest = index_stats(items)
    return "\n".join([
        BANNER_START,
        "",
        "> 📖 **想读报告，用 [阅读站](https://xbtlin.github.io/ai-berkshire/)**：成品报告按公司、专题、时间整理，"
        "电脑和手机都好读，可搜索、记住阅读进度。",
        ">",
        "> 📊 全部 %d 份报告（含底稿）· %d 家公司 · %d 个专题，GitHub 上的完整目录见 [研究报告索引](reports/README.md)，更新至 %s。"
        % (total, companies, themes, latest),
        "",
        BANNER_END,
    ])


def root_readme_block(items):
    """生成根 README 里的『研究索引』入口块。"""
    total, companies, themes, latest = index_stats(items)
    fresh = [i for i in published(items) if i["bucket"] != "筛选池"][:8]

    L = [MARK_START, ""]
    L.append("**📊 [全部研究索引 →](reports/README.md)** ｜ %d 份报告 · %d 家公司 · %d 个专题 · 更新至 %s"
             % (total, companies, themes, latest))
    L.append("")
    L.append("最近更新：")
    L.append("")
    L.append("| 日期 | 报告 | 归属 |")
    L.append("|------|------|------|")
    seen = defaultdict(int)
    rows = 0
    for it in fresh:
        if seen[it["group"]] >= 2:
            continue
        seen[it["group"]] += 1
        rows += 1
        L.append("| %s | [%s](%s) | %s |" % (
            it["date"] or "—",
            it["title"].replace("[", "〔").replace("]", "〕").replace("|", "丨"),
            url_path(it["path"]), display_name(it["group"])))
        if rows >= 6:
            break
    L.append("")
    L.append(MARK_END)
    return "\n".join(L)


def update_root_readme(items):
    if not os.path.exists(ROOT_README):
        return None, None
    old = open(ROOT_README, encoding="utf-8").read()
    new = old
    for start, end, builder in (
        (BANNER_START, BANNER_END, root_banner_block),
        (MARK_START, MARK_END, root_readme_block),
    ):
        if start in new and end in new:
            head = new.split(start)[0]
            tail = new.split(end, 1)[1]
            new = head + builder(items) + tail
    return old, new


def main():
    check = "--check" in sys.argv
    cfg = load_config()
    try:
        items, unknown, excluded = collect(cfg, git_dates())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    index_path = os.path.join(REPORTS, "index.json")
    readme_path = os.path.join(REPORTS, "README.md")
    payload = json.dumps(
        {"count": len(items), "published": len(published(items)),
         "drafts": len(items) - len(published(items)), "reports": items},
        ensure_ascii=False, indent=2) + "\n"
    readme = render(items, cfg)
    root_old, root_new = update_root_readme(items)

    if check:
        stale = []
        pairs = [(index_path, payload), (readme_path, readme)]
        if root_old is not None:
            pairs.append((ROOT_README, root_new))
        for p, new in pairs:
            old = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
            if old != new:
                stale.append(os.path.basename(p))
        if stale:
            print("索引已过期，请运行 python3 tools/reports_index.py：" + "、".join(stale))
            return 1
        print("索引是最新的")
        return 0

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(payload)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)
    if root_new is not None and root_new != root_old:
        with open(ROOT_README, "w", encoding="utf-8") as f:
            f.write(root_new)
        print("已刷新根 README 的研究索引入口块")

    missing = [i for i in items if not i["date"]]
    print("已索引 %d 份报告 -> reports/README.md、reports/index.json（其中成品 %d 份，底稿等中间产物 %d 份只进 index.json）"
          % (len(items), len(published(items)), len(items) - len(published(items))))
    if missing:
        print("  无法确定日期：%d 份" % len(missing))
    if excluded:
        print("  未纳入 Git 的本地报告（含被忽略文件）已排除：%d 份；如需发布，请先 git add 再生成索引" % len(excluded))
    if unknown:
        print("  未在 config.json 的 companies 名单里的新目录（默认按公司处理）：%s" % "、".join(unknown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
