#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import hashlib
import http.server
import json
import os
import secrets
import sys
import time
import webbrowser
from pathlib import Path
from urllib import error, parse, request

from env_utils import ConfigError, default_env_path, get_int_env, load_dotenv, require_env


SUPPORTED_FLOW_TYPES = {"authorization_code", "client_credentials"}
CACHE_SKEW_SECONDS = 60
BROWSER_TIMEOUT_SECONDS = 300


def cache_file_path() -> Path:
    return Path(__file__).resolve().parents[1] / ".oauth-token-cache.json"


def redirect_uri() -> str:
    host = os.getenv("OAUTH_REDIRECT_HOST", "localhost").strip() or "localhost"
    port = get_int_env("OAUTH_REDIRECT_PORT", 8765)
    return f"http://{host}:{port}/callback"


def load_cache() -> dict:
    cache_path = cache_file_path()
    if not cache_path.exists():
        return {"entries": {}}

    try:
        cache = json.loads(cache_path.read_text())
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Token cache is not valid JSON: {cache_path}") from exc

    if not isinstance(cache, dict):
        raise ConfigError(f"Token cache has invalid structure: {cache_path}")

    entries = cache.get("entries", {})
    if not isinstance(entries, dict):
        raise ConfigError(f"Token cache entries have invalid structure: {cache_path}")
    return {"entries": entries}


def save_cache(cache: dict) -> None:
    cache_path = cache_file_path()
    cache_path.write_text(json.dumps(cache, indent=2) + "\n")


def build_cache_key(flow_type: str) -> str:
    parts = {
        "flow_type": flow_type,
        "token_url": require_env("OAUTH_TOKEN_URL"),
        "client_id": require_env("OAUTH_CLIENT_ID"),
        "scope": os.getenv("OAUTH_SCOPE", "").strip(),
    }

    if flow_type == "client_credentials":
        client_secret = require_env("OAUTH_CLIENT_SECRET")
        parts["client_secret_hash"] = hashlib.sha256(client_secret.encode("utf-8")).hexdigest()
    else:
        parts["authorization_url"] = require_env("OAUTH_AUTHORIZATION_URL")
        parts["redirect_uri"] = redirect_uri()

    serialized = json.dumps(parts, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def read_cache_entry(cache_key: str) -> dict | None:
    cache = load_cache()
    entry = cache["entries"].get(cache_key)
    return entry if isinstance(entry, dict) else None


def write_cache_entry(cache_key: str, token_response: dict, flow_type: str) -> None:
    cache = load_cache()
    expires_in = token_response.get("expires_in")
    expires_at = int(time.time()) + int(expires_in) if expires_in else int(time.time()) + 300
    entry = {
        "flow_type": flow_type,
        "access_token": token_response["access_token"],
        "expires_at": expires_at,
    }
    refresh_token = token_response.get("refresh_token")
    if refresh_token:
        entry["refresh_token"] = refresh_token
    cache["entries"][cache_key] = entry
    save_cache(cache)


def valid_cached_access_token(entry: dict | None) -> str | None:
    if not entry:
        return None
    access_token = entry.get("access_token")
    expires_at = entry.get("expires_at")
    if not isinstance(access_token, str) or not isinstance(expires_at, int):
        return None
    if expires_at <= int(time.time()) + CACHE_SKEW_SECONDS:
        return None
    return access_token


def request_token(form_data: dict[str, str]) -> dict:
    token_url = require_env("OAUTH_TOKEN_URL")
    body = parse.urlencode(form_data).encode("utf-8")
    http_request = request.Request(
        token_url,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=30) as response:
            payload = response.read().decode("utf-8")
    except error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        detail = payload or exc.reason
        raise ConfigError(f"Token request failed with HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise ConfigError(f"Token request failed: {exc.reason}") from exc

    try:
        token_response = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Token response was not valid JSON: {exc}") from exc

    access_token = token_response.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise ConfigError(f"Token response did not include access_token: {json.dumps(token_response)}")
    return token_response


def client_credentials_token_response() -> dict:
    form_data = {
        "grant_type": "client_credentials",
        "client_id": require_env("OAUTH_CLIENT_ID"),
        "client_secret": require_env("OAUTH_CLIENT_SECRET"),
    }
    oauth_scope = os.getenv("OAUTH_SCOPE", "").strip()
    if oauth_scope:
        form_data["scope"] = oauth_scope
    return request_token(form_data)


def build_pkce_pair() -> tuple[str, str]:
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(48)).decode("utf-8").rstrip("=")
    challenge_digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(challenge_digest).decode("utf-8").rstrip("=")
    return code_verifier, code_challenge


def print_manual_login_url(authorize_url: str) -> None:
    print("Open this URL in your browser:", file=sys.stderr)
    print(authorize_url, file=sys.stderr)


def open_browser(authorize_url: str) -> None:
    if not webbrowser.open(authorize_url):
        print_manual_login_url(authorize_url)
        raise ConfigError(
            "Unable to open the browser for interactive authentication. "
            "Open the printed URL manually in your browser."
        )


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return

        self.server.callback_params = {k: v[0] for k, v in parse.parse_qs(parsed.query).items()}  # type: ignore[attr-defined]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Authentication complete</h1><p>You may close this window.</p></body></html>")

    def log_message(self, format: str, *args: object) -> None:
        return


class CallbackServer(http.server.ThreadingHTTPServer):
    callback_params: dict | None = None


def receive_authorization_callback() -> dict:
    redirect_host = os.getenv("OAUTH_REDIRECT_HOST", "localhost").strip() or "localhost"
    redirect_port = get_int_env("OAUTH_REDIRECT_PORT", 8765)
    try:
        httpd = CallbackServer((redirect_host, redirect_port), CallbackHandler)
    except OSError as exc:
        raise ConfigError(f"Unable to bind OAuth callback listener on {redirect_host}:{redirect_port}: {exc}") from exc

    httpd.timeout = 1
    deadline = time.time() + BROWSER_TIMEOUT_SECONDS
    with httpd:
        while time.time() < deadline:
            httpd.handle_request()
            if httpd.callback_params is not None:
                return httpd.callback_params

    raise ConfigError("Timed out waiting for the OAuth browser callback.")


def authorization_code_token_response() -> tuple[dict, bool]:
    cache_key = build_cache_key("authorization_code")
    entry = read_cache_entry(cache_key)
    refresh_token = entry.get("refresh_token") if entry else None

    if isinstance(refresh_token, str) and refresh_token:
        form_data = {
            "grant_type": "refresh_token",
            "client_id": require_env("OAUTH_CLIENT_ID"),
            "refresh_token": refresh_token,
        }
        oauth_scope = os.getenv("OAUTH_SCOPE", "").strip()
        if oauth_scope:
            form_data["scope"] = oauth_scope
        try:
            return request_token(form_data), True
        except ConfigError:
            pass

    authorization_url = require_env("OAUTH_AUTHORIZATION_URL")
    scope = require_env("OAUTH_SCOPE")
    code_verifier, code_challenge = build_pkce_pair()
    state = secrets.token_urlsafe(24)
    auth_query = {
        "response_type": "code",
        "client_id": require_env("OAUTH_CLIENT_ID"),
        "redirect_uri": redirect_uri(),
        "scope": scope,
        "prompt": "login",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    authorize_url = f"{authorization_url}?{parse.urlencode(auth_query)}"

    open_browser(authorize_url)

    callback_params = receive_authorization_callback()
    if callback_params.get("state") != state:
        raise ConfigError("OAuth callback state did not match the login request.")
    if "error" in callback_params:
        error_description = callback_params.get("error_description", callback_params["error"])
        raise ConfigError(f"OAuth authorization failed: {error_description}")

    auth_code = callback_params.get("code")
    if not auth_code:
        raise ConfigError("OAuth callback did not include an authorization code.")

    form_data = {
        "grant_type": "authorization_code",
        "client_id": require_env("OAUTH_CLIENT_ID"),
        "code": auth_code,
        "redirect_uri": redirect_uri(),
        "code_verifier": code_verifier,
    }
    token_response = request_token(form_data)
    return token_response, False


def acquire_access_token_with_metadata() -> tuple[str, dict]:
    flow_type = require_env("OAUTH_FLOW_TYPE")
    if flow_type not in SUPPORTED_FLOW_TYPES:
        supported = ", ".join(sorted(SUPPORTED_FLOW_TYPES))
        raise ConfigError(f"Unsupported OAUTH_FLOW_TYPE '{flow_type}'. Supported values: {supported}")

    cache_key = build_cache_key(flow_type)
    cached_token = valid_cached_access_token(read_cache_entry(cache_key))
    if cached_token:
        return cached_token, {"flow_type": flow_type, "cache_used": True, "refreshed": False, "interactive_login": False}

    if flow_type == "client_credentials":
        token_response = client_credentials_token_response()
        metadata = {"flow_type": flow_type, "cache_used": False, "refreshed": False, "interactive_login": False}
    else:
        token_response, refreshed = authorization_code_token_response()
        metadata = {
            "flow_type": flow_type,
            "cache_used": False,
            "refreshed": refreshed,
            "interactive_login": not refreshed,
        }

    write_cache_entry(cache_key, token_response, flow_type)
    return token_response["access_token"], metadata


def acquire_access_token() -> str:
    token, _ = acquire_access_token_with_metadata()
    return token


def main() -> int:
    parser = argparse.ArgumentParser(description="Acquire an OAuth2 access token for the Idabus API.")
    parser.add_argument("--env-file", default=str(default_env_path()), help="Path to the .env file.")
    parser.add_argument("--as-json", action="store_true", help="Print metadata instead of a plain success message.")
    args = parser.parse_args()

    env_file = Path(args.env_file)
    if not env_file.is_absolute():
        env_file = Path.cwd() / env_file

    try:
        load_dotenv(env_file)
        _, metadata = acquire_access_token_with_metadata()
    except ConfigError as exc:
        print(str(exc))
        return 1

    if args.as_json:
        metadata["token_acquired"] = True
        print(json.dumps(metadata, indent=2))
    else:
        print("Token acquisition succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
