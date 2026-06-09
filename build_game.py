import json
import os
import re
from datetime import datetime

POST_DIR = "game/posts"
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
            cat = "minecraft"
            color = "#22c55e"

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
# 最新記事JSON生成
# =====================
latest = []

for a in articles[:5]:
    latest.append({
        "title": a["title"],
        "url": "/" + a["path"]
    })

os.makedirs("game", exist_ok=True)

with open("game/latest.json", "w", encoding="utf-8") as f:
    json.dump(
        latest,
        f,
        ensure_ascii=False,
        indent=2
    )
# =====================
# カード生成
# =====================
cards = ""
for a in articles:
    cards += f"""
    <a class="card" href="/{a['path']}"">
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
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta charset="UTF-8">
<title>ひとりゲームニュース</title>
<meta name="description" content="マインクラフト攻略・建築・自動装置など最新情報や攻略法をわかりやすく解説するゲームニュースサイト">
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
<h1>ひとりゲームニュース</h1>
</header>

<nav class="nav">
  <a href="/game/index.html">ホーム</a>
<a href="search/初心者">初心者</a>
<a href="search/建築">建築</a>
<a href="search/サバイバル">サバイバル</a>
</nav>


<div class="keywords-section">
  <h2 class="keywords-title">おすすめキーワード</h2>

  <div class="keywords-grid">
    <a href="search/マイクラ">マイクラ</a>
    <a href="search/初心者">初心者</a>
    <a href="search/建築">建築</a>
    <a href="search/自動装置">自動装置</a>
    <a href="search/経験値トラップ">経験値TT</a>
    <a href="search/アイアンゴーレムトラップ">鉄トラップ</a>
  </div>
</div>



<div class="container">
{cards}
</div>
<div class="categories">
<a href="search/マイクラ">マイクラ</a>
<a href="search/建築">建築</a>
<a href="search/自動装置">自動装置</a>
</div>
<footer class="footer">

  <a href="https://htn-news.f5.si/privacy.html">プライバシーポリシー</a>
</footer>
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
