#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
REPO="${RESONANCE_REPO:-allojack69-ops/resonance-book-match}"
mkdir -p dist
rm -rf dist/apk
mkdir -p dist/apk
RUN_ID="$(gh run list --repo "$REPO" --workflow build-apk.yml --limit 1 --json databaseId --jq '.[0].databaseId')"
gh run download "$RUN_ID" --repo "$REPO" --name resonance-book-match-apk --dir dist/apk
find dist/apk -type f -name '*.apk' -print
