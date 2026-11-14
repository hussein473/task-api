import json
import os
import sys

from .discover import discover_books
from .extract import extract_book
from .validate import validate_records

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))


def write_json(name, data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, name), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    pages, found, unique = discover_books()
    print(f"catalogue_pages={pages} discovered={len(found)} unique_urls={len(unique)}")

    raw_records = []
    for item in unique:
        record = extract_book(item["url"], item["source_page"])
        if record:
            raw_records.append(record)
    print(f"detail_pages={len(raw_records)}")

    valid, errors = validate_records(raw_records)
    write_json("books.json", valid)
    write_json("errors.json", errors)

    print(f"valid_records={len(valid)} invalid_records={len(errors)}")
    print(f"all price_gbp numbers: {all(isinstance(r['price_gbp'], float) for r in valid)}")
    print(f"all urls https: {all(r['product_url'].startswith('https://') for r in valid)}")
    print("example:", {k: valid[0][k] for k in ("title", "price_text", "price_gbp", "rating_text")})

    raise SystemExit(0 if len(valid) == 60 else 1)
