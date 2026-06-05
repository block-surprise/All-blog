import os

BASE_URL = "https://htn-news.f5.si"
POST_DIR = "posts"

urls = ""

for root, dirs, files in os.walk(POST_DIR):
    for f in files:
        if f.endswith(".html"):  # ←ここ修正

            full_path = os.path.join(root, f).replace("\\", "/")

            # posts/ 以降だけにする
            url_path = full_path.split("posts/")[-1]

            urls += f"""
<url>
  <loc>{BASE_URL}/posts/{url_path}</loc>
</url>
"""

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

print("sitemap updated")
