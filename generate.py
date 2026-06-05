import os
import random
import feedparser
import urllib.parse
import google.generativeai as genai
from datetime import datetime

# =====================
# APIキー
# =====================
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# =====================
# RSSトレンド取得
# =====================
rss_url = "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
feed = feedparser.parse(rss_url)

topic = random.choice(feed.entries[:10]).title

# =====================
# カテゴリ分類
# =====================
def get_category(text):
    text = text.lower()

    if any(w in text for w in ["ai", "chatgpt", "gemini", "人工知能"]):
        return "ai"
    elif any(w in text for w in ["iphone", "android", "pc", "スマホ", "ガジェット"]):
        return "gadgets"
    else:
        return "news"

category = get_category(topic)

# =====================
# サムネ画像
# =====================
def get_image(query):
    base = "https://source.unsplash.com/800x400/?"
    return base + urllib.parse.quote(query)

image_url = get_image(topic)

# =====================
# SEOタイトル生成
# =====================
title_prompt = f"""
あなたはSEO専門の編集者です。

以下のニュースからクリックされるタイトルを1つ作ってください：

テーマ：{topic}

条件：
- 30文字以内
- 日本語
- クリックしたくなる
- 意外性を入れる
"""

title = model.generate_content(title_prompt).text.strip()

# =====================
# 本文生成
# =====================
body_prompt = f"""
あなたはプロのニュースライターです。

以下のテーマで記事を書いてください：

テーマ：{topic}

条件：
- 見出し付き（H2）
- 8000〜12000文字
- 初心者向け
- 具体例を入れる
- 自然な日本語
"""

body = model.generate_content(body_prompt).text

# =====================
# 記事HTML生成
# =====================
def build_html(title, body, category, image_url):
    return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>

<style>
body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f4f6f8;
    color: #111;
    line-height: 1.8;
}

/* ナビ */
nav {
    background: #111;
    padding: 12px 16px;
    position: sticky;
    top: 0;
    z-index: 10;
}

nav a {
    color: white;
    margin-right: 14px;
    text-decoration: none;
    font-size: 13px;
    opacity: 0.9;
}

nav a:hover {
    opacity: 1;
}

/* 全体レイアウト */
.container {
    max-width: 780px;
    margin: auto;
    padding: 16px;
}

/* 記事カード */
.article {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}

/* サムネ */
.article img {
    width: 100%;
    border-radius: 12px;
    margin-bottom: 18px;
}

/* カテゴリラベル */
.category {
    display: inline-block;
    font-size: 12px;
    padding: 4px 10px;
    border-radius: 999px;
    background: #eef2ff;
    color: #4f46e5;
    margin-bottom: 10px;
}

/* タイトル */
h1 {
    font-size: 24px;
    margin: 10px 0 18px;
    letter-spacing: -0.02em;
}

/* 見出し */
h2 {
    margin-top: 28px;
    font-size: 18px;
    border-left: 4px solid #4f46e5;
    padding-left: 10px;
}

/* 本文 */
p {
    margin: 12px 0;
    font-size: 15px;
}

/* 強調 */
strong {
    font-weight: 600;
}

/* モバイル最適化 */
@media (max-width: 600px) {
    .container {
        padding: 12px;
    }

    h1 {
        font-size: 20px;
    }
}
</style>
</head>
<body>

<nav>
  <a href="/index.html">ホーム</a>
  <a href="/posts/ai/">AI</a>
  <a href="/posts/gadgets/">ガジェット</a>
  <a href="/posts/news/">ニュース</a>
</nav>

<div class="article">

<img src="{image_url}" />

<div class="category">カテゴリ：{category}</div>

<h1>{title}</h1>

<div>
{body}
</div>

</div>

</body>
</html>
"""

# =====================
# 保存
# =====================
os.makedirs(f"posts/{category}", exist_ok=True)

date = datetime.now().strftime("%Y-%m-%d")
filename = f"posts/{category}/{date}.html"

with open(filename, "w", encoding="utf-8") as f:
    f.write(build_html(title, body, category, image_url))

print("記事生成完了:", title)
