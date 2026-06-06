import os
import re
from datetime import datetime

POST_DIR = "posts"
articles = []

# =====================
# タイトル抽出
# =====================
def extract_title(html_path):
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        match = re.search(r"<h1>(.*?)</h1>", html)
        if match:
            return match.group(1)

    except:
        pass

    return "タイトルなし"


# =====================
# 記事収集
# =====================
for root, dirs, files in os.walk(POST_DIR):
    for file in files:
        if not file.endswith(".html"):
            continue

        path = os.path.join(root, file).replace("\\", "/")
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

        # =====================
        # 日時
        # =====================
        filename = os.path.basename(path)

        try:
            dt = datetime.strptime(
                filename.replace(".html", ""),
                "%Y-%m-%d-%H%M%S"
            )
            ts = dt.timestamp()
            time_str = dt.strftime("%m-%d %H:%M")

        except:
            ts = os.path.getmtime(path)
            time_str = datetime.fromtimestamp(ts).strftime("%m-%d %H:%M")

        # ★追加
        articles.append({
            "title": title,
            "path": path,
            "cat": cat,
            "color": color,
            "time": time_str,
            "ts": ts
        })


# =====================
# ソート
# =====================
articles = sorted(articles, key=lambda x: x["ts"], reverse=True)

from search_builder import build_search_page

keywords = ["ChatGPT", "iPhone", "OpenAI", "AI", "ニュース","電車","ゲーム","政治","事件","スポーツ"]

for q in keywords:

    build_search_page(q, articles)

# =====================
# カード生成
# =====================
cards = ""
for a in articles:
    cards += f"""
    <a class="card" href="{a['path']}">
        <div class="tag" style="background:{a['color']}">{a['cat']}</div>
        <div class="title">{a['title']}</div>
        <div class="meta">{a['time']}</div>
    </a>
    """


# =====================
# HTML
# =====================
html = f"""
<!DOCTYPE html>
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

.nav {{
    background: #111;
    padding: 12px 18px;
    display: flex;
    gap: 14px;
    position: sticky;
    top: 0;
    overflow-x: auto;
}}

.nav a {{
    color: white;
    text-decoration: none;
    font-size: 14px;
    font-weight: 600;
    opacity: 0.85;
    padding: 6px 10px;
    border-radius: 8px;
    white-space: nowrap;
}}

.nav a:hover {{
    opacity: 1;
    background: rgba(255,255,255,0.12);
}}

header {{
    background: white;
    padding: 18px;
    border-bottom: 1px solid #eee;
}}

header h1 {{
    margin: 0;
    font-size: 18px;
    font-weight: 700;
}}
.keywords {{
    display: flex;
    overflow-x: auto;
    gap: 8px;
    padding: 10px;
    background: white;
    border-bottom: 1px solid #eee;
}}

.keywords a {{
    white-space: nowrap;
    font-size: 12px;
    padding: 6px 10px;
    border-radius: 999px;
    background: #f1f5f9;
    text-decoration: none;
    color: #111;
}}
.container {{
    max-width: 780px;
    margin: auto;
    padding: 10px 12px;
}}

.card {{
    display: block;
    background: white;
    padding: 14px;
    border-bottom: 1px solid #eee;
    text-decoration: none;
    color: inherit;
}}

.card:hover {{
    background: #f9fafb;
}}
.categories {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    padding: 10px;
}}

.categories a {{
    background: white;
    padding: 12px;
    text-align: center;
    border-radius: 10px;
    text-decoration: none;
    font-size: 13px;
    border: 1px solid #eee;
}}
.tag {{
    display: inline-block;
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 999px;
    color: white;
    margin-bottom: 6px;
}}

.title {{
    font-size: 15px;
    font-weight: 600;
}}

.meta {{
    font-size: 12px;
    color: #888;
}}

@media (max-width: 600px) {{
    header h1 {{
        font-size: 16px;
    }}

    .card {{
        padding: 12px;
    }}
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
<div class="keywords">
  <a href="/ai/">AI</a>
  <a href="/search/iPhone">iPhone</a>
  <a href="/search/OpenAI">OpenAI</a>
  <a href="/search/スポーツ">スポーツ</a>
  <a href="/search/電車">電車</a>
  <a href="/search/ゲーム">ゲーム</a>
</div>

<div class="container">

{cards}
</div>
<div class="categories">
  <a href="/posts/ai/">AIニュース</a>
  <a href="/posts/gadgets/">ガジェット</a>
  <a href="/posts/news/">国内ニュース</a>
</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
    # =====================
# カテゴリページ生成
# =====================

def build_category_page(category_name, articles, color):
    cards = ""

    for a in articles:
        cards += f"""
        <a class="card" href="{a['path']}">
            <div class="tag" style="background:{a['color']}">{a['cat']}</div>
            <div class="title">{a['title']}</div>
            <div class="meta">{a['time']}</div>
        </a>
        """

    html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{category_name}</title>

<style>
body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f5f7fb;
}}

.container {{
    max-width: 780px;
    margin: auto;
    padding: 10px 12px;
}}

.card {{
    display: block;
    background: white;
    padding: 14px;
    border-bottom: 1px solid #eee;
    text-decoration: none;
    color: inherit;
}}

.tag {{
    display: inline-block;
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 999px;
    color: white;
}}

.title {{
    font-size: 15px;
    font-weight: 600;
}}

.meta {{
    font-size: 12px;
    color: #888;
}}

header {{
    background: white;
    padding: 16px;
    border-bottom: 1px solid #eee;
}}
</style>
</head>

<body>

<header>
<h1>{category_name}</h1>
</header>

<div class="container">
{cards}
</div>

</body>
</html>
"""

    os.makedirs(f"posts/{category_name.lower()}", exist_ok=True)

    with open(f"posts/{category_name.lower()}/index.html", "w", encoding="utf-8") as f:
        f.write(html)


# =====================
# フィルタして生成
# =====================

ai_articles = [a for a in articles if a["cat"] == "AI"]
gadgets_articles = [a for a in articles if a["cat"] == "ガジェット"]
news_articles = [a for a in articles if a["cat"] == "ニュース"]

build_category_page("AI", ai_articles, "#4f46e5")
build_category_page("ガジェット", gadgets_articles, "#059669")
build_category_page("ニュース", news_articles, "#dc2626")

print("updated")
