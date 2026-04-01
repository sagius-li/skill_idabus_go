from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

import app as backend_app
from agent import AgentLoopError, TurnCompletion
from models import ToolEvent
from session_store import SessionStore


class _SuccessStreamingAgent:
    def stream_turn(self, messages, loaded_references=None):
        yield ToolEvent(type="status", message="Using Idabus tool: get-resource-by-id")
        return TurnCompletion(
            messages=[
                *messages,
                {"role": "assistant", "content": "Final streamed reply"},
            ],
            reply="Final streamed reply",
            loaded_skill_references=dict(loaded_references or {}),
        )


class _FailingStreamingAgent:
    def stream_turn(self, messages, loaded_references=None):
        if False:
            yield ToolEvent(type="status", message="unused")
        raise AgentLoopError("Too many tool steps.")


class StreamingChatEndpointTests(unittest.TestCase):
    def test_chat_stream_emits_ordered_events_and_persists_final_state(self) -> None:
        with patch.object(backend_app, "chat_agent", _SuccessStreamingAgent()), patch.object(
            backend_app,
            "session_store",
            SessionStore(ttl_seconds=3600),
        ):
            client = TestClient(backend_app.app)

            with client.stream(
                "POST",
                "/api/chat",
                json={"message": "Check resource", "history": []},
            ) as response:
                self.assertEqual(response.status_code, 200)
                events = [json.loads(line) for line in response.iter_lines() if line]

            self.assertEqual(events[0]["type"], "session_started")
            self.assertEqual(events[1]["type"], "tool_event")
            self.assertEqual(events[2]["type"], "assistant_message")
            self.assertEqual(events[3]["type"], "done")

            session_id = events[0]["sessionId"]
            saved_state = backend_app.session_store._sessions[session_id]
            self.assertEqual(saved_state.messages[-1]["role"], "assistant")
            self.assertEqual(saved_state.messages[-1]["content"], "Final streamed reply")

    def test_chat_stream_emits_error_and_does_not_persist_assistant_reply(self) -> None:
        with patch.object(backend_app, "chat_agent", _FailingStreamingAgent()), patch.object(
            backend_app,
            "session_store",
            SessionStore(ttl_seconds=3600),
        ):
            client = TestClient(backend_app.app)

            with client.stream(
                "POST",
                "/api/chat",
                json={"message": "Check resource", "history": []},
            ) as response:
                self.assertEqual(response.status_code, 200)
                events = [json.loads(line) for line in response.iter_lines() if line]

            self.assertEqual(events[0]["type"], "session_started")
            self.assertEqual(events[1], {"type": "error", "message": "Too many tool steps."})
            self.assertEqual(events[2]["type"], "done")

            session_id = events[0]["sessionId"]
            saved_state = backend_app.session_store._sessions[session_id]
            self.assertEqual(saved_state.messages, [{"role": "user", "content": "Check resource"}])


if __name__ == "__main__":
    unittest.main()
