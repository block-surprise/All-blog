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
        # カテゴリ判定（統一済み）
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
    <a class="card" href="/{a['path']}">
        <div class="tag" style="background:{a['color']}">{a['cat']}</div>
        <div class="title">{a['title']}</div>
        <div class="meta">{a['time']}</div>
    </a>
    """


# =====================
# HTML（ホーム）
# =====================
html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ひとりゲームニュース</title>
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon.png">
<style>
body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f5f7fb;
    color: #111;
}}

header {{
    background: white;
    padding: 16px;
    border-bottom: 1px solid #eee;
    font-weight: bold;
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
}}

.container {{
    max-width: 780px;
    margin: auto;
    padding: 14px;
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
</style>
</head>

<body>

<header>ひとりゲームニュース</header>

<nav class="nav">
  <a href="/game/index.html">ホーム</a>
  <a href="/game/mobile/">スマホ</a>
  <a href="/game/console/">家庭用</a>
  <a href="/game/news/">ニュース</a>
</nav>

<div class="container">
{cards}
</div>

</body>
</html>
"""


# =====================
# 保存
# =====================
os.makedirs("game", exist_ok=True)

with open("game/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("updated")
def build_category_page(category_name, articles, color, slug):

    cards = ""

    for a in articles:
        cards += f"""
        <a class="card" href="/{a['path']}">
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
body {{ font-family: sans-serif; background:#f5f7fb; }}
.container {{ max-width:780px; margin:auto; padding:14px; }}
.card {{ display:block; background:white; padding:14px; margin-bottom:8px; text-decoration:none; }}
.tag {{ font-size:11px; padding:3px 8px; border-radius:999px; color:white; }}
.title {{ font-weight:600; }}
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
   mobile_articles = [a for a in articles if a["cat"] == "mobile"]
console_articles = [a for a in articles if a["cat"] == "console"]
news_articles = [a for a in articles if a["cat"] == "news"]

build_category_page("スマホゲーム", mobile_articles, "#4f46e5", "mobile")
build_category_page("家庭用ゲーム", console_articles, "#059669", "console")
build_category_page("ゲームニュース", news_articles, "#dc2626", "news")
