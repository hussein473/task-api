import os
from datetime import datetime, timezone
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .fetch import CACHE_DIR, FAILURES, fetch_page

RATINGS = ["One", "Two", "Three", "Four", "Five"]


def _clean(text):
    return " ".join(text.split())


def _cache_name(url):
    parts = urlparse(url).path.strip("/").split("/")
    return f"book-{parts[-2]}.html"


def extract_book(url, source_page):
    """Fetch (or read from cache) one book page and return the 8 raw fields, or None."""
    filename = _cache_name(url)
    html = fetch_page(url, filename)
    if html is None:
        return None

    # provenance: when this copy of the page was actually downloaded
    cache_path = os.path.join(CACHE_DIR, filename)
    fetched_at = datetime.fromtimestamp(os.path.getmtime(cache_path), timezone.utc).isoformat()

    try:
        soup = BeautifulSoup(html, "html.parser")
        # aim at the product area only, not the whole page
        product = soup.select_one("article.product_page div.product_main")

        title = _clean(product.h1.get_text())
        price_text = _clean(product.select_one("p.price_color").get_text())
        availability_text = _clean(product.select_one("p.availability").get_text())
        classes = product.select_one("p.star-rating")["class"]
        rating_text = next((c for c in classes if c in RATINGS), None)

        description = None
        header = soup.select_one("#product_description")
        if header:
            paragraph = header.find_next_sibling("p")
            if paragraph:
                description = _clean(paragraph.get_text()) or None
    except (AttributeError, TypeError, KeyError) as e:
        FAILURES[url] = f"parse error: {e}"
        print(f"PARSE FAILED {url}: {e}")
        return None

    return {
        "title": title,
        "product_url": url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at,
    }
