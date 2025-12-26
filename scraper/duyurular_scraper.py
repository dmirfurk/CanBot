from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

URL = "https://www.erzincan.bel.tr/duyurular"

# --- CACHE ---
_cache = {
    "data": None,
    "time": None
}
CACHE_MINUTES = 10


def scrape_duyurular(limit=5):
    global _cache

    # cache kontrolü
    if _cache["data"] and _cache["time"]:
        if datetime.now() - _cache["time"] < timedelta(minutes=CACHE_MINUTES):
            print("[CACHE] Duyurular cache'ten geldi")
            return _cache["data"]

    print("[SCRAPE] Duyurular site'dan cekiliyor...")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        links = page.query_selector_all("a")

        for link in links:
            href = link.get_attribute("href")
            text = link.inner_text().strip()

            if not href or not text:
                continue

            if "duyuru" in href.lower() and len(text) > 10:
                if not href.startswith("http"):
                    href = "https://www.erzincan.bel.tr" + href

                results.append({
                    "title": text,
                    "link": href
                })

            if len(results) >= limit:
                break

        browser.close()

    _cache["data"] = results
    _cache["time"] = datetime.now()

    return results
