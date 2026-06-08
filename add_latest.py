import os

INSERT_HTML = “””

<h2>最新記事</h2>
<div id="latest-posts">
読み込み中...
</div>
<script src="/game/latest.js"></script>

“””

TARGET_DIR = “game/posts/minecraft”

for root, dirs, files in os.walk(TARGET_DIR):

for file in files:
    if not file.endswith(".html"):
        continue
    path = os.path.join(root, file)
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    # 既に追加済みならスキップ
    if 'id="latest-posts"' in html:
        continue
    marker = """
</div>
</div>
</body>
"""
    if marker in html:
        html = html.replace(
            marker,
            INSERT_HTML + marker
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("updated:", path)

print(“完了”)
