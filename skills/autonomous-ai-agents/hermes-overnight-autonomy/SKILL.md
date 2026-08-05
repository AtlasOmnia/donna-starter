---
name: hermes-overnight-autonomy
description: Use for unattended Hermes continuity and watchdogs.
version: 1.0.0
platforms:
- macos
- linux
- windows
metadata:
 hermes:
 tags:
 - hermes
 - kanban
 - overnight
 - autonomy
 - watchdog
 - recovery
 related_skills:
 - hermes-agent
 - kanban-orchestrator
 - automation-governance
---
# Hermes Overnight Autonomy

Use this skill when the user asks for Hermes projects to continue across the night, gateway restarts, worker failures, or 24/7 operation. The target is durable progress with bounded risk—not a tower of supervisors.

## Architecture decision

Use **Kanban as the durable execution kernel**:

- SQLite-backed cards preserve task bodies, dependencies, claims, heartbeats, run history, comments, retries, and circuit-breaker state.
- The gateway-embedded dispatcher is the normal scheduler and stale-claim reclaimer.
- Each unattended card has an explicit runtime cap, retry budget, named assignee, workspace, and acceptance contract.
- A separate OS-supervised watchdog provides liveness and alerting when the gateway or dispatcher is unavailable.
- Recovery remains disabled during calibration. Do not add a standalone Kanban daemon against the same board database or multiple competing relaunchers.

Kanban solves durable task lifecycle and dead-worker redispatch; it does not prove meaningful progress, resume in-memory reasoning, judge code quality, substitute models automatically, or survive total gateway loss by itself.

## Rollout stages

### Stage 0 — Read-only baseline

Before any mutation, collect:

1. Hermes version and live profile roster; never invent assignee names.
2. Gateway service state, launchd/systemd ownership, PID, and ticker/cron health.
3. Kanban board list, dispatcher configuration, board diagnostics, and current running tasks.
4. Existing watchdogs, rescue registries, cron jobs, launchers, and service labels; pause/avoid overlapping writers rather than creating duplicates.
5. Exact checkout/file ownership for every intended write surface.

Use the smallest existing empty board for a pilot when appropriate; do not create a second board merely to prove the lifecycle.

### Stage 1 — Disposable lifecycle pilot

Create one harmless card with:

- a real existing assignee;
- `workspace=scratch` unless repository work is explicitly required;
- a short runtime cap and one retry maximum;
- explicit instructions to show state, heartbeat, comment, and complete;
- no repository, credential, external-service, or configuration access.

Dispatch it through the board, then independently verify the run record, heartbeats, comment, completion summary, diagnostics, worker-PID release, and scratch cleanup.

### Stage 2 — Gateway acceptance

Confirm `kanban.dispatch_in_gateway` is enabled and the gateway is launchd/systemd supervised. A controlled gateway restart is a human approval gate; after approval, verify the service, ticker, active job count, and Kanban diagnostics. Do not claim restart resilience from a configuration read alone.

### Stage 3 — Alert-only watchdog

The watchdog is a one-shot deterministic collector supervised by the OS. It may read:

- all live Kanban board databases;
- running task status, worker PID, claim expiry, heartbeat age, runtime limit, and latest run status/outcome;
- gateway/dispatcher liveness;
- optional process/file/Git evidence needed to distinguish a live owner from an ownerless task.

It may write only its own lock and deduplication ledger. Healthy output must be exactly `[SILENT]`. New issues emit compact JSON with a stable `changed` flag; repeated unchanged issues do not notify again.

The collector must never kill, restart, reassign, block, complete, comment, launch, publish, or modify a project. A separate wrapper may send only new alerts through the supported direct `hermes send --to <platform>` CLI, reusing configured credentials without embedding secrets or requiring a running gateway.

### Stage 4 — Fail-closed recovery, only after calibration

Enable recovery only after synthetic failure tests prove the alert path and ownership model. Recovery must:

1. acquire one atomic expiring claim per campaign;
2. re-read the live registry and process tree after claiming;
3. require a bounded stale sample, not one quiet log read;
4. preserve dirty trees and all artifacts;
5. retire only the exact stale generation and its relaunch-capable parent/child chain;
6. dispatch one fresh, narrower successor with the remaining invariant;
7. allow at most one automatic resume before splitting to a fresh worker;
8. circuit-break and alert on repeated failure, missing assignee, credential/permission gates, merge conflicts, or human decisions.

A retry is not a resume. A replacement receives durable card context and filesystem checkpoints, not the failed worker's hidden chain of thought. Do not substitute models unless an explicit routing policy says which profile/model owns the replacement.

## Worker transaction contract

Every write-capable card should state:

- **One invariant:** the observable behavior that must become true.
- **Exact writable files:** everything else is read-only.
- **One focused gate:** the command that must go RED/GREEN or the deterministic acceptance probe.
- **One checkpoint:** local commit or verified artifact; no push/release unless separately approved.
- **No scope creep:** no broad discovery, plans, skill curation, credential edits, service restarts, or self-backgrounding unless explicitly part of the card.
- **Review gate:** implementation workers do not accept their own candidate; the controller reads the actual files/diff and reruns the gates.

If a worker remains in planning/inspection with no authorized file movement by the bounded midpoint, inspect the live process and log. Stop feeding the same context. Preserve valid work, retire the stale generation if justified, and create a fresh narrow repair card.

## macOS SQLite/WAL watchdog rule

Live Kanban databases may use SQLite WAL mode without persistent `-shm` sidecars. Two tempting read-only URI patterns are unsafe for this case:

- `immutable=1` can read a stale database and hide committed WAL content;
- URI `mode=ro` can fail to open a WAL database when SQLite cannot establish its shared-memory sidecar.

For a watchdog that issues only `SELECT`s, use a normal connection followed immediately by `PRAGMA query_only=ON`, then prove both live WAL visibility and write rejection in a temporary fixture. Do not execute journal-mode-changing pragmas in production.

## Kanban movement heartbeat — alert-only monitoring

Use this when the user explicitly requests recurring assessment of whether Kanban work is moving as intended. Treat it as **Stage 3 alert-only monitoring**, not recovery: the monitor may read board state, task graphs, run/heartbeat/claim evidence, dispatcher dry-run output, and OS process identity, but it must never kill, restart, reclaim, reassign, block, unblock, complete, comment, dispatch, or edit project state.

Use a two-layer design:

1. **Collector:** one-shot deterministic script. Enumerate every non-archived board from `boards list`, then issue board-scoped supported JSON CLI reads (`--board <slug> stats --json`, status-filtered `list --json`, `show --json`, and `dispatch --dry-run --json`). Never rely on whichever board happens to be current. Check ready-not-dispatched tasks, eligible `todo` cards that were not promoted, running cards whose run/PID/claim/heartbeat evidence disagrees, stale heartbeats/claims or explicit runtime overruns, malformed board reads, repeated dependency/block-loop histories, active dependency cycles/strongly connected components, and quiescent boards whose blocked/todo work has no runnable successor. Surface stale review, capability, or needs-input gates when they leave the board with no route forward. Verify the worker process command is actually bound to the task marker; PID existence alone is insufficient. Persist only an atomic deduplication ledger owned by the collector.
2. **Relay:** validate the collector sentinel/payload. Healthy or unchanged output must stay quiet. On a new `changed=true` issue, call the direct configured Hermes send CLI (for example `hermes send --to telegram --subject ... --quiet ...`) without printing credentials or subprocess output. Keep the scheduled job's own delivery local when the relay sends externally; otherwise a script-only job can forward a non-empty `[SILENT]` sentinel as user-visible noise.

Search existing enabled watchdogs and relay scripts before creating another one. Reuse a proven collector/relay when its coverage matches the request; do not create overlapping monitors for the same board. If a new movement-specific collector is needed, keep it separate from broad gateway/session watchdogs and use a stable idempotency key for any implementation card.

Acceptance requires independent verification, not only a worker summary: compile both scripts, run deterministic self-tests with temporary ledgers/fixtures, run the collector against the live board, run the relay against the live board without a synthetic alert, create the cron only after the artifact paths are released by their writer, and smoke the scheduler itself (`cronjob run` or equivalent) with an actual successful run readback. Preserve timeout/review events in Kanban history; controller-owned verification may close an implementation card only after the promised artifact and gates agree.

Do not call the monitor “24/7 recovery.” Automatic recovery is a separate, explicitly approved stage requiring process-tree, queued-successor, checkout/Git, and atomic-claim reconciliation.

## Scheduled watchdog ticks with bounded remediation

When a scheduled Kanban watchdog has an explicit per-tick prompt that authorizes a narrow remediation repertoire, treat that prompt as the live policy and use this skill for the control discipline. This is distinct from the alert-only collector mode above: the watchdog may perform only the prompt's named card actions, never general recovery.

1. Read the canonical watchdog prompt and its JSON ledger before touching the board. Use `kanban-overview` first, then board-scoped CLI reads; do not infer state from prior ticks.
2. Verify gateway liveness independently with the exact gateway process and recent dispatcher/housekeeping log activity. A live gateway with stale dispatcher output is an alert condition, not permission to restart it.
3. For every running card, `show` the card, verify heartbeat freshness against the prompt's threshold, and verify the spawned PID is live **and** its command contains the exact task marker. PID existence alone is insufficient.
4. Compare blocked event timestamps with the ledger's `last_tick`. Classify only newly blocked cards. A transient block is normally dispatcher-owned; before accepting that classification, run the prompt's runaway-recovery check for repeated `Recover:` chains or auto-decomposer duplicates.
5. A crash/timeout/gave-up card receives at most one ledgered re-drive for that block event: add the classification comment, then unblock once. If the same block recurs after that re-drive, leave it blocked and alert; do not create retry noise.
6. Create a bounded successor only when the prompt explicitly permits it and the blocker has a concrete, evidence-backed, low-risk fix. Inherit the assignee, keep writable scope and acceptance evidence exact, set the mandated retry/runtime/idempotency fields, and comment the successor link. A dependency that demonstrably landed is handled by commenting the evidence and unblocking the waiting card, not by creating a duplicate successor.
7. Preserve genuine human gates (credentials, permissions, approvals, publishing, payment, deletion, force-push, production deploy) with no board mutation. Alert only when the prompt's alert rules require it, deduplicated through the ledger.
8. For a board with zero running and zero ready but blocked/todo work, run `dispatch --dry-run --json` and inspect formal parent edges. Todo behind blocked/todo parents is correctly gated; report a graph defect only when all formal parents are done yet promotion still fails. Never promote manually just to create activity.
9. For a runaway recovery chain, archive only the exact chain descendants leaf-first, preserve the original root blocked, comment the verbatim deterministic error, record the chain, and always alert. Recheck after the prescribed dispatch cycles for regrowth.
10. Update only the watchdog ledger's timestamp/actions/alert dedupe state after verification. A healthy tick with no permitted board action or alert must emit exactly `[SILENT]`; do not turn ledger maintenance into a user-facing status report.

## Service installation and verification

For a macOS LaunchAgent:

1. Generate/verify the plist before loading it; keep the collector and relay paths explicit.
2. Create the dedicated log directory before bootstrap.
3. Run `plutil -lint`.
4. Confirm the label is not already loaded and that no competing service owns the same files.
5. Bootstrap only after review; then read back `launchctl print` and verify the actual `ProgramArguments`, interval, log paths, and exit code.
6. Confirm the RunAtLoad process exits cleanly and writes `[SILENT]` on a healthy board.
7. Reload after changing `ProgramArguments`; editing a plist on disk does not update an already-loaded service.

Keep the gateway watchdog and Kanban watchdog as separate labels with separate responsibilities. Never silently replace an existing broad monitor.

## Alert relay contract

The collector emits either:

- `[SILENT]`; or
- JSON containing `changed: bool` and `issues: list[dict]` (legacy strings may be tolerated).

The relay must:

- pass through `[SILENT]`;
- reject malformed payloads without sending;
- serialize structured issues deterministically;
- call `hermes send --to telegram --subject ... --quiet` only when `changed=true` and issues are nonempty;
- suppress repeated `changed=false` alerts;
- return nonzero on collector or delivery failure without printing subprocess output or credentials;
- provide a mocked self-test that proves healthy/no-send, new-alert/send-once, and repeated-alert/no-send behavior.

Do not send a real synthetic alert merely to prove the relay; test the command construction with an injected runner, and test the supported send command separately if needed.

## Final report

Report in this order:

1. **Yes/no status first** — distinguish accepted artifact, live service, and whole-product completion.
2. Exact artifact paths and service labels.
3. Real verification outputs: compile/self-test, live smoke, board diagnostics, launchd/systemd readback, and alert-log result.
4. What remains deliberately disabled or gated, especially automatic recovery.
5. Any blocked human gate or deferred overlap.

Do not call a watchdog “24/7 recovery” when it is only alert-only monitoring. Do not call a worker “done” from a clean process exit or its own summary without controller-owned artifact and gate verification.
