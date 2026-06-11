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
# 【日本国内サイト限定】実際の記事画像を取得するシステム（引用ベース）
# =====================
def get_actual_news_image(query, media_name):
    """勝手な英語翻訳を阻止し、日本国内(.jp)のサイトから本物の写真だけを強制抽出する"""
    try:
        # メディア名やキーワードを「""」で囲み、末尾に site:jp をつけて日本国内サイトに完全固定
        search_query = f'"{media_name}" "{query}" site:jp'
        encoded_query = urllib.parse.quote(search_query)
        
        # 日本地域（cc=JP）、言語（setlang=ja）に加えて、完全に日本語での検索結果を要求
        search_url = f"https://www.bing.com/images/search?q={encoded_query}&cc=JP&setlang=ja"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "ja,jp;q=0.9"
        }
        
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 検索結果の画像URLを検証
        for img in soup.find_all("img", class_="mimg"):
            img_url = img.get("src") or img.get("data-src")
            if img_url and img_url.startswith("http"):
                # ロゴやアイコン、極端に小さいシステム用画像（バナー広告等）は除外
                if not any(x in img_url.lower() for x in ["favicon", "logo", "icon", "avatar", "sprite", "google", "button", "banner"]):
                    # 縦長すぎる、横長すぎる広告枠を弾くため、サイズパラメータを調整（高画質化）
                    if "w=" in img_url:
                        img_url = re.sub(r'w=\d+', 'w=800', img_url)
                    if "h=" in img_url:
                        img_url = re.sub(r'h=\d+', 'h=500', img_url)
                    return img_url
                    
    except Exception as e:
        print("ニュース画像取得エラー:", e)
    return None

def download_image(url, save_dir="images"):
    """画像をimagesフォルダに固有の名前で物理保存する"""
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        ext = "jpg"
        file_name = f"{hashlib.md5(url.encode()).hexdigest()}.{ext}"
        save_path = os.path.join(save_dir, file_name)

        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(res.content)
            print(f"【成功】実際のニュース画像（引用）を保存しました: {save_path}")
            return f"/{save_dir}/{file_name}"
    except Exception as e:
        print("画像のダウンロードに失敗しました:", e)
    return None


# 実際のニュース画像を日本国内サイトから検索してダウンロード
print(f"画像検索対象（国内限定）: {source_name} {clean_topic}")
image_url = get_actual_news_image(clean_topic, source_name)

local_image_path = None
if image_url:
    print("本物の国内ニュース画像URLを発見:", image_url)
    local_image_path = download_image(image_url)

if not local_image_path:
    print("国内画像が直接取得できなかったため、予備のイメージ画像を割り当てます。")
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
# 本文生成（HTML）＋ AI暴走タグの超強力ブロック
# =====================
body_prompt = f"あなたはプロのテックメディア編集者です。\nテーマ：{clean_topic}\n以下をHTMLで書いてください：\n<h2>概要</h2>\n<p></p>\n<h2>背景</h2>\n<p></p>\n<h2>詳細解説</h2>\n<p></p>\n<h2>具体例</h2>\n<p></p>\n<h2>今後の影響</h2>\n<p></p>\n<h2>まとめ</h2>\n<p>3行で簡潔に</p>\n条件：\n- 1500〜3500文字\n- 渡された見出し（h2, pタグ）のみで本文を構成すること\n- htmlタグ、headタグ、bodyタグ、styleタグ、scriptタグの出力は絶対に禁止（デザインが破壊されるため）\n- ```によるコードブロック囲みも禁止"

body = generate_text(body_prompt) or ""

# ★【AI暴走対策・強力クレンジングシステム】
body = body.replace("```html", "").replace("```", "")
body = re.sub(r'<!DOCTYPE.*?>', '', body, flags=re.IGNORECASE | re.DOTALL)
body = re.sub(r'<html.*?>', '', body, flags=re.IGNORECASE | re.DOTALL)
body = re.sub(r'</html>', '', body, flags=re.IGNORECASE)
body = re.sub(r'<head.*?>.*?</head>', '', body, flags=re.IGNORECASE | re.DOTALL)
body = re.sub(r'<body.*?>', '', body, flags=re.IGNORECASE)
body = re.sub(r'</body>', '', body, flags=re.IGNORECASE)
body = re.sub(r'<style.*?>.*?</style>', '', body, flags=re.IGNORECASE | re.DOTALL)
body = re.sub(r'<script.*?>.*?</script>', '', body, flags=re.IGNORECASE | re.DOTALL)
body = body.strip()

content = f"{clean_topic} {body}"
category = get_category(content)


# =====================
# HTML生成（オリジナルデザイン完全維持 ＋ クリーンな本文の埋め込み）
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
