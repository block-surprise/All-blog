import os
import google.generativeai as genai
from datetime import datetime

# =====================
# APIキー設定
# =====================
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

# =====================
# テーマ（ここは後で自動化可能）
# =====================
topic = "最新のテクノロジートレンド"

# =====================
# SEOタイトル生成
# =====================
title_prompt = f"""
あなたはSEO専門の編集者です。

以下のテーマでクリックされるブログタイトルを1つ作ってください。

テーマ：{topic}

条件：
- 30文字以内
- クリックしたくなる
- 日本語
"""

title_res = model.generate_content(title_prompt)
title = title_res.text.strip()

# =====================
# 本文生成
# =====================
body_prompt = f"""
あなたはプロのブログライターです。

以下のテーマでブログ記事を書いてください：

テーマ：{topic}

条件：
- 見出し付き（H2構造）
- 1500〜2500文字
- 初心者にもわかりやすく
- 具体例を入れる
- 自然な日本語
"""

body_res = model.generate_content(body_prompt)
body = body_res.text

# =====================
# 保存準備
# =====================
os.makedirs("posts", exist_ok=True)

date = datetime.now().strftime("%Y-%m-%d")
filename = f"posts/{date}.md"

# =====================
# Markdown保存
# =====================
with open(filename, "w", encoding="utf-8") as f:
    f.write(f"# {title}\n\n")
    f.write(body)

print("記事生成完了:", title)
