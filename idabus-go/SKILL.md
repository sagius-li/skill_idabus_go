---
name: idabus-go
description: Connect to an Idabus web API through an OAuth2-compliant identity provider, send authenticated HTTP requests, and send SMTP email from the local helper scripts. Use when Codex needs to configure OAuth2 access for an Idabus API, inspect the local API specification, call documented endpoints with GET, POST, PUT, PATCH, or DELETE, or send email through the configured SMTP settings.
---

# Idabus Go

## Overview

- Authenticate to an Idabus API with OAuth2 and send generic authenticated HTTP requests. Use `references/api_spec.json` as the source of truth for endpoint names, parameter names, endpoint descriptions, and request body metadata before calling the API.

- Whenever object semantics are uncertain, load `references/object_types_and_attributes.md` before proceeding.

- For resource searches that use XPath, consult `references/idabus_xpath_dialect.md` before writing the query and prefer sending the XPath in the request body whenever the endpoint body supports an XPath field.

- If the user asks to send email, use `scripts/send_email.py` instead of building an ad hoc mail sender. Supply recipients with repeated `--to` flags and attachments with repeated `--attachment` flags.

## XPath Search Checklist

Before sending any XPath-backed search request:

1. Read `references/api_spec.json` to identify the exact endpoint contract.
2. If the endpoint has `request_body.schema_ref`, read the referenced schema in `references/api_schema.json`.
3. Read `references/idabus_xpath_dialect.md` and validate the XPath syntax against that dialect.
4. Unless the user explicitly requests case-sensitive matching, treat attribute value checks as case-insensitive by default. For `=`, `starts-with`, `contains`, `ends-with`, regex matching, and similar non-sensitive operators, one literal is usually enough; do not add duplicate case variants such as both `'amy wells'` and `'Amy Wells'`. Use `equals-sensitive`, `starts-with-sensitive`, `contains-sensitive`, `ends-with-sensitive`, or `regex-match-sensitive` only when the prompt explicitly requires case-sensitive behavior.
   Example: prefer `/person[starts-with(displayname,'amy wells')]` instead of `/person[starts-with(displayname,'amy wells') or starts-with(displayname,'Amy Wells')]`.
5. Check whether the request body schema supports an XPath field such as `xPath`.
6. Send the XPath in the request body whenever that body field exists.
7. Use query-parameter XPath transport only when the endpoint does not support XPath in the request body.
8. Request only the attributes needed for the task.

Anti-pattern: do not default to `xPathQuery` in query parameters just because the endpoint spec lists that parameter. If the same endpoint also accepts XPath in the request body, body transport wins.

## Schema Discovery With XPath

When the task is to discover schema metadata and the API exposes schema resources, XPath search may be used instead of full schema reads.

- For object type discovery, use `/objecttypedescription[name='...' or displayname='...']`.
- For attribute discovery, use `/attributetypedescription[name='...' or displayname='...']`.
- For binding discovery between an object type and an attribute, use `/bindingdescription[boundobjecttype='...' and boundattributetype='...']`.
- `boundobjecttype` and `boundattributetype` are reference attributes, so their values must be object IDs, not display names.
- When a binding lookup starts from names instead of IDs, first resolve the object type and attribute type IDs, then query the binding.
- Keep schema-discovery reads narrow by requesting only the fields needed for the next step.

## Quick Start

1. Copy `.env.example` to `.env`.
2. Fill in the API base URL, OAuth2 token URL, flow type, client ID, and the provider-specific settings required by that flow.
3. For `OAUTH_FLOW_TYPE=authorization_code`, also fill in `OAUTH_AUTHORIZATION_URL`, `OAUTH_REDIRECT_HOST` and `OAUTH_REDIRECT_PORT`, and confirm the client allows authorization code flow with PKCE and a localhost redirect URI.
4. For `OAUTH_FLOW_TYPE=client_credentials`, set `OAUTH_CLIENT_SECRET`.
5. Confirm that the identity provider supports the configured flow type and scope.
6. Review `references/api_spec.json` to identify the endpoint name, method, path template, and parameters to send.
7. If `request_body.schema_ref` is present, load the referenced schema from `references/api_schema.json` and use it to shape the body payload.
8. If the task searches resources with XPath, read `references/idabus_xpath_dialect.md`, build the XPath according to that dialect, and determine whether the request body supports an XPath field.
9. If the endpoint body supports XPath transport, send the XPath in the request body instead of query parameters.
10. If the endpoint defines a request body, build the JSON body before sending the request.
11. Build the request body around the exact resource attributes the task needs so the API returns neither extra fields nor too few fields.
12. Do not send a resource-read request without an explicit attribute list when the endpoint body supports attribute selection, even for exploratory or discovery calls.
13. If the task needs one field to discover the next request, ask only for that field and the minimal supporting fields needed to continue.
14. Run `python3 scripts/resource.py --endpoint-name <name>` or `python3 scripts/resource.py --method GET --path /example`.
15. If the task is to send email, run `python3 scripts/send_email.py` with SMTP settings loaded from `.env`.

## Configure Local Secrets

- Keep `.env` at the skill root next to `SKILL.md`.
- Commit `.env.example`, not `.env`.
- Never print or store the access token.
- Rotate the client secret outside this repository if the service client changes.
- `auth.py` stores cached tokens in `.oauth-token-cache.json`; keep that file local and ignored.
- `auth.py` opens interactive login in your current browser and requests fresh authentication with `prompt=login`.
- Read `references/api_spec.json` before choosing an endpoint name or parameter set.
- Read `references/api_setup.md` when wiring the authorization endpoint, token endpoint, scope, or base API URL.
- Keep SMTP settings for `scripts/send_email.py` in the same `.env` file: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, and `SMTP_FROM_EMAIL`.

## Send emails

- Only send emails if asked to.
- If there is no subject and body specified, find the suitable content for the email from the task context and use that as the subject and body.

The email script:

- loads SMTP configuration from `.env`
- validates sender and recipient email addresses before sending
- sends plain-text email through SMTP with optional TLS
- attaches local files when `--attachment` is provided
- prints a short success message to stdout

optional flags

- `--to recipient@example.com` repeated to send to multiple recipients with `scripts/send_email.py`
- `--attachment path/to/file` repeated to attach multiple files with `scripts/send_email.py`

To send a plain-text email:

```bash
python3 scripts/send_email.py --to alice@example.com --to bob@example.com --subject "Status update" --body "The sync completed successfully."
```

To send an email with attachments:

```bash
python3 scripts/send_email.py --to ops@example.com --subject "Daily reports" --body "Attached are the generated reports." --attachment ./report.csv --attachment ./summary.txt
```

To send an email body from a file:

```bash
python3 scripts/send_email.py --to team@example.com --subject "Release notes" --body-file ./release_notes.txt
```

## Simulation Sessions

- For any task that creates, updates, or deletes Idabus resources, you MUST create a simulation session first unless the user explicitly says to modify real data.
- You MUST include the simulation session ID on every Idabus request in that task, including all reads, writes, creations, deletions and validation checks.
- For a task that includes any simulated action, use the same simulation session for every request in that task, including read requests, so all requests share the same simulated state and data.
- It is a violation to create a simulation session and then omit the simulation session ID from any subsequent task request.
- Before the first request of that task, create a simulation session with `create-simulation-session`.
- Pass the created simulation session ID on every request in the task by using the endpoint parameter name defined in `references/api_spec.json`.
- After the task finishes, delete the simulation session with `delete-simulation-session`.
- For `delete-simulation-session`, you MUST supply `simulationSessionId` as the endpoint path parameter.
- If a simulation session was created, cleanup is mandatory. You MUST attempt deletion even if intermediate requests fail, and MUST report cleanup success or failure.

### Validate / check rsults in simulation sessions

- If anything should be validated or checked in a simulation session after a resource change is made, you MUST get the event id of the change request according to the `Events` section and wait untile the event is completed - means, the event and all its child events have finished processing.
- Validations or checks can only be done after the event, which changes the resources, is completed.

## Permission Checks

- For questions about whether a user can read, write, modify, delete, create, add, or remove something in Idabus, use `check-permissions` as the source of truth. Do not infer authorization from ordinary resource reads or from assumptions about roles.
- In the answer, always report whether access is permitted.
- Mention `requestorIsAdmin` when it is relevant to explaining the result.
- If allowing permission rules are returned, always include each rule's `objectid` and `displayname` in the answer.
- If no allowing permission rules are returned, explicitly say that no allowing permission rules were returned.

## Functions/Function Expressions

- Use the endpoint `execute-function-expression` to evaluate function expressions in Idabus.
- Use function expressions only when necessary and for problems that are complicated and cannot be solved with XPath alone.
- Treat the function expression language as a separate programming language embedded in the API. Function expressions should not be saved in files, but should be passed to the body of the API.
- For prompts related to "functions" or "function expressions", **always** first carefully consult all of the following three documentations:
  - `references/idabus_function_expression_language.md` for the syntax and semantics of function expressions in Idabus;
  - `references/idabus_supported_functions.md` for the catalog of supported functions and their usages;
    - Be careful to only use functions that exist! For example, don't simply assume that a function like `toLowerCase()` exists because it sounds plausible (it doesn't, it's called `toLower()`)!
  - `references/idabus_function_examples.md` for example usages of function expressions in different contexts.
- Only use `reduce()` when absolutely necessary. First check if there is a more elegant solution.

### Performance

When writing or reviewing function expressions, be careful to take performance into account. In particular,

- try to avoid the N+1 Query Problem: instead of having many small XPath queries or resource retrieval calls in a loop, see if it is possible to use a larger single query and use its result as a lookup;
  - but also try to avoid overly large queries unless necessary (e.g. fetching all or almost all person objects)

- try to avoid `contains` in a loop (quadratic complexity) if you can also construct a dictionary and use `containsKey` instead;

- write idiomatic code, e.g. use `xpathExists()` instead of `xpathCount(...) > 0`, or `xpathObjectIds()` when you just need a flat list of object IDs;

- some performance estimations:
  - in-memory operations are generally much faster than operations on the database (e.g. `xpath`, `getResource`)
  - due to latency, even a simple `xpathExists()` call takes about 5 to 10 ms.
  - the performance of XPath queries depends on the query (multi-step and nested queries are more expensive), on the number of returned results, and on which attributes are fetched.
  - fetching the display names of 1000 resources via XPath takes about 50 ms, of 5000 takes 150 ms, 10000 takes 300 ms etc.

## Call The API

Before sending a request:

- Resolve the endpoint from `references/api_spec.json`.
- Decide whether the task needs a simulation session before sending the first request.
- If the task contains any mutating action and the user did not explicitly opt out, create one simulation session first and reuse it for every request in the task.
- Gather path parameters, query parameters, headers, and request body requirements from that endpoint entry.
- If the endpoint has a `request_body`, construct a valid JSON body first instead of sending an ad hoc payload.
- For XPath-backed search endpoints, check the request body schema for an XPath field such as `xPath` before deciding how to send the query.
- When the body supports XPath transport, place the XPath in the request body and do not default to query parameters.
- Use query-parameter XPath transport only when the endpoint does not support an XPath field in the body.
- When the API supports attribute selection, filtering, expansions, or include lists in the body, request only the attributes needed for the current task.
- Treat omitted attribute lists on resource reads as over-fetching unless the task explicitly requires the full resource.
- Avoid over-fetching by excluding unused attributes, related objects, and broad wildcard selections.
- Avoid under-fetching by including every attribute required to complete the task in one request body when the endpoint supports it.
- If `request_body.schema_ref` points into `references/api_schema.json`, load that schema and use it to decide which fields, value types, arrays, and nested objects belong in the body.
- Treat `references/api_schema.json` as the source of truth for body structure when a schema reference is present.
- For resource searches that use XPath, read `references/idabus_xpath_dialect.md` first and use that syntax in the request body whenever possible.
- If a simulation session is active for the task, include its ID on reads and writes alike until cleanup is complete.
- After the task's API work is complete, delete any simulation session that was created for that task.
- Unless the user explicitly asks for output files, do not use `--output` and rely on stdout instead.
- If the user does ask for output files, save them under `idabus-go/output/`.

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

With an XPath search:

```bash
python3 scripts/resource.py --endpoint-name get-resource-by-xpath --json '{"xPath":"/person[displayName = '\''Albert Einstein'\'']","attributes":["firstname","lastname"],"pageSize":10,"queryFormat":"IncludeNull"}'
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

- `--output idabus-go/output/<name>.json` to save the raw JSON payload when the user explicitly asks for an output file
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
- expects XPath-backed requests to use request-body transport whenever the body schema supports an XPath field
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
- For XPath-backed endpoints, check both the endpoint entry and the referenced body schema before deciding whether the XPath belongs in the body or in query parameters.
- If the body schema supports an XPath field, treat request-body XPath transport as mandatory and treat query-parameter transport as fallback only.
- When building a request body for resource retrieval, prefer explicit attribute lists over broad defaults so the response matches the task's required fields.
- For XPath-backed search endpoints, use `references/idabus_xpath_dialect.md` as the source of truth for the XPath expression syntax.
- Prefer `--endpoint-name` over hardcoded paths when the endpoint exists in the specification.

## Events

- Every API call to the Idabus endpoints that creates, updates or deletes resources will return an event id in the response header `X-Idabus-Event-Id`. This event id can be used to query the status or other details of the event through the `get-resource-by-id` endpoint.
- If the task involves checking the status for finished events, the following status values indicate that the event and all its child events have finished processing:
  - `Success`
  - `Skipped`
  - `Failed`
  - `Denied`
  - `PostProcessingFailed`
  - `Canceled`
  - `ManuallyClosed`

## Resources

- `scripts/auth.py`: acquire an OAuth2 access token without printing secrets
- `scripts/resource.py`: send authenticated GET, POST, PUT, PATCH, or DELETE requests and print raw JSON
- `scripts/send_email.py`: send plain-text SMTP email to one or more recipients with optional file attachments
- `references/api_spec.json`: endpoint catalog with endpoint names, parameters, and descriptions
- `references/api_schema.json`: local JSON schema bundle for request bodies referenced from `api_spec.json`
- `references/idabus_xpath_dialect.md`: local reference for the Idabus XPath search syntax
- `references/api_setup.md`: fill in the authorization endpoint, token endpoint, scope, base API URL, and spec maintenance notes
