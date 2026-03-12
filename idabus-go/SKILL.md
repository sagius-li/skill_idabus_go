---
name: idabus-go
description: Connect to an Idabus web API through an OAuth2-compliant identity provider and send authenticated HTTP requests. Use when Codex needs to configure OAuth2 access for an Idabus API, inspect the local API specification, or call documented endpoints with GET, POST, PUT, PATCH, or DELETE.
---

# Idabus Go

## Overview

Authenticate to an Idabus API with OAuth2 and send generic authenticated HTTP requests. Use `references/api_spec.json` as the source of truth for endpoint names, parameter names, endpoint descriptions, and request body metadata before calling the API.

## Quick Start

1. Copy `.env.example` to `.env`.
2. Fill in the API base URL, OAuth2 token URL, flow type, client ID, and the provider-specific settings required by that flow.
3. For `OAUTH_FLOW_TYPE=authorization_code`, also fill in `OAUTH_AUTHORIZATION_URL`, `OAUTH_REDIRECT_HOST` and `OAUTH_REDIRECT_PORT`, and confirm the client allows authorization code flow with PKCE and a localhost redirect URI.
4. For `OAUTH_FLOW_TYPE=client_credentials`, set `OAUTH_CLIENT_SECRET`.
5. Confirm that the identity provider supports the configured flow type and scope.
6. Review `references/api_spec.json` to identify the endpoint name, method, path template, and parameters to send.
7. If the endpoint defines a request body, build the JSON body before sending the request.
8. Build the request body around the exact resource attributes the task needs so the API returns neither extra fields nor too few fields.
9. Do not send a resource-read request without an explicit attribute list when the endpoint body supports attribute selection, even for exploratory or discovery calls.
10. If the task needs one field to discover the next request, ask only for that field and the minimal supporting fields needed to continue.
11. If `request_body.schema_ref` is present, load the referenced schema from `references/api_schema.json` and use it to shape the body payload.
12. Run `python3 scripts/resource.py --endpoint-name <name>` or `python3 scripts/resource.py --method GET --path /example`.

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

Before sending a request:

- Resolve the endpoint from `references/api_spec.json`.
- Gather path parameters, query parameters, headers, and request body requirements from that endpoint entry.
- If the endpoint has a `request_body`, construct a valid JSON body first instead of sending an ad hoc payload.
- When the API supports attribute selection, filtering, expansions, or include lists in the body, request only the attributes needed for the current task.
- Treat omitted attribute lists on resource reads as over-fetching unless the task explicitly requires the full resource.
- Avoid over-fetching by excluding unused attributes, related objects, and broad wildcard selections.
- Avoid under-fetching by including every attribute required to complete the task in one request body when the endpoint supports it.
- If `request_body.schema_ref` points into `references/api_schema.json`, load that schema and use it to decide which fields, value types, arrays, and nested objects belong in the body.
- Treat `references/api_schema.json` as the source of truth for body structure when a schema reference is present.

Run:

```bash
python3 scripts/resource.py --endpoint-name get-resource-by-id --path-param id=12345 --json '{"attributes":["displayname","manager"],"queryFormat":"IncludeNull"}'
```

For chained lookups, keep each read narrowly scoped:

```bash
python3 scripts/resource.py --endpoint-name get-resource-by-id --path-param id=00912912-3750-40f2-af95-64f83ad4f5bb --json '{"attributes":["displayname","manager"],"queryFormat":"IncludeNull"}'
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
- expects the caller to build the request body from the endpoint metadata before invoking the request
- expects the caller to select only the necessary resource attributes in the request body when the endpoint supports field selection
- expects the caller to avoid body-less resource reads when the endpoint supports attribute selection
- expects `request_body.schema_ref` to be resolved against `references/api_schema.json` when present
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
- If an endpoint includes `request_body.schema_ref`, load the referenced schema from `references/api_schema.json` and use it to build the request body before sending the API call.
- When building a request body for resource retrieval, prefer explicit attribute lists over broad defaults so the response matches the task's required fields.
- Prefer `--endpoint-name` over hardcoded paths when the endpoint exists in the specification.

## Resources

- `scripts/auth.py`: acquire an OAuth2 access token without printing secrets
- `scripts/resource.py`: send authenticated GET, POST, PUT, PATCH, or DELETE requests and print raw JSON
- `references/api_spec.json`: endpoint catalog with endpoint names, parameters, and descriptions
- `references/api_schema.json`: local JSON schema bundle for request bodies referenced from `api_spec.json`
- `references/api_setup.md`: fill in the authorization endpoint, token endpoint, scope, base API URL, and spec maintenance notes
