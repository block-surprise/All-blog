import os

TARGET_DIR = "game/posts"

OLD_HTML = """
<h2>最新記事</h2>
<div id="latest-posts">
読み込み中...
</div>

<script src="/game/latest.js"></script>
"""

NEW_HTML = """
<div class="latest-box">

<h2>最新記事</h2>

<div id="latest-posts">
読み込み中...
</div>

</div>

<script src="/game/latest.js"></script>
"""

CSS = """

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

for root, dirs, files in os.walk(TARGET_DIR):

    for file in files:

        if not file.endswith(".html"):
            continue

        path = os.path.join(root, file)

        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        changed = False

        # 最新記事ブロック置換
        if OLD_HTML in html:
            html = html.replace(OLD_HTML, NEW_HTML)
            changed = True

        # CSS追加（未追加時のみ）
        if ".latest-box" not in html and "</style>" in html:
            html = html.replace(
                "</style>",
                CSS + "\n</style>"
            )
            changed = True

        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)

            print("updated:", path)

print("完了")
