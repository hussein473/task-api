# Polite scraper (A9)

## Target classification
- **Site:** Books to Scrape (https://books.toscrape.com)
- **Why this site:** toscrape.com describes it as a fictional bookstore built for people learning web scraping.
- **Scope:** first 3 catalogue pages only (60 books).
- **Data collected:** title, URL, price, availability, rating, description.
- **robots.txt result:** I requested https://books.toscrape.com/robots.txt once and got `404 Not Found` (checked on 2026-11-14): no robots file found. A missing file is not permission, so I rely on the sandbox notice on toscrape.com.
- **Why it's appropriate:** The site's own page says it wants to be scraped and is a safe place for beginners, so collecting a small amount of data from it is exactly what it is meant for.

I will not reuse this code on another site without checking its rules and terms first.
