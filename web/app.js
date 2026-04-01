const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const messages = document.getElementById("messages");
const statusNode = document.getElementById("status");
const sendButton = document.getElementById("send-button");

const SESSION_KEY = "idabus-chat-session-id";
let sessionId = window.localStorage.getItem(SESSION_KEY) || null;
const history = [];

function getErrorMessage(payload, fallback) {
  if (!payload) {
    return fallback;
  }

  if (typeof payload.detail === "string") {
    return payload.detail;
  }

  return fallback;
}

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

function handleStreamEvent(eventItem) {
  switch (eventItem.type) {
    case "session_started":
      sessionId = eventItem.sessionId;
      window.localStorage.setItem(SESSION_KEY, sessionId);
      break;
    case "tool_event":
      appendMessage("tool", eventItem.event.message);
      setStatus("Working...");
      break;
    case "assistant_message":
      appendMessage("assistant", eventItem.reply);
      history.push({ role: "assistant", content: eventItem.reply });
      break;
    case "error":
      appendMessage("tool", `Error: ${eventItem.message}`);
      setStatus("Error");
      break;
    case "done":
      if (statusNode.textContent !== "Error") {
        setStatus("Ready");
      }
      break;
    default:
      break;
  }
}

async function consumeChatStream(response) {
  if (!response.body) {
    throw new Error("Streaming is not supported in this browser.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });

    let newlineIndex = buffer.indexOf("\n");
    while (newlineIndex !== -1) {
      const line = buffer.slice(0, newlineIndex).trim();
      buffer = buffer.slice(newlineIndex + 1);

      if (line) {
        handleStreamEvent(JSON.parse(line));
      }

      newlineIndex = buffer.indexOf("\n");
    }

    if (done) {
      break;
    }
  }

  const tail = buffer.trim();
  if (tail) {
    handleStreamEvent(JSON.parse(tail));
  }
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

    if (!response.ok) {
      let payload = null;
      try {
        payload = await response.json();
      } catch {
        payload = null;
      }
      throw new Error(getErrorMessage(payload, "Request failed."));
    }

    await consumeChatStream(response);
  } catch (error) {
    const messageText = error instanceof Error ? error.message : "Request failed.";
    appendMessage("tool", `Error: ${messageText}`);
    setStatus("Error");
  } finally {
    setBusy(false);
    input.focus();
  }
});
