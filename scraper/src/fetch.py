import os
import time

import requests

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/hussein473/task-api)"
HEADERS = {"User-Agent": USER_AGENT}
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache"))
TIMEOUT = 10
DELAY = 0.6  # seconds between REAL requests

_last_request = 0.0


def _polite_wait():
    global _last_request
    elapsed = time.monotonic() - _last_request
    if elapsed < DELAY:
        time.sleep(DELAY - elapsed)
    _last_request = time.monotonic()


def fetch_page(url, filename):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, filename)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"CACHE HIT {filename} ({len(html)} chars)")
        return html

    _polite_wait()
    print(f"FETCH {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    except requests.RequestException as e:
        print(f"FAILED {url}: {e}")
        return None
    if response.status_code != 200:
        print(f"FAILED {url}: status {response.status_code}")
        return None

    response.encoding = "utf-8"
    html = response.text
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  saved {filename} ({len(html)} chars)")
    return html
