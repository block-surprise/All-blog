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

        if file == "index.html":
            continue

        path = os.path.join(root, file).replace("\\", "/")
        title = extract_title(path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                body = f.read()
        except:
            body = ""

        if "/ai/" in path:
            cat = "AI"
            slug = "ai"
            color = "#4f46e5"

        elif "/gadgets/" in path:
            cat = "ガジェット"
            slug = "gadgets"
            color = "#059669"

        else:
            cat = "ニュース"
            slug = "news"
            color = "#dc2626"

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

        articles.append({
            "title": title,
            "body": body,
            "path": path,
            "cat": cat,
            "slug": slug,
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
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3571574988222927"crossorigin="anonymous"></script>
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon.png">
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
.keywords-section {{
    background: white;
    padding: 14px;
    border-bottom: 1px solid #eee;
}}

.keywords-title {{
    font-size: 13px;
    margin: 0 0 10px 0;
    color: #666;
}}

.keywords-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
}}

.keywords-grid a {{
    display: block;
    text-align: center;
    padding: 10px 8px;
    border-radius: 10px;
    background: #f1f5f9;
    text-decoration: none;
    color: #111;
    font-size: 12px;
    transition: 0.15s;
}}

.keywords-grid a:hover {{
    background: #e2e8f0;
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
.footer {{
    text-align: center;
    padding: 20px;
    font-size: 13px;
    color: #666;
}}

.footer a {{
    color: #666;
    text-decoration: none;
}}

.footer a:hover {{
    text-decoration: underline;
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
<div class="keywords-section">
  <h2 class="keywords-title">おすすめキーワード</h2>

  <div class="keywords-grid">
    <a href="/search/iPhone">iPhone</a>
    <a href="/search/OpenAI">OpenAI</a>
    <a href="/search/スポーツ">スポーツ</a>
    <a href="/search/電車">電車</a>
    <a href="/search/ゲーム">ゲーム</a>
    <a href="/search/AI">AI</a>
  </div>
</div>

<div class="container">

{cards}
</div>
<div class="categories">
  <a href="/posts/ai/">AIニュース</a>
  <a href="/posts/gadgets/">ガジェット</a>
  <a href="/posts/news/">国内ニュース</a>
</div>
<footer class="footer">

  <a href="/privacy.html">プライバシーポリシー</a>

</footer>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
    # =====================
# カテゴリページ生成
# =====================

def build_category_page(category_name, articles, color, slug):
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

os.makedirs(f"posts/{slug}", exist_ok=True)

with open(f"posts/{slug}/index.html", "w", encoding="utf-8") as f:
        f.write(html)


# =====================
# フィルタして生成
# =====================

ai_articles = [a for a in articles if a["cat"] == "AI"]
gadgets_articles = [a for a in articles if a["cat"] == "ガジェット"]
news_articles = [a for a in articles if a["cat"] == "ニュース"]

build_category_page("AI", ai_articles, "#4f46e5", "ai")
build_category_page("ガジェット", gadgets_articles, "#059669", "gadgets")
build_category_page("ニュース", news_articles, "#dc2626", "news")
print("updated")
