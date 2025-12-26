from playwright.sync_api import sync_playwright


def fetch_page_text(url: str, max_length=2000):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url, timeout=60000)
        page.wait_for_timeout(8000)

        text = page.inner_text("body")
        browser.close()

    # Temizleme
    text = " ".join(text.split())
    return text[:max_length]
