from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any, Dict, Generator, List

from openai import OpenAI

from config import Settings
from idabus_tool import ToolExecutionError, run_idabus_request
from models import ToolEvent


BASE_SYSTEM_PROMPT = """You are a helpful AI assistant inside a custom chat app.

You can answer directly or decide to use the idabus_request tool when the task requires Idabus API access.

When using Idabus:
- Use idabus_request when Idabus API work is required.
- You always have the local SKILL.md instructions, but you do not automatically have the full contents of every referenced file.
- If SKILL.md mentions a local file and you need that file's contents, call load_skill_reference with the exact relative path written in SKILL.md instead of guessing.
- Only request local files that are explicitly referenced in SKILL.md.
- Prefer endpoint_name over raw paths whenever the endpoint exists in the local API catalog.
- Only use endpoint names that exist in the provided endpoint catalog. Do not invent endpoint names.
- Do not invent raw paths such as guessed REST endpoints when the local endpoint catalog does not list them.
- Keep reads narrow and request only the attributes needed for the task.
- For XPath-backed searches, prefer request-body XPath transport when the endpoint body supports it.
- For permission questions, use the relevant permission-check endpoint rather than assuming access.
- For mutating tasks, use simulation session behavior unless the user explicitly asks otherwise.
- Continue using the tool for multi-step tasks until the job is complete.
- Ask the user a follow-up only if required information is missing.
- Never reveal secrets, access tokens, or authorization headers.

Be concise and helpful in the final answer.
"""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "load_skill_reference",
            "description": "Load the contents of a local file that is explicitly referenced in the idabus-go SKILL.md.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reference_path": {"type": "string"},
                },
                "required": ["reference_path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "idabus_request",
            "description": "Run an authenticated Idabus API request using the local idabus-go skill.",
            "parameters": {
                "type": "object",
                "properties": {
                    "endpoint_name": {"type": "string"},
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                    },
                    "path": {"type": "string"},
                    "path_params": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                    },
                    "query_params": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                    },
                    "headers": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                    },
                    "json_body": {},
                },
                "additionalProperties": False,
            },
        },
    }
]


class AgentLoopError(RuntimeError):
    pass


class SkillReferenceError(RuntimeError):
    pass


@dataclass
class TurnCompletion:
    messages: list[dict[str, Any]]
    reply: str
    loaded_skill_references: dict[str, str]


REFERENCE_PATH_PATTERN = re.compile(r"`([^`\n]+(?:/[^`\n]+)+)`")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _load_endpoint_catalog(idabus_root: Path) -> str:
    spec_path = idabus_root / "references" / "api_spec.json"
    spec = json.loads(_read_text(spec_path))
    endpoints = spec.get("endpoints", [])
    lines: List[str] = []
    for endpoint in endpoints:
        if not isinstance(endpoint, dict):
            continue
        name = str(endpoint.get("name", "")).strip()
        method = str(endpoint.get("method", "")).strip()
        path = str(endpoint.get("path", "")).strip()
        description = str(endpoint.get("description", "")).strip()
        if not name:
            continue
        summary = f"- {name}: {method} {path}"
        if description:
            summary = f"{summary} - {description}"
        lines.append(summary)
    return "\n".join(lines)


def _extract_skill_reference_paths(skill_text: str) -> set[str]:
    references: set[str] = set()
    for match in REFERENCE_PATH_PATTERN.findall(skill_text):
        candidate = match.strip()
        if not candidate or candidate.startswith("/"):
            continue
        if " " in candidate or "\t" in candidate or "\n" in candidate:
            continue
        references.add(candidate)
    return references


def _normalize_reference_path(reference_path: str) -> str:
    candidate = reference_path.strip()
    if not candidate:
        raise SkillReferenceError("Reference path must not be empty.")

    path = PurePosixPath(candidate)
    if path.is_absolute():
        raise SkillReferenceError("Reference path must be relative to idabus-go.")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise SkillReferenceError("Reference path must not contain path traversal.")

    normalized = path.as_posix()
    if normalized == ".":
        raise SkillReferenceError("Reference path must point to a file.")
    return normalized


def load_skill_reference(idabus_root: Path, reference_path: str) -> tuple[str, str]:
    skill_text = _read_text(idabus_root / "SKILL.md")
    normalized_path = _normalize_reference_path(reference_path)
    allowed_references = _extract_skill_reference_paths(skill_text)
    if normalized_path not in allowed_references:
        raise SkillReferenceError(
            f"Reference path is not explicitly mentioned in SKILL.md: {normalized_path}"
        )

    root = idabus_root.resolve()
    resolved_path = (root / normalized_path).resolve()
    try:
        resolved_path.relative_to(root)
    except ValueError as exc:
        raise SkillReferenceError("Reference path must stay inside idabus-go.") from exc

    if not resolved_path.is_file():
        raise SkillReferenceError(f"Referenced file was not found: {normalized_path}")

    return normalized_path, _read_text(resolved_path)


def build_system_prompt(settings: Settings, loaded_references: dict[str, str] | None = None) -> str:
    skill_text = _read_text(settings.idabus_root / "SKILL.md")
    endpoint_catalog = _load_endpoint_catalog(settings.idabus_root)
    prompt = (
        f"{BASE_SYSTEM_PROMPT}\n\n"
        "Local endpoint catalog:\n"
        f"{endpoint_catalog}\n\n"
        "Local skill instructions:\n"
        f"{skill_text}\n"
    )
    if loaded_references:
        sections = [
            f"Local referenced file: {path}\n{content}"
            for path, content in loaded_references.items()
        ]
        prompt = f"{prompt}\nLoaded local references:\n\n" + "\n\n".join(sections) + "\n"
    return prompt


def _extract_text(message: Any) -> str:
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    if not content:
        return ""

    parts: list[str] = []
    for item in content:
        if isinstance(item, dict):
            text = item.get("text")
            if isinstance(text, str):
                parts.append(text)
            continue
        text = getattr(item, "text", None)
        if isinstance(text, str):
            parts.append(text)
    return "\n".join(part for part in parts if part).strip()


def _assistant_message_payload(message: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "role": "assistant",
        "content": _extract_text(message),
    }
    tool_calls = getattr(message, "tool_calls", None) or []
    if tool_calls:
        payload["tool_calls"] = [
            {
                "id": call.id,
                "type": call.type,
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                },
            }
            for call in tool_calls
        ]
    return payload


def _safe_json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True)


class ChatAgent:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = OpenAI(api_key=settings.openai_api_key)

    def stream_turn(
        self,
        messages: list[dict[str, Any]],
        loaded_references: dict[str, str] | None = None,
    ) -> Generator[ToolEvent, None, TurnCompletion]:
        working_messages = list(messages)
        active_references = dict(loaded_references or {})

        for _ in range(self._settings.chat_max_tool_rounds):
            completion = self._client.chat.completions.create(
                model=self._settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": build_system_prompt(self._settings, active_references),
                    },
                    *working_messages,
                ],
                tools=TOOLS,
                tool_choice="auto",
            )

            message = completion.choices[0].message
            assistant_payload = _assistant_message_payload(message)
            working_messages.append(assistant_payload)

            tool_calls = getattr(message, "tool_calls", None) or []
            if not tool_calls:
                reply = _extract_text(message) or "I couldn't produce a response."
                return TurnCompletion(
                    messages=working_messages,
                    reply=reply,
                    loaded_skill_references=active_references,
                )

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                except json.JSONDecodeError as exc:
                    raise AgentLoopError(f"Model returned invalid tool arguments for {tool_name}.") from exc

                if tool_name == "load_skill_reference":
                    reference_path = arguments.get("reference_path", "")
                    try:
                        normalized_path, content = load_skill_reference(
                            self._settings.idabus_root,
                            str(reference_path),
                        )
                        active_references[normalized_path] = content
                        tool_output = _safe_json_dump(
                            {
                                "reference_path": normalized_path,
                                "status": "loaded",
                            }
                        )
                    except SkillReferenceError as exc:
                        tool_output = _safe_json_dump({"error": str(exc)})
                    working_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_output,
                        }
                    )
                    continue

                if tool_name != "idabus_request":
                    raise AgentLoopError(f"Unsupported tool requested: {tool_name}")

                endpoint_name = arguments.get("endpoint_name") or arguments.get("path") or "custom request"

                try:
                    result = run_idabus_request(self._settings.idabus_root, arguments)
                    tool_output = _safe_json_dump(result)
                    yield ToolEvent(
                        type="status",
                        message=f"Using Idabus tool: {endpoint_name}",
                    )
                except ToolExecutionError as exc:
                    yield ToolEvent(
                        type="error",
                        message="Idabus request failed.",
                        details={"error": str(exc)},
                    )
                    tool_output = _safe_json_dump({"error": str(exc)})

                working_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_output,
                    }
                )

        raise AgentLoopError(
            "The assistant needed too many tool steps for this request. Please narrow the task and try again."
        )

    def run_turn(
        self,
        messages: list[dict[str, Any]],
        loaded_references: dict[str, str] | None = None,
    ) -> tuple[list[dict[str, Any]], str, list[ToolEvent], dict[str, str]]:
        stream = self.stream_turn(messages, loaded_references)
        tool_events: list[ToolEvent] = []

        while True:
            try:
                tool_events.append(next(stream))
            except StopIteration as stop:
                completion = stop.value
                break

        return (
            completion.messages,
            completion.reply,
            tool_events,
            completion.loaded_skill_references,
        )
