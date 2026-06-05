import os
import re
from datetime import datetime

POST_DIR = "posts"

articles = []

def extract_title(html_path):
    """HTMLの<h1>からタイトルを取得"""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        match = re.search(r"<h1>(.*?)</h1>", html)
        if match:
            return match.group(1)

    except:
        pass

    return "タイトルなし"

for root, dirs, files in os.walk(POST_DIR):
    for f in files:
        if not f.endswith(".html"):
            continue

        path = os.path.join(root, f).replace("\\", "/")

        # 👇ここが重要（ファイル名じゃなくHTMLから取得）
        title = extract_title(path)

        # カテゴリ判定
        if "/ai/" in path:
            cat = "AI"
            color = "#4f46e5"
        elif "/gadgets/" in path:
            cat = "ガジェット"
            color = "#059669"
        else:
            cat = "ニュース"
            color = "#dc2626"

        # 更新時間
        ts = os.path.getmtime(path)
        time = datetime.fromtimestamp(ts).strftime("%m-%d %H:%M")

        articles.append({
            "title": title,
            "path": path,
            "cat": cat,
            "color": color,
            "time": time,
            "ts": ts
        })

# 新しい順
articles = sorted(articles, key=lambda x: x["ts"], reverse=True)

cards = ""

for a in articles:
    cards += f"""
    <a class="card" href="{a['path']}">
        <div class="tag" style="background:{a['color']}">{a['cat']}</div>
        <div class="title">{a['title']}</div>
        <div class="meta">{a['time']}</div>
    </a>
    """

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ひとりテックニュース</title>

<style>
body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f5f7fb;
    color: #111;
}}

..nav {
    background: #111;
    padding: 12px 18px;
    display: flex;
    gap: 18px;
    position: sticky;
    top: 0;
    z-index: 1000;
    align-items: center;
}

.nav a {
    color: white;
    text-decoration: none;
    font-size: 14px;
    font-weight: 600;
    opacity: 0.85;
    padding: 6px 10px;
    border-radius: 8px;
    transition: 0.2s;
}

.nav a:hover {
    opacity: 1;
    background: rgba(255,255,255,0.12);
}
@media (max-width: 600px) {
    .nav {
        overflow-x: auto;
        white-space: nowrap;
        gap: 10px;
    }

    .nav a {
        font-size: 13px;
        flex-shrink: 0;
    }
}

header {{
    background: white;
    padding: 18px;
    border-bottom: 1px solid #eee;
}}

.container {{
    max-width: 800px;
    margin: auto;
    padding: 12px;
}}

.card {{
    display: block;
    background: white;
    margin: 12px 0;
    padding: 16px;
    border-radius: 16px;
    text-decoration: none;
    color: inherit;
}}

.tag {{
    display: inline-block;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 999px;
    color: white;
    margin-bottom: 8px;
}}

.title {{
    font-size: 16px;
    font-weight: 600;
}}

.meta {{
    font-size: 12px;
    color: #888;
}}
</style>
</head>

<body>
<header>
<h1>ひとりテックニュース</h1>
</header>
<nav class="nav">
  <a href="/index.html">ホーム</a>
  <a href="/posts/ai/">AI</a>
  <a href="/posts/gadgets/">ガジェット</a>
  <a href="/posts/news/">ニュース</a>
</nav>



<div class="container">
{cards}
</div>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("updated")
