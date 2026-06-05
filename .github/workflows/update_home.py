import os
from datetime import datetime

POST_DIR = "posts"

html_cards = ""

for root, dirs, files in os.walk(POST_DIR):
    for f in sorted(files, reverse=True):
        if f.endswith(".html"):
            path = os.path.join(root, f).replace("\\", "/")

            title = f.replace(".html", "")

            html_cards += f"""
            <div class="card">
              <a href="{path}">
                <h2>{title}</h2>
              </a>
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
    max-width: 900px;
    margin: auto;
    padding: 20px;
    background: #f4f6f8;
}}

header {{
    padding: 20px 0;
}}

h1 {{
    font-size: 32px;
}}

.sub {{
    color: gray;
    margin-bottom: 20px;
}}

.card {{
    background: white;
    padding: 15px;
    margin: 15px 0;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    transition: 0.2s;
}}

.card:hover {{
    transform: translateY(-2px);
}}

a {{
    text-decoration: none;
    color: black;
}}

h2 {{
    font-size: 18px;
    margin: 0;
}}
</style>

</head>
<body>

<header>
<h1>ひとりテックニュース</h1>
<div class="sub">ひとつひとつ分かりやすいニュース</div>
</header>

{html_cards}

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("homepage updated")
