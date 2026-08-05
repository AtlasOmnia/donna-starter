# Isolated Hermes worker store for live-DB contention

Use when tracked coding agents repeatedly end with `session_persistence_failed` or `Session DB append_message failed: database is locked`, while the repository handoff remains valid.

## Diagnose before changing anything

1. Confirm the exact failure in the profile's `logs/agent.log`; distinguish SQLite lock contention from disk exhaustion or corruption.
2. Check free space and run a read-only integrity/statistics probe. A large DB alone is not proof of corruption.
3. Use `lsof` on the **profile-specific** `state.db`, `state.db-wal`, and `state.db-shm`. Do not assume the default profile owns a named profile's store.
4. Identify every PID. Long-running gateway/TUI processes may be legitimate user sessions; do not terminate, restart, checkpoint, prune, optimize, or vacuum them without an explicit gate.
5. Reconcile the target worktree independently. Preserve valid RED tests or bounded dirty production work; session persistence failure does not imply repository loss.

## Safe bypass

When the live profile DB is healthy but lock-contended, run bounded coding workers with a fresh isolated `HERMES_HOME` on a filesystem with ample headroom:

```bash
ISO='/path/on-fast-disk/.hermes-worker-homes/<campaign>'
mkdir -p "$ISO"
chmod 700 "$ISO"
for name in config.yaml .env auth.json SOUL.md skills; do
 ln -s "/path/to/source-profile/$name" "$ISO/$name"
done
HERMES_HOME="$ISO" hermes sessions stats
chmod 600 "$ISO/state.db"
```

Use symlinks only after exact-target verification. The isolated home must not contain a copied live `state.db`, WAL, cron store, process registry, or gateway state.

## Persistence smoke

Before assigning repository writes, prove the isolated store can persist a complete turn:

```bash
HERMES_HOME="$ISO" hermes chat \
 --provider <provider> --model <model> --max-turns 3 --yolo -Q \
 -q 'Reply with exactly ISOLATED_OK and use no tools.'
HERMES_HOME="$ISO" hermes sessions stats
```

Require:
- exit 0 and exact expected answer;
- one new session with user+assistant messages;
- no `database is locked`, `session_persistence_failed`, or disk-I/O messages in the isolated logs;
- `lsof` proves the worker opened the isolated DB, not the live profile DB.

## Execution discipline

- Launch the implementation worker as a directly tracked process with `HERMES_HOME="$ISO"`; do not add `--profile`, which would select the profile's contended store again.
- Once RED evidence exists, minimize the worker's schema/context surface (for example `--toolsets terminal,file`) and use an implementation-only prompt instead of reloading broad orchestration skills.
- Queue later controllers serially behind the worker PID and give them the same isolated home. Give parallel read-only reviewers separate isolated homes; sharing one fresh DB simply recreates avoidable write contention.
- Keep one repository writer at a time.
- Treat linked credentials/config as a live boundary: symlinks avoid secret duplication, but an OAuth refresh or config write can still mutate the source profile through the link. For strictly read-only review this is usually acceptable; where hard isolation is required, use mode-`0600` copies and delete the temporary home after acceptance. Never print `.env` or `auth.json`.
- Use an artifact deadline: a live PID, API traffic, or expanding context is not progress. If no authorized production file, GREEN result, or commit appears within the bounded interval, terminate the degraded run and narrow the transaction rather than moving the ETA.
- During cancellation, verify that a queued launcher did not race into starting its child; reconcile owners again before replacement.
- Treat agent exit as transport completion only; independently verify commit, diff, tests, and clean status.
- Base ETAs on tangible repository artifacts and completed gates, not process uptime.
- Remove the isolated home only after the campaign closes and no process owns it. It may contain session transcripts and credential/config symlinks, so do not archive or publish it.

## What not to persist as doctrine

This is a contention bypass, not a claim that SQLite, named profiles, delegation, or the TUI are generally broken. Prefer normal profile execution whenever the profile store persists a smoke turn reliably.
