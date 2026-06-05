import os
import random
import feedparser
import urllib.parse
import google.generativeai as genai
from datetime import datetime

# =====================
# APIキー設定
# =====================
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# =====================
# RSSからトピック取得（トレンド自動化）
# =====================
rss_url = "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
feed = feedparser.parse(rss_url)

entries = feed.entries[:10]
topic = random.choice(entries).title

# =====================
# カテゴリ判定（超重要）
# =====================
def get_category(text):
    text = text.lower()

    if any(w in text for w in ["ai", "人工知能", "chatgpt", "gemini"]):
        return "ai"
    elif any(w in text for w in ["iphone", "android", "pc", "ガジェット", "スマホ"]):
        return "gadgets"
    else:
        return "news"

category = get_category(topic)

# =====================
# サムネ画像（簡易版）
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

以下のニューステーマでクリックされるタイトルを1つ作ってください。

テーマ：{topic}

条件：
- 30文字以内
- 日本語
- クリックしたくなる
- 意外性を入れる
"""

title_res = model.generate_content(title_prompt)
title = title_res.text.strip()

# =====================
# 本文生成
# =====================
body_prompt = f"""
あなたはテック系ニュースライターです。

以下のテーマで記事を書いてください：

テーマ：{topic}

条件：
- 見出し付き（H2）
- 1500〜2500文字
- わかりやすい日本語
- 初心者向け
- 具体例あり
"""

body_res = model.generate_content(body_prompt)
body = body_res.text

# =====================
# 保存先
# =====================
os.makedirs(f"posts/{category}", exist_ok=True)

date = datetime.now().strftime("%Y-%m-%d")
filename = f"posts/{category}/{date}.md"

# =====================
# Markdown生成
# =====================
with open(filename, "w", encoding="utf-8") as f:
    f.write(f"![thumbnail]({image_url})\n\n")
    f.write(f"# {title}\n\n")
    f.write(f"**カテゴリ：{category}**\n\n")
    f.write(body)

print("記事生成完了:", title, "| category:", category)
