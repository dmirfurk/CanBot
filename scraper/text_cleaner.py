import re

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"Anasayfa.*", "", text)
    return text.strip()
