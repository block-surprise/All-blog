import os
import random
import feedparser
import urllib.parse
import requests
import hashlib
import google.generativeai as genai
from datetime import datetime


# =====================
# APIキー
# =====================
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
import time

MODELS = [
    "gemini-2.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3-flash",
    "gemini-3.5-flash"
]

def generate_text(prompt):

    for model_name in MODELS:

        try:
            print("using:", model_name)

            model = genai.GenerativeModel(model_name)

            response = model.generate_content(prompt)

            if response and response.text:
                return response.text.strip()

        except Exception as e:
            print("failed:", model_name, e)

            # Quota超過なら少し待つ
            if "429" in str(e):
                time.sleep(10)

            continue

    return None


# =====================
# RSS取得
# =====================
rss_url = "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
feed = feedparser.parse(rss_url)

if not feed.entries:
    topic = "最新テックニュース"
else:
    topic = random.choice(feed.entries[:10]).title

# ノイズ除去
clean_topic = topic.split(" - ")[0].split("｜")[0].strip()


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
# 画像（保険3段階）
# =====================

def get_wikipedia_image(query):
    try:
        url = "https://ja.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(query)
        res = requests.get(url, timeout=5).json()

        if "thumbnail" in res and res["thumbnail"]:
            return res["thumbnail"]["source"]
    except:
        pass
    return None


def get_unsplash_image(query):
    try:
        return f"https://source.unsplash.com/800x400/?{urllib.parse.quote(query)}"
    except:
        return None


def get_picsum_image(query):
    seed = hashlib.md5(query.encode()).hexdigest()[:10]
    return f"https://picsum.photos/seed/{seed}/800/400"


def get_image(query):
    img = get_wikipedia_image(query)
    if img:
        return img

    img = get_unsplash_image(query)
    if img:
        return img

    return get_picsum_image(query)

import re

def make_image_query(title):

    m = re.search(r'「(.*?)」', title)
    if m:
        return m.group(1)

    title = title.split("、")[0]
    title = title.split("。")[0]
    title = title.split("…")[0]

    return title[:15]
image_query = make_image_query(clean_topic)

print("image query:", image_query)

image_url = get_image(image_query)
# =====================
# タイトル生成
# =====================
title_prompt = f"""
あなたはSEO編集者です。

テーマ：{clean_topic}

30文字以内のクリックされるタイトルを1つだけ出力してください。
記号・補足・説明は禁止。
"""

title = generate_text(title_prompt)

if not title:
    title = clean_topic

title = title.replace("\n", "")


# =====================
# 本文生成（HTML）
# =====================
body_prompt = f"""
あなたはプロのテックメディア編集者です。

テーマ：{clean_topic}

以下をHTMLで書いてください：

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
- ```禁止
"""
body = generate_text(body_prompt)

if body:

    body = body.replace("```html", "").replace("```", "")


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

header {{
    background: white;
    padding: 16px;
    border-bottom: 1px solid #eee;
    font-weight: bold;
}}

.nav {{
    background: #111;
    padding: 10px 14px;
    display: flex;
    gap: 12px;
    position: sticky;
    top: 0;
}}

.nav a {{
    color: white;
    text-decoration: none;
    font-size: 13px;
}}

.container {{
    max-width: 780px;
    margin: auto;
    padding: 14px;
}}

.article {{
    background: white;
    padding: 18px;
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
    margin-top: 26px;
}}
</style>
</head>

<body>

<header>ひとりテックニュース</header>

<nav class="nav">
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
