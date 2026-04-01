from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent import ChatAgent, SkillReferenceError, build_system_prompt, load_skill_reference
from config import Settings
from idabus_tool import ToolExecutionError


class SkillReferenceLoadingTests(unittest.TestCase):
    def _make_settings(self, root: Path) -> Settings:
        backend_root = root / "backend"
        web_root = root / "web"
        backend_root.mkdir()
        web_root.mkdir()
        return Settings(
            app_root=root,
            backend_root=backend_root,
            web_root=web_root,
            idabus_root=root / "idabus-go",
            openai_api_key="test-key",
            openai_model="gpt-4.1-mini",
            chat_max_tool_rounds=8,
            session_ttl_seconds=3600,
        )

    def _write_skill_fixture(self, root: Path) -> None:
        idabus_root = root / "idabus-go"
        references_root = idabus_root / "references"
        references_root.mkdir(parents=True)
        (references_root / "api_spec.json").write_text(
            json.dumps(
                {
                    "endpoints": [
                        {
                            "name": "get-resource-by-id",
                            "method": "GET",
                            "path": "/resources/{id}",
                            "description": "Fetch one resource.",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        (idabus_root / "SKILL.md").write_text(
            "\n".join(
                [
                    "# Idabus",
                    "Use `references/object_types_and_attributes.md` when object details are needed.",
                    "Use `references/idabus_xpath_dialect.md` for XPath syntax.",
                ]
            ),
            encoding="utf-8",
        )
        (references_root / "object_types_and_attributes.md").write_text(
            "object reference content",
            encoding="utf-8",
        )
        (references_root / "idabus_xpath_dialect.md").write_text(
            "xpath reference content",
            encoding="utf-8",
        )
        (references_root / "not_mentioned.md").write_text(
            "should not load",
            encoding="utf-8",
        )

    def test_load_skill_reference_succeeds_for_referenced_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_skill_fixture(root)

            path, content = load_skill_reference(
                root / "idabus-go",
                "references/object_types_and_attributes.md",
            )

            self.assertEqual(path, "references/object_types_and_attributes.md")
            self.assertEqual(content, "object reference content")

    def test_load_skill_reference_rejects_unmentioned_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_skill_fixture(root)

            with self.assertRaises(SkillReferenceError):
                load_skill_reference(root / "idabus-go", "references/not_mentioned.md")

    def test_load_skill_reference_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_skill_fixture(root)

            with self.assertRaises(SkillReferenceError):
                load_skill_reference(root / "idabus-go", "../backend/config.py")

    def test_build_system_prompt_includes_loaded_references_once_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_skill_fixture(root)
            settings = self._make_settings(root)

            prompt = build_system_prompt(
                settings,
                {"references/object_types_and_attributes.md": "object reference content"},
            )

            self.assertIn("Local skill instructions:", prompt)
            self.assertIn("Loaded local references:", prompt)
            self.assertIn("references/object_types_and_attributes.md", prompt)
            self.assertIn("object reference content", prompt)


class _FakeOpenAIClient:
    def __init__(self, messages: list[object]) -> None:
        self._messages = list(messages)
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create_completion),
        )

    def _create_completion(self, **_: object) -> object:
        message = self._messages.pop(0)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class ChatAgentStreamingTests(unittest.TestCase):
    def _make_settings(self, root: Path) -> Settings:
        backend_root = root / "backend"
        web_root = root / "web"
        backend_root.mkdir()
        web_root.mkdir()
        return Settings(
            app_root=root,
            backend_root=backend_root,
            web_root=web_root,
            idabus_root=root / "idabus-go",
            openai_api_key="test-key",
            openai_model="gpt-4.1-mini",
            chat_max_tool_rounds=8,
            session_ttl_seconds=3600,
        )

    def _write_skill_fixture(self, root: Path) -> None:
        idabus_root = root / "idabus-go"
        references_root = idabus_root / "references"
        references_root.mkdir(parents=True)
        (references_root / "api_spec.json").write_text(json.dumps({"endpoints": []}), encoding="utf-8")
        (idabus_root / "SKILL.md").write_text("# Idabus", encoding="utf-8")

    def test_stream_turn_yields_tool_events_before_final_reply(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_skill_fixture(root)
            agent = ChatAgent(self._make_settings(root))
            agent._client = _FakeOpenAIClient(
                [
                    SimpleNamespace(
                        content="",
                        tool_calls=[
                            SimpleNamespace(
                                id="call-1",
                                type="function",
                                function=SimpleNamespace(
                                    name="idabus_request",
                                    arguments=json.dumps({"endpoint_name": "get-resource-by-id"}),
                                ),
                            )
                        ],
                    ),
                    SimpleNamespace(
                        content="Tool result complete.",
                        tool_calls=[],
                    ),
                ]
            )

            with patch("agent.run_idabus_request", return_value={"ok": True}):
                stream = agent.stream_turn([{"role": "user", "content": "Check resource"}])
                first_event = next(stream)

                self.assertEqual(first_event.type, "status")
                self.assertEqual(first_event.message, "Using Idabus tool: get-resource-by-id")

                with self.assertRaises(StopIteration) as stop:
                    next(stream)

            completion = stop.exception.value
            self.assertEqual(completion.reply, "Tool result complete.")
            self.assertEqual(completion.messages[-1]["role"], "assistant")

    def test_stream_turn_yields_tool_error_and_continues(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_skill_fixture(root)
            agent = ChatAgent(self._make_settings(root))
            agent._client = _FakeOpenAIClient(
                [
                    SimpleNamespace(
                        content="",
                        tool_calls=[
                            SimpleNamespace(
                                id="call-1",
                                type="function",
                                function=SimpleNamespace(
                                    name="idabus_request",
                                    arguments=json.dumps({"path": "/custom"}),
                                ),
                            )
                        ],
                    ),
                    SimpleNamespace(
                        content="I handled the tool failure.",
                        tool_calls=[],
                    ),
                ]
            )

            with patch("agent.run_idabus_request", side_effect=ToolExecutionError("boom")):
                stream = agent.stream_turn([{"role": "user", "content": "Call custom"}])
                error_event = next(stream)

                self.assertEqual(error_event.type, "error")
                self.assertEqual(error_event.message, "Idabus request failed.")
                self.assertEqual(error_event.details, {"error": "boom"})

                with self.assertRaises(StopIteration) as stop:
                    next(stream)

            completion = stop.exception.value
            self.assertEqual(completion.reply, "I handled the tool failure.")


if __name__ == "__main__":
    unittest.main()
