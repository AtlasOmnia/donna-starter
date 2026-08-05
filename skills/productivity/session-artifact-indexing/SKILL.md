---
name: session-artifact-indexing
description: session-artifact-indexing — Create a durable index of documents, links, and files produced during multi-step sessions so the user can find them later.
version: 1.0.0
license: MIT
tags:
- productivity
- notes
- session-wrapup
- apple-notes
- file-indexing
metadata:
 hermes:
 tags:
 - productivity
 - notes
 - session-wrapup
 - apple-notes
 - file-indexing
 related_skills:
 - apple-notes
 - obsidian
---
# Session Artifact Indexing

Use this skill when a session creates or references several documents, trackers, plans, templates, source links, or skills that the user may need later.

Primary trigger phrases:
- “I lose track of things”
- “put the links somewhere”
- “make a note”
- “save the documents from this session”
- “where are the files from this?”
- Any multi-step work that creates 3+ durable files and ends with a natural handoff/checkpoint

The goal is not to duplicate all work. The goal is to create one clean index that the user can open later.

## Default Destination

For Apple Notes, use the user’s dedicated assistant folder:

`⭐ Hermes - Assistant`

If the task is explicitly Obsidian-first, use the relevant vault note instead. If the user asks for Apple Notes, use Apple Notes.

## What to Include

Create a titled note with grouped links:

1. Main planning / brainstorm docs
2. Working files / trackers
3. Templates
4. Skills created or updated
5. Existing reference files used
6. External public-source links
7. Current priority / next step, if the session established one

Use:
- `file://` links for local files
- normal `https://` links for web sources
- readable labels, not raw path dumps only

## Apple Notes Creation Pattern

For large note bodies, write an AppleScript file first and then run it with `osascript`.

Do not inline long AppleScript with HTML through a single shell command if the body contains `&` or `&amp;`; command safety scanning may interpret ampersands as shell backgrounding. Writing the script file first is cleaner and avoids false positives.

## Verification

Always verify the note exists before reporting success:

```bash
memo notes -f '⭐ Hermes - Assistant' 2>&1 | grep -i 'NOTE TITLE'
```

Report back with:
- note title
- folder name
- a concise list of included link groups

## Quality Bar

Good index note:
- Has a clear title
- Explains why it exists in one sentence
- Groups links logically
- Uses clickable local and web links
- Does not bury the user in full transcripts
- Gives him one place to resume from

Bad index note:
- Long pasted summary with no links
- Raw unordered file path dump
- No verification
- Stored somewhere unexpected
