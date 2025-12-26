import json
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

BASE_URL = "https://www.erzincan.bel.tr"

def build_site_index():
    pages = []
    visited = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL, timeout=60000)
        page.wait_for_timeout(5000)

        links = page.query_selector_all("a")

        for link in links:
            href = link.get_attribute("href")
            text = link.inner_text().strip()

            if not href:
                continue

            if href.startswith("/"):
                href = BASE_URL + href

            if not href.startswith(BASE_URL):
                continue

            clean_url = href.split("#")[0].split("?")[0]

            if clean_url in visited:
                continue

            visited.add(clean_url)

            pages.append({
                "url": clean_url,
                "title": text if text else clean_url.split("/")[-1]
            })

        browser.close()

    # keyword üretimi
    for p in pages:
        slug = p["url"].split("/")[-1]
        words = slug.replace("-", " ").replace("_", " ").split()
        title_words = p["title"].lower().split()

        p["keywords"] = list(set(words + title_words))

    with open("data/site_pages.json", "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(pages)} sayfa indexlendi")


if __name__ == "__main__":
    build_site_index()
