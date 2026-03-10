---
name: idabus-go
description: Connect to an Idabus web API through an OAuth2-compliant identity provider and fetch Idabus resources by ID. Use when Codex needs to configure OAuth2 access for an Idabus API, troubleshoot token acquisition or scope configuration, or call the API to retrieve a specific resource as raw JSON.
---

# Idabus Go

## Overview

Authenticate to an Idabus API with OAuth2 and fetch a single resource by ID. Use `OAUTH_FLOW_TYPE=client_credentials` for service-to-service access or `OAUTH_FLOW_TYPE=authorization_code` for interactive browser login with PKCE in your current browser.

## Quick Start

1. Copy `.env.example` to `.env`.
2. Fill in the API base URL, OAuth2 token URL, flow type, client ID, and the provider-specific settings required by that flow.
3. For `OAUTH_FLOW_TYPE=authorization_code`, also fill in `OAUTH_AUTHORIZATION_URL` and confirm the client allows authorization code flow with PKCE and a localhost redirect URI.
4. For `OAUTH_FLOW_TYPE=client_credentials`, set `OAUTH_CLIENT_SECRET`.
5. Confirm that the identity provider supports the configured flow type and scope.
6. Run `python3 scripts/fetch_resource.py --resource-id <id>`.

## Configure Local Secrets

- Keep `.env` at the skill root next to `SKILL.md`.
- Commit `.env.example`, not `.env`.
- Never print or store the access token.
- Rotate the client secret outside this repository if the service client changes.
- `auth.py` stores cached tokens in `.oauth-token-cache.json`; keep that file local and ignored.
- `auth.py` opens interactive login in your current browser and requests fresh authentication with `prompt=login`.
- Read `references/api_setup.md` when wiring the authorization endpoint, token endpoint, scope, or API path.

## Fetch One Resource by ID

Run:

```bash
python3 scripts/fetch_resource.py --resource-id 12345
```

Optional flags:

- `--output path/to/resource.json` to save the raw JSON payload
- `--env-file path/to/.env` to load a non-default env file
- `--timeout 60` to override the HTTP timeout for one request

The fetch script:

- loads configuration from `.env`
- reuses a cached OAuth2 access token when one is still valid
- acquires a new token with either client credentials or interactive browser login
- interpolates `resource_id` into `IDABUS_RESOURCE_PATH_TEMPLATE`
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

## Resources

- `scripts/auth.py`: acquire an OAuth2 access token without printing secrets
- `scripts/fetch_resource.py`: fetch one Idabus resource by ID and print raw JSON
- `references/api_setup.md`: fill in the authorization endpoint, token endpoint, scope, OpenAPI endpoint mapping, and grant prerequisites
