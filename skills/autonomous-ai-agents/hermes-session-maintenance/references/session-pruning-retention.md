# Session pruning and retention notes

Captured from a Hermes maintenance conversation about whether session history has a 90-day cap and whether to enable 30-day auto-prune.

## Facts verified in-session

- `hermes sessions prune --help` reports:
 - `--older-than OLDER_THAN`: delete sessions older than N days.
 - Default is 90 days.
 - `--source SOURCE` can restrict pruning to one source.
 - `--yes` skips confirmation.
- The active config had:
 - `sessions.auto_prune: false`
 - `sessions.retention_days: 90`
 - `sessions.vacuum_after_prune: true`
- Therefore 90 days was a default/manual retention value, not an active hard cap.
- The session database stats at the time were:
 - 35,417 sessions
 - 395,659 messages
 - 28,071 CLI sessions
 - 1,661 Telegram sessions
 - 9 Discord sessions
 - 6,729.3 MB database size

## Recommendation pattern

For a multi-GB session DB where most bloat is CLI session history, recommend 30-day auto-prune unless the user specifically needs long-term transcript search.

Suggested flow:

```bash
hermes sessions stats
hermes sessions export ~/hermes-sessions-backup-$(date +%Y%m%d).jsonl
hermes config set sessions.auto_prune true
hermes config set sessions.retention_days 30
hermes sessions prune --older-than 30
hermes sessions stats
```

Use `--source cli` if the user wants to preserve messaging history longer than terminal scratch work.

## Communication note

For the user, make the recommendation directly and briefly. Include the practical tradeoff: old conversations beyond retention stop being searchable/resumable, but memory/skills/config/cron/jobs/files are unaffected.
