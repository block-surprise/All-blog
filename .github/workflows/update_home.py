import os

POST_DIR = "posts"
OUTPUT_FILE = "index.html"

# Markdown記事一覧取得
files = sorted(os.listdir(POST_DIR), reverse=True)

items = ""

for f in files:
    if f.endswith(".md"):
        title = f.replace(".md", "")
        items += f"""
        <div class="card">
          <a href="posts/{f}">{title}</a>
        </div>
        """

html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ひとりテックニュース</title>

<style>
body {{
    font-family: sans-serif;
    max-width: 800px;
    margin: auto;
    padding: 20px;
    background: #f6f7fb;
}}

h1 {{
    color: #111;
}}

.card {{
    background: white;
    padding: 15px;
    margin: 10px 0;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}}

a {{
    text-decoration: none;
    color: #1a73e8;
    font-weight: bold;
}}

a:hover {{
    text-decoration: underline;
}}
</style>

</head>
<body>

<h1>ひとりテックニュース</h1>
<p>ひとつひとつ分かりやすいニュース
</p>

<h2>最新記事</h2>

{items}

</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("index.html updated")
