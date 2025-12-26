import requests
import json
import re
from bs4 import BeautifulSoup

BASE_URL = "https://www.erzincan.bel.tr"


def get_candidate_links():
    print("[*] robots.txt okunuyor...")
    r = requests.get(f"{BASE_URL}/robots.txt", timeout=30)
    r.encoding = "utf-8"

    links = set()

    # robots.txt icinden sitemap veya sayfa ipuclari
    for line in r.text.splitlines():
        if "sayfa" in line or "mudurluk" in line:
            path = line.split(":")[-1].strip()
            if path.startswith("/"):
                links.add(BASE_URL + path)

    # bilinen sabit sayfalar (manuel tanimli ama otomatik kullaniliyor)
    known_pages = [
        "/sayfa/nikah-islemleri",
        "/sayfa/cenaze-hizmetleri",
        "/sayfa/e-belediye",
        "/sayfa/iletisim",
        "/sayfa/su-kanalizasyon"
    ]

    for p in known_pages:
        links.add(BASE_URL + p)

    return list(links)


def extract_page_text(url):
    r = requests.get(url, timeout=30)
    r.encoding = "utf-8"

    soup = BeautifulSoup(r.text, "html.parser")

    main = soup.find("main") or soup.find("div", class_="container")
    if not main:
        return None

    text = main.get_text(separator=" ", strip=True)
    return text if len(text) > 300 else None


def build_dataset():
    links = get_candidate_links()
    dataset = []

    for link in links:
        print("[*]", link)
        text = extract_page_text(link)
        if text:
            dataset.append({
                "source": link,
                "content": text
            })

    with open("data/web_pages.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(dataset)} adet otomatik kayit olusturuldu")


if __name__ == "__main__":
    build_dataset()
