/* Front-end logic for the FAQ chatbot. */
"use strict";

const chatWindow = document.getElementById("chat-window");
const suggestionsBox = document.getElementById("suggestions");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");

let busy = false;

function scrollDown() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function addMessage(text, who, meta) {
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  div.textContent = text;
  if (meta) {
    const metaEl = document.createElement("span");
    metaEl.className = "meta";
    metaEl.textContent = meta;
    div.appendChild(metaEl);
  }
  chatWindow.appendChild(div);
  scrollDown();
  return div;
}

function addTyping() {
  const div = document.createElement("div");
  div.className = "msg bot typing";
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement("span");
    dot.className = "dot";
    div.appendChild(dot);
  }
  chatWindow.appendChild(div);
  scrollDown();
  return div;
}

function setSuggestions(questions) {
  suggestionsBox.innerHTML = "";
  for (const q of questions || []) {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.textContent = q;
    chip.addEventListener("click", () => {
      if (!busy) {
        input.value = q;
        form.requestSubmit();
      }
    });
    suggestionsBox.appendChild(chip);
  }
}

async function sendMessage(message) {
  busy = true;
  sendBtn.disabled = true;
  addMessage(message, "user");
  setSuggestions([]);
  const typing = addTyping();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();
    typing.remove();

    if (!res.ok) {
      addMessage(data.error || "Something went wrong. Please try again.", "bot");
      return;
    }

    const meta = data.matched
      ? `matched: “${data.matched_question}” · confidence ${(data.confidence * 100).toFixed(0)}%`
      : null;
    addMessage(data.answer, "bot", meta);
    setSuggestions(data.suggestions);
  } catch {
    typing.remove();
    addMessage("⚠️ Network error — is the Flask server running?", "bot");
  } finally {
    busy = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message || busy) return;
  input.value = "";
  sendMessage(message);
});
