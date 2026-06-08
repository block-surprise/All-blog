import os
import re

# =====================
# 安全なファイル名変換
# =====================
def safe_filename(query):
    return re.sub(r'[^a-zA-Z0-9ぁ-んァ-ン一-龥_-]', '_', query)


# =====================
# 検索マッチ
# =====================
def match(query, a):
    q = query.lower()

    if q in a["title"].lower():
        return True

    if "body" in a and a["body"]:
        if q in a["body"].lower():
            return True

    return False


# =====================
# 検索ページ生成（/search/xxx.html方式）
# =====================
def build_search_page(query, articles):

    filtered = [a for a in articles if match(query, a)]
    filtered = sorted(filtered, key=lambda x: x["ts"], reverse=True)

    cards = ""

    for a in filtered:
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
  <a href="/game/index.html">ホーム</a>
  <a href="/game/search/初心者.html">初心者</a>
  <a href="/game/search/建築.html">建築</a>
  <a href="/game/search/自動装置.html">自動装置</a>
</nav>
<div class="container">
{cards if cards else "<p>結果なし</p>"}
</div>

</body>
</html>
"""
    os.makedirs("game/search", exist_ok=True)

    filename = safe_filename(query)

    with open(f"game/search/{filename}.html", "w", encoding="utf-8") as f:

        f.write(html)

    print("search page created:", filename)
    def build_all_search_pages(articles):

    os.makedirs("game/search", exist_ok=True)

    keywords = set()

    # タイトルからキーワード抽出
    for a in articles:
        for word in a["title"].split():
            if len(word) >= 2:
                keywords.add(word)

    # 既存検索ページ削除（ゴミ防止）
    for f in os.listdir("game/search"):
        if f.endswith(".html"):
            os.remove(os.path.join("game/search", f))

    # 新規生成
    for kw in keywords:

        filename = safe_filename(kw)

        build_search_page(kw, articles)

    print("all search pages rebuilt:", len(keywords))
