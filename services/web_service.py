import json
from difflib import SequenceMatcher

class WebMatcher:
    def __init__(self, path="data/web_pages.json"):
        with open(path, encoding="utf-8") as f:
            self.pages = json.load(f)

    def similarity(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def find_answer(self, question):
        best_score = 0
        best_page = None

        for page in self.pages:
            score = self.similarity(question, page["content"][:500])

            if score > best_score:
                best_score = score
                best_page = page

        if best_score < 0.2:
            return None

        return {
            "answer": best_page["content"][:700] + "...",
            "source": best_page["url"]
        }
