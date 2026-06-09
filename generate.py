import os
import random
import re
import time
import hashlib
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
import feedparser
import requests
import google.generativeai as genai

# =====================
# APIキー
# =====================
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

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
    if any(w in text for w in [
        "ai", "chatgpt", "openai", "gpt", "gemini", "claude", "人工知能", "llm"
    ]):
        return "ai"
    elif any(w in text for w in [
        "iphone", "android", "ipad", "macbook", "pixel", "galaxy", "スマホ", "ガジェット"
    ]):
        return "gadgets"
    else:
        return "news"


# =====================
# 画像（Wikipediaから取得 ＆ 自動ダウンロード）
# =====================
def get_wikipedia_image_and_page(query):
    """Wikipediaから画像のURLと、その記事ページのURLをセットで取得する"""
    try:
        url = (
            "https://ja.wikipedia.org/api/rest_v1/page/summary/"
            + urllib.parse.quote(query)
        )
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return None, None

        data = res.json()
        image_url = None
        # 元の記事のURLを取得（デフォルトはWikipediaトップ）
        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "https://ja.wikipedia.org/")

        if "thumbnail" in data:
            image_url = data["thumbnail"]["source"]

        return image_url, page_url
    except Exception as e:
        print("wiki image error:", e)
    return None, None

def download_image(url, save_dir="images"):
    """画像をローカルにダウンロードして保存し、ブログ用のパスを返す"""
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 拡張子の取得 (.jpg など)
        ext = url.split(".")[-1].split("?")[0]
        if len(ext) > 4 or "/" in ext:
            ext = "jpg"

        # URLのハッシュ値から被らないファイル名を作る
        file_name = f"{hashlib.md5(url.encode()).hexdigest()}.{ext}"
        save_path = os.path.join(save_dir, file_name)

        # ダウンロード実行
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(res.content)
            print(f"画像を保存しました: {save_path}")
            # HTMLで読み込めるように、ルートパス形式で返す
            return f"/{save_dir}/{file_name}"
    except Exception as e:
        print("画像のダウンロードに失敗しました:", e)
    return None

def make_image_query(title):
    m = re.search(r'「(.*?)」', title)
    if m:
        return m.group(1)

    title = re.sub(r'（.*?）', '', title)
    title = re.sub(r'\(.*?\)', '', title)

    separators = ["、", "。", "…", "-", "｜", ":", "："]
    for s in separators:
        title = title.split(s)[0]

    return title.strip()[:15]


# 画像情報の取得と保存
image_query = make_image_query(clean_topic)
print("image query:", image_query)

remote_image_url, wikipedia_page_url = get_wikipedia_image_and_page(image_query)

local_image_path = None
if remote_image_url:
    print("Wikipedia image found:", remote_image_url)
    # ここで自動保存の関数を動かします
    local_image_path = download_image(remote_image_url)
else:
    print("No image found")


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

<h2>概要</h2>
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

content = f"{clean_topic} {body}"
category = get_category(content)


# =====================
# HTML生成
# =====================
def build_html(title, body, category, local_image_path, wikipedia_page_url):
    image_html = ""
    if local_image_path and wikipedia_page_url:
        # ダウンロードした画像を表示し、その下にデザインを崩さないよう小さめの文字で出典を挿入
        image_html = f'''
<img src="{local_image_path}" alt="{title}" loading="lazy">
<p style="text-align: center; font-size: 12px; color: #666; margin: 4px 0 20px 0;">
  出典：<a href="{wikipedia_page_url}" target="_blank" rel="noopener" style="color: #666; text-decoration: underline;">フリー百科事典『ウィキペディア（Wikipedia）』</a>
</p>
'''

    return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script async src="[https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3571574988222927](https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3571574988222927)" crossorigin="anonymous"></script>
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon.png">
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
    padding: 12px 18px;
    display: flex;
    gap: 14px;
    position: sticky;
    top: 0;
    z-index: 1000;
    align-items: center;
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
  <a href="/posts/ai/">人工知能</a>
  <a href="/posts/gadgets/">ガジェット</a>
  <a href="/posts/news/">ニュース</a>
</nav>

<div class="container">
<div class="article">

{image_html}

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

date = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d-%H%M%S")
filename = f"posts/{category}/{date}.html"

with open(filename, "w", encoding="utf-8") as f:
    f.write(build_html(title, body, category, local_image_path, wikipedia_page_url))

print("記事生成完了:", title)
