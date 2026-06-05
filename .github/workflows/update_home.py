import os
from datetime import datetime

POST_DIR = "posts"

articles = []

for root, dirs, files in os.walk(POST_DIR):
    for f in files:
        if f.endswith(".html"):
            path = os.path.join(root, f).replace("\\", "/")
            title = f.replace(".html", "")

            if "/ai/" in path:
                cat = "AI"
                color = "#4f46e5"
            elif "/gadgets/" in path:
                cat = "ガジェット"
                color = "#059669"
            else:
                cat = "ニュース"
                color = "#dc2626"

            articles.append({
                "title": title,
                "path": path,
                "cat": cat,
                "color": color,
                "time": datetime.now().strftime("%m-%d")
            })

articles = sorted(articles, key=lambda x: x["path"], reverse=True)

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
body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f5f7fb;
    color: #111;
}

.nav {
    background: #111;
    padding: 10px 14px;
    display: flex;
    gap: 14px;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.nav a {
    color: white;
    text-decoration: none;
    font-size: 13px;
    opacity: 0.85;
}

.nav a:hover {
    opacity: 1;
}

header {
    background: white;
    padding: 18px;
    border-bottom: 1px solid #eee;
}

header h1 {
    margin: 0;
    font-size: 18px;
}

.container {
    max-width: 800px;
    margin: auto;
    padding: 12px;
}

.card {
    display: block;
    background: white;
    margin: 12px 0;
    padding: 16px;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    text-decoration: none;
    color: inherit;
    transition: 0.2s;
    border-left: 4px solid #4f46e5;
}

.card:hover {
    transform: translateY(-3px);
}

.tag {
    display: inline-block;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 999px;
    margin-bottom: 8px;
    background: #eef2ff;
    color: #4f46e5;
    font-weight: 600;
}

.title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 6px;
}

.meta {
    font-size: 12px;
    color: #888;
}
</style>

</head>
<body>

<nav class="nav">
  <a href="/index.html">ホーム</a>
  <a href="/posts/ai/">AI</a>
  <a href="/posts/gadgets/">ガジェット</a>
  <a href="/posts/news/">ニュース</a>
</nav>

<header>
<h1>ひとりテックニュース</h1>
</header>

<div class="container">
{cards}
</div>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("updated")
