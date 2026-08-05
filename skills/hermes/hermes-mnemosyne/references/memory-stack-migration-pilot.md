# Memory-Stack Migration Pilot

Use when someone has LCM, built-in Hermes memory, and a separate knowledge/memory system such as gBrain, and is considering Mnemosyne.

## Architecture decision

- **LCM/context engine:** active-session continuity, compaction, transcript recovery.
- **Mnemosyne/memory provider:** selective semantic memory across sessions.
- **Built-in USER.md and MEMORY.md:** small, always-loaded bootstrap facts.
- **Existing knowledge system:** temporary read-only archive during migration, not a permanent fourth writer unless it has a distinct proven job.

LCM and Mnemosyne are complementary. A disliked or unreliable incumbent memory system should not be retained indefinitely merely to avoid making a migration decision.

## Pilot sequence

1. Export and back up the incumbent system.
2. Clone a disposable Hermes profile.
3. Set an explicit profile-local `MNEMOSYNE_DATA_DIR` before the first memory-enabled smoke.
4. Install the current Hermes adapter using upstream instructions; verify `hermes memory status`.
5. Begin with supervised/manual writes and auto-sleep disabled.
6. Test 20–50 memories across several sessions.
7. Include corrections, negation, expiry, two similar entities, invalidation, and an instruction containing “whenever.”
8. Measure correct recall, false recall, stale recall, misses, provenance, and latency.
9. Enable consolidation only after source ranking and corrections remain trustworthy.
10. Retire the incumbent writer if Mnemosyne wins; keep an archive for rollback.

## July 26, 2026 issue snapshot

Verified against `mnemosyne-oss/mnemosyne` at review time:

- #507 instruction extraction can invert “whenever” into “never”; referenced #508 did not exist.
- #506 sleep summaries may outrank source memories.
- #482 reports many ignored config keys.
- #537 reports Hermes runtime repair removing externally installed provider packages while data survives.
- #523–#525 cover cache, invalidation-reporting, and expiry defects.
- #327 and #370 cover gateway identity scoping and historical-session import gaps.
- PRs #541, #545, #531, and #521 were open; status must be rechecked live before relying on them.

This is a dated evidence snapshot, not a permanent claim. Recheck repository status and official Hermes documentation before a new migration.

## Update recovery

Before an update, back up the database and record provider status. Afterward verify the provider adapter, database path, stats, and one write/recall smoke before trusting production memory.
