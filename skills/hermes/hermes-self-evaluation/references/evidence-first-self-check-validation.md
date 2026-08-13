# Evidence-First Validation of Hermes Self-Check Findings

Use this before accepting or implementing recommendations from a Hermes self-check.

## 1. Separate symptom, interpretation, root cause, and proposal

For every finding, record:

- **Observed evidence:** exact query, path, command, timestamp, and value.
- **Interpretation:** what the evidence proves and what it does not.
- **Root cause:** confirmed producer or configuration path, not correlation.
- **Proposed change:** a verified control that governs the affected subsystem.
- **Verification:** the exact check that would prove the change worked.

An external model may detect a real anomaly while proposing the wrong cause or fix. Never implement a recommendation merely because the symptom is real.

## 2. Resolve profile-local state

Do not assume all profiles share one session store or configuration.

- Default profile commonly uses `~/.hermes/state.db`.
- Named profiles commonly use `~/.hermes/profiles/<name>/state.db`.
- Resolve the current profile inventory and applicable paths live.
- Label the source profile in every aggregate.
- Inspect `.schema sessions` and `.schema messages` before relying on columns.

## 3. Session lifecycle semantics

- `sessions.ended_at IS NULL` means the row is open in database lifecycle terms.
- Total retained rows are not active sessions.
- Gateway routing entries represent resumable mappings, not proof of an executing process.
- Long-lived messaging rows may be legitimate resumable conversations.
- Detached CLI, TUI, API, cron, or subagent rows require age-aware review and producer identification.
- Session retention generally applies to ended rows. Verify current behavior before recommending pruning or finalization.

Starter query:

```sql
SELECT source,
       COUNT(*) AS open_rows,
       MIN(started_at) AS oldest,
       MAX(started_at) AS newest
FROM sessions
WHERE ended_at IS NULL
GROUP BY source
ORDER BY open_rows DESC;
```

When counts spike, inspect first user messages and source metadata to identify the producer. Do not blame cron, gateway, or delegation without evidence.

## 4. Memory is layered

Audit each configured persistence layer independently:

1. Built-in profile memory files, if enabled.
2. The active memory provider from `hermes memory status`.
3. Provider-specific health or statistics commands that are explicitly read-only.
4. Profile-local versus shared or external memory paths.

Do not infer that learning is lost because one layer is empty. Report each layer as populated, empty, unavailable, disabled, or stale. A read-only audit must not consolidate, delete, rewrite, or migrate memory.

## 5. Validate proposed controls

Before recommending a key or command:

- Confirm it exists in current CLI `--help`, official documentation, or source.
- Confirm it controls the observed subsystem.
- Confirm whether it is global, profile-local, session-local, or platform-specific.
- Confirm whether it requires a new session, gateway restart, or no restart.
- Check whether the feature is enabled; a retention value may do nothing when the corresponding automation is disabled.
- Keep checkpoint retention separate from session lifecycle.
- Keep profile-scoped rollout separate from global rollout.
- Use redacted dry-runs when available.

Do not invent convenience keys or preserve stale syntax from an older release.

## 6. Delivery drift

A successful task run with a delivery error is not fully healthy. Separate:

1. Scheduler invocation.
2. Task execution.
3. State or watermark advancement.
4. Delivery to the exact configured destination.

If Hermes falls back to another chat or parent channel, report the intended and actual destinations separately. Fallback success is not destination correctness.

## 7. Tool and transport evidence

- A tool error can be a secondary symptom rather than the root cause.
- A process exit code proves transport completion, not artifact correctness.
- Repeated exact tool-call IDs are stronger replay evidence than high call volume.
- Stale logs or persisted rows are not current process evidence.
- Verify external side effects with readback from the destination.

## 8. Safe read-only boundaries

Self-checks may inspect status, CLI help, schemas, databases, file measurements, logs, configuration readback, process state, and storage signals.

They must not, without explicit authorization:

- restart or stop services;
- prune, finalize, vacuum, or migrate session stores;
- consolidate, delete, or rewrite memory;
- change provider, model, plugin, tool, or profile configuration;
- alter delivery destinations;
- publish, post, pay, or delete remote data.

Surface the evidence and the narrowest next action.

## Finding rubric

Classify each candidate finding:

- **Confirmed:** observation and root cause are supported; the control surface is verified.
- **Observed, cause unconfirmed:** symptom is real but producer or cause remains uncertain.
- **Configuration-dependent:** claim may be valid only under a verified setting or profile.
- **Stale:** based on old schema, old config, or superseded behavior.
- **Rejected:** contradicted by current evidence.

Only confirmed findings should become automatic changes. Everything else remains review-gated.