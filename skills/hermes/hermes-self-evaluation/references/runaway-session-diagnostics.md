# Runaway Session Diagnostics

Use this reference when a Hermes session ran far longer than expected, hit tool-call guardrails, repeated old work, or appeared to ignore a stop or steer instruction after compaction or restore.

Resolve the applicable profile’s `state.db` first. Do not assume the default profile owns the session.

## Minimum evidence

### 1. Session row and live schema

```bash
sqlite3 <resolved-state.db> ".schema sessions"
sqlite3 <resolved-state.db> ".schema messages"
```

Then query only columns confirmed by the schema. A typical session query is:

```sql
SELECT id, source, title, model, started_at, ended_at,
       message_count, input_tokens, output_tokens,
       reasoning_tokens, cache_read_tokens, cache_write_tokens,
       estimated_cost_usd
FROM sessions
WHERE id = '<SESSION_ID>';
```

### 2. Role counts

```sql
SELECT role, COUNT(*)
FROM messages
WHERE session_id = '<SESSION_ID>'
GROUP BY role;
```

### 3. Tool pressure

Inspect the live `messages` schema to determine whether tool names are stored in `tool_calls`, message content, or another column. Do not assume a `tool_name` column exists.

For JSON tool-call payloads, this Python check summarizes calls without executing anything:

```python
import collections
import json
import sqlite3
from pathlib import Path

state_db = Path("<RESOLVED_STATE_DB>").expanduser()
session_id = "<SESSION_ID>"
con = sqlite3.connect(state_db)
con.row_factory = sqlite3.Row

calls = []
for row in con.execute(
    """
    SELECT id, timestamp, tool_calls
    FROM messages
    WHERE session_id=? AND role='assistant'
      AND tool_calls IS NOT NULL AND tool_calls!=''
    ORDER BY id
    """,
    (session_id,),
):
    try:
        payload = json.loads(row["tool_calls"])
    except Exception:
        continue
    if isinstance(payload, dict):
        payload = [payload]
    for call in payload:
        if not isinstance(call, dict):
            continue
        call_id = call.get("call_id") or call.get("id")
        fn = call.get("function") or {}
        name = fn.get("name") or call.get("name")
        args = fn.get("arguments") or call.get("arguments") or ""
        calls.append((call_id, name, str(args)[:160], row["id"], row["timestamp"]))

by_name = collections.Counter(name for _, name, *_ in calls)
by_id = collections.Counter(call_id for call_id, *_ in calls if call_id)
repeated_ids = [(call_id, count) for call_id, count in by_id.items() if count > 1]

print("assistant tool calls:", len(calls))
print("top tools:", by_name.most_common(25))
print("repeated call IDs:", sorted(repeated_ids, key=lambda item: -item[1])[:20])
```

Repeated exact assistant call IDs are a high-signal indicator of stale tool-call replay. High tool volume alone is not.

### 4. Timeline density

```sql
SELECT strftime('%Y-%m-%d %H:%M', datetime(timestamp,'unixepoch','localtime')) AS minute,
       role,
       COUNT(*) AS count
FROM messages
WHERE session_id = '<SESSION_ID>'
GROUP BY minute, role
ORDER BY minute, role;
```

If timestamps are not Unix seconds in the live schema, adjust the conversion rather than forcing this query.

### 5. Stop and steer handling

List user messages and non-tool assistant text around the steering event:

```python
import sqlite3
from pathlib import Path

state_db = Path("<RESOLVED_STATE_DB>").expanduser()
session_id = "<SESSION_ID>"
con = sqlite3.connect(state_db)
con.row_factory = sqlite3.Row

print("USER MESSAGES")
for row in con.execute(
    """
    SELECT id, timestamp, substr(content,1,600) AS content
    FROM messages
    WHERE session_id=? AND role='user'
    ORDER BY id
    """,
    (session_id,),
):
    text = " ".join((row["content"] or "").split())
    print(row["id"], row["timestamp"], text[:400])

print("\nASSISTANT NON-TOOL TEXT")
for row in con.execute(
    """
    SELECT id, timestamp, substr(content,1,800) AS content
    FROM messages
    WHERE session_id=? AND role='assistant'
      AND (tool_calls IS NULL OR tool_calls='')
    ORDER BY id
    """,
    (session_id,),
):
    text = " ".join((row["content"] or "").split())
    if text:
        print(row["id"], row["timestamp"], text[:500])
```

Treat the latest user instruction as authoritative. If the user said stop or evaluate, do not continue the stale operational task.

### 6. Logs

Search the applicable profile logs for the session ID and these high-signal markers:

- `max_iterations_reached`
- `Preflight compression`
- `Pre-API compression`
- `CONTEXT COMPACTION`
- `gateway shutdown`
- `Operation interrupted`
- `tool-call guardrail`
- `idempotent_no_progress`
- repeated transport, browser, or terminal retries

### 7. Live process state

A database row is not proof of a live process. Check current process state separately before saying a runaway task is still active or safe to abandon. Do not kill a process unless the user authorized that action and its ownership is clear.

## Interpretation

- Many calls can be legitimate for complex browser, coding, or research work.
- Repeated exact call IDs suggest stale replay after restore or compaction.
- Compression markers followed by re-execution of completed actions suggest context contamination.
- Tool failures can explain retries without being the primary root cause.
- `ended_at IS NULL` describes persisted lifecycle state, not necessarily an executing process.
- A cap event is a termination symptom; inspect the final response and artifact evidence before classifying the outcome.

## Reporting format

1. One-line verdict.
2. Session metadata and role/tool counts.
3. Timeline around the latest steering instruction.
4. Repeated call-ID and relevant log evidence.
5. Root cause separated from secondary symptoms.
6. Current live-process state, if checked.
7. One bounded recommendation with a verification step.