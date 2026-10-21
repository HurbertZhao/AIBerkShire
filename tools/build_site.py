#!/usr/bin/env python3
"""把仓库里已入库的报告生成静态阅读站点，兼容电脑、手机与墨水屏阅读器。

输入：reports/index.json（由 tools/reports_index.py 生成）、投资炼丹/、实盘记录/ 下已纳入 Git 的 Markdown。
输出：site/ 目录，纯 HTML，无框架；按公司、专题、时间、类型、公众号发表五个维度建索引，另有站内搜索与 RSS。

用法：python3 tools/build_site.py [--out site]
依赖：markdown、pypinyin（pip install markdown pypinyin）
"""
import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from urllib.parse import quote

import markdown
from pypinyin import Style, lazy_pinyin

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_URL = "https://github.com/xbtlin/ai-berkshire"
SITE_URL = "https://xbtlin.github.io/ai-berkshire/"
SITE_NAME = "AI Berkshire 研究阅读"
# 访问统计：在 goatcounter.com 注册后填站点代码（如 "aiberkshire"）；留空则不加统计脚本。
# 也可用环境变量 GOATCOUNTER_CODE 覆盖。打开任意页面并在网址后加 #notrack 可让本机不计入统计。
GOATCOUNTER = os.environ.get("GOATCOUNTER_CODE", "")
# 国内主统计：百度统计站点 ID（统计代码里 hm.js? 后面那串 32 位字符）；留空则不加。也可用环境变量 BAIDU_TONGJI_ID。
BAIDU_TONGJI = os.environ.get("BAIDU_TONGJI_ID", "fb8b18770c2f12915beaa9539754eb5c")
FRONT = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.S)
H1 = re.compile(r"^#\s+(.+?)\s*$", re.M)
DATE8 = re.compile(r"(20[2-3]\d)(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])")
ASSET_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf", ".csv", ".json", ".txt", ".html"}
TYPE_ORDER = ["深度系列", "研究", "财报", "估值仓位", "组织管理", "横评对比", "公众号", "筛选", "底稿"]
NOISE_BUCKETS = {"筛选池"}


def sh(args):
    return subprocess.check_output(args, cwd=ROOT).decode("utf-8", "replace")


def tracked(prefix):
    out = subprocess.check_output(["git", "ls-files", "-z", "--", prefix], cwd=ROOT)
    return [p for p in out.decode("utf-8", "replace").split("\0") if p]


def page_id(path):
    return hashlib.sha1(path.encode("utf-8")).hexdigest()[:12]


def slug(name):
    s = re.sub(r"[^0-9A-Za-z一-鿿]+", "-", name).strip("-")
    return s or page_id(name)


def initial(name):
    c = name.strip()[:1]
    if not c:
        return "#"
    if re.match(r"[A-Za-z]", c):
        return c.upper()
    if re.match(r"[一-鿿]", c):
        return lazy_pinyin(c, style=Style.FIRST_LETTER)[0].upper()
    return "#"


def read(path):
    full = os.path.join(ROOT, path)
    if os.path.isfile(full):
        with open(full, encoding="utf-8", errors="replace") as f:
            return f.read()
    return blob(path).decode("utf-8", "replace")


def blob(path):
    """读取已入库内容；本地工作区缺失（例如他处未提交的删除）时回退到 HEAD。"""
    return subprocess.check_output(["git", "show", "HEAD:%s" % path], cwd=ROOT,
                                   stderr=subprocess.DEVNULL)


def available(path):
    if os.path.isfile(os.path.join(ROOT, path)):
        return True
    try:
        blob(path)
        return True
    except subprocess.CalledProcessError:
        return False


# ---------- 收集条目 ----------

def collect():
    items = []
    idx = json.load(open(os.path.join(ROOT, "reports", "index.json"), encoding="utf-8"))
    for r in idx["reports"]:
        if not available(r["path"]):
            continue
        items.append({
            "title": r["title"], "path": r["path"], "bucket": r["bucket"], "group": r["group"],
            "series": r.get("series", ""), "type": r.get("type", "研究"), "date": r.get("date", ""),
        })
    seen = {i["path"] for i in items}
    dir_meta = {}
    for i in items:
        dir_meta.setdefault(os.path.dirname(i["path"]), (i["bucket"], i["group"]))
    for p in tracked("reports/"):
        if not p.endswith("README.md") or p in seen or "/_index/" in p:
            continue
        d = os.path.dirname(p)
        bucket, group = dir_meta.get(d, (None, None))
        while bucket is None and d.count("/") > 0:
            d = os.path.dirname(d)
            bucket, group = dir_meta.get(d, (None, None))
        if bucket is None:
            parts = p.split("/")
            bucket, group = ("专题", parts[1] if len(parts) > 2 else "研究总览")
        text = read(p)
        m = H1.search(FRONT.sub("", text))
        items.append({"title": (m.group(1).strip() if m else "%s 导读" % group), "path": p,
                      "bucket": bucket, "group": group, "series": "", "type": "导读",
                      "date": git_date(p)})
    for p in tracked("筛选公司/"):
        if not p.endswith(".md"):
            continue
        parts = p.split("/")
        group = parts[1] if len(parts) > 2 else "筛选公司"
        text = read(p)
        m = H1.search(FRONT.sub("", text))
        name = os.path.basename(p)[:-3]
        dm = DATE8.search(name)
        items.append({"title": m.group(1).strip() if m else name, "path": p, "bucket": "筛选池",
                      "group": group, "series": "", "type": "筛选",
                      "date": "%s-%s-%s" % dm.groups() if dm else git_date(p)})
    for p in tracked("docs/"):
        if not p.endswith(".md") or os.path.basename(p) in ("ROADMAP.md", "README.md"):
            continue
        text = read(p)
        m = H1.search(FRONT.sub("", text))
        items.append({"title": m.group(1).strip() if m else os.path.basename(p)[:-3], "path": p,
                      "bucket": "专题", "group": "随笔与综述", "series": "", "type": "研究",
                      "date": git_date(p)})
    for p in tracked("投资炼丹/"):
        if not p.endswith(".md") or p.endswith("README.md"):
            continue
        parts = p.split("/")
        group = parts[1] if len(parts) > 2 else "其他"
        text = read(p)
        m = H1.search(FRONT.sub("", text))
        name = os.path.basename(p)[:-3]
        dm = DATE8.match(name)
        date = "%s-%s-%s" % dm.groups() if dm else ""
        title = m.group(1).strip() if m else re.sub(r"^\d{8}-", "", name).replace("-", " ")
        pub = re.search(r"发表标题：(.+)", text)
        if pub:
            title = pub.group(1).strip()
        items.append({"title": title, "path": p, "bucket": "公众号发表", "group": group,
                      "series": "", "type": "公众号", "date": date})
    for p in tracked("实盘记录/"):
        if not p.endswith(".md"):
            continue
        text = read(p)
        m = H1.search(FRONT.sub("", text))
        name = os.path.basename(p)[:-3]
        dm = DATE8.search(name)
        date = "%s-%s-%s" % dm.groups() if dm else git_date(p)
        items.append({"title": m.group(1).strip() if m else name, "path": p, "bucket": "实盘记录",
                      "group": "实盘记录", "series": "", "type": "实盘", "date": date})
    for it in items:
        it["id"] = page_id(it["path"])
        it["url"] = "r/%s.html" % it["id"]
    items.sort(key=lambda x: (x["date"] or "0000"), reverse=True)
    return items


# ---------- 内容筛选：只上成品，不上中间产物 ----------
# 中间产物（审计、核验、证据、底稿、数据收集、搜索日志、自动扫描、召回池分视角稿等）仍保留在 GitHub，
# 阅读站点只收录成品报告。被排除的页面若被正文引用，链接自动指向 GitHub 原文。
MID_DIR = re.compile(r"/(evidence|证据|research|data|sources|audit[^/]*|审计[^/]*|[^/]*审读[^/]*|[^/]*核验[^/]*|[^/]*证据)/", re.I)
# 只认明确的中间产物标记；"核查""证据""审计"等词单独出现时可能是成品研究的标题，不据此排除
MID_NAME = re.compile(
    r"底稿|核验报告|核验记录|核对底稿|审计说明|审计记录|审查记录|核查说明|核查记录|核查边界|来源登记|"
    r"来源与核验|来源与复核|来源与证据|来源与逻辑|data[_-]?collection|数据收集|search[-_]?log|^sources$|"
    r"素材|工作稿|草稿|draft|todo|待.{0,4}复核|抽检|附录|^财务表$|^计算|financial[-_]rigor|"
    r"readme__|__readme|审读|评审记录|audit[-_]notes|证据$", re.I)
POOL_PERSPECTIVE = re.compile(r"/0[1-4]-[^/]*视角\.md$")
BOTTLENECK_RUN = re.compile(r"^reports/bottleneck-map/(20\d\d-\d\d-\d\d|daily)/")


def exclude_reason(it):
    path, name, title = it["path"], os.path.basename(it["path"]), it["title"]
    if BOTTLENECK_RUN.match(path):
        return "自动扫描与日报"
    if MID_DIR.search("/" + path):
        return "证据/审计/调研目录"
    if MID_NAME.search(name[:-3]) or MID_NAME.search(title.strip()):
        return "审计核验底稿"
    if it["type"] == "底稿" and "系列说明" not in title:
        return "审计核验底稿"
    if it["bucket"] == "筛选池" and POOL_PERSPECTIVE.search(path):
        return "召回池分视角稿"
    if path in ("reports/README.md",) or path.startswith("reports/_index/"):
        return "索引页"
    if it["bucket"] == "筛选池" and name == "README.md" and path.count("/") > 2:
        return "召回池分视角稿"
    if it["type"] == "导读" and it.get("_size", 9999) < 600:
        return "过短"
    if it.get("_size", 9999) < 800:
        return "过短"
    return ""


def attach_workpapers(kept, hidden):
    """给成品挂上 GitHub 上的底稿：项目目录（reports/公司/项目/）挂同目录及子目录的全部底稿；
    公司根目录下的报告只挂文件名或子目录名日期相同的底稿。"""
    for it in kept:
        d = os.path.dirname(it["path"])
        project = it["path"].count("/") >= 3 and not it["path"].startswith("投资炼丹/")
        dm = DATE8.search(os.path.basename(it["path"]))
        day = "".join(dm.groups()) if dm else (it["date"] or "").replace("-", "")
        rows = []
        for h in hidden:
            hp = h["path"]
            if project:
                if hp.startswith(d + "/"):
                    rows.append(h)
            elif day and len(day) == 8 and hp.startswith(d + "/") and day in hp[len(d):]:
                rows.append(h)
        it["_work"] = sorted(rows, key=lambda r: r["path"])[:20]


def curate(items):
    # 公众号：有发表版（投资炼丹）的，隐藏 reports/ 里对应的原稿，避免同文两份
    drafts = set()
    for it in items:
        if it["bucket"] == "公众号发表":
            m = re.search(r"原稿：\[[^\]]*\]\(([^)]+)\)", read(it["path"]))
            if m:
                drafts.add(os.path.normpath(os.path.join(os.path.dirname(it["path"]), m.group(1))))
    kept, dropped, hidden = [], defaultdict(int), []
    for it in items:
        it["_size"] = len(read(it["path"]).encode("utf-8"))
        why = "已有公众号发表版" if it["path"] in drafts else exclude_reason(it)
        if why:
            dropped[why] += 1
            if why not in ("已有公众号发表版", "自动扫描与日报", "索引页", "过短"):
                it["_why"] = why
                hidden.append(it)
        else:
            kept.append(it)
    # 去重：内容完全相同的只留一份；同目录同标题的多个版本只留最新最长的一份
    seen_hash, best = {}, {}
    for it in sorted(kept, key=lambda x: (x["date"] or "", x["_size"]), reverse=True):
        h = hashlib.sha1(read(it["path"]).encode("utf-8")).hexdigest()
        key = (os.path.dirname(it["path"]), re.sub(r"\s+", "", it["title"]))
        if h in seen_hash or key in best:
            dropped["重复或旧版本"] += 1
            continue
        seen_hash[h] = 1
        best[key] = it
    kept = [it for it in kept if best.get((os.path.dirname(it["path"]), re.sub(r"\s+", "", it["title"]))) is it]
    for it in kept:
        if it["type"] == "底稿":
            it["type"] = "导读"
    attach_workpapers(kept, hidden)
    print("收录 %d 篇；排除 %d 篇：%s" % (len(kept), sum(dropped.values()),
          "，".join("%s %d" % kv for kv in sorted(dropped.items(), key=lambda x: -x[1]))))
    return kept


def git_date(path):
    try:
        out = sh(["git", "log", "-1", "--format=%cs", "--", path]).strip()
        return out
    except subprocess.CalledProcessError:
        return ""


# ---------- HTML 外壳 ----------

CSS = """
:root{--bg:#fbfbf9;--card:#fff;--fg:#1f2328;--muted:#656d76;--line:#e3e4e2;--accent:#0b5cad;--accent-bg:#eaf2fb;
--th:#f3f4f2;--code:#f3f4f2;--shadow:0 1px 2px rgba(0,0,0,.05);--radius:10px;--w:46rem;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme]){--bg:#15171a;--card:#1c1f23;--fg:#e6e6e3;--muted:#9aa1a9;
--line:#2d3136;--accent:#6cb0ff;--accent-bg:#1d2a3a;--th:#23272c;--code:#23272c;--shadow:none;color-scheme:dark}}
:root[data-theme=dark]{--bg:#15171a;--card:#1c1f23;--fg:#e6e6e3;--muted:#9aa1a9;--line:#2d3136;--accent:#6cb0ff;
--accent-bg:#1d2a3a;--th:#23272c;--code:#23272c;--shadow:none;color-scheme:dark}
html{font-size:17px;-webkit-text-size-adjust:100%}
html[data-size=s1]{font-size:15px}html[data-size=s3]{font-size:19px}html[data-size=s4]{font-size:22px}
*{box-sizing:border-box}
body{margin:0;color:var(--fg);background:var(--bg);line-height:1.8;
font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Noto Sans CJK SC","Source Han Sans SC","Microsoft YaHei",sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
header.top{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 88%,transparent);
-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.bar{max-width:72rem;margin:0 auto;padding:0 1rem;display:flex;align-items:center;gap:1rem;height:3.2rem}
.brand{font-weight:700;color:var(--fg);white-space:nowrap}
nav.main{display:flex;gap:.2rem;overflow-x:auto;scrollbar-width:none;flex:1;min-width:0}nav.main::-webkit-scrollbar{display:none}
nav.main a{color:var(--fg);padding:.3rem .65rem;border-radius:6px;white-space:nowrap;font-size:.93rem}
nav.main a:hover,nav.main a.on{background:var(--accent-bg);color:var(--accent);text-decoration:none}
.tools{display:flex;gap:.3rem;white-space:nowrap;flex-shrink:0}
.tools button{font:inherit;font-size:.82rem;color:var(--fg);background:var(--card);border:1px solid var(--line);
border-radius:6px;padding:.15rem .5rem;cursor:pointer}
.tools select{font:inherit;font-size:.82rem;color:var(--fg);background:var(--card);border:1px solid var(--line);border-radius:6px;padding:.1rem .3rem}
main{max-width:var(--w);margin:0 auto;padding:0 1rem 3rem;overflow-wrap:anywhere}
main.wide{max-width:72rem}
.crumb{font-size:.82rem;color:var(--muted);margin:1.2rem 0 0}.crumb a{color:var(--muted)}
h1{font-size:1.75rem;line-height:1.35;margin:.8rem 0 .5rem;letter-spacing:.01em}
h2{font-size:1.3rem;line-height:1.45;margin:2.2rem 0 .8rem;padding-bottom:.3rem;border-bottom:1px solid var(--line)}
h3{font-size:1.08rem;margin:1.6rem 0 .5rem}
.meta{color:var(--muted);font-size:.84rem;margin:.15rem 0 1rem}
ul.list{list-style:none;padding:0;margin:0;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}
ul.list li{padding:.75rem 1rem;border-bottom:1px solid var(--line)}ul.list li:last-child{border-bottom:0}
ul.list li:hover{background:var(--accent-bg)}
ul.list li>a{display:block;color:var(--fg);font-weight:500}ul.list li>a:hover{color:var(--accent);text-decoration:none}
ul.list .meta{margin:.15rem 0 0}
.grid{display:flex;flex-wrap:wrap;gap:.5rem;margin:.6rem 0}
.grid a.btn{display:inline-block;background:var(--card);border:1px solid var(--line);border-radius:999px;padding:.35rem .9rem;
color:var(--fg);font-size:.92rem;box-shadow:var(--shadow)}
.grid a.btn:hover{border-color:var(--accent);color:var(--accent);text-decoration:none}
.grid.big a.btn{border-radius:var(--radius);padding:.7rem 1.1rem;font-weight:600}
.idx{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:0}
.idx li{border-bottom:1px solid var(--line)!important}
article{font-size:1.02rem}
article p{margin:.9rem 0}
article a{text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}
.table-wrap{overflow-x:auto;margin:1.2rem 0;border:1px solid var(--line);border-radius:var(--radius);background:var(--card)}
table{border-collapse:collapse;font-size:.86rem;line-height:1.5;min-width:100%}
th,td{border-bottom:1px solid var(--line);padding:.45rem .7rem;vertical-align:top;text-align:left}
th{background:var(--th);font-weight:600;white-space:nowrap}
tbody tr:nth-child(even){background:color-mix(in srgb,var(--th) 45%,transparent)}
blockquote{border-left:3px solid var(--accent);margin:1.2rem 0;padding:.2rem 1rem;color:var(--muted);background:var(--card)}
pre{overflow-x:auto;background:var(--code);border-radius:8px;padding:.8rem;font-size:.82rem;line-height:1.5}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.88em;background:var(--code);padding:.1em .3em;border-radius:4px}
pre code{background:none;padding:0}
img{max-width:100%;height:auto;border-radius:6px}
hr{border:0;border-top:1px solid var(--line);margin:2rem 0}
details.toc{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:.2rem 1rem;margin:1rem 0}
summary{cursor:pointer;padding:.5rem 0;font-weight:600}
.toc ul{padding-left:1.1rem;margin:.2rem 0 .6rem;font-size:.9rem;line-height:1.7}
.toc a{color:var(--fg)}
.layout{display:block}
aside.side{display:none}
@media (min-width:1180px){main.doc{max-width:72rem}.layout{display:grid;grid-template-columns:minmax(0,46rem) 15rem;gap:3rem;justify-content:center}
aside.side{display:block}aside.side .toc{position:sticky;top:4.5rem;max-height:calc(100vh - 6rem);overflow:auto;font-size:.85rem;
border-left:1px solid var(--line);padding-left:1rem}aside.side .toc ul{padding-left:.8rem}
details.toc{display:none}}
.resume{position:fixed;left:50%;bottom:1.2rem;transform:translateX(-50%);z-index:12;background:var(--card);color:var(--fg);
border:1px solid var(--line);border-radius:999px;padding:.45rem .6rem .45rem 1rem;box-shadow:0 4px 16px rgba(0,0,0,.12);font-size:.9rem;white-space:nowrap}
.resume button{font:inherit;margin-left:.6rem;border:0;border-radius:999px;background:var(--accent);color:#fff;padding:.2rem .8rem;cursor:pointer}
.resume .x{margin-left:.5rem;color:var(--muted);cursor:pointer;padding:0 .3rem}
ul.list li.done>a{color:var(--muted);font-weight:400}.rd{color:var(--accent)}
ul.work li>a{font-weight:400;font-size:.95rem}
.wx{display:flex;gap:1rem;align-items:center;margin:2.4rem 0 1rem;padding:1rem;background:var(--card);
border:1px solid var(--line);border-radius:var(--radius)}.wx img{width:92px;height:92px;border-radius:6px;flex-shrink:0}
.wx b{display:block;font-size:1rem}.wx span{color:var(--muted);font-size:.86rem}
.wxline{margin:2.4rem 0 .6rem;padding-top:.8rem;border-top:1px solid var(--line);color:var(--muted);font-size:.85rem}
.wxline .fix{display:block;margin-top:.3rem}
.intro{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:1rem 1.2rem;margin:1rem 0 1.4rem}
.intro p{margin:.3rem 0}
.layers{display:grid;grid-template-columns:repeat(auto-fit,minmax(12rem,1fr));gap:.8rem;margin:1rem 0}
.layers div{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:.9rem 1rem}
.layers b{display:block;margin-bottom:.2rem}.layers span{color:var(--muted);font-size:.88rem}
.progress{position:fixed;top:0;left:0;height:3px;width:0;background:var(--accent);z-index:11}
footer{max-width:72rem;margin:3rem auto 0;padding:1.2rem 1rem 2rem;border-top:1px solid var(--line);font-size:.82rem;color:var(--muted)}
footer a{color:var(--muted);text-decoration:underline}
input.q{font:inherit;font-size:1.05rem;width:100%;padding:.7rem 1rem;border:1px solid var(--line);border-radius:var(--radius);
background:var(--card);color:var(--fg);outline:none}input.q:focus{border-color:var(--accent)}
@media (max-width:640px){html{font-size:16px}h1{font-size:1.45rem}.bar{gap:.5rem;padding:0 .6rem}.brand{display:none}
.tools .lbl{display:none}ul.list li{padding:.7rem .8rem}}
"""

PREF_JS = """
(function(){var h=document.documentElement,g=function(k){try{return localStorage.getItem(k)}catch(e){return null}};
var t=g('aib-theme'),s=g('aib-size');
if(t&&t!=='auto')h.setAttribute('data-theme',t);if(s)h.setAttribute('data-size',s);
var sz=['s1','','s3','s4'];
window.aibSize=function(d){var c=h.getAttribute('data-size')||'',i=sz.indexOf(c);i=Math.max(0,Math.min(3,i+d));
if(sz[i])h.setAttribute('data-size',sz[i]);else h.removeAttribute('data-size');try{localStorage.setItem('aib-size',sz[i])}catch(e){}};
window.aibTheme=function(v){if(v==='auto')h.removeAttribute('data-theme');else h.setAttribute('data-theme',v);
try{localStorage.setItem('aib-theme',v)}catch(e){}};
document.addEventListener('DOMContentLoaded',function(){var sel=document.getElementById('theme');
if(sel)sel.value=h.getAttribute('data-theme')||'auto';var bar=document.querySelector('.progress');
if(bar){var f=function(){var d=document.documentElement,m=d.scrollHeight-d.clientHeight;bar.style.width=(m>0?d.scrollTop/m*100:0)+'%'};
addEventListener('scroll',f,{passive:true});f()}});})();
"""

WECHAT_CARD = ('<div class="wx"><img src="%sfiles/assets/wechat-qr.png" alt="公众号复利炼丹炉二维码">'
               '<div><b>公众号「复利炼丹炉」</b><span>站上是全部成品报告；值得深研的公司和报告之外的判断与取舍，'
               '精选发在公众号。微信扫码关注。</span></div></div>')


def about_page(n_reports, n_companies, n_wechat, updated):
    return """
<h1>关于 AI Berkshire</h1>
<div class="meta">一个用 AI 做价值投资研究的开源项目 · 收录 %(n)d 篇成品报告 · %(c)d 家公司 · 更新至 %(u)s</div>

<h2>这是什么</h2>
<p>AI Berkshire 是一套开源的投资研究方法：把价值投资的分析框架写成 Claude Code 与 Codex 都能调用的研究技能（Skill），
让一个人加上 AI 代理，能完成一个投研小组的工作量：读一手财报、交叉核验数字、多视角对抗论证、写成结论明确的报告。</p>
<p>这个网站是项目的阅读入口，收录全部成品研究，按公司、专题、时间、类型整理，电脑、手机、电子阅读器都能读。</p>

<h2>三个地方，三种精度</h2>
<div class="layers">
<div><b>公众号「复利炼丹炉」</b><span>最精简。只发值得深研的公司，加上报告之外的个人判断与取舍。共 %(w)d 篇。</span></div>
<div><b>本网站</b><span>全部成品报告。日常阅读、按公司翻历史判断、查找都在这里。</span></div>
<div><b><a href="%(repo)s">GitHub 仓库</a></b><span>全部底稿：研究技能、审计核验、证据、中间稿都在。每篇报告页底部列有对应底稿。</span></div>
</div>

<h2>研究方法的几条原则</h2>
<ul>
<li><b>只用一手材料</b>：交易所公告、年报、业绩会原话。旧报告只当线索，不当证据。</li>
<li><b>事实与判断分开写</b>：凡是推算和判断都标明，数字注明来源与口径。</li>
<li><b>强制给结论</b>：不写"一方面、另一方面"的两头讨好，给出可以被检验的判断和检验时间点。</li>
<li><b>可追溯</b>：同一家公司的报告按时间排在一起，判断怎么变、为什么变，都能对照着看。</li>
</ul>

<h2>怎么用这个网站</h2>
<ul>
<li><a href="companies/index.html">按公司</a>：每家公司一页，分公众号发表、深度系列、财报、估值等类型。</li>
<li><a href="topics/index.html">专题</a>：行业研究、横向对比、筛选池。</li>
<li><a href="dates/index.html">按时间</a>与<a href="types/index.html">按类型</a>：看最近写了什么。</li>
<li><a href="search.html">搜索</a>：输入公司名或关键词，例如"拼多多 财报"。</li>
<li>右上角可调字号和深浅色；读过的文章会标记进度，下次打开可以接着读（只记在你自己的浏览器里）。</li>
<li>发现数据错误：每篇报告末尾有"提交纠错"，会打开 GitHub 的纠错表单并自动填好报告名称，请附上正确值和来源链接。</li>
<li>也可以用 RSS 订阅更新：<a href="feed.xml">feed.xml</a>。</li>
</ul>

<h2>关注公众号</h2>
%(card)s

<h2>想自己跑一遍</h2>
<p>研究技能、使用说明和全部报告原稿都在 <a href="%(repo)s">GitHub</a>，按仓库首页的"快速开始"装好即可在 Claude Code 或 Codex 里调用。
欢迎提 issue 和改进建议。</p>

<h2>官方渠道</h2>
<p>本项目只有三个官方渠道：GitHub 仓库 <a href="%(repo)s">xbtlin/ai-berkshire</a>、本站、微信公众号「复利炼丹炉」。</p>
<p><b>不收费、不荐股、不带单、不建投资群，也不以任何形式收款。</b>ai-berkshire.com、aiberkshire.com 等域名由他人注册，与本项目无关。
凡以 AI Berkshire 名义拉群、收费、推荐个股的，都不是本人。</p>

<h2>免责声明</h2>
<p class="meta">本站内容是个人研究记录，不构成任何投资建议。报告中的判断可能有误，数据以公司公告原件为准。投资有风险，决策请独立判断。</p>
""" % {"n": n_reports, "c": n_companies, "w": n_wechat, "u": updated, "repo": REPO_URL, "card": WECHAT_CARD % ""}


READ_JS = r"""
(function(){var K='aib-read',get=function(){try{return JSON.parse(localStorage.getItem(K)||'{}')}catch(e){return{}}},
put=function(d){try{localStorage.setItem(K,JSON.stringify(d))}catch(e){}};
document.addEventListener('DOMContentLoaded',function(){var b=document.body,root=b.getAttribute('data-root')||'',page=b.getAttribute('data-page');
var d=get();
if(page){var rec=d[page]||{p:0},el=document.documentElement;
 if(rec.p>0.05&&rec.p<0.95){var n=document.createElement('div');n.className='resume';
  n.innerHTML='上次读到 '+Math.round(rec.p*100)+'% <button>继续阅读</button><span class="x">×</span>';
  n.querySelector('button').onclick=function(){scrollTo(0,rec.p*(el.scrollHeight-el.clientHeight));n.remove()};
  n.querySelector('.x').onclick=function(){n.remove()};document.body.appendChild(n);setTimeout(function(){n.remove()},15000)}
 var t=null;addEventListener('scroll',function(){clearTimeout(t);t=setTimeout(function(){var m=el.scrollHeight-el.clientHeight;
  var p=m>0?el.scrollTop/m:1,cur=get();var r=cur[page]||{};r.p=p;r.t=Date.now();r.title=b.getAttribute('data-title');
  if(p>0.9)r.done=1;cur[page]=r;put(cur)},400)},{passive:true});
 var r0=d[page]||{};r0.t=Date.now();r0.title=b.getAttribute('data-title');if(r0.p==null)r0.p=0;d[page]=r0;put(d)}
var links=document.querySelectorAll('ul.list li>a');for(var i=0;i<links.length;i++){var h=links[i].getAttribute('href')||'';
 var key=h.replace(/^(\.\.\/)+/,'');var r=d[key];if(r){var m=links[i].parentNode.querySelector('.meta');
 if(m){m.insertAdjacentHTML('beforeend',' · <span class="rd">'+(r.done?'已读':'读到 '+Math.round((r.p||0)*100)+'%')+'</span>')}
 if(r.done)links[i].parentNode.classList.add('done')}}
var box=document.getElementById('recent-read');if(box){var arr=Object.keys(d).map(function(k){return{k:k,r:d[k]}})
 .filter(function(x){return x.r.title}).sort(function(a,b){return b.r.t-a.r.t}).slice(0,6);
 if(arr.length){box.innerHTML='<h2>最近读过</h2><ul class="list">'+arr.map(function(x){var e=document.createElement('a');e.textContent=x.r.title;
  return '<li><a href="'+root+x.k+'">'+e.innerHTML+'</a><div class="meta">'+(x.r.done?'已读完':'读到 '+Math.round((x.r.p||0)*100)+'%')+'</div></li>'}).join('')+'</ul>'}}
});})();
"""

NAV = [("index.html", "首页"), ("companies/index.html", "公司"), ("topics/index.html", "专题"),
       ("dates/index.html", "时间"), ("types/index.html", "类型"), ("wechat/index.html", "公众号"),
       ("search.html", "搜索"), ("about.html", "关于")]


def analytics_tag():
    """统计脚本：本机打开任意页面网址加 #notrack 后不再加载任何统计脚本，#track 恢复。"""
    if not (GOATCOUNTER or BAIDU_TONGJI):
        return ""
    loads = []
    if BAIDU_TONGJI:
        loads.append("window._hmt=window._hmt||[];var b=document.createElement('script');"
                     "b.async=true;b.src='https://hm.baidu.com/hm.js?%s';document.head.appendChild(b);" % BAIDU_TONGJI)
    if GOATCOUNTER:
        loads.append("var g=document.createElement('script');g.async=true;g.src='//gc.zgo.at/count.js';"
                     "g.setAttribute('data-goatcounter','https://%s.goatcounter.com/count');document.head.appendChild(g);" % GOATCOUNTER)
    return ("<script>(function(){var skip=false;try{if(location.hash==='#notrack'){localStorage.setItem('skipgc','1');"
            "alert('本设备的访问将不再计入统计')}if(location.hash==='#track'){localStorage.removeItem('skipgc')}"
            "skip=!!localStorage.getItem('skipgc')}catch(e){}if(skip)return;%s})();</script>" % "".join(loads))


def shell(title, body, depth, crumb="", section="", main_class="", progress=False, page=""):
    rel = "../" * depth
    links = "".join('<a href="%s%s"%s>%s</a>' % (rel, u, ' class="on"' if t == section else "", t) for u, t in NAV)
    head = (
        '<header class="top"><div class="bar"><a class="brand" href="{r}index.html">AI Berkshire</a>'
        '<nav class="main">{links}</nav><div class="tools">'
        '<button onclick="aibSize(-1)" title="缩小字号">A−</button><button onclick="aibSize(1)" title="放大字号">A+</button>'
        '<select id="theme" onchange="aibTheme(this.value)" title="外观"><option value="auto">自动</option>'
        '<option value="light">浅色</option><option value="dark">深色</option></select>'
        '</div></div></header>'
    ).format(r=rel, links=links)
    crumb_html = '<div class="crumb">%s</div>' % crumb if crumb else ""
    return (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="theme-color" content="#fbfbf9">'
        '<title>%s · %s</title><link rel="stylesheet" href="%sstyle.css">'
        '<link rel="alternate" type="application/rss+xml" title="%s" href="%sfeed.xml">'
        '<script>%s</script>' + analytics_tag() + '</head><body data-root="%s" data-page="%s" data-title="%s">%s%s<main class="%s">%s%s</main>'
        '<footer>%s ｜ <a href="%sabout.html">关于本站</a> ｜ 公众号「复利炼丹炉」 ｜ <a href="%s">GitHub 仓库</a> ｜ <a href="%sfeed.xml">RSS 订阅</a> ｜ 生成于 %s</footer></body></html>'
    ) % (html.escape(title), SITE_NAME, rel, SITE_NAME, rel, PREF_JS + READ_JS, rel, page, html.escape(title, quote=True),
         '<div class="progress"></div>' if progress else "", head, main_class, crumb_html, body,
         SITE_NAME, rel, REPO_URL, rel, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))


def li(it, depth, show_group=True):
    rel = "../" * depth
    bits = [it["date"] or "日期不详"]
    if show_group and it["group"]:
        bits.append(it["group"])
    if it["type"]:
        bits.append(it["type"])
    return '<li><a href="%s%s">%s</a><div class="meta">%s</div></li>' % (
        rel, it["url"], html.escape(it["title"]), " · ".join(html.escape(b) for b in bits))


def ul(items, depth, show_group=True, limit=None):
    rows = items if limit is None else items[:limit]
    return '<ul class="list">%s</ul>' % "".join(li(i, depth, show_group) for i in rows)


# ---------- Markdown → HTML ----------

LINK_ATTR = re.compile(r'(href|src)="([^"]+)"')


def convert(it, by_path, out_dir):
    text = FRONT.sub("", read(it["path"]))
    m1 = H1.search(text)
    if m1 and (m1.start() < 1500 or m1.group(1).strip() == it["title"]):
        text = text[:m1.start()] + text[m1.end():]
    md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "toc"],
                           extension_configs={"toc": {"toc_depth": "2-3"}})
    body = md.convert(text)
    base = os.path.dirname(it["path"])
    missing = []

    def fix(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"^(https?:|mailto:|#|data:)", url):
            return m.group(0)
        clean = url.split("#")[0].split("?")[0]
        target = os.path.normpath(os.path.join(base, clean)).replace("\\", "/")
        if target in by_path:
            return '%s="../%s"' % (attr, by_path[target]["url"])
        ext = os.path.splitext(target)[1].lower()
        src = os.path.join(ROOT, target)
        if ext in ASSET_EXT and available(target):
            dst = os.path.join(out_dir, "files", target)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst):
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                else:
                    with open(dst, "wb") as fh:
                        fh.write(blob(target))
            return '%s="../files/%s"' % (attr, quote(target))
        if available(target):
            return '%s="%s/blob/main/%s"' % (attr, REPO_URL, quote(target))
        missing.append(url)
        return m.group(0)

    body = LINK_ATTR.sub(fix, body)
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    toc = md.toc if md.toc and md.toc.count("<li>") >= 3 else ""
    return body, toc


# ---------- 各类页面 ----------

def write(out_dir, rel_path, content):
    p = os.path.join(out_dir, rel_path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)


def build(out_dir):
    items = curate(collect())
    by_path = {i["path"]: i for i in items}
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    write(out_dir, "style.css", CSS)
    write(out_dir, ".nojekyll", "")

    companies = defaultdict(list)
    topics = defaultdict(list)
    screens = defaultdict(list)
    wechat = defaultdict(list)
    months = defaultdict(list)
    types = defaultdict(list)
    for it in items:
        if it["bucket"] == "公司":
            companies[it["group"]].append(it)
        elif it["bucket"] == "公众号发表":
            wechat[it["group"]].append(it)
            companies[it["group"]].append(it)
        elif it["bucket"] == "筛选池":
            screens[it["group"]].append(it)
        elif it["bucket"] == "实盘记录":
            topics["实盘记录"].append(it)
        else:
            topics[it["group"]].append(it)
        if it["date"]:
            months[it["date"][:7]].append(it)
        types[it["type"]].append(it)

    # 专题目录里写单家公司的报告（如七姐妹逐家报告），同时挂到对应公司页
    alias = {"谷歌": "Google", "Alphabet": "Google", "特斯拉": "Tesla", "Amazon": "亚马逊", "微软": "微软", "苹果": "苹果", "贵州茅台": "茅台"}
    names = sorted(set(companies) | set(alias), key=len, reverse=True)
    for it in items:
        if it["bucket"] not in ("专题",):
            continue
        t = it["title"].strip()
        hit = None
        for n in names:
            if re.match(re.escape(n) + r"(（|\(|：|:|\s)", t):
                hit = alias.get(n, n)
                break
        if not hit:
            m = re.match(r"^([^（(：:\s]{1,12})（([A-Z0-9]{1,6}(\.[A-Z]{1,2})?)）", t)
            if m:
                hit = alias.get(m.group(1), m.group(1))
        if hit and it not in companies[hit]:
            companies[hit].append(it)
            it["_also"] = hit
    for c in companies:
        companies[c].sort(key=lambda x: x["date"] or "", reverse=True)

    # 专题显示名：优先用目录 README 的标题
    tname = {}
    for it in items:
        if os.path.basename(it["path"]) != "README.md":
            continue
        d = os.path.basename(os.path.dirname(it["path"]))
        if d in topics and d not in tname:
            tname[d] = it["title"]
            if it["group"] != d and it in topics.get(it["group"], []):
                topics[it["group"]].remove(it)
                topics[d].append(it)
                it["group"] = d
    disp = lambda g: tname.get(g, g)

    comp_url = {c: "companies/%s/index.html" % slug(c) for c in companies}
    topic_url = {t: "topics/%s/index.html" % slug(t) for t in topics}
    screen_url = {s: "screens/%s/index.html" % slug(s) for s in screens}

    def group_link(it, depth):
        rel = "../" * depth
        if it["bucket"] in ("公司", "公众号发表") and it["group"] in comp_url:
            return '<a href="%s%s">%s</a>' % (rel, comp_url[it["group"]], html.escape(it["group"]))
        if it["bucket"] == "筛选池" and it["group"] in screen_url:
            return '<a href="%s%s">%s</a>' % (rel, screen_url[it["group"]], html.escape(it["group"]))
        g = "实盘记录" if it["bucket"] == "实盘记录" else it["group"]
        if g in topic_url:
            return '<a href="%s%s">%s</a>' % (rel, topic_url[g], html.escape(disp(g)))
        return html.escape(disp(g))

    # 报告页
    for it in items:
        body, toc = convert(it, by_path, out_dir)
        same = [x for x in (companies.get(it["group"]) or topics.get(it["group"]) or screens.get(it["group"]) or [])
                if x["id"] != it["id"]][:12]
        meta = " · ".join(x for x in [it["date"], it["type"]] if x)
        head = "<h1>%s</h1><div class=\"meta\">%s ｜ %s ｜ <a href=\"%s/blob/main/%s\">GitHub 原文</a></div>" % (
            html.escape(it["title"]), group_link(it, 1), html.escape(meta), REPO_URL, quote(it["path"]))
        if toc:
            head += '<details class="toc"><summary>目录</summary>%s</details>' % toc
        tail = ""
        issue = "%s/issues/new?%s" % (REPO_URL, "&".join("%s=%s" % (k, quote(v, safe="")) for k, v in [
            ("template", "data_error.yml"), ("title", "[Data] " + it["title"][:60]),
            ("ticker", it["group"] if it["bucket"] in ("公司", "公众号发表") else ""),
            ("source", "%s （阅读站：%s%s）" % (it["path"], SITE_URL, it["url"]))]))
        tail += ('<p class="wxline">精选研究与报告之外的判断，首发在公众号「复利炼丹炉」'
                 ' · <a href="../about.html">扫码关注</a>'
                 '<span class="fix">发现数据错误？<a href="%s" rel="nofollow">提交纠错</a>（需附正确值与来源）</span></p>') % html.escape(issue)
        if it.get("_work"):
            tail += ('<h2>底稿与核验（GitHub）</h2><div class="meta">这些文件不在阅读站上展示，点开为 GitHub 原文。</div>'
                     '<ul class="list work">%s</ul>') % "".join(
                '<li><a href="%s/blob/main/%s">%s</a><div class="meta">%s · %s</div></li>' % (
                    REPO_URL, quote(w["path"]), html.escape(w["title"]), html.escape(w["_why"]),
                    html.escape(w["path"][len(os.path.dirname(it["path"])) + 1:] if w["path"].startswith(os.path.dirname(it["path"]) + "/") else w["path"]))
                for w in it["_work"])
        if same:
            tail += "<h2>同一专题的其他报告</h2>" + ul(same, 1, show_group=False)
        crumb = '<a href="../index.html">首页</a> › %s' % group_link(it, 1)
        side = '<aside class="side"><div class="toc"><div class="meta">本文目录</div>%s</div></aside>' % toc if toc else "<aside class=\"side\"></aside>"
        page = '<div class="layout"><div>%s<article>%s</article>%s</div>%s</div>' % (head, body, tail, side)
        write(out_dir, it["url"], shell(it["title"], page, 1, crumb, main_class="doc", progress=True, page=it["url"]))

    # 公司索引与公司页
    def company_page(name, rows):
        groups = defaultdict(list)
        for r in rows:
            key = "公众号发表" if r["bucket"] == "公众号发表" else r["type"]
            groups[key].append(r)
        order = ["导读", "公众号发表"] + TYPE_ORDER
        parts = ["<h1>%s</h1><div class=\"meta\">共 %d 篇，最近更新 %s</div>" % (
            html.escape(name), len(rows), rows[0]["date"] if rows and rows[0]["date"] else "—")]
        for k in order + [k for k in groups if k not in order]:
            if k in groups:
                parts.append("<h2>%s（%d）</h2>%s" % (html.escape(k), len(groups[k]), ul(groups[k], 2, show_group=False)))
        return "".join(parts)

    for c, rows in companies.items():
        write(out_dir, comp_url[c], shell(c, company_page(c, rows), 2,
                                          '<a href="../../index.html">首页</a> › <a href="../index.html">公司</a>'))
    letters = defaultdict(list)
    for c in companies:
        letters[initial(c)].append(c)
    top = sorted(companies, key=lambda c: -len(companies[c]))[:24]
    body = "<h1>按公司</h1><div class=\"meta\">%d 家公司，%d 篇报告</div><h2>报告最多的公司</h2><div class=\"grid\">%s</div>" % (
        len(companies), sum(len(v) for v in companies.values()),
        "".join('<a class="btn" href="../%s">%s %d</a>' % (comp_url[c], html.escape(c), len(companies[c])) for c in top))
    body += "<h2>全部公司（按拼音首字母）</h2>"
    for L in sorted(letters):
        names = sorted(letters[L], key=lambda c: lazy_pinyin(c))
        body += "<h3>%s</h3><ul class=\"list idx\">%s</ul>" % (L, "".join(
            '<li><a href="../%s">%s</a><div class="meta">%d 篇 · 最近 %s</div></li>' % (
                comp_url[c], html.escape(c), len(companies[c]), companies[c][0]["date"] or "—") for c in names))
    write(out_dir, "companies/index.html", shell("按公司", body, 1, section="公司"))

    # 专题
    def simple_group_page(name, rows, depth, crumb):
        by_series = defaultdict(list)
        for r in rows:
            by_series[r["series"] or ""].append(r)
        parts = ["<h1>%s</h1><div class=\"meta\">共 %d 篇</div>" % (html.escape(name), len(rows))]
        if len(by_series) > 1:
            for s in sorted(by_series, key=lambda s: (s == "", s), reverse=True):
                parts.append("<h2>%s（%d）</h2>%s" % (html.escape(s or "主报告"), len(by_series[s]), ul(by_series[s], depth, show_group=False)))
        else:
            parts.append(ul(rows, depth, show_group=False))
        return shell(name, "".join(parts), depth, crumb)

    for t, rows in topics.items():
        write(out_dir, topic_url[t], simple_group_page(disp(t), rows, 2, '<a href="../../index.html">首页</a> › <a href="../index.html">专题</a>'))
    for s, rows in screens.items():
        write(out_dir, screen_url[s], simple_group_page(s, rows, 2, '<a href="../../index.html">首页</a> › <a href="../../topics/index.html">专题</a>'))
    tnames = sorted(topics, key=lambda t: topics[t][0]["date"] or "", reverse=True)
    body = "<h1>专题与横评</h1><ul class=\"list\">%s</ul>" % "".join(
        '<li><a href="../%s">%s</a><div class="meta">%d 篇 · 最近 %s</div></li>' % (
            topic_url[t], html.escape(disp(t)), len(topics[t]), topics[t][0]["date"] or "—") for t in tnames)
    body += "<h2>筛选池与召回池</h2><ul class=\"list\">%s</ul>" % "".join(
        '<li><a href="../%s">%s</a><div class="meta">%d 篇 · 最近 %s</div></li>' % (
            screen_url[s], html.escape(s), len(screens[s]), screens[s][0]["date"] or "—")
        for s in sorted(screens, key=lambda s: screens[s][0]["date"] or "", reverse=True))
    write(out_dir, "topics/index.html", shell("专题", body, 1, section="专题"))

    # 时间
    years = defaultdict(list)
    for m in months:
        years[m[:4]].append(m)
    body = "<h1>按时间</h1>"
    for y in sorted(years, reverse=True):
        body += "<h2>%s 年</h2><div class=\"grid\">%s</div>" % (y, "".join(
            '<a class="btn" href="%s.html">%s 月 %d</a>' % (m, int(m[5:]), len(months[m])) for m in sorted(years[y], reverse=True)))
    write(out_dir, "dates/index.html", shell("按时间", body, 1, section="时间"))
    for m, rows in months.items():
        main = [r for r in rows if r["bucket"] not in NOISE_BUCKETS]
        noise = [r for r in rows if r["bucket"] in NOISE_BUCKETS]
        body = "<h1>%s 年 %d 月</h1><div class=\"meta\">%d 篇</div>%s" % (m[:4], int(m[5:]), len(rows), ul(main, 1))
        if noise:
            body += "<details><summary>筛选池与召回池日报（%d）</summary>%s</details>" % (len(noise), ul(noise, 1))
        write(out_dir, "dates/%s.html" % m, shell("%s 年 %d 月" % (m[:4], int(m[5:])), body, 1,
                                                   '<a href="../index.html">首页</a> › <a href="index.html">时间</a>'))

    # 类型
    tlist = [t for t in TYPE_ORDER if t in types] + [t for t in types if t not in TYPE_ORDER]
    body = "<h1>按类型</h1><div class=\"grid\">%s</div>" % "".join(
        '<a class="btn" href="%s.html">%s %d</a>' % (slug(t), html.escape(t), len(types[t])) for t in tlist)
    write(out_dir, "types/index.html", shell("按类型", body, 1, section="类型"))
    for t in tlist:
        rows = types[t]
        main = [r for r in rows if r["bucket"] not in NOISE_BUCKETS]
        noise = [r for r in rows if r["bucket"] in NOISE_BUCKETS]
        body = "<h1>%s</h1><div class=\"meta\">%d 篇</div>%s" % (html.escape(t), len(rows), ul(main, 1))
        if noise:
            body += "<details><summary>筛选池与召回池（%d）</summary>%s</details>" % (len(noise), ul(noise, 1))
        write(out_dir, "types/%s.html" % slug(t), shell(t, body, 1, '<a href="../index.html">首页</a> › <a href="index.html">类型</a>'))

    # 公众号发表
    wrows = sorted((r for rows in wechat.values() for r in rows), key=lambda r: r["date"], reverse=True)
    body = "<h1>公众号发表版</h1><div class=\"meta\">%d 篇，正文为公众号发表版本</div>%s" % (len(wrows), ul(wrows, 1))
    write(out_dir, "wechat/index.html", shell("公众号", body, 1, section="公众号"))

    # 搜索
    sdata = [{"t": i["title"], "g": i["group"], "k": i["type"], "d": i["date"], "u": i["url"]} for i in items]
    write(out_dir, "search.json", json.dumps(sdata, ensure_ascii=False, separators=(",", ":")))
    body = ("<h1>搜索</h1><p>输入公司名、关键词或日期（如 2026-09），按标题、公司、类型匹配。</p>"
            '<input class="q" id="q" type="search" placeholder="例如：拼多多 财报" autofocus>'
            '<div class="meta" id="n"></div><ul class="list" id="out"></ul>'
            "<script>var D=null;function esc(s){return s.replace(/[&<>\"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]})}"
            "function run(){var q=document.getElementById('q').value.trim().toLowerCase();var out=document.getElementById('out'),n=document.getElementById('n');"
            "if(!q){out.innerHTML='';n.textContent='';return}var ws=q.split(/\\s+/);var r=D.filter(function(x){var s=(x.t+' '+x.g+' '+x.k+' '+x.d).toLowerCase();return ws.every(function(w){return s.indexOf(w)>=0})});"
            "n.textContent='共 '+r.length+' 条'+(r.length>200?'，只显示前 200 条':'');"
            "if(!r.length){out.innerHTML='<li>没找到相关报告。想看这家公司的研究，可以在公众号「复利炼丹炉」留言（<a href=\"about.html\">扫码</a>），或在 GitHub <a rel=\"nofollow\" href=\"" + REPO_URL + "/issues/new?template=suggestion.yml&title='+encodeURIComponent('[建议] 希望研究：'+q)+'\">提研究建议</a>。</li>';}"
            "else{out.innerHTML=r.slice(0,200).map(function(x){return '<li><a href=\"'+x.u+'\">'+esc(x.t)+'</a><div class=\"meta\">'+esc([x.d,x.g,x.k].filter(Boolean).join(' · '))+'</div></li>'}).join('')}"
            "clearTimeout(window._lt);window._lt=setTimeout(function(){if(q.length>=2&&q!==window._lq&&window._hmt){window._lq=q;"
            "window._hmt.push(['_trackEvent','站内搜索',r.length?'有结果':'无结果',q])}},1500)}"
            "fetch('search.json').then(function(r){return r.json()}).then(function(d){D=d;document.getElementById('q').addEventListener('input',run);run()});</script>")
    write(out_dir, "search.html", shell("搜索", body, 0, section="搜索"))

    # 关于页与公众号二维码
    qr_dst = os.path.join(out_dir, "files", "assets", "wechat-qr.png")
    os.makedirs(os.path.dirname(qr_dst), exist_ok=True)
    with open(qr_dst, "wb") as fh:
        fh.write(open(os.path.join(ROOT, "assets", "wechat-qr.png"), "rb").read()
                 if os.path.isfile(os.path.join(ROOT, "assets", "wechat-qr.png")) else blob("assets/wechat-qr.png"))
    n_wechat = sum(len(v) for v in wechat.values())
    write(out_dir, "about.html", shell("关于", about_page(len(items), len(companies), n_wechat,
                                                         items[0]["date"] if items else "—"), 0, section="关于"))

    # 首页
    pool, seen_titles = [], set()
    for i in items:
        tkey = re.sub(r"\s+", "", i["title"])
        if tkey in seen_titles or i["bucket"] in NOISE_BUCKETS or i["series"] == "evidence" or i["type"] == "导读":
            continue
        seen_titles.add(tkey)
        pool.append(i)
    bundles = defaultdict(list)
    for i in pool:
        bundles[(i["date"], i["group"], i["bucket"])].append(i)
    recent_rows, used, shown = [], set(), 0
    for i in pool:
        key = (i["date"], i["group"], i["bucket"])
        if key in used:
            continue
        rows = bundles[key]
        if len(rows) >= 3:
            used.add(key)
            url = comp_url.get(i["group"]) if i["bucket"] in ("公司", "公众号发表") else (
                topic_url.get(i["group"]) or screen_url.get(i["group"]))
            name = i["group"] if i["bucket"] in ("公司", "公众号发表") else disp(i["group"])
            titles = "；".join(r["title"].split("：")[0].split("独立")[0] for r in rows[:7])
            recent_rows.append('<li><a href="%s">%s（%d 篇）</a><div class="meta">%s · %s%s</div></li>' % (
                url or rows[0]["url"], html.escape(name), len(rows), i["date"], html.escape(titles[:90]),
                "等" if len(rows) > 7 else ""))
        else:
            recent_rows.append(li(i, 0))
        shown += 1
        if shown >= 30:
            break
    body = "<h1>%s</h1><p class=\"meta\">%d 篇报告 · %d 家公司 · 最近更新 %s</p>" % (
        SITE_NAME, len(items), len(companies), items[0]["date"] if items else "—")
    body += "<div class=\"grid big\">%s</div>" % "".join(
        '<a class="btn" href="%s">%s</a>' % (u, t) for u, t in [
            ("companies/index.html", "按公司"), ("topics/index.html", "专题与横评"), ("dates/index.html", "按时间"),
            ("types/index.html", "按类型"), ("wechat/index.html", "公众号发表版"), ("search.html", "搜索")])
    if available("reader/duan-popmart.html"):
        body += '<p><a class="btn" href="duan-popmart.html">段永平 × 泡泡玛特 · 原帖阅读器</a></p>'
    body += '<div id="recent-read"></div>'
    body += "<h2>最近更新</h2><ul class=\"list\">%s</ul>" % "".join(recent_rows)
    body += "<h2>报告最多的公司</h2><div class=\"grid\">%s</div>" % "".join(
        '<a class="btn" href="%s">%s %d</a>' % (comp_url[c], html.escape(c), len(companies[c])) for c in top[:16])
    write(out_dir, "index.html", shell("首页", '<div class="hero">' + body + "</div>", 0, section="首页"))
    write(out_dir, "404.html", shell("没有这一页", "<h1>没有这一页</h1><p><a href=\"index.html\">回首页</a></p>", 0))

    # RSS
    feed_items = [i for i in items if i["bucket"] not in NOISE_BUCKETS][:50]
    base = "https://xbtlin.github.io/ai-berkshire/"
    rss = ['<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>%s</title><link>%s</link><description>投资研究报告</description>' % (SITE_NAME, base)]
    for i in feed_items:
        rss.append("<item><title>%s</title><link>%s%s</link><guid>%s%s</guid><pubDate>%s</pubDate><description>%s</description></item>" % (
            html.escape(i["title"]), base, i["url"], base, i["url"],
            datetime.strptime(i["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000") if i["date"] else "",
            html.escape(" · ".join(x for x in [i["group"], i["type"]] if x))))
    rss.append("</channel></rss>")
    write(out_dir, "feed.xml", "".join(rss))

    # 原帖阅读器直接加载来源站点；页面本身只包含来源索引与辅助摘要。
    if available("reader/duan-popmart.html"):
        write(out_dir, "duan-popmart.html", read("reader/duan-popmart.html"))

    print("生成 %d 篇报告页，%d 家公司，%d 个专题，%d 个月份 -> %s" % (len(items), len(companies), len(topics) + len(screens), len(months), out_dir))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "site"))
    args = ap.parse_args()
    build(args.out)
