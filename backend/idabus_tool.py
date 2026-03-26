from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class ToolExecutionError(RuntimeError):
    pass


def _append_mapping_args(command: List[str], flag_name: str, mapping: Optional[Dict[str, Any]]) -> None:
    if not mapping:
        return
    for key, value in mapping.items():
        command.extend([flag_name, f"{key}={value}"])


def _stringify_body(json_body: Any) -> str:
    try:
        return json.dumps(json_body)
    except TypeError as exc:
        raise ToolExecutionError("Tool json_body must be JSON serializable.") from exc


def run_idabus_request(idabus_root: Path, arguments: Dict[str, Any]) -> Dict[str, Any]:
    endpoint_name = arguments.get("endpoint_name")
    method = arguments.get("method", "GET")
    path = arguments.get("path")
    path_params = arguments.get("path_params")
    query_params = arguments.get("query_params")
    headers = arguments.get("headers")
    json_body = arguments.get("json_body")

    if not endpoint_name and not path:
        raise ToolExecutionError("Provide either endpoint_name or path for idabus_request.")

    command = ["python3", "scripts/resource.py"]
    if endpoint_name:
        command.extend(["--endpoint-name", str(endpoint_name)])
    if method:
        command.extend(["--method", str(method)])
    if path:
        command.extend(["--path", str(path)])

    _append_mapping_args(command, "--path-param", path_params)
    _append_mapping_args(command, "--query", query_params)
    _append_mapping_args(command, "--header", headers)

    if json_body is not None:
        command.extend(["--json", _stringify_body(json_body)])

    completed = subprocess.run(
        command,
        cwd=idabus_root,
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "Unknown Idabus tool error."
        raise ToolExecutionError(stderr)

    stdout = completed.stdout.strip()
    if not stdout:
        return {}

    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ToolExecutionError("Idabus tool returned invalid JSON.") from exc
