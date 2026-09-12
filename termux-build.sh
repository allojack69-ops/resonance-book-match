#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

# Resonance Book Match — Termux -> GitHub -> APK
# One command after GitHub CLI authentication.

REPO_DEFAULT="allojack69-ops/resonance-book-match"
REPO="${RESONANCE_REPO:-$REPO_DEFAULT}"
BRANCH="${RESONANCE_BRANCH:-main}"

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing: $1"; exit 1; }; }
need git
need gh

cd "$(dirname "$0")"

echo "== Resonance Book Match =="
echo "Repository: $REPO"

gh auth status

# Make sure this extracted folder is a real git repository.
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Initializing local git repository..."
  git init -b "$BRANCH"
  git add .
  git commit -m "Initial Resonance Book Match Android app"
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "Creating GitHub repository: $REPO"
  gh repo create "$REPO" --public --source=. --remote=origin --push
else
  echo "Pushing current repository"
  git add .
  if ! git diff --cached --quiet; then
    git commit -m "Update Resonance Book Match Android app"
  fi
  git branch -M "$BRANCH"
  git push -u origin "$BRANCH"
fi

echo "Starting GitHub Actions build..."
gh workflow run build-apk.yml --repo "$REPO" --ref "$BRANCH"

echo "Waiting for the APK build..."
sleep 5
RUN_ID="$(gh run list --repo "$REPO" --workflow build-apk.yml --limit 1 --json databaseId --jq '.[0].databaseId')"
gh run watch "$RUN_ID" --repo "$REPO" --exit-status

mkdir -p dist
rm -rf dist/resonance-book-match-apk
mkdir -p dist/resonance-book-match-apk

gh run download "$RUN_ID" --repo "$REPO" --name resonance-book-match-apk --dir dist/resonance-book-match-apk

APK="$(find dist/resonance-book-match-apk -type f -name '*.apk' | head -n 1)"
if [ -z "$APK" ]; then
  echo "APK was not found in the downloaded artifact."
  exit 1
fi

cp "$APK" ./resonance-book-match.apk

echo
echo "APK READY: $PWD/resonance-book-match.apk"
echo "Copy to shared storage with:"
echo "  cp resonance-book-match.apk /sdcard/Download/"
echo ""
echo "Then open Download/resonance-book-match.apk on the phone to install."
