import re

STOPWORDS = {
    "nedir", "ne", "neler", "kim", "mi", "mu",
    "bugun", "bugunun", "nelerdir",
    "var", "mi", "icin", "ile"
}

SUFFIXES = [
    "leri", "lerin", "larin",
    "ler", "lar",
    "nin","nun",
    "de", "da", "te", "ta"
]

def normalize_word(word: str) -> str:
    w = word.lower()

    for suf in SUFFIXES:
        if w.endswith(suf) and len(w) > len(suf) + 2:
            w = w[:-len(suf)]
            break

    return w


def extract_keywords(sentence: str):
    words = sentence.lower().split()
    cleaned = []

    for w in words:
        nw = normalize_word(w)
        if nw and nw not in STOPWORDS:
            cleaned.append(nw)

    return cleaned
