---
name: daily-note-wrapup
description: daily-note-wrapup — Create, verify, and index daily wrap-up notes in an Obsidian vault.
platforms:
- macos
- linux
- windows
---
# Daily Note Wrap-Up Workflow

Use this skill for evening wrap-up work that creates tomorrow's daily note and updates the monthly daily-note index.

## Core rules
- Treat the requested daily-note structure as a contract; preserve section order exactly.
- Carry forward incomplete work into tomorrow's note.
- On weekends, omit any work-specific section (for example `### [Work]`) entirely rather than leaving an empty heading or placeholder bullet.
- If a section has nothing to place, follow the user's exact omission rule for that section rather than inventing filler text.
- Keep today's note untouched; only create or update tomorrow's note and the monthly index.
- Serialize all mutations to the same file. Never launch parallel patches against one note or monthly index; combine related edits into one cohesive patch when practical, or patch sequentially with a read-back between changes.

## Structure gotchas
- The daily note template is not a generic form: match the user's requested headings and ordering exactly, including weekend-only omissions.
- Do not leave a blank `### [Work]` heading on weekends; remove the section entirely.
- Use `None` only where the requested structure explicitly asks for it (for example, `Waiting / Blocked`), and omit empty sections otherwise.

## Recommended workflow
1. Determine today's date and tomorrow's date in the relevant timezone.
2. Read today's daily note and extract useful context from `## Log` and `## Wins`.
3. Gather carry-forward items from incomplete work and overdue Todoist items. Treat these as independent inputs: unchecked items in today's note still carry forward even when Todoist returns no matches. Before interpreting an empty Todoist result as "nothing due," confirm that the command actually applied date/filter semantics rather than literal keyword matching; preserve the command evidence, but do not silently discard known pending work.
4. Write tomorrow's daily note with the exact requested structure.
5. Update the monthly index for the target month under the correct `## Weekdays` or `## Weekends` section.
6. Read both files back from disk before reporting completion.
7. If the on-disk note looks stale, reordered, or partially replaced, rewrite the whole file through a sibling temp file + atomic rename and then re-read before trusting the result.
8. If the atomic replacement still snaps back after a delay, stage the intended note, then run `scripts/atomic-note-replace-verify.sh <intended-note> <target-note>`. It atomically replaces the target, protects the new inode while a stale one-shot writer abandons its write, clears protection safely, and proves byte stability for 30 seconds locked plus 20 seconds unlocked. Afterward, separately validate the note's required headings/content and the monthly index.

## Verification
- If there is no canonical test or build command, create a temporary verification script under `tempfile.gettempdir()` with a `hermes-verify-` filename prefix.
- Run the script against the on-disk note contents, then remove it when finished.
- Report this as ad-hoc verification, not a green test suite.
- After writing, verify the actual file on disk, not just the write tool response. If a note read-back looks stale or mismatched, do not trust the snapshot; confirm with a direct filesystem read (`Path.read_text()` / `stat()`) and, if needed, perform an atomic temp-file rewrite before declaring success.

## Monthly index cleanup
- Add the target day's wikilink under the correct weekday/weekend section.
- If a placeholder or draft link exists for the same date, replace it with the canonical wikilink.
- Do not leave duplicate entries for the same day.

## Pitfalls
- Whole-note rewrites are often safer than fragile incremental edits when the target structure must be exact.
- A note that looks correct in a write response still needs a filesystem read-back.
- Treat a concurrent-modification warning followed by an immediate read-back of the old template scaffolding as evidence of an active stale writer. Do not retry another ordinary live-file rewrite; move directly to the sibling-temp atomic replacement and bounded immutable-hold procedure (see the script and the notes above).
- Verify the daily note and monthly index independently: a stale writer may revert the note while the index update remains correct.
- If another process may be touching the note, verify the final on-disk text rather than trusting an intermediate snapshot.

## Support files
- `scripts/atomic-note-replace-verify.sh` — reusable macOS atomic replacement with cleanup traps and 30-second locked plus 20-second unlocked SHA-256 stability checks.
## Public support files

- `scripts/atomic-note-replace-verify.sh`
