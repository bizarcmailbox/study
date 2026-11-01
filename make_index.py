#!/usr/bin/env python3
"""Generate index.html for the study site (Korean, mobile-friendly)."""
import html, os, re, sys
from datetime import datetime

site = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

def title_of(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            m = re.search(r"<title>(.*?)</title>", f.read(20000), re.S | re.I)
            return html.unescape(m.group(1).strip()) if m else ""
    except OSError:
        return ""

def day_files(folder):
    out = []
    d = os.path.join(site, folder)
    for name in os.listdir(d) if os.path.isdir(d) else []:
        m = re.fullmatch(r"day-(\d+)\.html", name)
        if m:
            out.append((int(m.group(1)), name))
    return sorted(out, reverse=True)

sections = []
for folder, label, emoji in [("japanese", "일본어", "🇯🇵"), ("chinese", "중국어", "🇨🇳"), ("bible", "성경 퀴즈", "📖")]:
    items = []
    for n, name in day_files(folder):
        t = title_of(os.path.join(site, folder, name))
        sub = t.split("·", 1)[1].strip() if "·" in t else ""
        items.append((f"{folder}/{name}", f"{label} Day {n}", sub))
    sections.append((f"{emoji} {label}", items))

french_order = ["french-songs-2.html", "french-quiz-2.html", "french-songs.html", "french-quiz.html"]
fdir = os.path.join(site, "french")
fnames = [f for f in french_order if os.path.exists(os.path.join(fdir, f))]
fnames += sorted(f for f in (os.listdir(fdir) if os.path.isdir(fdir) else []) if f.endswith(".html") and f not in fnames)
sections.append(("🇫🇷 프랑스어 노래", [(f"french/{f}", title_of(os.path.join(fdir, f)) or f, "") for f in fnames]))

parts = []
for head, items in sections:
    if not items:
        continue
    lis = "\n".join(
        f'<li><a href="{html.escape(href)}">{html.escape(t)}'
        + (f'<span>{html.escape(s)}</span>' if s else "") + "</a></li>"
        for href, t, s in items)
    parts.append(f"<section><h2>{head}</h2><ul>{lis}</ul></section>")

updated = datetime.now().strftime("%Y-%m-%d %H:%M")
page = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>나우 학습 자료</title>
<style>
body{{font-family:-apple-system,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;margin:0;background:#f5f6f8;color:#222}}
header{{background:#3d5afe;color:#fff;padding:20px 16px}} header h1{{margin:0;font-size:22px}} header p{{margin:6px 0 0;font-size:13px;opacity:.85}}
main{{padding:8px 12px 40px;max-width:640px;margin:auto}}
h2{{font-size:18px;margin:22px 4px 8px}}
ul{{list-style:none;padding:0;margin:0;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
li+li{{border-top:1px solid #eee}}
a{{display:block;padding:14px 16px;color:#1a237e;text-decoration:none;font-size:16px}}
a span{{display:block;color:#666;font-size:13px;margin-top:2px}}
a:active{{background:#eef}}
</style></head><body>
<header><h1>📚 나우 학습 자료</h1><p>최근 업데이트: {updated} (싱가포르 시간) · 최신 순</p></header>
<main>
{''.join(parts)}
</main></body></html>
"""
with open(os.path.join(site, "index.html"), "w", encoding="utf-8") as f:
    f.write(page)
print("index.html written")
