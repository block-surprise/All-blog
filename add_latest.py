import os

TARGET_DIR = "posts"

INSERT_BLOCK = """<div style="margin-top: 40px; padding: 24px; background: #fafafa; border: 1px solid #e5e7eb; border-radius: 12px; display: flex; flex-direction: column; gap: 16px;">
  <div style="font-size: 11px; color: #4f46e5; font-weight: bold; letter-spacing: 0.05em; text-transform: uppercase;">
    この記事を書いた人
  </div>
  <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
    <img src="/images/p/001.png" alt="管理人" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; background: #e5e7eb;">
    <div style="flex: 1; min-width: 200px;">
      <div style="font-size: 16px; font-weight: bold; color: #111; margin-bottom: 4px;">管理人</div>
      <div style="font-size: 13px; color: #4b5563; line-height: 1.5;">
        普段はウェブページ制作等を行なっています。
      </div>
    </div>
  </div>
  <div style="display: flex; justify-content: flex-end; margin-top: 4px;">
    <a href="/profile.html" style="display: inline-block; font-size: 13px; color: white; background: #4f46e5; text-decoration: none; padding: 8px 20px; border-radius: 8px; font-weight: bold; white-space: nowrap; transition: background 0.2s;">
      詳細を見る
    </a>
  </div>
</div>
"""

count = 0

for root, dirs, files in os.walk(TARGET_DIR):
    for file in files:
        # HTMLファイル以外はスキップ
        if not file.endswith(".html"):
            continue

        # index.html は除外
        if file == "index.html":
            continue

        path = os.path.join(root, file)

        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        # すでに挿入されている場合はスキップ
        if "この記事を書いた人" in html:
            continue

        # </body> の直前に挿入する
        if "</body>" in html:
            html = html.replace(
                "</body>",
                INSERT_BLOCK + "\n</body>"
            )
        else:
            # もし </body> タグがない特殊なHTMLファイルの場合は、ファイルの最末尾に追加
            html = html + "\n" + INSERT_BLOCK

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        count += 1
        print("updated:", path)

print(f"完了: {count}件")
