# Polite scraper (A9)

## Target classification
- **Site:** Books to Scrape (https://books.toscrape.com)
- **Why this site:** toscrape.com describes it as a fictional bookstore built for people learning web scraping.
- **Scope:** first 3 catalogue pages only (60 books).
- **Data collected:** title, URL, price, availability, rating, description.
- **robots.txt result:** I requested https://books.toscrape.com/robots.txt once and got `404 Not Found` (checked on 2026-11-14): no robots file found. A missing file is not permission, so I rely on the sandbox notice on toscrape.com.
- **Why it's appropriate:** The site's own page says it wants to be scraped and is a safe place for beginners, so collecting a small amount of data from it is exactly what it is meant for.

I will not reuse this code on another site without checking its rules and terms first.


## How to run it

Python lane (Python 3.10+). Run from the **repository root**, not from inside `scraper/`:

    pip install -r scraper/requirements.txt
    python -m scraper.src.main

This processes exactly the first 3 catalogue pages, finds 60 unique book URLs, writes `scraper/output/books.json`, `errors.json` and `run-report.json`, and prints a short report. The first run takes about a minute because of the politeness delay; reruns read from the cache and take a second or two.

To prove that one bad page cannot kill a run, add one made-up book URL on purpose:

    python -m scraper.src.main --with-broken-url

Libraries: Requests (HTTP), Beautiful Soup (HTML), Pydantic (validation).

## Record schema

Each record in `books.json` looks like this (only `description` may be `null`):

    title              string, required
    product_url        string, absolute https:// URL, the record's identity
    price_text         string, the original text, e.g. "£51.77"
    price_gbp          number, cleaned from price_text, e.g. 51.77
    availability_text  string, e.g. "In stock (22 available)"
    rating_text        "One" | "Two" | "Three" | "Four" | "Five"
    description        string or null (never invented)
    source_page        the catalogue page the book was found on
    fetched_at         when that page was downloaded (provenance)

Records that fail validation go to `errors.json` with the reason and never reach `books.json`. Duplicates (same `product_url`) count once, so a rerun gives the same 60 records, not 120.

## Politeness rules

- Honest user-agent that names the project and links to this repo.
- Timeout of 10 seconds on every request.
- At least 0.6 seconds between real requests; cached pages need no delay.
- Status code checked before parsing; only 200 counts as a page.
- One retry for timeouts and 5xx errors only. 404 and 403 are never retried.
- Every page is cached in `scraper/cache/` (git-ignored), so development does not hit the site again.
- Only the first 3 catalogue pages (60 books) are ever requested.

## Run report

This is a real `run-report.json`. It is from a rerun, so it was served from the cache; the first run downloaded 63 pages (3 catalogue pages + 60 book pages).

    {
      "start_time": "2026-11-14T18:52:51.051288+00:00",
      "duration_seconds": 0.53,
      "catalogue_pages": 3,
      "pages_discovered": 60,
      "pages_fetched": 0,
      "cache_hits": 63,
      "valid_records": 60,
      "invalid_records": 0,
      "failed_pages": 0
    }

Broken-URL test (`--with-broken-url`): one made-up URL returned 404, was logged in `errors.json` and skipped, and the 60 good records survived (`failed_pages: 1`). Its report is saved in `scraper/output/run-report-broken-url-test.json`.

## Why no browser

The book data is already in the HTML the server sends, so a headless browser would only add cost and slowness.

## Ethics note

Before I scrape a site, I check that it allows it. This one is a practice site made for scraping, so it's fine. If a site has an official API, I'd use that instead. I don't get around logins, paywalls or blocks, I only take the data I actually need, and I go slowly so I don't overload the server.

## Honest limitation

My scraper only works as long as the site's HTML stays the same. It looks for specific parts of the page, like the title and the price. If the site changes its layout, those pages will fail and show up in `errors.json` instead of `books.json`. It also only collects 60 of the 1000 books, and the descriptions are saved exactly as they appear on the page, even when the text looks odd.