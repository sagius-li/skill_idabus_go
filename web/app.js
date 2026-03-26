const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const messages = document.getElementById("messages");
const statusNode = document.getElementById("status");
const sendButton = document.getElementById("send-button");

const SESSION_KEY = "idabus-chat-session-id";
let sessionId = window.localStorage.getItem(SESSION_KEY) || null;
const history = [];

function setStatus(text) {
  statusNode.textContent = text;
}

function appendMessage(role, content) {
  const node = document.createElement("article");
  node.className = `message ${role}`;
  node.textContent = content;
  messages.appendChild(node);
  messages.scrollTop = messages.scrollHeight;
}

function setBusy(isBusy) {
  sendButton.disabled = isBusy;
  input.disabled = isBusy;
}

appendMessage(
  "assistant",
  "Ask anything. I can answer directly or use the Idabus integration when the task needs it."
);

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) {
    return;
  }

  appendMessage("user", message);
  history.push({ role: "user", content: message });
  input.value = "";
  setBusy(true);
  setStatus("Thinking...");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sessionId,
        message,
        history,
      }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Request failed.");
    }

    sessionId = payload.sessionId;
    window.localStorage.setItem(SESSION_KEY, sessionId);

    for (const eventItem of payload.toolEvents || []) {
      appendMessage("tool", eventItem.message);
    }

    appendMessage("assistant", payload.reply);
    history.push({ role: "assistant", content: payload.reply });
    setStatus("Ready");
  } catch (error) {
    const messageText = error instanceof Error ? error.message : "Request failed.";
    appendMessage("tool", `Error: ${messageText}`);
    setStatus("Error");
  } finally {
    setBusy(false);
    input.focus();
  }
});
