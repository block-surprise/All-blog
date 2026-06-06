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
        # 日時処理（ファイル名優先）
        # =====================
        filename = os.path.basename(path)

        try:
            dt = datetime.strptime(
                filename.replace(".html", ""),
                "%Y-%m-%d-%H%M%S"
            )

            time_str = dt.strftime("%m-%d %H:%M")
            ts = dt.timestamp()

        except:
            ts = os.path.getmtime(path)
            time_str = datetime.fromtimestamp(ts).strftime("%m-%d %H:%M")

        # ★ここが超重要（追加忘れがバグ原因）
        articles.append({
            "title": title,
            "path": path,
            "cat": cat,
            "color": color,
            "time": time_str,
            "ts": ts
        })


# =====================
# 並び替え（新しい順）
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
# HTML生成
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

/* ナビ */
.nav {{
    background: #111;
    padding: 12px 18px;
    display: flex;
    gap: 14px;
    position: sticky;
    top: 0;
    z-index: 1000;
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

/* ヘッダー */
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

/* コンテナ */
.container {{
    max-width: 780px;
    margin: auto;
    padding: 10px 12px;
}}

/* カード */
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
    margin-bottom: 4px;
}}

.meta {{
    font-size: 12px;
    color: #888;
}}

/* モバイル */
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

<div class="container">
{cards}
</div>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("updated")
