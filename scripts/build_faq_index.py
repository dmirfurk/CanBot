import json
import time
import sys
import os

# Path ayarı (Modül hatası almamak için)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from playwright.sync_api import sync_playwright

FAQ_URL = "https://www.erzincan.bel.tr/sss"

def build_faq_index():
    print("🤖 SSS Taraması başlıyor...")
    faq_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(FAQ_URL, timeout=60000)
            # Sayfanın iyice yüklenmesini bekle
            page.wait_for_timeout(5000) 
            
            # Erzincan Bel. sitesindeki yapı genelde "card" veya "panel" yapısındadır.
            # Tüm kartları (soru-cevap bloklarını) seçiyoruz.
            # Not: Sitedeki HTML yapısına göre burası değişebilir, 
            # ancak genelde .card yapısı kullanılır.
            cards = page.query_selector_all(".card")
            
            if not cards:
                # Alternatif yapı: accordion-item
                cards = page.query_selector_all(".accordion-item")

            print(f"🔍 {len(cards)} adet olası soru bloğu bulundu.")

            for card in cards:
                try:
                    # Soru kısmı genelde card-header veya button içindedir
                    question_el = card.query_selector(".card-header") or card.query_selector("button")
                    # Cevap kısmı genelde card-body veya collapse içindedir
                    answer_el = card.query_selector(".card-body") or card.query_selector(".collapse")

                    if question_el and answer_el:
                        question_text = question_el.inner_text().strip()
                        # Cevabın içindeki HTML taglerini temizlemek için text_content kullanabiliriz
                        # ya da inner_text (ama gizliyse inner_text boş gelebilir)
                        answer_text = answer_el.text_content().strip()

                        # Gereksiz karakter temizliği
                        question_text = question_text.replace("\n", " ").replace("  ", " ")
                        answer_text = answer_text.replace("\n", " ").replace("  ", " ")

                        if len(question_text) > 5 and len(answer_text) > 5:
                            faq_data.append({
                                "question": question_text,
                                "answer": answer_text
                            })
                except Exception as e:
                    print(f"Hata oluştu: {e}")
                    continue

        except Exception as e:
            print(f"❌ Sayfaya erişilemedi: {e}")
        
        browser.close()

    # Veriyi kaydet
    if faq_data:
        # data klasörü yoksa oluştur
        if not os.path.exists("data"):
            os.makedirs("data")
            
        with open("data/faq.json", "w", encoding="utf-8") as f:
            json.dump(faq_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ İşlem tamam! {len(faq_data)} adet soru-cevap 'data/faq.json' dosyasına kaydedildi.")
    else:
        print("⚠️ Hiç soru çekilemedi. Site HTML yapısı farklı olabilir.")

if __name__ == "__main__":
    build_faq_index()