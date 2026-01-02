import json
import os
from nlp.text_utils import extract_keywords, turkish_lower

# TheFuzz kütüphanesi
try:
    from thefuzz import fuzz
except ImportError:
    fuzz = None

DATA_PATH = "data/site_pages.json"
FAQ_PATH = "data/faq.json"
SPECIAL_PATH = "data/special_data.json"

# Verileri Yükle (Encoding hatası olmasın diye utf-8-sig kullanıyoruz)
SITE_PAGES = []
FAQ_DATA = []
SPECIAL_DATA = []

if os.path.exists(DATA_PATH):
    with open(DATA_PATH, encoding="utf-8-sig") as f: 
        SITE_PAGES = json.load(f)

if os.path.exists(FAQ_PATH):
    with open(FAQ_PATH, encoding="utf-8-sig") as f:
        FAQ_DATA = json.load(f)

if os.path.exists(SPECIAL_PATH):
    with open(SPECIAL_PATH, encoding="utf-8-sig") as f:
        SPECIAL_DATA = json.load(f)

# --- YENİ EKLENEN SOHBET FONKSİYONU ---
def check_chit_chat(question):
    """Kullanıcının selam, hal hatır, kimlik ve durum bildiren mesajlarını yanıtlar."""
    q = turkish_lower(question)
    
    # 1. Kimlik Soruları (Sen kimsin?)
    identity_keywords = ["sen kimsin", "kimsin", "adin ne", "adın ne", "ismin ne", "bot musun"]
    if any(x in q for x in identity_keywords):
        return {
            "answer": "Ben Erzincan Belediyesi için geliştirilmiş yapay zeka asistanıyım. 🤖<br>Size belediye hizmetleri, duyurular ve iletişim bilgileri konusunda yardımcı olmak için buradayım.",
            "items": []
        }

    # 2. Durum Soruları (Bot'a sorulan: Naber, Nasılsın?)
    status_keywords = ["nasılsın", "nasilsin", "naber", "ne haber", "ne var ne yok", "nasıl gidiyor"]
    if any(x in q for x in status_keywords):
        return {
            "answer": "Teşekkürler, dijital dünyamda her şey yolunda! 🚀 Sistemlerim Erzincan halkına hizmet etmek için %100 çalışıyor. Siz nasılsınız?",
            "items": []
        }

    # --- YENİ EKLENEN KISIM: KULLANICI CEVABI (İyiyim) ---
    # Kullanıcı "İyiyim", "Süperim" vb. derse
    user_status_good = ["iyiyim", "çok iyiyim", "süperim", "harikayım", "bomba gibiyim", "fena değilim", "idare eder", "çok şükür"]
    if any(x in q for x in user_status_good):
        return {
            "answer": "Bunu duyduğuma çok sevindim! 🧿 Gününüz hep böyle güzel geçsin. Peki, size nasıl yardımcı olabilirim?",
            "items": []
        }
    
    user_status_bad = ["kötüyüm", "moralim bozuk", "iyi değilim", "hastayım"]
    if any(x in q for x in user_status_bad):
        return {
            "answer": "Bunu duyduğuma üzüldüm. 😔 Geçmiş olsun. Umarım size yardımcı olarak modunuzu biraz olsun düzeltebilirim. Bir isteğiniz var mı?",
            "items": []
        }
    # -----------------------------------------------------

    # 3. Selamlaşma (Genel)
    greeting_keywords = ["selam", "merhaba", "slm", "sa ", "sa.", "günaydın", "iyi akşamlar", "iyi geceler", "iyi günler"]
    if q == "sa" or any(x in q for x in greeting_keywords):
        return {
            "answer": "Merhaba! 👋 Erzincan Belediyesi'ne hoş geldiniz. Size nasıl yardımcı olabilirim?",
            "items": []
        }

    # 4. Teşekkür ve Veda
    farewell_keywords = ["teşekkür", "sağol", "sagol", "görüşürüz", "baybay", "hoşçakal", "kolay gelsin", "tamamdır"]
    if any(x in q for x in farewell_keywords):
        return {
            "answer": "Rica ederim, ne demek! 😊 Her zaman bekleriz. İyi günler dilerim.",
            "items": []
        }

    return None
# --------------------------------------

# Özel Veri Kontrolü
def check_special_data(question_keywords):
    if not SPECIAL_DATA: return None
    best_item = None
    max_score = 0
    q_text = " ".join(question_keywords)
    
    for item in SPECIAL_DATA:
        score = 0
        item_keywords = item["keywords"]
        for k in item_keywords:
            if k in q_text: score += 30
        
        if fuzz:
            for k in item_keywords:
                for qk in question_keywords:
                    if fuzz.ratio(k, qk) > 85: score += 20
        
        if score > 40 and score > max_score:
            max_score = score
            best_item = item

    if best_item:
        return {"answer": best_item["answer"], "items": [{"title": best_item["title"], "url": best_item["url"], "snippet": "Özel Bilgi"}]}
    return None


def route_question(question: str):
    # 1. SOHBET (CHIT-CHAT) KONTROLÜ (YENİ)
    # Eski selamlaşma kodunu sildik, yerine bunu koyduk.
    chit_chat_result = check_chit_chat(question)
    if chit_chat_result:
        return chit_chat_result

    # Keywordleri çıkar
    q_keywords = extract_keywords(question)

    # 2. Özel Veri Kontrolü
    special_result = check_special_data(q_keywords)
    if special_result:
        return special_result

    # 3. FAQ Kontrolü
    if fuzz and FAQ_DATA:
        q_lower = turkish_lower(question)
        best_match = None
        best_ratio = 0
        for item in FAQ_DATA:
            ratio = fuzz.token_set_ratio(q_lower, turkish_lower(item["question"]))
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = item
        if best_match and best_ratio >= 75:
            return {"answer": f"📚 <b>SSS Bölümünde şunu buldum:</b><br>{best_match['answer']}", "items": []}

    # 4. Site İçi Arama
    if not q_keywords:
         return {"answer": "Ne demek istediğinizi tam anlayamadım. Biraz daha detay verebilir misiniz?", "items": []}

    best_page = None
    best_score = 0
    MIN_SCORE_THRESHOLD = 15 

    for page in SITE_PAGES:
        score = 0
        page_keywords = page.get("keywords", [])
        url_slug = page["url"].split("/")[-1].replace("-", " ")
        url_slug = turkish_lower(url_slug)

        for qk in q_keywords:
            if qk in url_slug: score += 10
            for pk in page_keywords:
                pk = turkish_lower(pk)
                if fuzz:
                    if fuzz.ratio(qk, pk) > 85: score += 5
                    elif fuzz.ratio(qk, pk) > 60: score += 2
                else:
                    if qk == pk: score += 5
                    elif qk in pk or pk in qk: score += 2

        q_str = " ".join(q_keywords)
        if "iletisim" in q_str and "iletisim" in page["url"]: score += 15
        if "duyuru" in q_str and "duyuru" in page["url"]: score += 15
        if "baskan" in q_str and "baskan" in page["url"]: score += 15

        if score > best_score:
            best_score = score
            best_page = page

    if best_page and best_score >= MIN_SCORE_THRESHOLD:
        return {
            "answer": "Web sitemizde konuyla ilgili şu sayfayı buldum:",
            "items": [{"title": best_page["title"], "url": best_page["url"], "snippet": f"Puan: {best_score}"}]
        }

    return {"answer": "Maalesef bu konuda bir bilgim yok veya ne demek istediğinizi anlayamadım. 😔", "items": []}