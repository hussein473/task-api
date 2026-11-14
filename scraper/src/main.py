import json
import sys

from .discover import discover_books
from .extract import extract_book

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # so "£" prints correctly on Windows

    pages, found, unique = discover_books()
    print(f"catalogue_pages={pages}")
    print(f"discovered={len(found)}")
    print(f"unique_urls={len(unique)}")

    raw_records = []
    for item in unique:
        record = extract_book(item["url"], item["source_page"])
        if record:
            raw_records.append(record)

    print("--- one complete raw record ---")
    print(json.dumps(raw_records[0], indent=2, ensure_ascii=False))
    print(f"detail_pages={len(raw_records)}")
    print(f"without_description={sum(1 for r in raw_records if r['description'] is None)}")

    raise SystemExit(0 if len(raw_records) == 60 else 1)
