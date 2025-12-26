from playwright.sync_api import sync_playwright, TimeoutError


def scrape_duyurular():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("[*] Sayfa aciliyor...")
        page.goto("https://erzincan.bel.tr/duyurular", timeout=60000)

        try:
            # SAYFA KENDINI YENILESE BILE, KART GELENE KADAR BEKLE
            page.wait_for_selector("a:has-text('Devamini Oku')", timeout=15000)
        except TimeoutError:
            print("[!] Kart bulunamadi (timeout)")
            browser.close()
            return []

        print("[*] Kartlar bulundu, DOM okunuyor...")

        links = page.query_selector_all("a:has-text('Devamini Oku')")

        print(f"[+] Bulunan duyuru sayisi: {len(links)}")

        for link in links:
            try:
                href = link.get_attribute("href")
                title = link.inner_text().strip()

                if href:
                    results.append({
                        "title": title,
                        "url": "https://erzincan.bel.tr" + href
                    })
            except:
                continue

        browser.close()

    return results
