from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SessionState:
    session_id: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    updated_at: float = field(default_factory=time.time)


class SessionStore:
    def __init__(self, ttl_seconds: int) -> None:
        self._ttl_seconds = ttl_seconds
        self._sessions: dict[str, SessionState] = {}

    def _prune(self) -> None:
        now = time.time()
        expired = [
            session_id
            for session_id, state in self._sessions.items()
            if now - state.updated_at > self._ttl_seconds
        ]
        for session_id in expired:
            self._sessions.pop(session_id, None)

    def get_or_create(
        self,
        session_id: Optional[str],
        seed_messages: Optional[List[Dict[str, Any]]] = None,
    ) -> SessionState:
        self._prune()
        if session_id and session_id in self._sessions:
            state = self._sessions[session_id]
            state.updated_at = time.time()
            return state

        new_session_id = session_id or uuid.uuid4().hex
        state = SessionState(session_id=new_session_id, messages=list(seed_messages or []))
        self._sessions[new_session_id] = state
        return state

    def save(self, state: SessionState) -> None:
        state.updated_at = time.time()
        self._sessions[state.session_id] = state
