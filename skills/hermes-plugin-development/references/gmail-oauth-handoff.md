# Gmail OAuth Handoff and Least-Privilege Preflight

Use this when a Hermes plugin adds Gmail authorization or when a delegated implementation hands an OAuth command to a user.

## OAuth client compatibility

A Python flow using `InstalledAppFlow.run_local_server(..., port=0)` requires a Google OAuth client JSON with a top-level `installed` configuration, created in Google Cloud as an **OAuth client ID → Desktop app**. A top-level `web` client is not interchangeable: it may allow only a fixed redirect such as `http://localhost:1`, while the local flow selects a random callback port and Google rejects the request as invalid/redirect-mismatch.

Before authorizing, inspect only non-secret metadata and reject the wrong type. Never print `client_id` or `client_secret`. If the consent screen is in Testing, add the account as a test user.

## File/path preflight

Example filenames are placeholders. Verify the exact downloaded JSON path before running the flow:

```bash
test -f "/path/to/downloaded-desktop-client.json" && echo "client JSON present"
```

A generic `Authorization failed` message may intentionally hide the underlying exception. Check path existence and the active environment's `google-auth-oauthlib` import before retrying.

## Terminal handoff

Do not paste a `cd` line and a following Python command when the newline may be lost. That makes the shell treat the entire string as arguments to `cd`, producing `cd: too many arguments`.

Prefer one complete, fully quoted absolute command:

```bash
"/repo/.venv/bin/python" \
 "/repo/integrations/<plugin>/auth.py" \
 --client-json "/path/to/downloaded-desktop-client.json" \
 --services gmail
```

For paths containing spaces, quote every path. When computer-use places an OAuth command in Terminal, capture first, type one complete command, verify the text, and stop before Return if browser authorization is the next human gate.

## Least-privilege boundary

Gmail-only mode must request exactly `https://www.googleapis.com/auth/gmail.readonly`; it must not silently include Gmail send/modify or unrelated Drive/Docs/Sheets/Contacts scopes. Keep OAuth client JSON and tokens outside the repository and never claim live access until the user completes authorization.
