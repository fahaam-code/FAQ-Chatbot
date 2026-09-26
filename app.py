"""Modern Gemini AI Chatbot with Conversation Memory."""

import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("gemini-chatbot")

app = Flask(__name__)

GEMINI_AVAILABLE = False
try:
    from google import genai
    from google.genai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    logger.warning("google-genai package not found. Please install requirements.txt")

_gemini_client = None
_gemini_client_key = None

DEFAULT_SUGGESTIONS = [
    "Explain how LLMs and neural networks work",
    "Write a Python function to parse JSON data",
    "Give me 5 practical tips to boost daily focus",
    "Brainstorm startup ideas in renewable energy",
]

MODELS_TO_TRY = [
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
]

SYSTEM_INSTRUCTION = (
    "You are a friendly, versatile, and highly capable AI Chatbot.\n\n"
    "Guidelines:\n"
    "- Help the user with any question, task, problem, or topic.\n"
    "- Provide clear, concise, and structured answers using markdown formatting (bullet points, bold text, code blocks).\n"
    "- When writing code, provide clean, idiomatic examples with brief explanations.\n"
    "- Maintain a supportive, polite, and helpful tone."
)


def get_active_gemini_key() -> str | None:
    """Retrieve Gemini API key from environment, reloading .env if needed."""
    load_dotenv(ENV_PATH, override=True)
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    return key.strip() if key.strip() else None


def get_gemini_client(api_key: str | None = None):
    """Retrieve or create persistent Gemini client."""
    global _gemini_client, _gemini_client_key
    key = (api_key or get_active_gemini_key() or "").strip()
    if not key or not GEMINI_AVAILABLE:
        return None
    if _gemini_client is None or _gemini_client_key != key:
        try:
            _gemini_client = genai.Client(api_key=key)
            _gemini_client_key = key
        except Exception as e:
            logger.warning("Failed to initialize Gemini client: %s", e)
            return None
    return _gemini_client


def generate_gemini_response(
    user_message: str,
    history: list[dict[str, str]] | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Generate response using Gemini with multi-turn conversation memory."""
    client = get_gemini_client(api_key)
    if not client:
        return {
            "answer": (
                "👋 Welcome! To start chatting, please set your Google Gemini API key by clicking "
                "the **Set Gemini Key** button in the top bar.\n\n"
                "You can get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey)."
            ),
            "engine": "System",
            "active": False,
        }

    # Build conversation contents list
    contents = []
    if history:
        # Keep last 14 turns for context
        for item in history[-14:]:
            role = "user" if item.get("role") == "user" else "model"
            text = (item.get("content") or "").strip()
            if text:
                contents.append({"role": role, "parts": [{"text": text}]})

    contents.append({"role": "user", "parts": [{"text": user_message}]})

    for model_name in MODELS_TO_TRY:
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=genai_types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.7,
                    max_output_tokens=1000,
                ),
            )
            if resp and resp.text:
                return {
                    "answer": resp.text.strip(),
                    "engine": "Google Gemini",
                    "model": model_name,
                    "active": True,
                }
        except Exception as err:
            logger.warning("Attempt with model %s failed: %s", model_name, err)

    return {
        "answer": "⚠️ Gemini service is currently experiencing high demand. Please try again in a moment.",
        "engine": "Google Gemini",
        "active": True,
    }


@app.get("/")
def index():
    has_gemini = bool(get_active_gemini_key() and GEMINI_AVAILABLE)
    return render_template(
        "index.html",
        starters=DEFAULT_SUGGESTIONS,
        has_gemini=has_gemini,
    )


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not message:
        return jsonify(error="Please type a message."), 400
    if len(message) > 2000:
        return jsonify(error="Message too long — please keep it under 2,000 characters."), 400

    api_key = get_active_gemini_key()
    response = generate_gemini_response(message, history=history, api_key=api_key)
    return jsonify(response)


@app.get("/api/status")
def status():
    has_key = bool(get_active_gemini_key())
    return jsonify(
        gemini_available=GEMINI_AVAILABLE,
        gemini_active=has_key and GEMINI_AVAILABLE,
    )


@app.get("/api/suggestions")
def suggestions():
    return jsonify(suggestions=DEFAULT_SUGGESTIONS)


@app.post("/api/config")
def set_config():
    global _gemini_client
    data = request.get_json(silent=True) or {}
    api_key = (data.get("gemini_api_key") or "").strip()

    if not api_key:
        return jsonify(error="API Key cannot be empty."), 400

    if GEMINI_AVAILABLE:
        try:
            client = genai.Client(api_key=api_key)
            client.models.generate_content(
                model=MODELS_TO_TRY[0],
                contents="ping",
            )
            _gemini_client = client
        except Exception as ex:
            if "API_KEY_INVALID" in str(ex) or "INVALID_ARGUMENT" in str(ex):
                return jsonify(error=f"Invalid Gemini API key: {ex}"), 400

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write(f"# Gemini API Key\nGEMINI_API_KEY={api_key}\n")

    os.environ["GEMINI_API_KEY"] = api_key
    return jsonify(success=True, message="Gemini API Key saved and activated successfully! 🚀")


if __name__ == "__main__":
    app.run(debug=True)
