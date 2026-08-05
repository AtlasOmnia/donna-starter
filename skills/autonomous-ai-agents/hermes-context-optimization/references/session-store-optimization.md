# Session-store search-index optimization

Use when `~/.hermes/state.db` is large, session search is sluggish, or the user runs `hermes sessions optimize-storage`.

## Safe workflow

1. Run the requested command normally first:
 ```bash
 hermes sessions optimize-storage
 ```
 Read its disk-space preflight rather than guessing requirements. A full run includes SQLite `VACUUM` and generally needs free space roughly comparable to the database size.

2. If the preflight refuses for insufficient VACUUM headroom, use Hermes' supported index-only path:
 ```bash
 set -o pipefail
 printf 'y\n' | hermes sessions optimize-storage --no-vacuum
 ```
 `--no-vacuum` rebuilds and compacts the FTS search index but does not physically shrink `state.db`. A later full VACUUM is still required to return free pages to the filesystem.

3. Large stores can exceed a foreground tool timeout. The operation is resumable, so move it to a tracked background process rather than repeatedly losing it to foreground limits:
 - launch with `terminal(background=true, notify_on_complete=true)`;
 - monitor with `process(wait)` / `process(poll)`;
 - do not use shell `nohup`, trailing `&`, or an untracked process.

4. Progress can reach `100% (0/0)` and then remain at `Reclaiming old index…` for several minutes. That is a real cleanup phase, not proof of a hang. Keep the tracked process running unless it exits or shows an error.

5. If a foreground timeout interrupts the command, rerun the same Hermes operation once under the tracked-background pattern. Hermes resumes from its checkpoint (for example, from 90% or directly at 100%) rather than rebuilding from zero.

6. Require a successful terminal result:
 ```text
 ✓ Search index optimized.
 Database size: BEFORE -> AFTER (reclaimed N MB)
 ```

7. Verify the canonical store remains readable:
 ```bash
 hermes sessions stats
 ```
 Record session/message counts and database size. Do not claim disk reclamation when the command reports `reclaimed 0.0 MB`; index optimization and filesystem shrinkage are separate outcomes.

## Reporting

State clearly:
- whether the search index completed;
- whether `--no-vacuum` was used;
- whether physical space was reclaimed;
- what external prerequisite remains for a later full VACUUM (current preflight-required free space, not a stale hardcoded number).
