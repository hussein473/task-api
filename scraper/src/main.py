from .fetch import fetch_page

if __name__ == "__main__":
    html = fetch_page("https://books.toscrape.com/catalogue/page-1.html", "catalogue-page-1.html")
    print("ok" if html else "failed")
    raise SystemExit(0 if html else 1)
