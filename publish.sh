#!/usr/bin/env bash
# publish.sh — sync David's study HTML files to GitHub Pages (bizarcmailbox/study).
# Usage: /workspace/study-site/publish.sh [--no-push]
# Idempotent: safe to run any time; commits only when something changed.
set -euo pipefail

SITE=/workspace/study-site
REPO=bizarcmailbox/study
BASE_URL="https://bizarcmailbox.github.io/study"
TOKEN_FILE="$HOME/.config/nau/gh_token"
NO_PUSH=0; [[ "${1:-}" == "--no-push" ]] && NO_PUSH=1

exec 9>/tmp/study-site-publish.lock
flock -w 600 9   # serialize runs from different routines

cd "$SITE"
mkdir -p japanese chinese bible french
# Sync only the quiz HTML files (no summaries, audio dirs, .apkg, etc.)
sync_dir() {  # sync_dir SRC DEST GLOB...  (mirror matching files, delete stale ones)
  local src=$1 dest=$2; shift 2
  mkdir -p "$dest"
  local f base keep=()
  shopt -s nullglob
  for g in "$@"; do for f in "$src"/$g; do
    base=$(basename "$f"); keep+=("$base")
    cmp -s "$f" "$dest/$base" || cp -p "$f" "$dest/$base"
  done; done
  for f in "$dest"/*; do
    base=$(basename "$f")
    [[ " ${keep[*]} " == *" $base "* ]] || rm -f "$f"
  done
  shopt -u nullglob
}
sync_dir /workspace/japanese-vocab/daily japanese 'day-*.html'
sync_dir /workspace/chinese-vocab/daily  chinese  'day-*.html'
sync_dir /workspace/bible-quiz/daily     bible    'day-*.html'
sync_dir /workspace/french-songs         french   'french-songs*.html' 'french-quiz*.html'
touch .nojekyll

# Refuse files >= 95 MB (GitHub hard limit is 100 MB)
big=$(find japanese chinese bible french -type f -size +95M || true)
if [[ -n "$big" ]]; then echo "ERROR: files too large for GitHub:" >&2; echo "$big" >&2; exit 1; fi

python3 "$SITE/make_index.py" "$SITE"

[[ -d .git ]] || { git init -q -b main; git remote add origin "https://github.com/$REPO.git"; }
git config user.name  "Nau (Grok Bot)"
git config user.email "bizarcmailbox@users.noreply.github.com"
git add -A
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  git commit -q -m "Update study files $(date '+%Y-%m-%d %H:%M %Z')"
  echo "Committed: $(git log -1 --format=%s)"
fi

if [[ $NO_PUSH -eq 0 ]]; then
  TOKEN=$(cat "$TOKEN_FILE")
  AUTH=$(printf 'x-access-token:%s' "$TOKEN" | base64 -w0)
  # Token passed only as a transient header: never stored in .git/config or printed.
  git -c http.extraheader="AUTHORIZATION: basic $AUTH" push -q origin main 2>&1 | sed "s/$TOKEN/***/g"
  unset TOKEN AUTH
  echo "Pushed to github.com/$REPO (Pages refresh takes ~1 min)."
fi

echo "Index:    $BASE_URL/"
echo "Japanese: $BASE_URL/japanese/day-XX.html   (e.g. day-15.html)"
echo "Chinese:  $BASE_URL/chinese/day-XX.html    (e.g. day-05.html)"
echo "Bible:    $BASE_URL/bible/day-N.html       (e.g. day-5.html)"
echo "French:   $BASE_URL/french/french-songs.html, french-quiz.html, french-songs-2.html, french-quiz-2.html, french-songs-3.html, french-quiz-3.html"
