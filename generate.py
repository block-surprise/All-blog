import os
from openai import OpenAI
from datetime import datetime

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

topic = "最新のテクノロジートレンド"

prompt = f"""
あなたはプロのブログライターです。
以下のテーマでブログ記事を書いてください。

テーマ：{topic}

条件：
- 見出し付き
- 1500文字以上
- わかりやすく
- 日本語
"""

res = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

content = res.choices[0].message.content

os.makedirs("posts", exist_ok=True)

date = datetime.now().strftime("%Y-%m-%d")
filename = f"posts/{date}.md"

with open(filename, "w", encoding="utf-8") as f:
    f.write(f"# {topic}\n\n")
    f.write(content)

print("done")
