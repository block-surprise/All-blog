import os
import google.generativeai as genai
from datetime import datetime

# ===== APIキー設定 =====
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# ===== モデル指定 =====
model = genai.GenerativeModel("gemini-1.5-flash")

# ===== テーマ（ここは後で自動化できる）=====
topic = "最新のテクノロジートレンド"

# ===== プロンプト（記事品質の核）=====
prompt = f"""
あなたはプロのSEOブログライターです。

以下のテーマでブログ記事を書いてください：

テーマ：{topic}

条件：
- 日本語
- 見出し付き（H2構造）
- 1500〜2500文字
- 初心者にもわかる
- 具体例を必ず入れる
- タイトルはクリックしたくなるものにする
- AIっぽさを消して自然な文章にする
"""

# ===== AI生成 =====
response = model.generate_content(prompt)
content = response.text

# ===== 保存先フォルダ =====
os.makedirs("posts", exist_ok=True)

# ===== ファイル名 =====
date = datetime.now().strftime("%Y-%m-%d")
filename = f"posts/{date}.md"

# ===== Markdownとして保存 =====
with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("記事生成完了")
