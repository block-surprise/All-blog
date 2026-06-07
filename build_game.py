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
body {{ font-family:sans-serif; background:#f5f7fb; }}
.container {{ max-width:780px; margin:auto; padding:14px; }}
.card {{ display:block; background:white; padding:14px; margin-bottom:8px; text-decoration:none; }}
.tag {{ font-size:11px; padding:3px 8px; border-radius:999px; color:white; }}
</style>
</head>
<body>

<h1>ひとりゲームニュース</h1>

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
