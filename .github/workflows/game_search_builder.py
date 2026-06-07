import os
import re

def safe_filename(query):
    return re.sub(r'[^a-zA-Z0-9ぁ-んァ-ン一-龥_-]', '_', query)


def match(query, a):
    q = query.lower()
    return q in a["title"].lower()


def load_game_posts():
    posts = []

    base = "game/posts"

    if not os.path.exists(base):
        return posts

    for root, dirs, files in os.walk(base):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file).replace("\\", "/")

                posts.append({
                    "title": file.replace(".html", ""),
                    "path": path,
                    "cat": "ゲーム",
                    "ts": os.path.getmtime(path)
                })

    return posts


def build_game_search(query):

    articles = load_game_posts()

    filtered = [a for a in articles if match(query, a)]
    filtered = sorted(filtered, key=lambda x: x["ts"], reverse=True)

    cards = ""

    for a in filtered:
        cards += f"""
        <a class="card" href="/{a['path']}">
            <div class="tag">{a['cat']}</div>
            <div class="title">{a['title']}</div>
        </a>
        """

    html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>検索: {query}</title>

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

header {{
    background: white;
    padding: 16px;
    border-bottom: 1px solid #eee;
}}
</style>
</head>

<body>

<header>
<h1>検索結果: {query}</h1>
</header>
<nav class="nav">
  <a href="/index.html">ホーム</a>
  <a href="/posts/ai/">AI</a>
  <a href="/posts/gadgets/">ガジェット</a>
  <a href="/posts/news/">ニュース</a>
</nav>
<div class="container">
{cards if cards else "<p>結果なし</p>"}
</div>

</body>
</html>
"""

    os.makedirs("search/game", exist_ok=True)

    with open(f"search/game_{safe_filename(query)}.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("game search created")
