import os
from flask import Flask, request

app = Flask(__name__)

# =====================
# 検索マッチ関数
# =====================
def match(query, a):
    q = query.lower()

    # タイトル検索
    if q in a.get("title", "").lower():
        return True

    # 本文検索（あれば）
    if a.get("body"):
        if q in a["body"].lower():
            return True

    return False


# =====================
# 検索HTML生成
# =====================
def build_search_html(query, articles):

    filtered = []

    for a in articles:
        if match(query, a):
            filtered.append(a)

    filtered = sorted(filtered, key=lambda x: x.get("ts", 0), reverse=True)

    cards = ""

    for a in filtered:
        cards += f"""
        <a class="card" href="/{a['path']}">
            <div class="tag" style="background:{a.get('color', '#999')}">{a.get('cat', '')}</div>
            <div class="title">{a.get('title')}</div>
            <div class="meta">{a.get('time', '')}</div>
        </a>
        """

    return f"""
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

<div class="container">
{cards if cards else "<p>結果なし</p>"}
</div>

</body>
</html>
"""


# =====================
# /search?q= ルート
# =====================
@app.route("/search")
def search():
    q = request.args.get("q", "")

    # articlesは外から渡す想定（generate.pyとかで作ってるやつ）
    return build_search_html(q, articles)


if __name__ == "__main__":
    app.run(debug=True)
