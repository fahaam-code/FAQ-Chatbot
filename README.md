# CodeAlpha — FAQ Chatbot

**CodeAlpha AI Internship · Task 2**

A Flask chatbot that answers user questions by matching them against a
knowledge base of FAQs, using classic NLP: **NLTK preprocessing** +
**TF-IDF / cosine-similarity intent matching** — exactly the approach the
task specifies.

## ✨ Features

- **NLTK text pipeline** — tokenization, cleaning, stop-word removal, lemmatization
- **TF-IDF + cosine similarity** to find the most similar FAQ (uni + bigrams)
- **Confidence scoring** — below a threshold the bot honestly says
  "I'm not sure" and suggests the closest questions instead
- **Chat UI** — message bubbles, typing indicator, clickable suggestion chips
- **Per-answer transparency** — shows which FAQ matched and its confidence %
- **Swappable knowledge base** — edit `faqs.json` to cover any product/topic
- `GET /api/faqs` returns the full FAQ list (e.g. for a "view all" panel)

## 🛠️ Tech Stack

| Layer        | Technology                                   |
|--------------|----------------------------------------------|
| Backend      | Python, Flask                                |
| NLP          | NLTK (tokenize, stopwords, WordNet lemmatizer) |
| Matching     | scikit-learn TF-IDF + cosine similarity      |
| Frontend     | HTML, CSS, vanilla JavaScript                |
| Knowledge    | `faqs.json` (default topic: CodeAlpha FAQs)  |

## 🚀 Setup & Run

```bash
# 1. Create and activate a virtual environment
py -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app (NLTK data downloads automatically on first start)
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## 🧠 How Matching Works

1. Every FAQ question is cleaned: lowercase → strip punctuation →
   tokenize (NLTK) → remove stop words → lemmatize.
2. The cleaned questions are vectorised with TF-IDF (1–2 word n-grams).
3. A user message goes through the same pipeline, and **cosine similarity**
   is computed against every FAQ.
4. The best match above a **0.35 confidence threshold** is returned;
   otherwise the bot offers the closest questions as suggestions.

## 📁 Project Structure

```
CodeAlpha_FAQChatbot/
├── app.py                  # Flask routes + FaqBot (TF-IDF matcher)
├── nlp_utils.py            # NLTK preprocessing helpers
├── faqs.json               # FAQ knowledge base (edit to change topics)
├── templates/
│   └── index.html          # Chat UI page
├── static/
│   ├── style.css           # Styling
│   └── script.js           # Chat logic (bubbles, typing, chips)
├── requirements.txt
└── README.md
```

## 🔌 API

| Endpoint     | Method | Body              | Response                                        |
|--------------|--------|-------------------|-------------------------------------------------|
| `/api/chat`  | POST   | `{"message"}`     | `{"answer", "matched", "confidence", "suggestions", ...}` |
| `/api/faqs`  | GET    | —                 | `{"topic", "faqs": [...]}`                      |

## 📸 Screenshot

_(Add a screenshot of a chat conversation here before submitting.)_

---
Built as part of the [CodeAlpha](https://www.codealpha.tech/) AI Internship.
