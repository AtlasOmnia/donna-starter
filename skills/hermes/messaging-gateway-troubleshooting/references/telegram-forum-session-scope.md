# Telegram forum `/sessions` scope diagnosis and repair

Use this reference when `/sessions` or `/resume` appears empty or unusable inside a Telegram forum topic even though the session database contains Telegram conversations.

## Diagnostic sequence

1. Correlate the user's command with `gateway.log` send timestamps and reply lengths.
 - The canonical empty-list reply is `No sessions found...`; matching its exact rendered length can identify the response when logs record only character counts.
2. Inspect the live session database, not conversation history:
 - `sessions.source`, `user_id`, `chat_id`, `thread_id`, `title`, and `origin_json`.
 - Compare the caller's parent chat and topic/thread against candidate rows.
3. Inspect the gateway routing mirror only as supporting evidence. It preserves live `SessionSource` origins (`platform`, `chat_id`, `user_id`, `thread_id`) and can explain why authorization differs between live-origin and persisted-only rows.
4. Trace both listing and resume authorization. A listing fix is incomplete if the displayed session still fails `/resume <id>`.
5. Treat unrelated warnings separately. A TUI-side `signal only works in main thread` traceback from MCP discovery is not evidence that Telegram `/sessions` failed unless its timestamp and call path actually intersect the gateway command handler.

## Root-cause pattern

Telegram forum topics have different `thread_id` values under one parent `chat_id`. Exact-thread authorization is safe but makes `/sessions` useless from a fresh topic: every older topic is filtered out.

The safe policy distinction is:

- Keep exact-thread matching as the default for all platforms.
- Add a Telegram-only sibling-topic path.
- Require both topics to have non-empty, different thread IDs.
- Require the same parent `chat_id`.
- Require explicit same-owner proof using the participant identity that session keying uses (`user_id_alt or user_id`).
- Do not interpret `thread_sessions_per_user=false` as permission to cross topic boundaries. Sharing applies within one topic, not across sibling topics.
- Preserve Matrix, DM, cross-chat, cross-platform, and cross-owner behavior.
- Apply the same policy to both live-origin and persisted-row authorization paths.

## TDD matrix

Create RED tests before production code for:

- same Telegram parent chat + same owner + sibling topic appears in `/sessions`;
- the listed sibling session is accepted by `/resume`;
- current session remains excluded;
- same-topic older session remains visible;
- different parent chat is blocked;
- different participant is blocked;
- persisted-only sibling session follows the same owner/chat policy;
- missing thread, same thread, and non-Telegram sources do not enter the sibling helper;
- existing Matrix and DM security tests remain green.

## Deployment and restart safety

- Implement in an isolated worktree when the live Hermes checkout is dirty; verify target files are untouched before applying the bounded patch.
- Preserve an update-safe patch artifact and register it in the local patch-recovery script when upstream still lacks the repair.
- Run focused gateway tests, `py_compile`, `git diff --check`, patch reverse-check, and recovery-script syntax checks.
- A gateway restart can interrupt gateway-owned long-running chat workers. Inspect the gateway process's live children before activation.
- Hermes may block `gateway restart` from a command executing inside the gateway process tree because SIGTERM would kill the command itself. Do not record this as a permanent feature limitation. Use a separately supervised external one-shot activation process only after active gateway-owned workers drain, and write a deterministic result artifact proving old/new gateway PIDs or the reason activation was withheld.
