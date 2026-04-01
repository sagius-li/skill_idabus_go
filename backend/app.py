from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from agent import AgentLoopError, ChatAgent
from config import ConfigError, load_settings
from models import ChatMessage, ChatRequest, ChatResponse
from session_store import SessionStore


settings = load_settings()
session_store = SessionStore(ttl_seconds=settings.session_ttl_seconds)
chat_agent = ChatAgent(settings)

app = FastAPI(title="Idabus Chat Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _seed_messages(history: list[ChatMessage]) -> list[dict[str, str]]:
    return [{"role": message.role, "content": message.content} for message in history]


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    state = session_store.get_or_create(request.sessionId, seed_messages=_seed_messages(request.history))
    state.messages.append({"role": "user", "content": request.message})

    try:
        updated_messages, reply, tool_events, loaded_skill_references = chat_agent.run_turn(
            state.messages,
            state.loaded_skill_references,
        )
    except (AgentLoopError, ConfigError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="The chat service failed to process the request.") from exc

    state.messages = updated_messages
    state.loaded_skill_references = loaded_skill_references
    session_store.save(state)
    return ChatResponse(sessionId=state.session_id, reply=reply, toolEvents=tool_events)


if settings.web_root.exists():
    app.mount("/assets", StaticFiles(directory=settings.web_root), name="assets")


@app.get("/")
def index() -> FileResponse:
    index_path = settings.web_root / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found.")
    return FileResponse(index_path)
