# AI Chatbot

A modern, streamlined AI Chatbot web application powered by **Google Gemini API** (`google-genai` SDK) and built with **Flask**. Features multi-turn conversational memory, rich markdown and code formatting, dynamic suggestion chips, and in-browser API key management.

## ✨ Features

- **Google Gemini AI Integration** — Powered by Google's latest Gemini models with automatic fast-fallback support.
- **Multi-Turn Conversation Memory** — Retains context across questions and replies just like ChatGPT.
- **Rich Markdown & Code Rendering** — Supports structured lists, bold/italic text, inline code, and dedicated code blocks.
- **Dynamic Suggestion Chips** — Starter prompts for immediate engagement.
- **In-Browser API Key Configuration** — Activate or update your Gemini API key directly from the UI or via `.env`.
- **Lightweight Architecture** — Zero unnecessary dependencies or bloated datasets; pure Flask and Gemini.

## 🛠️ Tech Stack

| Layer     | Technology                            |
|-----------|---------------------------------------|
| LLM       | Google Gemini API (`google-genai` SDK)|
| Backend   | Python 3, Flask, python-dotenv        |
| Frontend  | HTML5, CSS3, Vanilla JavaScript       |

## 🚀 Setup & Run

```bash
# 1. Create and activate a virtual environment
py -m venv .venv
.\.venv\Scripts\activate        # Windows
# source .venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Set your Gemini API key in .env or via the web UI
# GEMINI_API_KEY=your_gemini_api_key_here

# 4. Run the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## 📁 Project Structure

```
Final Chatbot/
├── app.py                  # Flask application & Gemini conversation handler
├── templates/
│   └── index.html          # Clean chat interface & API key modal
├── static/
│   ├── style.css           # Modern aesthetic UI styling
│   └── script.js           # Multi-turn chat client & modal logic
├── .env.example            # Environment configuration template
├── requirements.txt        # Minimal dependencies (Flask, google-genai, python-dotenv)
└── README.md
```

## 🔌 API Endpoints

| Endpoint           | Method | Body                                    | Description                                           |
|--------------------|--------|-----------------------------------------|-------------------------------------------------------|
| `/api/chat`        | POST   | `{"message": "...", "history": [...]}`  | Send message with conversation history and get reply  |
| `/api/status`      | GET    | —                                       | Check Gemini connection status                        |
| `/api/config`      | POST   | `{"gemini_api_key": "..."}`             | Validate, save, and activate Gemini API key           |
| `/api/suggestions` | GET    | —                                       | Get starter prompt suggestions                        |
