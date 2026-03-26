from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from config import Settings
from idabus_tool import ToolExecutionError, run_idabus_request
from models import ToolEvent


SYSTEM_PROMPT = """You are a helpful AI assistant inside a custom chat app.

You can answer directly or decide to use the idabus_request tool when the task requires Idabus API access.

When using Idabus:
- Use idabus_request when Idabus API work is required.
- Prefer endpoint_name over raw paths when the endpoint is known.
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

    def run_turn(self, messages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str, list[ToolEvent]]:
        working_messages = list(messages)
        tool_events: list[ToolEvent] = []

        for _ in range(self._settings.chat_max_tool_rounds):
            completion = self._client.chat.completions.create(
                model=self._settings.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
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
                return working_messages, reply, tool_events

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                except json.JSONDecodeError as exc:
                    raise AgentLoopError(f"Model returned invalid tool arguments for {tool_name}.") from exc

                if tool_name != "idabus_request":
                    raise AgentLoopError(f"Unsupported tool requested: {tool_name}")

                endpoint_name = arguments.get("endpoint_name") or arguments.get("path") or "custom request"
                tool_events.append(
                    ToolEvent(
                        type="status",
                        message=f"Using Idabus tool: {endpoint_name}",
                    )
                )

                try:
                    result = run_idabus_request(self._settings.idabus_root, arguments)
                    tool_output = _safe_json_dump(result)
                except ToolExecutionError as exc:
                    tool_events.append(
                        ToolEvent(
                            type="error",
                            message="Idabus request failed.",
                            details={"error": str(exc)},
                        )
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
