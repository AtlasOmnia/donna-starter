---
name: hermes-session-maintenance
description: 'hermes-session-maintenance — Maintain Hermes Agent session history: inspect size, export backups, prune old ended sessions, and configure safe auto-prune retention.'
version: 1.0.0
license: MIT
platforms:
- linux
- macos
- windows
metadata:
 hermes:
 tags:
 - hermes
 - sessions
 - pruning
 - maintenance
 - sqlite
 - retention
 related_skills:
 - hermes-agent
---
# Hermes Session Maintenance

Use this skill when the user asks about pruning Hermes sessions, session retention, session DB size, `hermes sessions prune`, `sessions.auto_prune`, `sessions.retention_days`, session export/backup, or whether old conversations should be capped.

## Operating principles

- Treat this as Hermes configuration/maintenance work. If broader Hermes setup or CLI behavior is involved, also load `hermes-agent` for authoritative command references.
- Do not assume retention policy from memory. Check live state before recommending destructive cleanup.
- Pruning is deletion. Prefer exporting a safety snapshot before the first aggressive prune or before reducing retention substantially.
- Distinguish default behavior from active behavior:
 - `hermes sessions prune` defaults to `--older-than 90`.
 - `sessions.retention_days` may also default to 90.
 - `sessions.auto_prune: false` means nothing is being deleted automatically.
- Only ended sessions are prune candidates; active sessions are not pruned.

## Standard workflow

1. Inspect current volume:
 ```bash
 hermes sessions stats
 ```
 Use total sessions, messages, per-source counts, and DB size to shape the recommendation.

2. Inspect prune command behavior when needed:
 ```bash
 hermes sessions prune --help
 ```

3. Check current config values:
 ```bash
 hermes config show
 ```
 If the summary output does not include the session settings, inspect the config file's `sessions:` block directly. Do not use `hermes config get`; this CLI supports `show`, `edit`, `set`, `path`, `env-path`, `check`, and `migrate`, not `get`.

4. Recommend retention based on actual size and user needs.
 - 90 days is conservative/default.
 - 30 days is reasonable when the DB is multi-GB and session search is mostly used for recent operational continuity.
 - Shorter than 30 days should usually be explicit user preference or a storage emergency.

5. Before first major prune, export a backup:
 ```bash
 hermes sessions export ~/hermes-sessions-backup-$(date +%Y%m%d).jsonl
 ```

6. Enable auto-prune if approved:
 ```bash
 hermes config set sessions.auto_prune true
 hermes config set sessions.retention_days 30
 ```

7. Reclaim space immediately with a manual prune:
 ```bash
 hermes sessions prune --older-than 30
 ```
 Add `--yes` only if the user has authorized non-interactive deletion.

8. Verify after pruning:
 ```bash
 hermes sessions stats
 ```

## Source-specific cleanup

When one channel is the bloat source, prune only that source:

```bash
hermes sessions prune --older-than 30 --source cli
hermes sessions prune --older-than 90 --source telegram
```

Use this when the user wants to preserve messaging history longer than CLI scratch sessions.

For ongoing split retention, do not rely on global `sessions.auto_prune` because it has one retention window and can prematurely prune the longer-lived source. Use a quiet script under `~/.hermes/scripts/` and a local no-agent cron job instead:

```bash
hermes config set sessions.auto_prune false
hermes config set sessions.retention_days 45 # documentation/default only when auto_prune is off
# ~/.hermes/scripts/prune-sessions-by-source.sh:
# hermes sessions prune --older-than 15 --source cli --yes
# hermes sessions prune --older-than 45 --source telegram --yes
```

Schedule it daily with `deliver='local'` and `no_agent=true` so it does not message the user unless it fails. Cron script paths must be relative to `~/.hermes/scripts/`, not absolute.

For the detailed split-retention pattern and one-time CLI purge procedure, see `references/source-specific-retention-and-cli-clear.md`.

## One-time CLI clears

When the user explicitly asks to clear all CLI sessions, first try the CLI pruner:

```bash
hermes sessions prune --older-than 0 --source cli --yes
```

Then verify. If many CLI sessions remain, check whether they are unended/active (`ended_at IS NULL`). The built-in pruner only removes prune candidates, so historical CLI sessions that were never marked ended may remain.

For an explicit destructive CLI-only clear, keep the newest/current CLI session, delete `messages` and `sessions` rows for other `source='cli'` sessions directly in `~/.hermes/state.db`, then checkpoint/VACUUM after stopping processes that hold the DB. Preserve Telegram/Discord/cron/subagent sessions unless separately requested. See the reference file above for the SQL and verification queries.

## Pitfalls

- Do not present the 90-day default as a hard cap. It is a default cutoff for pruning/retention, not an immutable limit.
- Do not say auto-prune is active just because `retention_days` is set. `sessions.auto_prune` must be true.
- Do not skip `hermes sessions stats`; the right recommendation depends on live DB size and source mix.
- The live session store is typically `~/.hermes/state.db`, not `~/.hermes/sessions.db`. If reclaiming disk space manually, inspect `state.db` and its `-wal`/`-shm` companions.
- SQLite may not physically shrink after pruning while Hermes CLI/gateway/dashboard processes hold `state.db` open. A WAL checkpoint may need gateway/dashboard temporarily stopped; a full VACUUM may still require all Hermes CLI sessions to exit. Do not leave a large `state.db-wal` behind after attempting VACUUM — run `PRAGMA wal_checkpoint(TRUNCATE);` once locks are clear.
- Do not imply memory, skills, cron jobs, notes, or project files are affected by session pruning. Session pruning affects session transcripts/state only.
- Do not over-explain when the user asks for a go/no-go recommendation. Give the recommendation, the tradeoff, and the exact commands.
- For the user, session-retention questions usually want a direct recommendation first, not a long policy discussion. If live stats show a multi-GB DB and mostly recent operational use, recommend 30 days with auto-prune; mention 45 days as the conservative alternative and 90 days only for deliberate archive-style use.

## Session forensics: token burn, suspected loops, and runaway turns

Use this skill not only for pruning/retention, but also when the user says a session "looped," burned too many tokens, felt unusually slow, or may have resent content repeatedly.

### Fast diagnostic workflow

1. Read the session from the DB and identify whether the waste came from:
 - repeated assistant/tool turns inside one user request,
 - duplicate gateway delivery,
 - oversized skill/tool payloads,
 - or a genuinely long final answer.
2. Check session totals in `state.db`:
 ```bash
 sqlite3 ~/.hermes/state.db <<'SQL'
 .headers on
 .mode column
 SELECT id, source, title, model, input_tokens, output_tokens,
 cache_read_tokens, reasoning_tokens, api_call_count, message_count,
 datetime(started_at,'unixepoch','localtime') AS started,
 datetime(ended_at,'unixepoch','localtime') AS ended
 FROM sessions
 WHERE id='SESSION_ID';
 SQL
 ```
3. Inspect per-message shape to see the turn pattern and tool payload sizes:
 ```bash
 sqlite3 ~/.hermes/state.db <<'SQL'
 .headers on
 .mode column
 SELECT id, role, tool_name, tool_call_id, length(COALESCE(content,'')) AS content_len,
 datetime(timestamp,'unixepoch','localtime') AS ts
 FROM messages
 WHERE session_id='SESSION_ID'
 ORDER BY id;
 SQL
 ```
4. Check gateway timing/delivery behavior:
 - look for `inbound message`, `response ready`,
 - and especially `Suppressing normal final send ... content_delivered=True`.
 That pattern usually means streaming already delivered the final answer once, so the problem was not duplicate send.
5. Attribute blame precisely:
 - large `skill_view` payloads,
 - multiple overlapping `web_search` / `web_extract` calls,
 - repeated assistant-empty/tool turns,
 - or unnecessary env dumps for simple lookup questions.

### What to conclude

- If gateway logs show one inbound and one `response ready`, with `content_delivered=True`, call it an internal tool-call cascade or context-growth problem — not a transport resend loop.
- If a single loaded skill or search result dominates payload size, call that out explicitly. Quantify it.
- Distinguish input-token burn from output-token size. Often the answer is short; the cost came from replaying tool results back into the model.

### Pitfalls

- Do not call every high-token session a "loop." Many are just over-eager research/tool fan-out.
- Do not blame Telegram delivery when gateway logs show suppression of duplicate final send.
- Do not stop at `session_search()` if the user is asking about token burn. Use `state.db` and `gateway.log` so the diagnosis is grounded.
- Do not save transient missing-binary issues as durable skill knowledge. The durable lesson is to avoid loading bulky skills or fanning out searches unnecessarily when a cheap-first path would answer the question.

### Cheap-first guidance to recommend after diagnosis

For lightweight link-analysis or one-question sessions:
- prefer one direct extract/read path first,
- avoid loading a full skill unless the tool is truly needed for writes or auth-specific operations,
- cap redundant searches,
- and use minimal env queries for session-ID lookups instead of broad dumps.

See also: `references/session-forensics-token-burn.md`.

## References

- `references/session-pruning-retention.md` — condensed notes from the session where 30-day auto-prune was evaluated against a 6.7GB session DB.
- `references/session-forensics-token-burn.md` — diagnosing whether a session burned tokens because of duplicate delivery, internal tool cascades, or oversized tool payloads.
## Public support files

- `references/session-forensics-token-burn.md`
- `references/session-pruning-retention.md`
- `references/source-specific-retention-and-cli-clear.md`
