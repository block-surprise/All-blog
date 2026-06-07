import os

BASE_URL = "https://htn-news.f5.si"

POST_DIRS = [
    "posts",
    "game/posts"
]

urls = ""


def add_urls(base_dir, prefix):
    global urls

    if not os.path.exists(base_dir):
        return

    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".html"):

                full_path = os.path.join(root, f).replace("\\", "/")

                # 相対パス取得
                url_path = full_path.split(base_dir + "/")[-1]

                urls += f"""
<url>
  <loc>{BASE_URL}/{prefix}/{url_path}</loc>
</url>
"""


# =====================
# posts
# =====================
add_urls("posts", "posts")

# =====================
# game/posts
# =====================
add_urls("game/posts", "game/posts")


# =====================
# XML生成
# =====================
xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

<url>
  <loc>{BASE_URL}</loc>
</url>

{urls}

</urlset>
"""

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(xml)

print("sitemap updated (posts + game)")
