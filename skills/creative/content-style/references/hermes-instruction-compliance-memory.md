# Hermes instruction compliance and bounded memory

Condensed source notes for beginner-facing Reddit answers. Verify live documentation before quoting defaults because configuration and features can change.

## Core framing

- A natural-language rule is a soft control. Better prompts and stronger models improve compliance but do not provide certainty.
- A runtime control is only hard for the exact path it governs. Do not say “the model cannot bypass the gate” without checking alternate tools or routes.
- `approvals.mode: smart` uses an auxiliary model for low-risk approval decisions and therefore remains probabilistic. Manual approval, tool removal, filesystem permissions, and sandbox boundaries are stronger controls.
- The useful principle is: make prohibited actions impossible where practical and make required outcomes observable everywhere else.
- An assistant saying “done” or “I followed the rule” is not evidence. Prefer tests, readback, screenshots, tool logs, or independent verification.

## Recommended beginner answer order

1. Give the direct answer: perfect prompt obedience is impossible.
2. Distinguish prompt instructions from runtime enforcement.
3. Explain that enforcement must cover every route to the protected action.
4. Give a short layered setup: SOUL/AGENTS rules, skills, restricted tools, acceptance criteria, verification.
5. Explain memory using separate storage roles rather than implementation jargon.
6. Close with the limitation: bounded and reviewable does not mean infallible.

## Built-in memory facts

Source: Hermes docs, Persistent Memory and Configuration pages.

- Default `MEMORY.md` limit: 2,200 characters, approximately 800 tokens.
- Default `USER.md` limit: 1,375 characters, approximately 500 tokens.
- Both are injected into the system prompt as a frozen snapshot at session start.
- Writes persist to disk immediately, but the injected copy does not change until the next session. This preserves prefix caching.
- Overflow does not auto-compact or silently evict entries. The write returns an error and exposes current entries for consolidation or removal. A longer `replace` can also overflow.
- Exact duplicates are deduplicated as a successful no-op; do not describe them as rejected errors.
- `memory.write_approval: true` stages writes for user review before applying them.
- Session history is stored in SQLite (`~/.hermes/state.db`) with FTS5 and retrieved on demand through `session_search`; it is not injected wholesale into every prompt.
- Practical division: memory = compact durable facts; skills = procedures; session search = detailed historical context.

## Avoid these overclaims

- “Gates guarantee obedience.” They only enforce covered paths.
- “Memory updates are unavailable until restart.” Disk state updates immediately; only the system-prompt snapshot is frozen.
- “Duplicates are rejected.” They are skipped without adding another entry.
- “Bounded memory prevents bad memories.” It limits prompt bloat and provides correction controls; stale or incorrect entries remain possible.
- “A judge proves compliance.” A model judge is another probabilistic check unless backed by deterministic acceptance tests.

## Authoritative pages

- https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
- https://hermes-agent.nousresearch.com/docs/user-guide/configuration
- https://hermes-agent.nousresearch.com/docs/user-guide/security
