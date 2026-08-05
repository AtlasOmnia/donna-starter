# Skill Pruning Workflow

## Context

Initial prompt ~26k tokens. Skills index alone ~5k tokens across 148 registered skills. Goal: reduce by disabling unused skills via `skills.disabled` in config.yaml.

## Key findings

### Data source for skill usage
- `agent.log` does NOT embed skill names in grepable format — log lines show tool completions but not the `name` argument.
- `state.db` (SQLite at `~/.hermes/state.db`) IS the authoritative source. The `messages` table has a `tool_calls` JSON column containing function call arguments including `skill_view.name` and `skill_manage.name`.
- Session JSONL files in `~/.hermes/sessions/` also contain this data but are harder to query at scale.

### Skill name normalization
Skill names in `state.db` include path prefixes (e.g., `autonomous-ai-agents/hermes-agent`, `apple:imessage`). Normalize with `sed 's|.*/||'` to match directory names. Some legacy entries have colons or duplicate forms — strip both `/` and `:` prefixes.

### Cron job check
No cron jobs currently reference skills via `skills:` arrays. Always verify before disabling — a skill loaded by cron would be useless if disabled.

### Config gotcha
YAML silently uses the LAST occurrence of a duplicate key. The original config had two `disabled:` keys under `skills:` — the second (with only `nonexistent-test`) overrode the first (with 84 skills). Always verify with `grep -n "disabled:" ~/.hermes/config.yaml` after edits.

### Results
- **Before:** 148 skills, ~5k tokens for skills index
- **After:** 64 active skills, 84 disabled, ~2.5k tokens estimated
- **Net savings:** ~2.5k tokens on every session start
