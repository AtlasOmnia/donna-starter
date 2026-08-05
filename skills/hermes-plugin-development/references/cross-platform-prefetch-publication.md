# Cross-Platform Deterministic-Prefetch Publication

Use this reference when turning a local Hermes prefetch integration into a public Mac/Windows plugin.

## Pattern

A deterministic prefetch plugin runs a bounded, read-only provider lookup from `pre_llm_call`, injects structured context into the current model request, and lets the main model write the response. It is appropriate for obvious queries such as calendar lookup, Gmail search, Drive search, contacts, reminders, and notes. It is not a replacement for model reasoning on ambiguous requests or for confirmation-gated mutations.

Required invariants:

- Profile identity is request-scoped and fail-closed when unknown; discovery may be process-global in a multiplexed gateway.
- Intent matching is deterministic and excludes mutation verbs: send, reply, forward, create, update, move, delete, share, cancel, and reschedule.
- Provider calls use argument-list subprocess/API calls, hard wall-clock deadlines, bounded result counts, bounded field/body sizes, and structured JSON.
- Ambiguous intent, timeout, auth failure, malformed output, or provider error returns `None`/normal-path fallback rather than blocking the conversation.
- Metadata/snippets are the default context; full email bodies, attachments, and large documents require an explicit user request.
- Hook-dispatched tool calls emit dispatch/completion logs, but live acceptance must inspect actual logs and API-call count rather than relying on final prose.

## Public export boundary

Never publish the live `~/.hermes/plugins/<name>/` directory. Stage a clean tree containing source, manifest, sample config, tests, README, license, packaging metadata, and `.gitignore`. Exclude caches, logs, backups, local profile state, credentials, personal resource IDs, and absolute machine paths.

The public backend must not depend on a developer's installed skill path or interpreter path. Use a portable Python module/entry point, `sys.executable`, `get_hermes_home()`, and `shutil.which()` as appropriate. Do not make a Bash launcher the only execution path; test native Windows execution as well as macOS.

Sample configuration should be disabled by default and profile-agnostic. Document the minimum Hermes version and live hook requirements. Verify fresh-process discovery and API-server behavior on both platforms; fake-context tests alone do not prove installation compatibility.

## Google Workspace and Gmail

Prefer the narrowest Google OAuth scopes for the actual feature. Calendar is simpler than Gmail; Gmail and broad Drive access can involve sensitive/restricted scopes, app verification, privacy-policy requirements, and possibly security-assessment obligations depending on the distribution and data flow.

Official references:

- https://developers.google.com/identity/protocols/oauth2/scopes
- https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification

Choose deliberately between:

- A shared OAuth client: better onboarding, greater publisher verification/compliance responsibility.
- Bring-your-own OAuth client: lower shared publisher burden, substantially worse onboarding.
- An IMAP/SMTP adapter such as Himalaya: provider-independent, but separate account setup and credential/keyring behavior.

Document exactly what email/calendar fields enter the model request, whether the selected provider is hosted, what remains local, and how the user disables each service.

## Suggested public architecture

For multiple services, prefer one profile-guarded workspace-prefetch plugin with service adapters and shared timeout/result/privacy code instead of unrelated per-service copies. Keep provider-specific adapters isolated so Google OAuth, IMAP, Apple-local tools, and web APIs do not share credentials or assumptions.

Recommended release order:

1. Portable read-only Calendar adapter.
2. Gmail metadata/snippet search with explicit OAuth scope and egress disclosure.
3. Drive/Contacts only after least-privilege scopes are settled.
4. Optional Himalaya adapter for non-Google or provider-independent email.

## Acceptance matrix

For each adapter, test:

- approved profile → exactly one prefetch and one main model call;
- unapproved/unknown profile → no prefetch;
- unrelated request → no prefetch;
- mutation request → no prefetch and normal confirmation path remains;
- valid provider result → bounded context injected;
- timeout/auth/malformed result → fail-open fallback;
- user-controlled search text cannot become shell syntax or arbitrary command execution;
- fresh process after install/restart discovers the plugin;
- macOS and Windows path, subprocess, encoding, and timeout behavior pass;
- source/public-history scan finds no personal paths, tokens, private IDs, or local profile names.
