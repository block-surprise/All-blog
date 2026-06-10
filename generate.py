import os
import random
import re
import time
import hashlib
import urllib.parse
import subprocess
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
# RSS取得 ＆ ニューステーマ決定
# =====================
cache_buster = int(time.time())
rss_url = f"https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja&_={cache_buster}"
feed = feedparser.parse(rss_url)

if not feed.entries:
    chosen_entry = None
    clean_topic = "最新テックニュース"
    source_url = "https://news.google.com/"
    source_name = "Googleニュース"
else:
    # 毎回違うニュースが選ばれやすいように範囲を広げる
    chosen_entry = random.choice(feed.entries[:15])
    topic = chosen_entry.title
    clean_topic = topic.split(" - ")[0].split("｜")[0].strip()
    source_url = chosen_entry.link
    source_name = chosen_entry.get("source", {}).get("title", "ニュース配信元")

print("選択されたテーマ:", clean_topic)


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
# 【Google回避・安全第一】画像検索から本物の関連写真をぶち抜く
# =====================
def get_safe_search_image(query):
    """ニュースタイトルから検索エンジン経由で本物の関連写真URLを取得する（Googleのブロックを完全回避）"""
    try:
        # 検索ワードをエンコード
        encoded_query = urllib.parse.quote(f"{query} ニュース")
        search_url = f"https://www.bing.com/images/search?q={encoded_query}&qft=+filterui:aspect-square"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 検索結果から画像のURL（mimgクラス）を抽出
        for img in soup.find_all("img", class_="mimg"):
            img_url = img.get("src") or img.get("data-src")
            if img_url and img_url.startswith("http"):
                # Google関連のアイコンやロゴ、ユーザーアイコンを徹底的に排除する強力なフィルター
                if not any(x in img_url.lower() for x in ["favicon", "logo", "icon", "avatar", "sprite", "googleusercontent", "google"]):
                    return img_url
                    
    except Exception as e:
        print("画像検索スクレイピングエラー:", e)
    return None

def download_image(url, save_dir="images"):
    """画像をimagesフォルダに保存する（URL文字列から固有のファイル名を作るため、もう二度と同じファイル名に固定されません）"""
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        ext = "jpg"
        # URLの文字列をハッシュ化。URLが変わればファイル名も絶対に変わります
        file_name = f"{hashlib.md5(url.encode()).hexdigest()}.{ext}"
        save_path = os.path.join(save_dir, file_name)

        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(res.content)
            print(f"【成功】新画像を保存しました: {save_path}")
            return f"/{save_dir}/{file_name}"
    except Exception as e:
        print("画像のダウンロードに失敗しました:", e)
    return None


# ニュースのメディア名とタイトルを組み合わせて、安全に画像をWeb検索
search_term = f"{source_name} {clean_topic}"
print("画像検索キーワード:", search_term)

image_url = get_safe_search_image(clean_topic)

local_image_path = None
if image_url:
    print("Web上でニュースに関連する写真を発見しました:", image_url)
    local_image_path = download_image(image_url)

# 万が一の保険（フリーイメージ）
if not local_image_path:
    print("画像が取得できなかったため、一時的なイメージ画像を割り当てます。")
    seed_num = int(hashlib.md5(clean_topic.encode()).hexdigest(), 16) % 1000
    image_url = f"https://picsum.photos/seed/{seed_num}/800/500"
    local_image_path = download_image(image_url)


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
# HTML生成（デザイン完全維持）
# =====================
def build_html(title, body, category, local_image_path, source_url, source_name):
    image_html = ""
    if local_image_path:
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
}}

.related {{
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
  <a href="/posts/ai/">AI</a>
  <a href="/posts/gadgets/">ガジェット</a>
  <a href="/posts/news/">ニュース</a>
</nav>

<div class="container">
<div class="article">

{image_html}

<div class="category">{category}</div>

<h1>{title}</h1>

{body}

<div style="margin-top: 40px; padding: 24px; background: #fafafa; border: 1px solid #e5e7eb; border-radius: 12px; display: flex; flex-direction: column; gap: 16px;">
  
  <div style="font-size: 11px; color: #4f46e5; font-weight: bold; letter-spacing: 0.05em; text-transform: uppercase;">
    この記事を書いた人
  </div>

  <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
    <img src="/images/p/001.png" alt="管理人" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; background: #e5e7eb;">
    
    <div style="flex: 1; min-width: 200px;">
      <div style="font-size: 16px; font-weight: bold; color: #111; margin-bottom: 4px;">管理人</div>
      <div style="font-size: 13px; color: #4b5563; line-height: 1.5;">
        普段はウェブページ制作等を行なっています。
      </div>
    </div>
  </div>
  
  <div style="display: flex; justify-content: flex-end; margin-top: 4px;">
    <a href="/profile.html" style="display: inline-block; font-size: 13px; color: white; background: #4f46e5; text-decoration: none; padding: 8px 20px; border-radius: 8px; font-weight: bold; white-space: nowrap; transition: background 0.2s;">
      詳細を見る
    </a>
  </div>

</div>
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
    f.write(build_html(title, body, category, local_image_path, source_url, source_name))

print("記事生成完了:", title)


# =====================
# GitHub強制追跡
# =====================
if local_image_path:
    subprocess.run(["git", "add", "-f", "images/"], check=False)
    print("Gitに新画像の追跡を強制しました。")

