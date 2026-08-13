# Privacy-safe diagnostic and Support Report review

Use this checklist for desktop applications that export a diagnostic bundle a user may share with support.

## Authority and data flow

- Generate the report in the trusted main process. Renderer IPC should be payload-free or accept only an exact empty object; the renderer must never submit report fields, logs, paths, or diagnostic bodies.
- Wrap the channel in the same privileged-sender validation as other sensitive IPC.
- Main owns the save dialog, fixed filename, serialization, size check, atomic write, and restrictive file mode where supported.
- Cancellation is a normal result. Renderer-facing failures use stable sanitized codes/messages.

## Exact allowlist

Define a versioned schema with exact keys and bounded enum/boolean/integer/timestamp values. Good candidates are:

- report schema and application version classes;
- coarse OS/runtime class (not hostname, username, machine ID, locale-derived identity, or home path);
- consent version/state and coarse readiness/configuration enums;
- schema/migration health codes;
- bounded counts and last-occurrence timestamps for canonical diagnostic codes.

Reject or make structurally impossible:

- raw `Error`, stack, log line, arbitrary metadata, environment variable, raw provider/model body;
- prompt, transcript, learner response/content, source text/excerpt, citation body;
- filename/path, source title, model-local identifier, hostname, username, device/account/session ID;
- credential, token, endpoint containing identity, or renderer/database dump.

Do not sanitize a broad object and call the residue safe. Construct the report from typed allowlisted primitives. Deep-freeze or clone-and-validate the final structure, cap diagnostic entries/counts/timestamps and total serialized bytes, and reject unknown keys.

## Diagnostic recorder

- Recording APIs accept only a closed diagnostic-code union; no `unknown`, `Error`, message, context, or metadata parameter.
- Store bounded counters and coarse timestamps only. Cap map size and counter growth.
- Map internal failures to codes at each trusted call site; keep sanitized console diagnostics separate from the report store.
- Never derive a Support Report from logs, renderer state, transcripts, source tables, model responses, filesystem inventory, or exception serialization.

## UI and disclosure

Provide a reachable review/export control that says exactly what is included and excluded, that the file remains local until the user shares it, and that local deletion cannot delete provider-held data. Cover keyboard/focus, live status, disabled/busy state, 44px targets, reduced motion, light theme, and the minimum supported viewport.

Provider/source disclosures should be derived from canonical operation constants where possible. Distinguish the synthetic no-source-content preflight from source-bearing generation operations.

## Consent versioning

- Bump consent when purpose, destination, content classes, retention, or externally shared behavior materially expands.
- A wording clarification that accurately describes an already-consented flow does not automatically require a bump.
- Whichever decision is made, encode it in tests: current, stale, missing, review-open, acknowledge, and withdraw.

## Required adversarial tests

1. Exact schema keys and deterministic byte/count limits.
2. Malicious errors containing secrets, paths, control characters, source excerpts, prompts, transcripts, learner text, and raw provider bodies cannot enter serialized output.
3. Unknown diagnostic codes or arbitrary metadata are rejected at compile/runtime boundaries.
4. Approved renderer sender can request export but cannot influence content or path; unapproved sender is rejected.
5. Atomic write, restrictive mode where applicable, cancel, and write-failure behavior.
6. UI reachability, focus restoration, status/live region, and exact inclusion/exclusion disclosure.
7. Canonical validate registration plus production scans over generated preload/dist artifacts.

## Independent review discipline

A broad reviewer that exits after repeated context compression has produced no verdict, even when the implementation is green. Replace it with a bounded changed-range-only, read-only review that returns PASS/HOLD with a small finding cap. Then verify any finding against the exact final SHA and rerun the affected executable gates.
