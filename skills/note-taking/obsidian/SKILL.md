---
name: obsidian
description: obsidian — Read, search, create, and edit notes in the Obsidian vault.
platforms:
- linux
- macos
- windows
---
# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

## Daily wrap-up workflow

For evening wrap-up work, follow the exact note structure, carry-forward handling, Todoist integration, monthly index update, and verification pattern below.

When you are writing tomorrow's daily note:
- Treat the requested structure as a contract; preserve heading order exactly.
- Populate carry-forward items from today's incomplete work and Todoist overdue items.
- If the note is managed by another process or opens with template scaffolding, verify the on-disk file after writing and again after a brief pause before reporting success.
- Prefer an atomic temp-file write + rename when a whole-note rewrite is clearer than incremental edits.

When doing the wrap-up itself:
- Build tomorrow's note without overwriting today's note.
- Follow the requested section order exactly; daily notes are contracts, not freeform summaries.
- Pull the carry-forward list from incomplete work and overdue Todoist items, then sort them into the correct task section for tomorrow.
- On weekends, omit the entire `### [Work]` section rather than leaving an empty placeholder.
- Update the monthly index under the correct `## Weekdays` or `## Weekends` section for tomorrow's actual day.
- If the monthly index contains a temporary placeholder or duplicate entry for tomorrow, replace it with the canonical link and remove the placeholder so the index stays clean.
- If a write tool warns that the file changed externally, re-read the file from disk before treating the edit as finished.
- If a note-tool snapshot still looks stale after a successful atomic rewrite, confirm with a direct filesystem read (`Path.read_text()` + `stat()`) before declaring failure.

- For exact-structure notes, prefer a whole-file rewrite over incremental patching when practical, then verify the final on-disk text line-by-line. If a rewrite is needed, use a temp file + atomic rename so the note cannot be left in a half-updated state.
- Verify the written note by reading it back before reporting success, and confirm there are no template leftovers such as placeholder bullets or stray `- None (or ...)` text.
- For macOS/BSD date math, use `TZ=America/Chicago date -v+1d ...` for tomorrow; GNU `date -d tomorrow` is not portable here.

## Session logs and continuity

When a session spans multiple projects, keep a broad **Daily Log** as the top-level continuity note and place project-specific detail in nested notes.

- Use the Daily Log for the cross-project summary of what was accomplished, what was learned, and what remains open.
- Put each project under its own subheading in the broad log, then link to deeper project notes for detail.
- If a project already has its own journal, keep that as the detail layer and link it back to the Daily Log.

