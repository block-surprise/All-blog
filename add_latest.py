import os

TARGET_DIR = "posts"

# 挿入したい正しいブロック
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
</div>"""

count = 0

for root, dirs, files in os.walk(TARGET_DIR):
    for file in files:
        if not file.endswith(".html"):
            continue
        if file == "index.html":
            continue

        path = os.path.join(root, file)

        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        # 【ステップ1】すでに間違った位置に入ってしまったブロックがあれば一旦削除
        # 前後に改行が含まれている場合を考慮して、ブロック単体を取り除く
        if INSERT_BLOCK in html:
            html = html.replace(INSERT_BLOCK, "")

        # 【ステップ2】「<h2>まとめ</h2>」の後の最初の「</p>」を探して、その直後に挿入する
        if "<h2>まとめ</h2>" in html:
            # 「<h2>まとめ</h2>」の開始位置を見つける
            summary_idx = html.find("<h2>まとめ</h2>")
            
            # その位置以降で、最初の「</p>」の位置を見つける
            p_close_idx = html.find("</p>", summary_idx)
            
            if p_close_idx != -1:
                # 「</p>」の文字数（4文字）分進めた位置を挿入ポイントにする
                insert_pos = p_close_idx + 4
                
                # スライスを使って、</p> の直後にパーツを滑り込ませる
                html = html[:insert_pos] + "\n\n" + INSERT_BLOCK + html[insert_pos:]
            else:
                # 万が一 </p> が見つからない場合は安全のためスキップ
                continue
        else:
            # <h2>まとめ</h2> がない記事の場合はスキップ
            continue

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        count += 1
        print("fixed & updated:", path)

print(f"完了: {count}件")
