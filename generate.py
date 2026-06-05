import os
import random
import feedparser
import urllib.parse
import requests
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

# ノイズ除去（重要）
clean_topic = topic.split(" - ")[0].split("｜")[0]


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

category = get_category(clean_topic)


# =====================
# 画像取得（Wikipedia優先）
# =====================
def get_wikipedia_image(query):
    try:
        url = "https://ja.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(query)
        res = requests.get(url, timeout=5).json()

        if "thumbnail" in res and res["thumbnail"]:
            return res["thumbnail"]["source"]
        return None
    except:
        return None


def get_unsplash_image(query):
    return f"https://source.unsplash.com/800x400/?{urllib.parse.quote(query)}"


image_url = get_wikipedia_image(clean_topic)

if not image_url:
    image_url = get_unsplash_image(clean_topic.split(" ")[0])


# =====================
# タイトル生成
# =====================
title_prompt = f"""
あなたはSEO編集者です。

テーマ：{clean_topic}

30文字以内でクリックされるタイトルを作ってください。

ルール：
- 30文字以内
- 日本語
- タイトルだけ出力
- 記号・補足禁止
"""

title = model.generate_content(title_prompt).text.strip()


# =====================
# 本文（HTMLで生成）
# =====================
body_prompt = f"""
あなたはプロのテックメディア編集者です。

テーマ：{clean_topic}

以下構成でHTMLで書いてください：

<h2>なぜ重要か</h2>
<p></p>

<h2>背景</h2>
<p></p>

<h2>詳細解説</h2>
<p></p>

<h2>具体例</h2>
<p></p>

<h2>今後の影響</h2>
<p></p>

<h2>まとめ</h2>
<p>3行で簡潔に</p>

条件：
- 1500〜3500文字
- HTMLのみ
- 説明禁止
"""

body = model.generate_content(body_prompt).text


# =====================
# HTML生成
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
body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f4f6f8;
    color: #111;
    line-height: 1.8;
}}

.site-header {{
    background: white;
    padding: 18px;
    font-weight: bold;
    border-bottom: 1px solid #eee;
}}

nav {{
    background: #111;
    padding: 12px 16px;
    position: sticky;
    top: 0;
    display: flex;
    gap: 14px;
}}

nav a {{
    color: white;
    text-decoration: none;
    font-size: 13px;
}}

.container {{
    max-width: 780px;
    margin: auto;
    padding: 16px;
}}

.article {{
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}}

.article img {{
    width: 100%;
    border-radius: 12px;
}}

.category {{
    display: inline-block;
    font-size: 12px;
    padding: 4px 10px;
    border-radius: 999px;
    background: #eef2ff;
    color: #4f46e5;
    margin: 10px 0;
}}

h2 {{
    border-left: 4px solid #4f46e5;
    padding-left: 10px;
    font-size: 18px;
    margin-top: 28px;
}}
</style>
</head>
<body>

<header class="site-header">ひとりテックニュース</header>

<nav>
  <a href="/index.html">ホーム</a>
  <a href="/posts/ai/">AI</a>
  <a href="/posts/gadgets/">ガジェット</a>
  <a href="/posts/news/">ニュース</a>
</nav>

<div class="container">

<div class="article">

<img src="{image_url}" alt="{title}" loading="lazy">

<div class="category">{category}</div>

<h1>{title}</h1>

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

date = datetime.now().strftime("%Y-%m-%d-%H%M%S")
filename = f"posts/{category}/{date}.html"

with open(filename, "w", encoding="utf-8") as f:
    f.write(build_html(title, body, category, image_url))

print("記事生成完了:", title)
