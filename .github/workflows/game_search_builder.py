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
<html>
<body>
<h1>ゲーム検索: {query}</h1>
{cards}
</body>
</html>
"""

    os.makedirs("search/game", exist_ok=True)

    with open(f"search/game_{safe_filename(query)}.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("game search created")
