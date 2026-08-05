# Context-overflow recovery

## Trigger

Use this reference when Hermes reports one or more of:

- `Context length exceeded`
- `Max compression attempts reached`
- `Context length exceeded and cannot compress further`
- `compression is currently blocked (ineffective)`

This is a recovery boundary for the affected session. It is not, by itself, evidence of a gateway outage, Telegram topic corruption, project-data loss, or application failure.

## Recovery procedure

1. Read the live status/log boundary once. If Hermes has already exhausted its compression attempts, stop retrying `/compress` in that session.
2. Preserve the old session. Do not use destructive session deletion commands.
3. For Telegram private-chat topics, send `/new` inside the affected topic. Hermes documents this as resetting the current topic's session with a new session ID and fresh history without touching other topics.
4. Do **not** use `/resume` or `/topic <old-session-id>` as the recovery mechanism. Those commands are for restoring the old session and can reintroduce the oversized transcript.
5. Give the fresh session a compact handoff containing:
 - the current checkout and incumbent-writer check;
 - the last verified artifact/test/runtime boundary;
 - the single remaining gate;
 - explicit exclusions and human gates;
 - the evidence required before declaring completion.
6. Monitor the new session with `/context` or `/usage`; close it at a clean handoff boundary if it starts accumulating another oversized transcript.

## Authoritative behavior references

- Slash command reference: https://hermes-agent.nousresearch.com/docs/reference/slash-commands
 - `/new` / `/reset` starts a fresh session.
 - `/context` and `/usage` are read-only inspection surfaces.
- Telegram reference: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram#new-inside-a-topic
 - Each topic has an isolated history and context window.
 - `/new` inside a topic resets only that topic's session.
 - `/topic <session-id>` restores an existing session and is therefore the wrong choice for an unrecoverable oversized session.

## Verified incident pattern

An acceptance session reached approximately 255,557 tokens against a runtime context around 272,000 tokens. Hermes attempted compression repeatedly, then logged that the maximum compression attempts had been reached and that the context could not be compressed further. The live configuration had automatic model context detection (`model.context_length` unset), compression enabled, threshold `0.85`, target ratio `0.70`, and DeepSeek configured for auxiliary compression.

The gateway remained healthy and Telegram remained configured. The session history was still present in Hermes' session store. The correct recovery was a fresh topic session plus a short handoff, not gateway restart, repeated compression, or restoration of the oversized session.

The last verified boundary was:

- source fix and packaged candidate passed codesign and isolated launch;
- existing-file persistence passed at disk, SQLite, and UI layers;
- native Finder drag/drop remained HOLD because no destination file, SQLite row, or UI update was observed;
- the candidate app bundle was untouched and the candidate process was cleaned up.

That boundary is included only as a model for writing a compact handoff. Re-verify the current checkout, writer ownership, artifacts, and acceptance evidence before continuing any future task.