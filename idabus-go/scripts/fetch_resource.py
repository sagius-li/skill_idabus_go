#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib import error, parse, request

from auth import acquire_access_token
from env_utils import ConfigError, default_env_path, get_int_env, load_dotenv, require_env


def build_resource_url(resource_id: str) -> str:
    base_url = require_env("IDABUS_API_BASE_URL").rstrip("/")
    template = os.getenv("IDABUS_RESOURCE_PATH_TEMPLATE", "/resources/{resource_id}")
    resource_path = template.format(resource_id=parse.quote(resource_id, safe=""))
    return f"{base_url}{resource_path}"


def fetch_json(resource_id: str, timeout: int) -> tuple[int, object]:
    url = build_resource_url(resource_id)
    token = acquire_access_token()

    http_request = request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
            return response.status, json.loads(payload)
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch one Idabus resource by ID.")
    parser.add_argument("--resource-id", required=True, help="Idabus resource identifier.")
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
        _, payload = fetch_json(args.resource_id, timeout)
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
