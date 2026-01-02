import json
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.erzincan.bel.tr"

def build_site_index():
    pages = []
    visited = set()

    print("🌍 Site taraması başlıyor...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # timeout süresini artırdık ama wait_until ile sayfa yüklenince beklemez
            page.goto(BASE_URL, timeout=90000, wait_until="domcontentloaded")
            # Sabit 5 sn yerine body gelene kadar bekle
            page.wait_for_selector("body", timeout=10000) 
        except Exception as e:
            print(f"❌ Ana sayfaya erişilemedi: {e}")
            browser.close()
            return

        # Linkleri topla
        links = page.query_selector_all("a")
        print(f"🔗 {len(links)} adet link bulundu, işleniyor...")

        for link in links:
            try:
                href = link.get_attribute("href")
                text = link.inner_text().strip()

                if not href: continue

                # Relative link düzeltme
                if href.startswith("/"):
                    href = BASE_URL + href

                # Sadece bu domaindeki linkleri al
                if not href.startswith(BASE_URL): continue
                
                # Dosyaları atla (pdf, jpg vs)
                if href.endswith((".pdf", ".jpg", ".png", ".jpeg", ".zip")): continue

                clean_url = href.split("#")[0].split("?")[0]

                if clean_url in visited: continue
                visited.add(clean_url)

                # Boş başlıkları URL'den üret
                title = text if text else clean_url.split("/")[-1].replace("-", " ")

                pages.append({
                    "url": clean_url,
                    "title": title
                })
            except:
                continue

        browser.close()

    # Keyword üretimi ve Türkçe karakter temizliği
    from nlp.text_utils import extract_keywords # Senin fonksiyonunu kullanıyoruz
    
    print("🧠 Keywordler çıkartılıyor...")
    for p in pages:
        # Title ve URL slug'ını birleştirip keyword çıkarıyoruz
        slug = p["url"].split("/")[-1].replace("-", " ")
        combined_text = f"{p['title']} {slug}"
        p["keywords"] = extract_keywords(combined_text)

    # Klasör yoksa oluştur
    import os
    if not os.path.exists("data"):
        os.makedirs("data")

    with open("data/site_pages.json", "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    print(f"✅ İşlem tamam! Toplam {len(pages)} sayfa data/site_pages.json dosyasına kaydedildi.")

if __name__ == "__main__":
    build_site_index()