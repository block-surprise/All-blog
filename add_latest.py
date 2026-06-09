import os

TARGET_DIR = "."

OLD = '<link rel="apple-touch-icon" href="/favicon.png">'
NEW = '<link rel="apple-touch-icon" href="/favicon2.png">'

count = 0

for root, dirs, files in os.walk(TARGET_DIR):

    for file in files:

        if not file.endswith(".html"):
            continue

        path = os.path.join(root, file)

        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        if OLD not in html:
            continue

        html = html.replace(OLD, NEW)

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        count += 1
        print("updated:", path)

print(f"完了: {count}件")
