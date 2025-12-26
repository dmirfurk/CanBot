import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_detail_page(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    paragraphs = soup.find_all("p")

    texts = []
    for p in paragraphs:
        t = p.get_text(strip=True)
        if len(t) > 40:
            texts.append(t)

    return "\n".join(texts)
