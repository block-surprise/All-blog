import os
import random
import feedparser
import urllib.parse
import markdown
import requests
import google.generativeai as genai
from datetime import datetime


# =====================
# APIキー
# =====================
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")


# =====================
# RSS
# =====================
rss_url = "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
feed = feedparser.parse(rss_url)

topic = random.choice(feed.entries[:10]).title


# =====================
# カテゴリ
# =====================
def get_category(text):
    text = text.lower()
    if any(w in text for w in ["ai", "chatgpt", "gemini", "人工知能"]):
        return "ai"
    elif any(w in text for w in ["iphone", "android", "pc", "スマホ", "ガジェット"]):
        return "gadgets"
    return "news"


category = get_category(topic)


# =====================
# Wikipedia画像（重要）
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


# fallback Unsplash
def get_image(query):
    wiki = get_wikipedia_image(query)
    if wiki:
        return wiki

    return f"https://source.unsplash.com/800x400/?{urllib.parse.quote(query)}"


image_url = get_image(topic)


# =====================
# タイトル生成
# =====================
title_prompt = f"""
あなたはSEO編集者です。

テーマ：{topic}

30文字以内のクリックされる日本語タイトルを1行だけ出力
"""

title = model.generate_content(title_prompt).text.strip()


# =====================
# 本文生成
# =====================
body_prompt = f"""
プロのテックメディア編集者として記事を書く。

テーマ：{topic}

構成:
- なぜ重要か
- 背景
- 詳細解説
- 具体例
- 今後の影響
- まとめ

1500〜3000文字
"""

raw_body = model.generate_content(body_prompt).text
body = markdown.markdown(raw_body)


# =====================
# HTML
# =====================
def build_html(title, body, category, image_url):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>

<style>
body {{ font-family: sans-serif; margin:0; background:#f4f6f8; }}
.container {{ max-width:800px; margin:auto; padding:16px; }}
.article {{ background:white; padding:20px; border-radius:12px; }}
img {{ width:100%; border-radius:10px; }}
.category {{ color:white; padding:4px 10px; border-radius:999px; display:inline-block; background:#4f46e5; }}
h1 {{ font-size:24px; }}
h2 {{ border-left:4px solid #4f46e5; padding-left:10px; }}
</style>
</head>

<body>
<div class="container">
<div class="article">

<img src="{image_url}">
<div class="category">{category}</div>
<h1>{title}</h1>

{body}

</div>
</div>
</body>
</html>"""


# =====================
# 保存
# =====================
os.makedirs(f"posts/{category}", exist_ok=True)

filename = f"posts/{category}/{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.html"

with open(filename, "w", encoding="utf-8") as f:
    f.write(build_html(title, body, category, image_url))

print("OK:", title)
