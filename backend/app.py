from __future__ import annotations

import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from agent import AgentLoopError, ChatAgent
from config import ConfigError, load_settings
from models import (
    AssistantMessageEvent,
    ChatMessage,
    ChatRequest,
    ChatStreamEvent,
    DoneEvent,
    ErrorEvent,
    SessionStartedEvent,
    ToolStreamEvent,
)
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


def _serialize_stream_event(event: ChatStreamEvent) -> str:
    return json.dumps(event.model_dump(), ensure_ascii=True) + "\n"


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat")
def chat(request: ChatRequest) -> StreamingResponse:
    state = session_store.get_or_create(request.sessionId, seed_messages=_seed_messages(request.history))
    state.messages.append({"role": "user", "content": request.message})

    def event_stream():
        yield _serialize_stream_event(
            SessionStartedEvent(type="session_started", sessionId=state.session_id)
        )

        stream = chat_agent.stream_turn(
            state.messages,
            state.loaded_skill_references,
        )

        while True:
            try:
                tool_event = next(stream)
            except StopIteration as stop:
                completion = stop.value
                state.messages = completion.messages
                state.loaded_skill_references = completion.loaded_skill_references
                session_store.save(state)
                yield _serialize_stream_event(
                    AssistantMessageEvent(type="assistant_message", reply=completion.reply)
                )
                yield _serialize_stream_event(DoneEvent(type="done"))
                break
            except (AgentLoopError, ConfigError) as exc:
                yield _serialize_stream_event(ErrorEvent(type="error", message=str(exc)))
                yield _serialize_stream_event(DoneEvent(type="done"))
                break
            except Exception:  # noqa: BLE001
                yield _serialize_stream_event(
                    ErrorEvent(
                        type="error",
                        message="The chat service failed to process the request.",
                    )
                )
                yield _serialize_stream_event(DoneEvent(type="done"))
                break
            else:
                yield _serialize_stream_event(ToolStreamEvent(type="tool_event", event=tool_event))

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


if settings.web_root.exists():
    app.mount("/assets", StaticFiles(directory=settings.web_root), name="assets")


@app.get("/")
def index() -> FileResponse:
    index_path = settings.web_root / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found.")
    return FileResponse(index_path)
