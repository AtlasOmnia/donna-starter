# Live API-Server Plugin Contract Validation

Use this procedure when a Hermes backend plugin must be callable through the OpenAI-compatible API server and must receive trusted, server-owned session context. Source inspection or an in-process registry unit test is not sufficient.

## Contract to prove

The live chain must be demonstrated end to end:

1. The API adapter reads `X-Hermes-Session-Id` from the request.
2. Hermes creates or resumes the server-side agent with that session ID.
3. Tool execution dispatches through the registry with runtime kwargs.
4. The plugin handler receives `session_id` from Hermes-owned kwargs—not from caller-controlled tool arguments.
5. The response remains correctly associated with the same server session.

Never add `session_id` to the plugin's public tool schema merely to make a test pass. That converts trusted runtime context into caller-controlled input.

## Preflight

1. Resolve the active `HERMES_HOME` from the actual launcher/service environment. On Windows it may be under `%LOCALAPPDATA%` while a separate `%USERPROFILE%\.hermes` checkout also exists.
2. Inspect config structure without printing secret values. Record only key presence and length.
3. Confirm the supported user-scoped plugin directory and the plugin manifest/toolset name.
4. Confirm the API platform's actual toolset allowlist. Plugin discovery does not imply API exposure; `platform_toolsets.api_server` must include the plugin toolset when the runtime uses platform-specific surfaces.
5. Trace the target runtime version's header-to-handler chain in source. Function names can differ across releases; follow the actual data flow rather than relying on one expected symbol name.
6. Back up config and record pre-change hashes before any live modification.

## Installation and restart

- Stage reviewed files into the active user-scoped plugin directory only.
- Apply the smallest config delta: enable the plugin and add its toolset to the API server surface.
- Keep credentials out of command lines, logs, and evidence files.
- Restart through the user's approved launcher/service path. Do not invent a second daemon path or leave an SSH-owned child process expected to survive logout.
- Verify the new process identity, listener, health endpoint, plugin discovery, and exposed tool surface before running contract probes.

## Required live matrix

Capture machine-readable evidence for each case:

- **Server-owned execution:** a normal request causes the model/agent to call the probe tool; evidence identifies the server process and plugin invocation.
- **Exact propagation:** a unique `X-Hermes-Session-Id` appears unchanged in plugin runtime kwargs and the response header/body where the API contract exposes it.
- **Argument rejection:** attempts to provide `session_id` as a public tool argument are rejected or ignored; the runtime value still comes from Hermes kwargs.
- **Streaming:** SSE completes correctly, exposes the expected session identity, and records the plugin result once.
- **Negative/auth:** missing or invalid API credentials and malformed/unsafe session headers fail closed without invoking the plugin.
- **Cancellation:** cancelling a request does not orphan work, duplicate a tool call, corrupt the session, or leave a stuck per-session resource.
- **Concurrency:** distinct session IDs remain isolated under concurrent requests; same-session behavior follows the documented serialization/continuity policy.
- **Restart persistence:** after an approved restart, the plugin remains discovered/exposed and a fresh request still passes exact propagation.
- **Lifecycle/cleanup:** temporary locks, probe state, and cancellation/concurrency resources return to the expected steady state.

A direct call to the registry or handler is useful rehearsal but does not satisfy the live gate.

## Evidence freeze

- Write bounded JSON artifacts with secrets redacted before serialization.
- Include runtime/process identity, config hash before/after, plugin file hashes, request case IDs, response status, response session ID, observed handler kwargs, invocation counts, timestamps, and cleanup state.
- Generate SHA-256 hashes on the target machine, copy artifacts to the controller, and independently recompute every hash.
- Keep machine-specific absolute paths and private endpoints out of committed documentation. Commit only portable contract statements, sanitized summaries, test fixtures, and expected evidence schemas.

## Stop conditions

Stop dependent product work and open a Hermes-core remediation plan when any of these is true:

- The API adapter accepts the header but the plugin receives no trusted `session_id` runtime kwarg.
- Session identity reaches the handler only through caller tool arguments.
- Streaming and non-streaming paths disagree on identity propagation.
- Cancellation or concurrency causes cross-session leakage, duplicate invocation, or persistent orphaned state.
- The plugin cannot remain exposed after restart through supported user-scoped configuration.

Do not substitute source reasoning, a mocked test, or plausible output for a failed live path.
