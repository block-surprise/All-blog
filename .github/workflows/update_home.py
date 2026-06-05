import os
from datetime import datetime

POST_DIR = "posts"
OUTPUT_FILE = "index.html"

files = sorted(os.listdir(POST_DIR), reverse=True)

items = ""

for f in files:
    if f.endswith(".md"):
        name = f.replace(".md", "")
        items += f'<li><a href="posts/{f}">{name}</a></li>\n'

html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>AI Blog</title>
</head>
<body>
<h1>AI Blog</h1>
<p>自動生成ブログ</p>

<h2>記事一覧</h2>
<ul>
{items}
</ul>

</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("index updated")
