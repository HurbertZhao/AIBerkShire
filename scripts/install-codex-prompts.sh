#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${CODEX_HOME:-$HOME/.codex}/prompts"

python3 "$ROOT/scripts/sync-codex-prompts.py"
mkdir -p "$DEST"
cp "$ROOT"/codex-prompts/*.md "$DEST"/

echo "Installed Codex slash prompts to $DEST"
echo "Restart Codex to pick up new slash prompts."
