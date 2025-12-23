from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class FAQMatcher:
    def __init__(self, faq_list):
        self.questions = [item["question"] for item in faq_list]
        self.answers = faq_list
        self.vectorizer = TfidfVectorizer()
        self.question_vectors = self.vectorizer.fit_transform(self.questions)

    def find_best_match(self, user_question):
        user_vec = self.vectorizer.transform([user_question])
        similarities = cosine_similarity(user_vec, self.question_vectors)
        best_idx = similarities.argmax()
        best_score = similarities[0][best_idx]

        if best_score < 0.3:
            return None

        return self.answers[best_idx]
