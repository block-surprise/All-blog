import os
import random
import google.generativeai as genai
from datetime import datetime
from zoneinfo import ZoneInfo
import time

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
- 攻略・建築・サバイバル・装置・小技
- 具体的でクリックされやすい
- 1行のみ
"""

clean_topic = generate_text(topic_prompt)

if not clean_topic:
    clean_topic = "マインクラフト初心者がやるべきこと"

clean_topic = clean_topic.replace("\n", "").strip()


# =====================
# 固定カテゴリ（マイクラ）
# =====================
category = "minecraft"


# =====================
# ランダム画像（任意）
# =====================
def get_random_image():
    try:
        files = [
            f for f in os.listdir(IMAGE_DIR)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        ]

        if not files:
            return None

        return "/" + IMAGE_DIR + "/" + random.choice(files)

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
"""

title = generate_text(title_prompt)
if not title:
    title = clean_topic

title = title.replace("\n", "")


# =====================
# 本文生成（マイクラ特化）
# =====================
body_prompt = f"""
あなたはマインクラフト攻略ブログのプロ編集者です。

テーマ：{clean_topic}

以下をHTMLで書いてください：

<h2>概要</h2>
<p></p>

<h2>やり方</h2>
<p></p>

<h2>コツ</h2>
<p></p>

<h2>注意点</h2>
<p></p>

<h2>応用</h2>
<p></p>

<h2>まとめ</h2>
<p>3行で簡潔に</p>

条件：
- マインクラフト初心者向け
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

h2 {{
    border-left: 4px solid #4f46e5;
    padding-left: 10px;
}}
</style>
</head>

<body>

<header>ひとりテックマイクラ</header>

<div class="container">
<div class="article">

{img}

<div class="category">{category}</div>

<h1>{title}</h1>

{body}

</div>
</div>

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
