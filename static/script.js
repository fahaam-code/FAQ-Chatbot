/* Front-end logic for the Gemini AI Chatbot. */
"use strict";

const chatWindow = document.getElementById("chat-window");
const suggestionsBox = document.getElementById("suggestions");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");

// Modal elements
const apiKeyBtn = document.getElementById("api-key-btn");
const apiModal = document.getElementById("api-modal");
const closeModalBtn = document.getElementById("close-modal-btn");
const geminiKeyInput = document.getElementById("gemini-key-input");
const saveKeyBtn = document.getElementById("save-key-btn");
const modalMsg = document.getElementById("modal-msg");
const geminiDot = document.getElementById("gemini-dot");
const geminiStatusText = document.getElementById("gemini-status-text");

let busy = false;
const conversationHistory = [];

function scrollDown() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function formatMarkdown(text) {
  if (!text) return "";
  // Escape HTML characters
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Code blocks: ```language ... ```
  html = html.replace(/```([a-zA-Z0-9_]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    return `<pre><code class="code-block">${code.trim()}</code></pre>`;
  });

  // Inline code `code`
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Bold **text**
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  // Italic *text*
  html = html.replace(/(^|[^*])\*([^*]+?)\*([^*]|$)/g, "$1<em>$2</em>$3");

  // Lists
  const lines = html.split("\n");
  let inList = false;
  const processed = [];

  for (let line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
      if (!inList) {
        processed.push("<ul class='msg-list'>");
        inList = true;
      }
      processed.push(`<li>${trimmed.substring(2)}</li>`);
    } else {
      if (inList) {
        processed.push("</ul>");
        inList = false;
      }
      processed.push(line);
    }
  }
  if (inList) {
    processed.push("</ul>");
  }

  return processed.join("<br/>")
    .replace(/<\/ul><br\/>/g, "</ul>")
    .replace(/<br\/><ul/g, "<ul")
    .replace(/<\/pre><br\/>/g, "</pre>")
    .replace(/<br\/><pre/g, "<pre");
}

function addMessage(text, who, engine) {
  const div = document.createElement("div");
  div.className = `msg ${who}`;

  const bodyEl = document.createElement("div");
  bodyEl.className = "msg-text";
  if (who === "bot") {
    bodyEl.innerHTML = formatMarkdown(text);
  } else {
    bodyEl.textContent = text;
  }
  div.appendChild(bodyEl);

  if (engine && who === "bot") {
    const metaEl = document.createElement("span");
    metaEl.className = "meta";
    const badge = document.createElement("span");
    badge.className = "engine-badge";
    badge.textContent = engine;
    metaEl.appendChild(badge);
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
      body: JSON.stringify({
        message,
        history: conversationHistory.slice(-12),
      }),
    });
    const data = await res.json();
    typing.remove();

    if (!res.ok) {
      addMessage(data.error || "Something went wrong. Please try again.", "bot");
      return;
    }

    addMessage(data.answer, "bot", data.engine);

    // Save to conversation memory
    conversationHistory.push({ role: "user", content: message });
    conversationHistory.push({ role: "model", content: data.answer });
  } catch {
    typing.remove();
    addMessage("⚠️ Network error — is the server running?", "bot");
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

// Modal Logic
if (apiKeyBtn && apiModal) {
  apiKeyBtn.addEventListener("click", () => {
    modalMsg.textContent = "";
    modalMsg.className = "modal-msg";
    geminiKeyInput.value = "";
    apiModal.classList.remove("hidden");
    geminiKeyInput.focus();
  });

  closeModalBtn.addEventListener("click", () => {
    apiModal.classList.add("hidden");
  });

  apiModal.addEventListener("click", (e) => {
    if (e.target === apiModal) {
      apiModal.classList.add("hidden");
    }
  });

  saveKeyBtn.addEventListener("click", async () => {
    const key = geminiKeyInput.value.trim();
    if (!key) {
      modalMsg.textContent = "Please enter a valid API key.";
      modalMsg.className = "modal-msg error";
      return;
    }

    saveKeyBtn.disabled = true;
    modalMsg.textContent = "Validating and saving key...";
    modalMsg.className = "modal-msg";

    try {
      const res = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gemini_api_key: key }),
      });
      const data = await res.json();

      if (!res.ok) {
        modalMsg.textContent = data.error || "Failed to save API key.";
        modalMsg.className = "modal-msg error";
        return;
      }

      modalMsg.textContent = "Gemini API activated successfully! 🚀";
      modalMsg.className = "modal-msg success";
      geminiDot.classList.add("active");
      geminiStatusText.textContent = "Gemini Active";

      setTimeout(() => {
        apiModal.classList.add("hidden");
      }, 1200);
    } catch {
      modalMsg.textContent = "Network error while saving key.";
      modalMsg.className = "modal-msg error";
    } finally {
      saveKeyBtn.disabled = false;
    }
  });
}

// Initial status check
fetch("/api/status")
  .then((res) => res.json())
  .then((data) => {
    if (data.gemini_active) {
      geminiDot.classList.add("active");
      geminiStatusText.textContent = "Gemini Active";
    } else {
      geminiDot.classList.remove("active");
      geminiStatusText.textContent = "Set Gemini Key";
    }
  })
  .catch(() => {});

// Load initial starter suggestions
const initSuggestionsEl = document.getElementById("initial-suggestions");
if (initSuggestionsEl) {
  try {
    const initialSuggestions = JSON.parse(initSuggestionsEl.textContent);
    if (Array.isArray(initialSuggestions) && initialSuggestions.length > 0) {
      setSuggestions(initialSuggestions);
    }
  } catch (err) {
    console.error("Failed to parse initial suggestions", err);
  }
}
