import os

BASE_URL = "https://htn-news.f5.si"
POST_DIR = "posts"

urls = ""

for root, dirs, files in os.walk(POST_DIR):

    for f in files:

        if f.endswith(".md"):

            path = os.path.join(root, f).replace("\\", "/")

            urls += f"""

<url>

  <loc>{BASE_URL}/{path}</loc>

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
