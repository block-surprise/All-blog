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
from bs4 import BeautifulSoup
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
            if "429" in str(e):
                time.sleep(10)
            continue
    return None


# =====================
# RSS取得 ＆ ニュース元URLの解析
# =====================
rss_url = "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
feed = feedparser.parse(rss_url)

if not feed.entries:
    chosen_entry = None
    clean_topic = "最新テックニュース"
    source_url = "https://news.google.com/"
    source_name = "Googleニュース"
else:
    chosen_entry = random.choice(feed.entries[:10])
    topic = chosen_entry.title
    clean_topic = topic.split(" - ")[0].split("｜")[0].strip()
    # ニュースの元記事URLと配信メディア名を取得
    source_url = chosen_entry.link
    source_name = chosen_entry.get("source", {}).get("title", "ニュース配信元")

print("選択されたテーマ:", clean_topic)
print("引用元URL:", source_url)
print("引用元メディア:", source_name)


# =====================
# カテゴリ分類
# =====================
def get_category(text):
    text = text.lower()
    if any(w in text for w in ["ai", "chatgpt", "openai", "gpt", "gemini", "claude", "人工知能", "llm"]):
        return "ai"
    elif any(w in text for w in ["iphone", "android", "ipad", "macbook", "pixel", "galaxy", "スマホ", "ガジェット"]):
        return "gadgets"
    else:
        return "news"


# =====================
# 【確定引用システム】ニュースサイトから画像を自動抽出して保存
# =====================
def download_image(url, save_dir="images"):
    """画像をローカルにダウンロードして保存する"""
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        ext = url.split(".")[-1].split("?")[0].lower()
        if ext not in ["jpg", "jpeg", "png", "webp"]:
            ext = "jpg"

        file_name = f"{hashlib.md5(url.encode()).hexdigest()}.{ext}"
        save_path = os.path.join(save_dir, file_name)

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(res.content)
            print(f"画像を保存しました: {save_path}")
            return f"/{save_dir}/{file_name}"
    except Exception as e:
        print("画像のダウンロードに失敗しました:", e)
    return None

def get_news_image(article_url):
    """ニュース記事のページを開き、アイキャッチ画像（OGP画像）を確定で抽出する"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        # Googleニュースの転送URLから実際の記事URLを追跡して取得
        res = requests.get(article_url, headers=headers, timeout=8, allow_redirects=True)
        final_url = res.url
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        # ニュースサイトのメタタグ（OGP）から高画質なアイキャッチ画像を探す
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"], final_url
            
        # 見つからない場合はページ内の最初の大きな画像を探す
        for img in soup.find_all("img"):
            src = img.get("src")
            if src and src.startswith("http") and not any(x in src for x in ["icon", "logo", "avatar"]):
                return src, final_url
                
    except Exception as e:
        print("ニュースサイトからの画像抽出エラー:", e)
    return None, article_url

# 確定引用画像の取得処理
remote_image_url, final_source_url = get_news_image(source_url)

local_image_path = None
if remote_image_url:
    print("ニュースサイト内で画像を発見:", remote_image_url)
    local_image_path = download_image(remote_image_url)
else:
    print("ニュースサイト内に画像が見つかりませんでした")


# =====================
# タイトル生成
# =====================
title_prompt = f"あなたはSEO編集者です。\nテーマ：{clean_topic}\n30文字以内のクリックされるタイトルを1つだけ出力してください。\n記号・補足・説明は禁止。"
title = generate_text(title_prompt) or clean_topic
title = title.replace("\n", "")


# =====================
# 本文生成（HTML）
# =====================
body_prompt = f"あなたはプロのテックメディア編集者です。\nテーマ：{clean_topic}\n以下をHTMLで書いてください：\n<h2>概要</h2>\n<p></p>\n<h2>背景</h2>\n<p></p>\n<h2>詳細解説</h2>\n<p></p>\n<h2>具体例</h2>\n<p></p>\n<h2>今後の影響</h2>\n<p></p>\n<h2>まとめ</h2>\n<p>3行で簡潔に</p>\n条件：\n- 1500〜3500文字\n- HTMLのみ\n- ```禁止"
body = generate_text(body_prompt) or ""
body = body.replace("```html", "").replace("```", "")

content = f"{clean_topic} {body}"
category = get_category(content)


# =====================
# HTML生成
# =====================
def build_html(title, body, category, local_image_path, source_url, source_name):
    image_html = ""
    if local_image_path:
        # ニュースサイトから取得した画像をローカルパスで表示し、その真下にニュース元への引用リンクを生成
        image_html = f'''
<img src="{local_image_path}" alt="{title}" loading="lazy">
<p style="text-align: center; font-size: 12px; color: #666; margin: 4px 0 20px 0;">
  出典：<a href="{source_url}" target="_blank" rel="noopener" style="color: #666; text-decoration: underline;">{source_name}</a>
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
}}.related {{
    margin-top: 30px;
    padding: 14px;
    background: #f9fafb;
    border-radius: 12px;
}}

.related a {{
    display: block;
    color: #4f46e5;
    text-decoration: none;
    font-size: 14px;
    margin: 4px 0;
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
<div style="margin-top: 40px; padding: 18px; background: #fafafa; border: 1px solid #eee; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; gap: 16px;">
  <div>
    <div style="font-size: 11px; color: #4f46e5; font-weight: bold; letter-spacing: 0.05em; margin-bottom: 2px;">この記事を書いた人</div>
    <div style="font-size: 15px; font-weight: bold; color: #111;">管理人</div>
  </div>
  
  
  <a href="/profile.html" style="display: inline-block; font-size: 13px; color: white; background: #4f46e5; text-decoration: none; padding: 8px 16px; border-radius: 8px; font-weight: bold; white-space: nowrap;">
    詳細を見る
  </a>
</div>
</body>
</html>

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
    f.write(build_html(title, body, category, local_image_path, final_source_url, source_name))

print("記事生成完了:", title)


