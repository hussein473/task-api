import os
import time

import requests

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/hussein473/task-api)"
HEADERS = {"User-Agent": USER_AGENT}
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache"))
TIMEOUT = 10
DELAY = 0.6        # seconds between REAL requests
RETRY_WAIT = 2.0   # extra wait before the single retry

STATS = {"fetched": 0, "cache_hits": 0}  # counted for the run report
FAILURES = {}                            # url -> reason, for errors.json

_last_request = 0.0


def _polite_wait():
    global _last_request
    elapsed = time.monotonic() - _last_request
    if elapsed < DELAY:
        time.sleep(DELAY - elapsed)
    _last_request = time.monotonic()


def fetch_page(url, filename):
    """Return the page HTML, or None if it could not be fetched (reason goes in FAILURES)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, filename)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        STATS["cache_hits"] += 1
        print(f"CACHE HIT {filename} ({len(html)} chars)")
        return html

    for attempt in (1, 2):
        _polite_wait()
        print(f"FETCH {url}" + (" (retry)" if attempt == 2 else ""))
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        except (requests.Timeout, requests.ConnectionError) as e:
            reason = f"{type(e).__name__} (attempt {attempt})"
            if attempt == 1:
                print(f"  {reason}, retrying once")
                time.sleep(RETRY_WAIT)
                continue
            FAILURES[url] = reason
            print(f"FAILED {url}: {reason}")
            return None
        except requests.RequestException as e:
            FAILURES[url] = f"{type(e).__name__}: {e}"
            print(f"FAILED {url}: {FAILURES[url]}")
            return None

        if response.status_code == 200:
            response.encoding = "utf-8"
            html = response.text
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            STATS["fetched"] += 1
            print(f"  saved {filename} ({len(html)} chars)")
            return html

        # only server errors (5xx) are worth one more try; 404/403/other 4xx are not
        if 500 <= response.status_code < 600 and attempt == 1:
            print(f"  status {response.status_code}, retrying once")
            time.sleep(RETRY_WAIT)
            continue

        FAILURES[url] = f"HTTP {response.status_code}"
        print(f"FAILED {url}: status {response.status_code}")
        return None

    return None
