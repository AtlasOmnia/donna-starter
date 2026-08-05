# Least-Privilege Workspace OAuth

Use this reference when adding Gmail, Calendar, or another sensitive Google Workspace adapter to a Hermes plugin.

## Why this exists

Shared setup documentation can drift from the installed OAuth helper. A documented `--services` selector may not exist in the actual parser, while the helper's default scope list may request unrelated write-capable services. Never infer least privilege from the README alone.

## Safe workflow

1. Inspect the installed helper's real `--help`, parser, and scope constants.
2. Decide the exact service scope before any browser authorization.
3. If the shared helper cannot express the required scope, add a source-owned auth helper with an explicit allowlist.
4. For Gmail-only mode, request exactly:

 ```text
 https://www.googleapis.com/auth/gmail.readonly
 ```

5. Accept a user-supplied Desktop OAuth client JSON only from outside the repository.
6. Store refresh/access-token material under a user-local Hermes home path outside Git; reject client/token paths inside the repository.
7. Keep authorization out of implementation and unit-test runs. Mock OAuth/API calls and test exact scopes, path rejection, malformed responses, missing auth, and mutation exclusions.
8. Stop at the browser-consent gate and require the user to authorize separately.

## Gmail adapter boundaries

- GET/list/search and bounded metadata/snippet retrieval only.
- No full-body or attachment prefetch by default.
- No send, reply, forward, delete, trash, archive, mark-read, label mutation, draft creation, or other write operation.
- Prefetch disabled by default and profile/configuration gated.
- Fail open to normal Hermes behavior on ambiguity, auth failure, timeout, malformed output, or backend failure.

## Local authorization command shape

After the source-owned helper and its optional OAuth dependency are present, the documented command should look like:

```bash
python -m pip install google-auth-oauthlib
python path/to/integration/auth.py \
 --client-json /external/path/google-desktop-client.json \
 --services gmail
```

The command must store the token outside the repository and must not alter an existing Calendar token. A combined `calendar,gmail` mode is acceptable only when it requests exactly the two corresponding read-only scopes.

## Verification evidence

Report these separately:

- Unit/fixture evidence proves the scope and adapter contract.
- Local smoke without credentials proves structured `missing_auth` behavior and no network call.
- Browser authorization proves only that the user granted the exact requested scope.
- A live Gmail query is a separate post-authorization acceptance gate.

Never report green tests as proof that a user's Gmail account has been authorized.
