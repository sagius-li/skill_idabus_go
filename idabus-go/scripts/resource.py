#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib import error, parse, request

from auth import acquire_access_token
from env_utils import ConfigError, default_env_path, get_int_env, load_dotenv, require_env


SUPPORTED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def default_spec_path() -> Path:
    return Path(__file__).resolve().parents[1] / "references" / "api_spec.json"


def load_api_spec(spec_path: Path) -> dict:
    if not spec_path.exists():
        raise ConfigError(f"API specification file not found: {spec_path}")
    try:
        spec = json.loads(spec_path.read_text())
    except json.JSONDecodeError as exc:
        raise ConfigError(f"API specification file is not valid JSON: {spec_path}") from exc
    if not isinstance(spec, dict):
        raise ConfigError(f"API specification file must contain a JSON object: {spec_path}")
    return spec


def resolve_endpoint(spec: dict, endpoint_name: str) -> dict:
    endpoints = spec.get("endpoints", [])
    if not isinstance(endpoints, list):
        raise ConfigError("API specification field 'endpoints' must be a list.")
    for endpoint in endpoints:
        if isinstance(endpoint, dict) and endpoint.get("name") == endpoint_name:
            return endpoint
    raise ConfigError(f"Endpoint '{endpoint_name}' was not found in the API specification.")


def parse_key_value_pairs(raw_items: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_item in raw_items:
        if "=" not in raw_item:
            raise ConfigError(f"Invalid key=value argument: {raw_item}")
        key, value = raw_item.split("=", 1)
        key = key.strip()
        if not key:
            raise ConfigError(f"Invalid key=value argument: {raw_item}")
        result[key] = value
    return result


def apply_path_params(path_template: str, path_params: dict[str, str]) -> str:
    try:
        return path_template.format(**{key: parse.quote(value, safe="") for key, value in path_params.items()})
    except KeyError as exc:
        raise ConfigError(f"Missing path parameter for template placeholder: {exc.args[0]}") from exc


def build_url(path: str, query_params: dict[str, str]) -> str:
    base_url = require_env("IDABUS_API_BASE_URL").rstrip("/")
    normalized_path = path if path.startswith("/") else f"/{path}"
    url = f"{base_url}{normalized_path}"
    if query_params:
        url = f"{url}?{parse.urlencode(query_params)}"
    return url


def build_body(args: argparse.Namespace) -> tuple[bytes | None, str | None]:
    if args.json and args.body_file:
        raise ConfigError("Use either --json or --body-file, not both.")

    if args.json:
        try:
            payload = json.loads(args.json)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"--json is not valid JSON: {exc}") from exc
        return json.dumps(payload).encode("utf-8"), "application/json"

    if args.body_file:
        body_path = Path(args.body_file)
        if not body_path.exists():
            raise ConfigError(f"Body file not found: {body_path}")
        content_type = args.content_type or "application/json"
        return body_path.read_bytes(), content_type

    return None, None


def execute_request(
    method: str,
    path: str,
    query_params: dict[str, str],
    headers: dict[str, str],
    body: bytes | None,
    content_type: str | None,
    timeout: int,
) -> tuple[int, object]:
    url = build_url(path, query_params)
    token = acquire_access_token()
    final_headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        **headers,
    }
    if content_type and "Content-Type" not in final_headers:
        final_headers["Content-Type"] = content_type

    http_request = request.Request(
        url,
        headers=final_headers,
        data=body,
        method=method,
    )

    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
            return response.status, json.loads(payload) if payload else {}
    except error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        detail = payload or exc.reason
        raise ConfigError(f"API request failed with HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise ConfigError(f"API request failed: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"API response was not valid JSON: {exc}") from exc


def write_output(output_path: Path, payload: object) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n")


def resolve_request_from_args(args: argparse.Namespace) -> tuple[str, str]:
    method = args.method.upper()
    path = args.path or ""

    if args.endpoint_name:
        spec_path = Path(args.spec_file)
        if not spec_path.is_absolute():
            spec_path = Path.cwd() / spec_path
        spec = load_api_spec(spec_path)
        endpoint = resolve_endpoint(spec, args.endpoint_name)
        spec_method = str(endpoint.get("method", "")).upper()
        spec_path_value = str(endpoint.get("path", ""))
        if spec_method not in SUPPORTED_METHODS:
            raise ConfigError(f"Endpoint '{args.endpoint_name}' has an unsupported method in the specification.")
        if not spec_path_value:
            raise ConfigError(f"Endpoint '{args.endpoint_name}' does not define a path in the specification.")
        method = spec_method if args.method == "GET" else method
        path = spec_path_value if not args.path else args.path

    if method not in SUPPORTED_METHODS:
        supported = ", ".join(sorted(SUPPORTED_METHODS))
        raise ConfigError(f"Unsupported HTTP method '{method}'. Supported values: {supported}")
    if not path:
        raise ConfigError("Provide either --path or --endpoint-name.")

    path_params = parse_key_value_pairs(args.path_param)
    return method, apply_path_params(path, path_params)


def main() -> int:
    parser = argparse.ArgumentParser(description="Send an authenticated HTTP request to the configured API.")
    parser.add_argument("--method", default="GET", help="HTTP method: GET, POST, PUT, PATCH, or DELETE.")
    parser.add_argument("--path", help="Relative API path, for example /resources/123.")
    parser.add_argument("--endpoint-name", help="Endpoint name from the API specification file.")
    parser.add_argument("--spec-file", default=str(default_spec_path()), help="Path to the API specification JSON file.")
    parser.add_argument("--path-param", action="append", default=[], help="Path parameter in key=value form.")
    parser.add_argument("--query", action="append", default=[], help="Query parameter in key=value form.")
    parser.add_argument("--header", action="append", default=[], help="Additional HTTP header in key=value form.")
    parser.add_argument("--json", help="Inline JSON request body.")
    parser.add_argument("--body-file", help="Path to a file used as the request body.")
    parser.add_argument("--content-type", help="Content-Type header for --body-file.")
    parser.add_argument("--output", help="Optional path to save the JSON payload.")
    parser.add_argument("--env-file", default=str(default_env_path()), help="Path to the .env file.")
    parser.add_argument("--timeout", type=int, help="HTTP timeout in seconds.")
    args = parser.parse_args()

    env_file = Path(args.env_file)
    if not env_file.is_absolute():
        env_file = Path.cwd() / env_file

    try:
        load_dotenv(env_file)
        timeout = args.timeout if args.timeout is not None else get_int_env("IDABUS_API_TIMEOUT", 30)
        query_params = parse_key_value_pairs(args.query)
        headers = parse_key_value_pairs(args.header)
        method, path = resolve_request_from_args(args)
        body, content_type = build_body(args)
        _, payload = execute_request(method, path, query_params, headers, body, content_type, timeout)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    rendered = json.dumps(payload, indent=2)
    print(rendered)

    if args.output:
        write_output(Path(args.output), payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
