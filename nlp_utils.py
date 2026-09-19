"""CodeAlpha Task 2 — FAQ Chatbot.

NLP preprocessing helpers: tokenization, cleaning, stop-word removal and
lemmatization using NLTK, exactly the pipeline the task requires.
"""

from __future__ import annotations

import re
import ssl

import nltk
from nltk.stem import WordNetLemmatizer

_REQUIRED_RESOURCES = ("punkt_tab", "stopwords", "wordnet", "omw-1.4")

_lemmatizer = WordNetLemmatizer()
_stopwords: set[str] | None = None


def ensure_nltk_data() -> None:
    """Download the NLTK resources we need (no-op once present)."""
    try:
        ssl._create_default_https_context = ssl.create_default_context
    except Exception:  # pragma: no cover
        pass
    for resource in _REQUIRED_RESOURCES:
        try:
            nltk.data.find(_resource_path(resource))
        except LookupError:
            nltk.download(resource, quiet=True)


def _resource_path(resource: str) -> str:
    return {
        "punkt_tab": "tokenizers/punkt_tab",
        "punkt": "tokenizers/punkt",
        "stopwords": "corpora/stopwords",
        "wordnet": "corpora/wordnet",
        "omw-1.4": "corpora/omw-1.4",
    }[resource]


def _get_stopwords() -> set[str]:
    global _stopwords
    if _stopwords is None:
        from nltk.corpus import stopwords

        _stopwords = set(stopwords.words("english"))
    return _stopwords


def preprocess(text: str) -> str:
    """Clean + tokenize + lemmatize a piece of text.

    Steps: lowercase -> strip punctuation/numbers -> tokenize ->
    remove stop words -> lemmatize -> rejoin.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)  # drop punctuation & symbols
    tokens = nltk.word_tokenize(text)
    stops = _get_stopwords()
    kept = [t for t in tokens if t not in stops and t.strip()]
    lemmas = [_lemmatizer.lemmatize(t) for t in kept]
    return " ".join(lemmas)
