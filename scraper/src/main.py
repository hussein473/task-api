import json
import os
import sys
import time
from datetime import datetime, timezone

from .discover import START_URL, discover_books
from .extract import extract_book
from .fetch import FAILURES, STATS
from .validate import validate_records

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
BROKEN_URL = "https://books.toscrape.com/catalogue/this-book-does-not-exist_0/index.html"


def write_json(name, data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, name), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run(with_broken_url=False):
    start_iso = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()

    pages, found, unique = discover_books()
    print(f"catalogue_pages={pages} discovered={len(found)} unique_urls={len(unique)}")

    items = list(unique)
    if with_broken_url:  # break things on OUR side, on purpose, to prove the run survives
        items.append({"url": BROKEN_URL, "source_page": START_URL})

    raw_records, failures = [], []
    for item in items:
        record = extract_book(item["url"], item["source_page"])  # one bad page never stops the loop
        if record:
            raw_records.append(record)
        else:
            failures.append({"stage": "fetch_or_parse", "url": item["url"],
                             "reason": FAILURES.get(item["url"], "unknown")})

    valid, invalid = validate_records(raw_records)
    errors = failures + [{"stage": "validate", **e} for e in invalid]

    report = {
        "start_time": start_iso,
        "duration_seconds": round(time.monotonic() - started, 2),
        "catalogue_pages": pages,
        "pages_discovered": len(unique),
        "pages_fetched": STATS["fetched"],
        "cache_hits": STATS["cache_hits"],
        "valid_records": len(valid),
        "invalid_records": len(invalid),
        "failed_pages": len(failures),
    }

    write_json("books.json", valid)
    write_json("errors.json", errors)
    write_json("run-report.json", report)
    return report, valid


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    broken = "--with-broken-url" in sys.argv

    report, valid = run(with_broken_url=broken)
    print("--- run report ---")
    print(json.dumps(report, indent=2))

    expected_failures = 1 if broken else 0
    ok = len(valid) == 60 and report["failed_pages"] == expected_failures
    raise SystemExit(0 if ok else 1)
