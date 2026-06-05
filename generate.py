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
あなたはプロのテックニュースライターです。

以下のテーマで記事を書いてください：

テーマ：{topic}

条件：
- 見出し付き（H2）
- 1500〜2500文字
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
    font-family: sans-serif;
    max-width: 800px;
    margin: auto;
    padding: 20px;
    background: #f4f6f8;
    line-height: 1.8;
    color: #111;
}

nav {
    background: #111;
    padding: 10px;
    margin-bottom: 20px;
    border-radius: 10px;
}

nav a {
    color: white;
    margin-right: 15px;
    text-decoration: none;
    font-size: 14px;
}

.article {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

h1 {
    font-size: 26px;
    margin-bottom: 10px;
}

h2 {
    margin-top: 25px;
    font-size: 20px;
}

img {
    width: 100%;
    border-radius: 10px;
    margin-bottom: 20px;
}

.category {
    font-size: 13px;
    color: gray;
    margin-bottom: 10px;
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
