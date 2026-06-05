import os

BASE_URL = "https://htn-news.f5.si"
POST_DIR = "posts"

files = sorted(os.listdir(POST_DIR), reverse=True)

urls = ""

for f in files:
    if f.endswith(".md"):
        urls += f"""
  <url>
    <loc>{BASE_URL}/posts/{f}</loc>
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

print("sitemap generated")
