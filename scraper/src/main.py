from .discover import discover_books

if __name__ == "__main__":
    pages, found, unique = discover_books()
    print(f"catalogue_pages={pages}")
    print(f"discovered={len(found)}")
    print(f"unique_urls={len(unique)}")
    raise SystemExit(0 if (pages == 3 and len(unique) == 60) else 1)
