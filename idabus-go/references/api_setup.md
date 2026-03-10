# Idabus API Setup Reference

Use this reference when configuring the skill for a specific Idabus API and OAuth2 identity provider.

## Required OAuth2 Values

- `OAUTH_TOKEN_URL`: token endpoint that issues the access token
- `OAUTH_FLOW_TYPE`: either `authorization_code` or `client_credentials`
- `OAUTH_CLIENT_ID`: OAuth2 client identifier
- `OAUTH_CLIENT_SECRET`: required for `client_credentials`
- `OAUTH_SCOPE`: optional scope string when the provider expects one
- `OAUTH_AUTHORIZATION_URL`: required when `OAUTH_FLOW_TYPE=authorization_code`
- `OAUTH_REDIRECT_HOST`: optional, defaults to `127.0.0.1`
- `OAUTH_REDIRECT_PORT`: optional, defaults to `8765`

When `OAUTH_FLOW_TYPE=authorization_code`, the script opens the current browser and runs authorization code flow with PKCE. The authorization request includes `prompt=login` to ask the provider for fresh authentication. If the browser cannot be opened, the script prints the authorization URL for manual use.

## Required API Values

- `IDABUS_API_BASE_URL`: base URL for the Idabus API
- `IDABUS_RESOURCE_PATH_TEMPLATE`: relative path for single-resource lookup; keep `{resource_id}` in the template

## OpenAPI / Swagger Inputs To Capture

Record these values from the API's OpenAPI document before first production use:

- resource lookup path
- path parameter name for the resource ID
- expected success response shape
- authentication scheme and scope name
- error response codes for unauthorized, forbidden, and not found

## OAuth2 Troubleshooting

Common auth failures:

- `invalid_client`: wrong client ID or client secret
- `invalid_grant`: invalid refresh token or rejected code exchange
- `invalid_scope`: scope is not valid for the API or client
- `unsupported_grant_type`: provider does not allow the configured grant type
- browser callback errors: the provider rejected the sign-in or redirect
- local callback bind failures: the configured localhost port is already in use
- browser launch failures: the current browser cannot be opened automatically

## Token Cache

- `auth.py` stores tokens in `.oauth-token-cache.json` at the skill root.
- The cache applies to both `client_credentials` and browser-based login.
- For `client_credentials`, the cached access token is reused until expiry.
- For browser-based login, the script prefers a valid cached token, then refresh token, then a fresh browser sign-in.

If the provider does not support either configured grant, the auth script must be extended in a future revision.
