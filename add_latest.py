import os

TARGET_DIR = "game/posts/minecraft"

OLD_CSS = """
.latest-box {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}

.latest-box h2 {
    font-size: 20px;
    margin-bottom: 12px;
}

.latest-item {
    display: block;
    padding: 12px;
    margin-bottom: 10px;
    background: #f8fafc;
    border-radius: 10px;
    text-decoration: none;
    color: #111;
    border: 1px solid #e5e7eb;
}

.latest-item:hover {
    background: #eef2ff;
}

.latest-title {
    font-size: 14px;
    font-weight: 600;
}

.latest-date {
    font-size: 12px;
    color: #666;
    margin-top: 4px;
}
"""

NEW_CSS = """
.latest-box {
    margin-top: 30px;
    padding: 16px;
    background: #fff;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}

.latest-box h2 {
    font-size: 18px;
    margin-bottom: 12px;
}

#latest-posts {
    margin-top: 10px;
}

.latest-item {
    display: block;
    padding: 12px 4px;
    text-decoration: none;
    color: #111;
}

.latest-item:not(:last-child) {
    border-bottom: 1px solid #e5e7eb;
}

.latest-item:hover {
    background: #f8fafc;
}

.latest-title {
    font-size: 14px;
    font-weight: 600;
    line-height: 1.5;
}

.latest-date {
    font-size: 12px;
    color: #777;
    margin-top: 4px;
}
"""

count = 0

for root, dirs, files in os.walk(TARGET_DIR):

    for file in files:

        if not file.endswith(".html"):
            continue

        path = os.path.join(root, file)

        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        if OLD_CSS not in html:
            continue

        html = html.replace(OLD_CSS, NEW_CSS)

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        count += 1
        print("updated:", path)

print(f"完了: {count}件")
