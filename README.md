# CanBot (RAG Sürümü)

Bu repo Erzincan Belediyesi web içeriği üzerinden soru-cevap yapabilen bir chatbot API'sini içerir.

## RAG Nedir?
**RAG (Retrieval-Augmented Generation)** yaklaşımında sistem:
1) Önce yerel veri kaynağından (site taraması/FAQ) **ilgili bilgileri bulur (retrieval)**  
2) Sonra bu bulunan içeriklere dayanarak **cevap üretir (generation)**

Bu projede RAG, yerel olarak çalışan **TF-IDF tabanlı bir retrieval index** ile uygulanmıştır.
> Not: İsterseniz daha sonra TF-IDF yerine embedding + vektör veritabanı (Chroma/FAISS + embedding modeli) ile yükseltilebilir.

---

## Kurulum

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

## RAG Index Oluşturma / Güncelleme

Proje `data/site_pages.json` ve `data/faq.json` içeriğinden bir index üretir.

```bash
python -m scripts.build_rag_index
```

Bu işlem `db/rag_index.pkl` dosyasını oluşturur.

## Çalıştırma

```bash
python -m uvicorn main:app --reload
```

API:
- `GET /` sağlık kontrol
- `POST /chat` soru sor

Örnek istek:
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"bugün etkinlik var mı\"}"
```

## Cevap Formatı
`/chat` yanıtı:

```json
{
  "answer": "....",
  "items": [
    {"title": "...", "url": "...", "snippet": "..."}
  ]
}
```

## RAG Akışı (Özet)
- `nlp/router.py` içinde önce sohbet/özel veri/heuristic arama çalışır
- Yeterli eşleşme olmazsa **RAG fallback** devreye girer:
  - `rag/rag_engine.py::answer_with_sources()`
  - Top-k kaynak bulunur
  - Cevap, bulunan kaynaklara dayanarak (uydurmadan) döndürülür
