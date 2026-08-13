# Session forensics: token burn vs real loop

Use when a user says a session kept looping, felt slow, or burned far more tokens than expected.

## Goal
Determine whether the problem was:
- duplicate delivery / resend,
- too many tool turns inside one answer,
- oversized tool payloads repeatedly replayed into context,
- or an actually long final response.

## Core evidence sources
1. `~/.hermes/state.db`
 - `sessions` table for totals
 - `messages` table for per-turn structure and payload sizes
2. `~/.hermes/logs/gateway.log`
 - one inbound vs many
 - `response ready`
 - duplicate-send suppression lines
3. `~/.hermes/sessions/sessions.json`
 - session key/session id mapping only
 - useful for routing metadata, not root-cause diagnosis

## Recommended SQL

Session totals:
```bash
sqlite3 ~/.hermes/state.db <<'SQL'
.headers on
.mode column
SELECT id, source, title, model,
 input_tokens, output_tokens, cache_read_tokens, reasoning_tokens,
 api_call_count, message_count,
 datetime(started_at,'unixepoch','localtime') AS started,
 datetime(ended_at,'unixepoch','localtime') AS ended
FROM sessions
WHERE id='SESSION_ID';
SQL
```

Per-message structure:
```bash
sqlite3 ~/.hermes/state.db <<'SQL'
.headers on
.mode column
SELECT id, role, tool_name, tool_call_id,
 length(COALESCE(content,'')) AS content_len,
 datetime(timestamp,'unixepoch','localtime') AS ts
FROM messages
WHERE session_id='SESSION_ID'
ORDER BY id;
SQL
```

## Interpreting patterns

### A. Internal tool-call cascade
Signs:
- many assistant rows with empty content followed by tool rows
- several search/extract calls for one simple user request
- high input tokens, modest output tokens
- one inbound message and one final `response ready`

Interpretation:
The model kept making more tool calls and rereading the growing transcript. This is not a gateway resend loop.

### B. Duplicate delivery suspicion ruled out
Signs in `gateway.log`:
- `Suppressing normal final send ... content_delivered=True`
- only one `response ready` for the user message

Interpretation:
Streaming already delivered the response once. Hermes intentionally skipped the second final send. Do not blame Telegram delivery.

### C. Oversized tool payloads
Common offenders:
- full `skill_view` loads when only a small fact was needed
- overlapping `web_search` results
- large `web_extract` dumps
- broad environment dumps for narrow metadata lookups

Interpretation:
The answer cost comes from replaying bulky tool outputs, not from the final response itself.

## Concrete lesson from a live session

Observed pattern:
- one user question about an X post
- full `xurl` skill load
- failed terminal call because `xurl` was missing
- fallback to `web_extract`
- four separate `web_search` calls
- final answer only 6.7k chars, but total input tokens exceeded 212k

Key diagnosis:
- not a transport loop
- not duplicate Telegram delivery
- it was an over-eager research/tool cascade
- the largest single payload was the loaded skill document, followed by redundant search results

## Reporting style
When explaining this to the user:
- say clearly whether it was a resend loop or an internal tool cascade
- quantify the top payload offenders
- separate cost source from answer size
- recommend the cheaper path that should have been used

## Preferred remediation guidance
For simple link-analysis or session-metadata questions:
- use one direct extract/read path first
- avoid loading a full skill unless the tool is genuinely needed
- cap redundant searches
- query only the specific session env vars needed instead of dumping all Hermes env vars
