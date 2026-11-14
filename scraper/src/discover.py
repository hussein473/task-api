from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .fetch import fetch_page

START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_PAGES = 3


def discover_books():
    """Walk the first 3 catalogue pages by following the site's own 'next' link.

    Returns (pages_visited, all_links_found, unique_links).
    Each link is {"url": absolute book url, "source_page": catalogue page it was found on}.
    """
    page_url = START_URL
    pages = 0
    found = []

    while page_url and pages < MAX_PAGES:
        pages += 1
        html = fetch_page(page_url, f"catalogue-page-{pages}.html")
        if html is None:
            break
        soup = BeautifulSoup(html, "html.parser")

        for a in soup.select("article.product_pod h3 a"):
            found.append({"url": urljoin(page_url, a["href"]), "source_page": page_url})

        next_link = soup.select_one("li.next a")
        page_url = urljoin(page_url, next_link["href"]) if next_link else None

    seen = set()
    unique = []
    for item in found:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)

    return pages, found, unique
