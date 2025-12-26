import json
from nlp.text_utils import extract_keywords
STOP_WORDS = {
    "belediye", "belediyenin", "sayın",
    "bilgi", "bilgileri", "hakkında",
    "ile", "ve", "ya",
    "nedir", "nelerdir",
    "kim", "kimler"
}


with open("data/site_pages.json", encoding="utf-8") as f:
    SITE_PAGES = json.load(f)

def route_question(question: str):
    q_keywords = extract_keywords(question)
    q_keywords = [q for q in q_keywords if q not in STOP_WORDS]

    best_page = None
    best_score = 0

    for page in SITE_PAGES:
        score = 0
        page_keywords = [k.lower() for k in page["keywords"]]

        url_slug = page["url"].split("/")[-1].replace("-", " ").lower()

        for qk in q_keywords:
            # slug'da geçiyorsa ÇOK güçlü
            if qk in url_slug:
                score += 8

            for pk in page_keywords:
                # birebir eşleşme
                if qk == pk:
                    score += 4
                # benzerlik
                elif qk in pk or pk in qk:
                    score += 2

        # 🔥 ÖZEL BOOSTLAR (elle değil, mantıksal)
        if "iletisim" in q_keywords and "iletisim" in page["url"]:
            score += 10

        if "duyuru" in q_keywords and "duyuru" in page["url"]:
            score += 10

        if "meclis" in q_keywords and "meclis" in page["url"]:
            score += 10

        if score > best_score:
            best_score = score
            best_page = page

    if best_page and best_score > 0:
        return {
            "answer": "Bu soruya en uygun sayfayi buldum:",
            "title": best_page["title"],
            "url": best_page["url"],
            "score": best_score
        }

    return {
        "answer": "Bu soruya uygun bir sayfa bulamadim.",
        "url": None,
        "title": None,
        "score": 0
    }

