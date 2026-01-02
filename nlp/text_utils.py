import re

# Türkçe'ye özgü durdurma kelimeleri
STOPWORDS = {
    "nedir", "ne", "neler", "kim", "mi", "mu", "mı", "mü",
    "bugün", "bugünün", "nelerdir", "nasıl", "nerede",
    "var", "için", "ile", "ve", "veya", "hakkında",
    "belediye", "belediyesi", "sayın", "bilgi"
}

SUFFIXES = [
    "leri", "lerin", "ların", "larin",
    "ler", "lar",
    "nin", "nın", "nun", "nün",
    "de", "da", "te", "ta",
    "yi", "yı", "yu", "yü",
    "sı", "si", "su", "sü"
]

def turkish_lower(text: str) -> str:
    """Türkçe karakterlere uygun küçük harfe çevirme."""
    translation_table = str.maketrans({
        "İ": "i", "I": "ı", "Ş": "ş", "Ğ": "ğ", "Ü": "ü", "Ö": "ö", "Ç": "ç"
    })
    return text.translate(translation_table).lower()

def normalize_word(word: str) -> str:
    w = turkish_lower(word)
    
    # Basit stemming (sondan ek atma)
    for suf in SUFFIXES:
        if w.endswith(suf) and len(w) > len(suf) + 3:
            w = w[:-len(suf)]
            break 
            
    return w

def extract_keywords(sentence: str):
    # Noktalama işaretlerini kaldır
    sentence = re.sub(r'[^\w\s]', '', sentence)
    
    words = sentence.split()
    cleaned = []

    for w in words:
        w_clean = turkish_lower(w)
        
        if w_clean in STOPWORDS:
            continue

        nw = normalize_word(w)
        if nw and nw not in STOPWORDS:
            cleaned.append(nw)

    return cleaned