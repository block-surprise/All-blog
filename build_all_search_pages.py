def build_all_search_pages(articles):

    os.makedirs("game/search", exist_ok=True)

    keywords = set()

    for a in articles:
        for word in a["title"].split():
            if len(word) >= 2:
                keywords.add(word)

    # 既存削除
    for f in os.listdir("game/search"):
        if f.endswith(".html"):
            os.remove(os.path.join("game/search", f))

    # 再生成
    for kw in keywords:

        filename = safe_filename(kw)

        build_search_page(kw, articles)

    print("all search pages rebuilt:", len(keywords))
