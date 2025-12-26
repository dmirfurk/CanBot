import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.erzincan.bel.tr"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_duyuru_links(max_links=50):
    url = f"{BASE_URL}/duyurular"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for a in soup.select("a[href]"):
        href = a.get("href")
        if href.startswith("/duyurular/") and href.count("/") > 2:
            links.append(BASE_URL + href)

    # tekrarlarý sil
    return list(dict.fromkeys(links))[:max_links]
