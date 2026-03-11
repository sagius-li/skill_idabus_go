---
name: idabus-go
description: Connect to an Idabus web API through an OAuth2-compliant identity provider and send authenticated HTTP requests. Use when Codex needs to configure OAuth2 access for an Idabus API, inspect the local API specification, or call documented endpoints with GET, POST, PUT, PATCH, or DELETE.
---

# Idabus Go

## Overview

Authenticate to an Idabus API with OAuth2 and send generic authenticated HTTP requests. Use `references/api_spec.json` as the source of truth for endpoint names, parameter names, and endpoint descriptions before calling the API.

## Quick Start

1. Copy `.env.example` to `.env`.
2. Fill in the API base URL, OAuth2 token URL, flow type, client ID, and the provider-specific settings required by that flow.
3. For `OAUTH_FLOW_TYPE=authorization_code`, also fill in `OAUTH_AUTHORIZATION_URL`, `OAUTH_REDIRECT_HOST` and `OAUTH_REDIRECT_PORT`, and confirm the client allows authorization code flow with PKCE and a localhost redirect URI.
4. For `OAUTH_FLOW_TYPE=client_credentials`, set `OAUTH_CLIENT_SECRET`.
5. Confirm that the identity provider supports the configured flow type and scope.
6. Review `references/api_spec.json` to identify the endpoint name, method, path template, and parameters to send.
7. Run `python3 scripts/resource.py --endpoint-name <name>` or `python3 scripts/resource.py --method GET --path /example`.

## Configure Local Secrets

- Keep `.env` at the skill root next to `SKILL.md`.
- Commit `.env.example`, not `.env`.
- Never print or store the access token.
- Rotate the client secret outside this repository if the service client changes.
- `auth.py` stores cached tokens in `.oauth-token-cache.json`; keep that file local and ignored.
- `auth.py` opens interactive login in your current browser and requests fresh authentication with `prompt=login`.
- Read `references/api_spec.json` before choosing an endpoint name or parameter set.
- Read `references/api_setup.md` when wiring the authorization endpoint, token endpoint, scope, or base API URL.

## Call The API

Run:

```bash
python3 scripts/resource.py --endpoint-name get-resource --path-param resource_id=12345
```

With query parameters:

```bash
python3 scripts/resource.py --endpoint-name search-resources --query status=active --query limit=10
```

With an inline JSON body:

```bash
python3 scripts/resource.py --method POST --path /resources --json '{"name":"demo","enabled":true}'
```

With a request body file:

```bash
python3 scripts/resource.py --method PATCH --endpoint-name update-resource --path-param resource_id=12345 --body-file payload.json
```

Optional flags:

- `--output path/to/resource.json` to save the raw JSON payload
- `--env-file path/to/.env` to load a non-default env file
- `--timeout 60` to override the HTTP timeout for one request
- `--query key=value` to add query parameters
- `--header key=value` to add extra request headers
- `--json '{"name":"demo"}'` or `--body-file payload.json` for POST, PUT, or PATCH bodies

The request script:

- loads configuration from `.env`
- reuses a cached OAuth2 access token when one is still valid
- acquires a new token with either client credentials or interactive browser login
- resolves endpoint definitions from `references/api_spec.json` when `--endpoint-name` is used
- applies path, query, header, and body inputs to the request
- calls the API with a bearer token
- prints JSON to stdout and optionally saves it to disk

## Troubleshoot Authentication

- Check that `OAUTH_TOKEN_URL` points to the provider's token endpoint.
- Check that `OAUTH_AUTHORIZATION_URL` is configured when `OAUTH_FLOW_TYPE=authorization_code`.
- Check that `OAUTH_SCOPE` matches the API scope expected by the provider.
- Expect `invalid_client` when the client ID or client secret is wrong.
- Expect browser-based sign-in to fail when the client is not allowed to use authorization code flow with PKCE or the localhost redirect URI is not registered.
- Expect the authorization request to include `prompt=login`, which asks the provider to force re-authentication in the current browser session.
- Expect a manual-login fallback when the browser cannot be opened automatically.
- Expect `invalid_scope` when the requested scope is not exposed to the client.
- Expect `unsupported_grant_type` when the provider does not allow the token request grant type needed by the configured flow.
- If repeated requests keep opening the browser, delete `.oauth-token-cache.json` and check whether the provider is returning refresh tokens and `expires_in`.

## API Specification

- `references/api_spec.json` contains the endpoint catalog for this skill. Read it before calling the API.
- Each endpoint entry should include the endpoint name, method, path, parameter names, and a short description.
- Prefer `--endpoint-name` over hardcoded paths when the endpoint exists in the specification.

## Resources

- `scripts/auth.py`: acquire an OAuth2 access token without printing secrets
- `scripts/resource.py`: send authenticated GET, POST, PUT, PATCH, or DELETE requests and print raw JSON
- `references/api_spec.json`: endpoint catalog with endpoint names, parameters, and descriptions
- `references/api_setup.md`: fill in the authorization endpoint, token endpoint, scope, base API URL, and spec maintenance notes
