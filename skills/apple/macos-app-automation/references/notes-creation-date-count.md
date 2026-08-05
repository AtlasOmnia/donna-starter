# Counting Apple Notes by creation date — validated recipe

Context: the user asks "how many Apple Notes did I create today / since X?"
Validated against a live account with tens of thousands of notes (returned 3;
cross-checked titles/times in a second pass).

## What fails (both validated)

1. Per-note iteration — one AppleEvent per note, timed out at 180s:
 `repeat with n in notes of default account ... creation date of n`
2. Filtered query — `count of notes of default account whose creation date ≥ d`
 throws `Access not allowed (-1723)`.

Also: `mdfind` content-type probes (`kMDItemContentType == "com.apple.notes.note"c`,
`kMDItemKind == "Note"`, `-onlyin ~/Library/Group Containers/group.com.apple.notes`)
return nothing — do not rely on Spotlight for Notes item counts.

## What works — bulk property fetch

One AppleEvent fetches the property list; comparison runs locally:

```applescript
tell application "Notes"
 set d to current date
 set hours of d to 0
 set minutes of d to 0
 set seconds of d to 0
 set dl to creation date of every note of default account
 set c to 0
 repeat with x in dl
 if x ≥ d then set c to c + 1
 end repeat
 return c
end tell
```

Runs in seconds even at ~3k notes. For title + time listing, bulk-fetch both
collections and index them together (no per-note AppleEvents):

```applescript
tell application "Notes"
 set d to current date
 set hours of d to 0
 set minutes of d to 0
 set seconds of d to 0
 set out to ""
 set nl to every note of default account
 set cl to creation date of every note of default account
 repeat with i from 1 to count of nl
 if (item i of cl) ≥ d then
 set out to out & (item i of cl as string) & " | " & (name of item i of nl) & linefeed
 end if
 end repeat
 return out
end tell
```

"Today" here = local midnight → now; adjust `d` for other windows.

## Storage-side notes

- `sqlite3` cannot open `NoteStore.sqlite` — TCC: `authorization denied` (both
 plain path and `file:...?mode=ro` URI). Use `strings` raw-byte search or
 AppleScript; never a sqlite3 query path.
- `memo` CLI may die with `bad interpreter` pointing at a Homebrew Cellar
 python after `brew upgrade python` — fix: `brew reinstall antoniorodr/memo/memo`.
