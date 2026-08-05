# Source-specific retention and one-time CLI clear

Session-derived operational notes for Hermes session maintenance.

## Split retention pattern

Global `sessions.auto_prune` only supports one retention window. For mixed usage where CLI scratch sessions are disposable but Telegram continuity matters, disable global auto-prune and schedule a source-specific script instead.

Known-good policy for the default profile:

- CLI: 15 days
- Telegram: 45 days
- Schedule: daily at 4:30 AM
- Script: `~/.hermes/scripts/prune-sessions-by-source.sh` (user-local — verify it exists)
- Log: `~/.hermes/logs/session-retention-prune.log`

Script shape:

```bash
#!/usr/bin/env bash
set -euo pipefail
HERMES="~/.hermes/hermes-agent/venv/bin/hermes"
LOG="~/.hermes/logs/session-retention-prune.log"
mkdir -p "$(dirname "$LOG")"
{
 echo "[$(date '+%Y-%m-%d %H:%M:%S')] Source-specific session prune started"
 "$HERMES" sessions prune --older-than 15 --source cli --yes
 "$HERMES" sessions prune --older-than 45 --source telegram --yes
 echo "[$(date '+%Y-%m-%d %H:%M:%S')] Source-specific session prune complete"
} >> "$LOG" 2>&1
exit 0
```

Cron creation uses a relative script path, not an absolute path:

```bash
# script must live under ~/.hermes/scripts/
# cron script value: prune-sessions-by-source.sh
```

Use `no_agent=true` and `deliver=local` so a successful maintenance prune stays silent.

## One-time CLI clear caveat

`hermes sessions prune --older-than 0 --source cli --yes` does not necessarily clear all CLI sessions. In practice it may prune only a small subset because many CLI sessions have `ended_at IS NULL` and are therefore treated as active/unended by the pruner.

When the user explicitly asks for a one-time clear of all CLI sessions, the practical approach is:

1. Preserve/keep the newest current CLI session so the active turn can finish.
2. Stop gateway/dashboard processes that hold `~/.hermes/state.db` open if needed.
3. Directly delete messages and sessions for `source='cli'` except the kept newest session.
4. Restart gateway/dashboard.
5. Run `VACUUM` and `PRAGMA wal_checkpoint(TRUNCATE);` after locks are clear to reclaim disk.
6. Verify with `hermes sessions stats` and a direct source count.

SQLite outline:

```sql
-- Determine newest/current CLI session first:
SELECT id FROM sessions WHERE source='cli' ORDER BY started_at DESC LIMIT 1;

PRAGMA foreign_keys=OFF;
BEGIN IMMEDIATE;
CREATE TEMP TABLE cli_delete_ids AS
 SELECT id FROM sessions WHERE source='cli' AND id <> '<KEEP_ID>';
DELETE FROM messages WHERE session_id IN (SELECT id FROM cli_delete_ids);
DELETE FROM sessions WHERE id IN (SELECT id FROM cli_delete_ids);
COMMIT;
PRAGMA wal_checkpoint(TRUNCATE);
```

Then, once gateway/dashboard locks are released:

```sql
PRAGMA wal_checkpoint(TRUNCATE);
VACUUM;
PRAGMA wal_checkpoint(TRUNCATE);
```

Verification queries:

```sql
SELECT source, COUNT(*) FROM sessions GROUP BY source ORDER BY source;
SELECT COUNT(*) FROM messages WHERE session_id IN (SELECT id FROM sessions WHERE source='cli');
```

## Safety boundaries

- Do this only on explicit user request; it is destructive.
- Preserve the current/newest CLI session unless the user explicitly says to wipe absolutely everything and accepts interrupting the active CLI session.
- Telegram sessions are independent and should not be touched when the request is only CLI cleanup.
- Session pruning/deletion does not affect memory, skills, cron jobs, project files, vault notes, or Telegram's own retained chat history.
