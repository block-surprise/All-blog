import os
import re
import random
import google.generativeai as genai
from datetime import datetime
from zoneinfo import ZoneInfo
import time
from search_builder import build_all_search_pages
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

IMAGE_DIR = "images"


# =====================
# テキスト生成
# =====================
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
            if "429" in str(e):
                time.sleep(10)

    return None


# =====================
# マイクラテーマ生成（重要）
# =====================
topic_prompt = """
あなたはマインクラフト攻略ブログの編集者です。

SEOで読まれるブログテーマを1つだけ作ってください。

条件：
- マインクラフトに関係する
- 興味が湧くこと
- 具体的でクリックされやすい
- 1行のみ
- 記号は使わない
"""

clean_topic = generate_text(topic_prompt)

if not clean_topic:
    clean_topic = "マインクラフト初心者がやるべきこと"

clean_topic = clean_topic.replace("\n", "").strip()


# =====================
# 固定カテゴリ（マイクラ）
# =====================
category = "minecraft"
articles = []

# =====================
# ランダム画像（任意）
# =====================
def get_random_image():
    try:
        images = [
            "a.jpeg",
            "b.jpeg",
            "c.png",
            "d.png"
        ]

        return "/" + IMAGE_DIR + "/" + random.choice(images)

    except:
        return None
image_url = get_random_image()
# =====================
# タイトル生成
# =====================
title_prompt = f"""
あなたはSEO編集者です。

テーマ：{clean_topic}

30文字以内でクリックされるタイトルを1つだけ出してください。

条件：
- タイトル以外の文字を置かない
- (何文字)などはいれない
- 記号は使わない
"""

title = generate_text(title_prompt)
if not title:
    title = clean_topic

title = title.replace("\n", "")


# =====================
# 本文生成（マイクラ特化）
# =====================
section_prompt = f"""
テーマ：{clean_topic}

このテーマに合ったブログ見出しを5つ作ってください。

条件：
- <h2>タグだけで出力
- 内容に自然に合う構成
- ランキングならランキング構成
- 攻略なら手順構成
- 改行するべきところでは改行すること
- 最新の情報を2026年最新などは書かず書く場合は最新版や最新情報などと書くこと
"""
sections = generate_text(section_prompt)

body_prompt = f"""
テーマ：{clean_topic}

以下の見出しに合わせて記事を書いてください：

{sections}

条件：
- h2の本文だけを書く

- HTML断片のみ

- DOCTYPE禁止

- htmlタグ禁止

- headタグ禁止

- bodyタグ禁止

- h1タグ禁止

- 各見出しごとに十分な解説を書く

- 1500〜3500文字
"""
body = generate_text(body_prompt)
if body:

    body = body.replace("```html", "")
    body = body.replace("```", "")

    # html/body/head削除
    body = re.sub(
        r'<!DOCTYPE.*?<body[^>]*>',
        '',
        body,
        flags=re.S | re.I
    )

    body = re.sub(
        r'</body>.*?</html>',
        '',
        body,
        flags=re.S | re.I
    )

    body = re.sub(
        r'<head.*?>.*?</head>',
        '',
        body,
        flags=re.S | re.I
    )

    body = re.sub(
        r'<html.*?>',
        '',
        body,
        flags=re.S | re.I
    )

    body = body.replace("</html>", "")
body = re.sub(
    r'<h1.*?>.*?</h1>',
    '',
    body,
    count=1,
    flags=re.S | re.I
)

if body:
    body = body.replace("```html", "").replace("```", "")


# =====================
# HTML生成
# =====================
def build_html(title, body, category, image_url):

    img = ""
    if image_url:
        img = f'<img src="{image_url}" alt="{title}" loading="lazy">'

    return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3571574988222927"crossorigin="anonymous"></script>
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon.png">
<style>
body {{
    margin: 0;
    font-family: sans-serif;
    background: #f4f6f8;
    color: #111;
    line-height: 1.8;
}}

header {{
    background: #111;
    color: white;
    padding: 12px;
    text-align: center;
}}
header a {{
    color: white;           
    text-decoration: none;  
}}


.container {{
    max-width: 800px;
    margin: auto;
    padding: 14px;
}}

.article {{
    background: white;
    padding: 18px;
    border-radius: 12px;
}}

img {{
    width: 100%;
    border-radius: 10px;
}}

.category {{
    display: inline-block;
    background: #4f46e5;
    color: white;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
}}

h1 {{
    font-size: 20px;
    line-height: 1.4;
    margin-top: 12px;
    margin-bottom: 18px;
}}

h2 {{
    font-size: 16px;
    border-left: 4px solid #4f46e5;
    padding-left: 10px;
    margin-top: 24px;
    margin-bottom: 10px;
}}
.latest-box {{
    margin-top: 30px;
    padding: 16px;
    background: #fff;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}}

.latest-box h2 {{
    font-size: 18px;
    margin-bottom: 12px;
}}

#latest-posts {{
    margin-top: 10px;
}}

.latest-item {{
    display: block;
    padding: 12px 4px;
    text-decoration: none;
    color: #111;
}}

.latest-item:not(:last-child) {{
    border-bottom: 1px solid #e5e7eb;
}}

.latest-item:hover {{
    background: #f8fafc;
}}

.latest-title {{
    font-size: 14px;
    font-weight: 600;
    line-height: 1.5;
}}

.latest-date {{
    font-size: 12px;
    color: #777;
    margin-top: 4px;
}}
.footer {{
    text-align: center;
    padding: 20px;
    font-size: 13px;
    color: #666;
}}

.footer a {{
    color: #666;
    text-decoration: none;
}}

.footer a:hover {{
    text-decoration: underline;
}}
</style>
</head>

<body>

<header>
  <a href="https://htn-news.f5.si/game/">ひとりゲームニュース</a>
</header>

<div class="container">
<div class="article">

{img}

<div class="category">{category}</div>

<h1>{title}</h1>

{body}

</div>
</div>
<div class="latest-box">

<h2>最新記事</h2>

<div id="latest-posts">
読み込み中...
</div>

</div>

<script src="/game/latest.js"></script>
 <footer class="footer">

  <a href="https://htn-news.f5.si/privacy.html">・プライバシーポリシー</a>
  <a href="https://htn-news.f5.si/a10">・不適切な内容等削除申請フォーム</a>
</footer>
</body>
</html>
"""


# =====================
# 保存（game/posts に出力）
# =====================
os.makedirs("game/posts/minecraft", exist_ok=True)

date = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d-%H%M%S")

filename = f"game/posts/minecraft/{date}.html"

with open(filename, "w", encoding="utf-8") as f:
    f.write(build_html(title, body, category, image_url))

print("記事生成完了:", title)

articles.append({
    "title": title,
    "body": body,
    "path": filename,
    "ts": datetime.now().timestamp(),
    "cat": category,
    "color": "#dc2626",
    "time": datetime.now().strftime("%m-%d %H:%M")
})

build_all_search_pages(articles)
