import requests
from bs4 import BeautifulSoup
import json
import os
import time
from urllib.parse import urljoin, urlparse

# --- HEDEF LİNKLER ---
# Botun kesinlikle girmesini ve içini deşmesini istediğimiz yerler
TARGET_ROOTS = [
    "https://www.erzincan.bel.tr",
    "https://www.erzincan.bel.tr/mudurlukler",       # Artık burayı ana durak kabul edecek
    "https://www.erzincan.bel.tr/muhtarliklar",      # Burayı da
    "https://www.erzincan.bel.tr/yonetmelikler",     # Burayı da
    "https://www.erzincan.bel.tr/faaliyet-raporlari",
    "https://webportal.erzincan.bel.tr/web/guest/2",
    "https://webportal.erzincan.bel.tr/web/guest/15"
]

ALLOWED_DOMAINS = ["erzincan.bel.tr", "webportal.erzincan.bel.tr", "www.erzincan.bel.tr"]
OUTPUT_FILE = "data/site_pages.json"

IGNORE_EXTENSIONS = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".png", ".zip", ".rar", ".jpeg", ".css", ".js", ".gif")

visited_urls = set()
pages_data = []

def normalize_text(text):
    if not text: return ""
    return " ".join(text.split())

def is_allowed_url(url):
    try:
        domain = urlparse(url).netloc.replace("www.", "")
        for allowed in ALLOWED_DOMAINS:
            if allowed.replace("www.", "") in domain:
                return True
    except:
        return False
    return False

def get_keywords_from_title(title):
    clean_title = title.replace("T.C. Erzincan Belediyesi", "").replace("|", "").strip()
    words = clean_title.lower().split()
    clean_words = [w for w in words if len(w) > 2]
    return clean_words

def crawl(url, depth=0, max_depth=2):
    if url.endswith("/"): url = url[:-1]
    
    # Kök portal adresine takılmasın
    if url == "https://webportal.erzincan.bel.tr": return

    # Zaten gezdiysek atla
    if url in visited_urls: return

    # Dosya uzantılarını atla
    if any(url.lower().endswith(ext) for ext in IGNORE_EXTENSIONS): return
    
    # İzin verilmeyen domaini atla
    if not is_allowed_url(url): return

    print(f"🕷️ [{depth}] Taranıyor: {url}")
    visited_urls.add(url)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15) # Timeout arttırdım
        if response.status_code != 200:
            print(f"❌ Hata ({response.status_code}): {url}")
            return

        soup = BeautifulSoup(response.content, "html.parser")

        # --- VERİ ÇIKARMA ---
        title = soup.title.string if soup.title else ""
        if not title:
            h1 = soup.find("h1")
            if h1: title = h1.get_text().strip()
            else:
                pt = soup.find("span", class_="portlet-title-text")
                if pt: title = pt.get_text().strip()

        title = normalize_text(title)
        
        # Keyword üret
        keywords = get_keywords_from_title(title)
        if "webportal" in url: keywords.extend(["online", "ödeme", "sorgulama", "borç"])
        if "mudurluk" in url: keywords.append("müdürlük")
        if "muhtarlik" in url: keywords.append("muhtarlık")

        # KAYDET
        # Başlığı düzgün olanları kaydet
        if len(title) > 2:
            page_info = {
                "url": url,
                "title": title,
                "keywords": list(set(keywords)),
                "snippet": ""  # Temiz kalsın
            }
            pages_data.append(page_info)
            # Logda ne bulduğunu görelim
            print(f"   ✅ Eklendi: {title}")

        # --- LİNKLERİ BULMA ---
        if depth < max_depth:
            # Tüm linkleri al
            links = soup.find_all("a", href=True)
            
            # Sadece bu sayfadaki link sayısı
            found_count = 0
            
            for link in links:
                href = link["href"]
                if href.startswith("javascript") or href.startswith("#") or href.startswith("mailto"): continue
                
                full_link = urljoin(url, href)
                
                # Eğer izinli domainse ve henüz gezilmediyse
                if is_allowed_url(full_link) and full_link not in visited_urls:
                    found_count += 1
                    crawl(full_link, depth + 1, max_depth)
            
            if found_count > 0:
                print(f"      ↪️ {found_count} yeni link bulundu.")

    except Exception as e:
        print(f"⚠️ Hata: {url} -> {e}")

if __name__ == "__main__":
    print("🚀 Gelişmiş Liste Taraması Başlıyor...")
    
    # BU DÖNGÜ ÇOK ÖNEMLİ!
    for root_url in TARGET_ROOTS:
        # HİLE BURADA: Her yeni hedef URL için visited listesinden siliyoruz!
        # Böylece ana sayfa onu daha önce gezmiş olsa bile, biz onu 
        # "Sıfır Noktası" kabul edip derinlemesine (depth=0) tekrar tarıyoruz.
        if root_url in visited_urls:
            visited_urls.remove(root_url)
        
        # Derinliği 3 yaptık ki müdürlüklerin içine (sayfanın içindeki linke) kesin girsin.
        crawl(root_url, depth=0, max_depth=3)
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(pages_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n🏁 İŞLEM TAMAMLANDI!")
    print(f"📄 Toplam {len(pages_data)} sayfa kaydedildi.")