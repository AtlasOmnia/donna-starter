---
name: notes-automation-workflows
description: 'notes-automation-workflows — Automate bulk Apple Notes workflows: discovery, filtering, and scripted enrichment for links/photos.'
version: 1.0.0
author: Hermes Agent
license: MIT
platforms:
- macos
metadata:
 hermes:
 tags:
 - Notes
 - AppleScript
 - Apple
 - note-enrichment
 - macOS
category: productivity
---
# Notes Automation Workflows

Use this skill for scripted, repeatable Apple Notes operations that go beyond single-note edits.

## When to use

- "Review my notes from last N days" or periodic cleanup/triage tasks.
- Adding structured summaries to notes that contain links.
- Adding summaries for image/photo notes.
- Updating notes programmatically without manual, one-by-one edits.
- Creating a translated or otherwise transformed copy of a rich-text note while preserving its structure.

## When *not* to use

- Single small edits: use the `memo`/`Notes` interactive flow directly.
- Sensitive credential text cleanup: use explicit user confirmation before summarizing.
- Non-Apple notes sources (Obsidian, Notion, etc.)

## Prerequisites

- macOS Notes.app
- `osascript` available
- User has granted Automation access to Notes.app in
 System Settings → Privacy & Security → Automation
- Apple Notes has the target notes in a reachable account (usually iCloud)

### `memo` CLI reliability

The `memo` CLI tool frequently breaks after Homebrew/Python updates due to a stale interpreter path. Diagnose with `/opt/homebrew/bin/memo 2>&1` — typical error: *bad interpreter: No such file or directory*. Fix via `brew uninstall memo && brew install antoniorodr/memo/memo`. When broken, fall through entirely to AppleScript (see search section below).

## Searching notes reliably

**Title-only AppleScript query is the fastest, most reliable search method.** Use before any other approach:

```bash
# Search by title only — instant even with thousands of notes
osascript -e 'tell application "Notes" to get name of every note whose name contains "keyword"'

# Retrieve title + body of a single matched note (use sparingly)
osascript -e 'tell application "Notes" to set target to first note whose name contains "keyword"' \
 -e '{name:name of target, body:(body of target)}'
```

**Critical timing constraint:** Body access (`body of n`) iterated across every note in a large account **times out at 30s**. Title-only search has no this problem. Restrict full-body iteration to single-note retrieval or folder-scoped queries.

## Core strategy

For anything beyond one note, use **AppleScript first-pass enumeration + AppleScript updates**.
Avoid relying on `memo` index-based addressing for scripts.

For a single note that must be created and shown on screen, follow the quick-create procedure. It covers the `memo` bad-interpreter fallback, account/folder discovery, HTML-body creation, `show`/`activate`, and folder-scoped read-back verification.

### Reliable read/write path

Use AppleScript with `body` (not `plain text`) and `id`:

```applescript
tell application "Notes"
 set target to first note whose id is "<note-id>"
 set noteBody to (body of target) as string
 set noteAttachments to count of attachments of target
end tell
```

Prefer updating by `id` for correctness and stability.

## 14-day sweep pattern

When a user asks for the last X days, start with a filtered enumeration in AppleScript so every candidate is in-bounds before heavy processing.

```applescript
tell application "Notes"
 set cutoff to (current date) - (14 * days)
 set out to ""
 repeat with a in accounts
 set nset to (notes of a whose (modification date >= cutoff))
 repeat with n in nset
 set out to out & (id of n as string) & "\u001f" & (name of n as string) & "\u001f" & (count of attachments of n as string) & "\u001f" & ((body of n) as string) & "\n"
 end repeat
 end repeat
 return out
end tell
```

This keeps pagination/sort order issues out of the script and gives a stable candidate list.

## Classification rules used in enrichment workflows

After loading candidates, classify each note before writing:

1. **Link note**
 - URL regex appears in title or body (`http://` or `https://`).
2. **Photo/attachment note**
 - `attachments > 0`
 - stripped text body is minimal/noisy (`len(text) <= ~40`) or only boilerplate.
3. **Regular text note**
 - No actionable link
 - Non-empty readable text and no dedicated attachment-only signals

For link notes, summarize source content and prepend the note body with a single summary block.
For photo-only notes, prepend a concise photo summary block (or a clear placeholder if the image is inaccessible).

## Idempotent updates

Never duplicate summary blocks. Before writing, check if `body` already contains your summary marker, e.g.:

```applescript
if (body of target) does not contain "<b>Summary:</b>" then
 set body of target to ("<div><b>Summary:</b> ...</div><div><br></div>") & (body of target)
end if
```

## Content formatting requirements

- Keep all appended summaries as HTML and prepend via `body`.
- Wrap each inserted piece in `<div>` and separate entries with `<div><br></div>`.
- Keep summaries short and task-scoped (2–5 sentences max).

## Link-source handling

`web_extract` coverage varies by site. If a source is unsupported:

- record that as a blocker in the summary
- summarize from cached context only when allowed
- keep a clear label so the next pass can retry when source access improves

## Validation checklist

After writes, verify:

- expected notes in scope were touched
- link notes now include one summary block each
- photo/attachment-only notes are marked in a consistent format
- non-link/non-photo notes were not unexpectedly rewritten

