#!/bin/bash
# 重新生成阅读站点并发布到 gh-pages 分支（https://xbtlin.github.io/ai-berkshire/）。
# 用法：bash tools/deploy_site.sh
# 说明：仓库令牌没有 workflow 权限，所以不走 Actions，改为本地构建后推送 gh-pages；
#       网络不稳时按目录分批提交、逐批推送，失败自动重试。
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="${TMPDIR:-/tmp}/aib-site-$$"
SITE="$TMP/site"; WT="$TMP/ghp"
PY="${PYTHON:-python3}"
mkdir -p "$TMP"
"$PY" "$ROOT/tools/build_site.py" --out "$SITE" || exit 1
cd "$ROOT" && git fetch -q origin gh-pages
git worktree add -q --detach "$WT" origin/gh-pages || exit 1
cd "$WT"
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -R "$SITE/." .
push() { for i in 1 2 3 4 5 6; do git -c http.postBuffer=524288000 -c http.version=HTTP/1.1 push -q origin HEAD:refs/heads/gh-pages 2>/dev/null && return 0; sleep 5; done; echo "推送失败：$1"; return 1; }
batch() { git add -A -- "$@" 2>/dev/null; git diff --cached --quiet && return 0; git -c core.quotepath=false commit -q -m "阅读站点更新：$*"; push "$*"; }
batch index.html style.css 404.html .nojekyll search.html search.json feed.xml
batch companies topics screens dates types wechat
batch files
for h in 0 1 2 3 4 5 6 7 8 9 a b c d e f; do batch r/$h*; done
git add -A; git diff --cached --quiet || { git -c core.quotepath=false commit -q -m "阅读站点更新：清理"; push 清理; }
cd "$ROOT" && git worktree remove --force "$WT"; rm -rf "$TMP"
gh api -X POST repos/xbtlin/ai-berkshire/pages/builds >/dev/null 2>&1
echo "已发布：https://xbtlin.github.io/ai-berkshire/"
