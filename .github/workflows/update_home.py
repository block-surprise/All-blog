import os

BASE_DIR = "posts"
OUTPUT_FILE = "index.html"

categories = ["ai", "gadgets", "news"]

html_blocks = ""

for cat in categories:
    path = os.path.join(BASE_DIR, cat)

    if not os.path.exists(path):
        continue

    files = sorted(os.listdir(path), reverse=True)

    items = ""

    for f in files:
        if f.endswith(".md"):
            items += f'<li><a href="posts/{cat}/{f}">{f.replace(".md","")}</a></li>\n'

    html_blocks += f"""
    <h2>{cat.upper()}</h2>
    <ul>
    {items}
    </ul>
    """

html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>ひとりテックニュース</title>
</head>
<body>

<h1>ひとりテックニュース</h1>

{html_blocks}

</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("index updated")
