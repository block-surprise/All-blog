import os
import re
from datetime import datetime

POST_DIR = "game_posts"
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

        # =====================
        # カテゴリ判定
        # =====================
        if "/mobile/" in path:
            cat = "mobile"
            color = "#4f46e5"

        elif "/console/" in path:
            cat = "console"
            color = "#059669"

        else:
            cat = "news"
            color = "#dc2626"

        filename = os.path.basename(path)

        try:
            dt = datetime.strptime(filename.replace(".html", ""), "%Y-%m-%d-%H%M%S")
            ts = dt.timestamp()
            time_str = dt.strftime("%m-%d %H:%M")
        except:
            ts = os.path.getmtime(path)
            time_str = datetime.fromtimestamp(ts).strftime("%m-%d %H:%M")

        articles.append({
            "title": title,
            "path": path,
            "cat": cat,
            "color": color,
            "time": time_str,
            "ts": ts,
            "body": body
        })


# =====================
# ソート
# =====================
articles = sorted(articles, key=lambda x: x["ts"], reverse=True)


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
# ホームHTML
# =====================
html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>ひとりゲームニュース</title>
<style>
header {{
    background: white;
    padding: 16px;
    border-bottom: 1px solid #eee;
    font-weight: bold;
}}

.nav {{
    background: #111;
    padding: 12px 18px;
@@ -146,62 +146,12 @@ def extract_title(html_path):
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
    padding: 14px;
}}

.card {{
@@ -213,25 +163,6 @@ def extract_title(html_path):
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
@@ -250,70 +181,45 @@ def extract_title(html_path):
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
<h1>ひとりゲームニュース</h1>
</header>

<nav class="nav">
  <a href="/game/index.html">ホーム</a>
<a href="/game/mobile/">スマホ</a>
<a href="/game/console/">家庭用</a>
<a href="/game/news/">ゲームニュース</a>
  <a href="/game/mobile/">スマホ</a>
  <a href="/game/console/">家庭用</a>
  <a href="/game/news/">ニュース</a>
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

</body>
</html>
"""

os.makedirs("game", exist_ok=True)

with open("game/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("updated")


# =====================
# カテゴリページ
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
<title>{category_name}</title>
<style>
body {{ font-family:sans-serif; background:#f5f7fb; }}
.container {{ max-width:780px; margin:auto; padding:14px; }}
.card {{ display:block; background:white; padding:14px; margin-bottom:8px; text-decoration:none; }}
</style>
</head>
<body>

<h1>{category_name}</h1>

<div class="container">
{cards}
</div>

</body>
</html>
"""

    os.makedirs(f"game/{slug}", exist_ok=True)

    with open(f"game/{slug}/index.html", "w", encoding="utf-8") as f:
        f.write(html)


# =====================
# フィルタ
# =====================
mobile_articles = [a for a in articles if a["cat"] == "mobile"]
console_articles = [a for a in articles if a["cat"] == "console"]
news_articles = [a for a in articles if a["cat"] == "news"]

build_category_page("スマホゲーム", mobile_articles, "#4f46e5", "mobile")
build_category_page("家庭用ゲーム", console_articles, "#059669", "console")
build_category_page("ゲームニュース", news_articles, "#dc2626", "news")
