from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    sessionId: Optional[str] = None
    history: List[ChatMessage] = Field(default_factory=list)


class ToolEvent(BaseModel):
    type: Literal["status", "error"]
    message: str
    details: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    sessionId: str
    reply: str
    toolEvents: List[ToolEvent] = Field(default_factory=list)


class SessionStartedEvent(BaseModel):
    type: Literal["session_started"]
    sessionId: str


class ToolStreamEvent(BaseModel):
    type: Literal["tool_event"]
    event: ToolEvent


class AssistantMessageEvent(BaseModel):
    type: Literal["assistant_message"]
    reply: str


class ErrorEvent(BaseModel):
    type: Literal["error"]
    message: str


class DoneEvent(BaseModel):
    type: Literal["done"]


ChatStreamEvent = Union[
    SessionStartedEvent,
    ToolStreamEvent,
    AssistantMessageEvent,
    ErrorEvent,
    DoneEvent,
]
