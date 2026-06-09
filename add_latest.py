import os

TARGET_DIR = "posts"

INSERT_BLOCK = """\
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3571574988222927" crossorigin="anonymous"></script>
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon2.png">
"""

count = 0

for root, dirs, files in os.walk(TARGET_DIR):

    for file in files:

        if not file.endswith(".html"):
            continue

        path = os.path.join(root, file)

        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        # すでにどれかあるならスキップ
        if (
            "adsbygoogle.js" in html or
            'rel="icon"' in html or
            'apple-touch-icon' in html
        ):
            continue

        # <title>の直後に挿入
        if "<title>" in html:
            html = html.replace(
                "</title>",
                "</title>\n" + INSERT_BLOCK
            )
        else:
            continue

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        count += 1
        print("updated:", path)

print(f"完了: {count}件")
