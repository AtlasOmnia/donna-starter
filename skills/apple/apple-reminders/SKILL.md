---
name: apple-reminders
description: 'apple-reminders — Apple Reminders via remindctl: add, list, complete.'
version: 1.0.0
author: Hermes Agent
license: MIT
platforms:
- macos
metadata:
 hermes:
 tags:
 - Reminders
 - tasks
 - todo
 - macOS
 - Apple
prerequisites:
 commands:
 - remindctl
---
# Apple Reminders

Use `remindctl` to manage Apple Reminders directly from the terminal. Tasks sync across all Apple devices via iCloud.

## Prerequisites

- **macOS** with Reminders.app
- Install: `brew install steipete/tap/remindctl`
- Grant Reminders permission when prompted
- Check: `remindctl status` / Request: `remindctl authorize`
- If macOS reports Full Access but `remindctl status` still says `Not determined` or `Denied`, test AppleScript instead:
 ```bash
 osascript -e 'tell application "Reminders" to return name of every list'
 ```
 If AppleScript works, use Reminders AppleScript as a fallback for list/read/create operations; the TCC grant may apply to Terminal/Python but not the `remindctl` binary context.

## When to Use

- User mentions "reminder" or "Reminders app"
- Creating personal to-dos with due dates that sync to iOS
- Managing Apple Reminders lists
- User wants tasks to appear on their iPhone/iPad

## When NOT to Use

- Scheduling agent alerts → use the cronjob tool instead
- Calendar events → use Apple Calendar or Google Calendar
- Project task management → use GitHub Issues, Notion, etc.
- If user says "remind me" but means an agent alert → clarify first
- **Things 3** — if the user's primary task manager is Things 3, note it has no terminal CLI; it exposes data only via URL scheme (`things://...`) or manual export (File → Export → JSON/HTML).

## Quick Reference

### View Reminders

```bash
remindctl # Today's reminders
remindctl today # Today
remindctl tomorrow # Tomorrow
remindctl week # This week
remindctl overdue # Past due
remindctl all # Everything
remindctl 2026-01-04 # Specific date
```

**Pitfall — `remindctl list` can hang:** `remindctl list --all` timed out after 180s in testing. Use `remindctl today`, `remindctl week`, or date-specific queries instead of broad list commands. If you must see everything, pipe through a timeout:
```bash
timeout 30 remindctl all 2>&1
```

### Manage Lists

```bash
remindctl list # List all lists
remindctl list Work # Show specific list
remindctl list Projects --create # Create list
remindctl list Work --delete # Delete list
```

### Create Reminders

```bash
remindctl add "Buy milk"
remindctl add --title "Call mom" --list Personal --due tomorrow
remindctl add --title "Meeting prep" --due "2026-02-15 09:00"
```

### Due Time vs Alarm / Early Nudge

`--due` and `--alarm` are different fields:

- `--due` sets the reminder's due date/time.
- `--alarm` sets the EventKit alarm/notification trigger. Timed due reminders may default to an alarm at the due time, but pass `--alarm` explicitly when the user asks for an earlier nudge.

For a reminder due at 2:00 PM with a notification 30 minutes earlier:

```bash
remindctl add --title "Hairdresser" --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
```

To edit an existing reminder:

```bash
remindctl edit 87354 --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
```

The Reminders UI may show or group the item by the alarm time because that is when the notification fires. Verify with JSON instead of assuming the due time moved:

```bash
remindctl today --json
```

Expected shape:

- `dueDate`: actual due time
- `alarmDate`: notification / early nudge time

Apple's public `EKReminder` docs list only reminder-specific properties. Alarm support comes from inherited `EKCalendarItem` behavior exposed by remindctl's `--alarm` flag.

### Complete / Delete

```bash
remindctl complete 1 2 3 # Complete by ID
remindctl delete 4A83 --force # Delete by ID
```

### Subtasks / Parent Reminders

`remindctl` 0.1.1 does **not** expose subtask/parent operations in `add` or `edit`. It can create and edit flat reminders only. If the user asks to reorganize existing reminders as subtasks, first verify whether a supported AppleScript/ReminderKit path exists on the current macOS version; do **not** assume `remindctl` can do it.

Fallback options, in order:
1. Use the Reminders UI manually/with computer-use if accessible.
2. If UI automation is not accessible and the user expects direct action, the local Reminders SQLite store contains `ZREMCDREMINDER.ZPARENTREMINDER` and `ZCKPARENTREMINDERIDENTIFIER`, but direct DB edits are fragile. Back up the active store first and verify with a read-only query afterward. Prefer this only for narrow, reversible edits.

### Output Formats

```bash
remindctl today --json # JSON for scripting
remindctl today --plain # TSV format
remindctl today --quiet # Counts only
```

## Date Formats

Accepted by `--due` and date filters:
- `today`, `tomorrow`, `yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601 (`2026-01-04T12:34:56Z`)

## Rules

1. When user says "remind me", clarify: Apple Reminders (syncs to phone) vs agent cronjob alert
2. Always confirm reminder content and due date before creating
3. Use `--json` for programmatic parsing
