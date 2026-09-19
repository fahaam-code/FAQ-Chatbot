"""CodeAlpha Task 2 — FAQ Chatbot.

A Flask chatbot that answers user questions by matching them against a
knowledge base of FAQs:

* NLTK preprocessing (tokenize, clean, stop-word removal, lemmatize)
* TF-IDF vectorisation + cosine similarity (scikit-learn) for intent matching
* Confidence scoring with a graceful fallback when nothing matches

Swap `faqs.json` for your own product/topic FAQs to reuse the bot anywhere.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
from flask import Flask, jsonify, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp_utils import ensure_nltk_data, preprocess

BASE_DIR = Path(__file__).resolve().parent
FAQS_PATH = BASE_DIR / "faqs.json"

# Below this cosine similarity the bot admits it doesn't know.
CONFIDENCE_THRESHOLD = 0.35
# Number of similar questions offered as suggestions on a miss.
SUGGESTION_COUNT = 3

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("faq-chatbot")

app = Flask(__name__)


class FaqBot:
    """TF-IDF + cosine similarity matcher over a FAQ knowledge base."""

    def __init__(self, faqs_path: Path):
        with open(faqs_path, encoding="utf-8") as fh:
            data = json.load(fh)
        self.topic: str = data.get("topic", "FAQ")
        self.faqs: list[dict] = data["faqs"]
        self.questions = [entry["question"] for entry in self.faqs]

        # Preprocess every FAQ question once, then vectorise the corpus.
        corpus = [preprocess(q) for q in self.questions]
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        logger.info("Loaded %d FAQs for topic '%s'", len(self.faqs), self.topic)

    def answer(self, user_message: str) -> dict:
        """Return the best matching FAQ answer for a user message."""
        cleaned = preprocess(user_message)
        if not cleaned:
            return {
                "answer": "I couldn't quite read that — could you rephrase your question?",
                "matched": False,
                "confidence": 0.0,
                "suggestions": self.random_questions(),
            }

        query_vec = self.vectorizer.transform([cleaned])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        if best_score < CONFIDENCE_THRESHOLD:
            return {
                "answer": (
                    "I'm not sure about that one 🤔 — it may not be in my knowledge base. "
                    "Try one of these questions instead:"
                ),
                "matched": False,
                "confidence": round(best_score, 3),
                "suggestions": self._top_questions(similarities, SUGGESTION_COUNT),
            }

        return {
            "answer": self.faqs[best_idx]["answer"],
            "matched": True,
            "confidence": round(best_score, 3),
            "matched_question": self.faqs[best_idx]["question"],
            "suggestions": [],
        }

    def _top_questions(self, similarities: np.ndarray, count: int) -> list[str]:
        """The `count` most similar FAQ questions (for suggestion chips)."""
        order = np.argsort(similarities)[::-1]
        picked: list[str] = []
        for idx in order[: count + 1]:
            q = self.faqs[int(idx)]["question"]
            if q not in picked:
                picked.append(q)
            if len(picked) == count:
                break
        return picked

    def random_questions(self) -> list[str]:
        """A few sample questions to show the user."""
        return [self.faqs[i]["question"] for i in (0, 2, len(self.faqs) - 1)]


ensure_nltk_data()
bot = FaqBot(FAQS_PATH)


@app.get("/")
def index():
    return render_template("index.html", topic=bot.topic)


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify(error="Please type a message."), 400
    if len(message) > 500:
        return jsonify(error="That message is too long — keep it under 500 characters."), 400
    return jsonify(bot.answer(message))


@app.get("/api/faqs")
def list_faqs():
    """Full FAQ list — handy for a 'View all questions' panel."""
    return jsonify(topic=bot.topic, faqs=bot.faqs)


if __name__ == "__main__":
    app.run(debug=True)
