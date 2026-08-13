---
name: hermes-self-evaluation
description: hermes-self-evaluation — Use when the user asks to evaluate, audit, or optimize Hermes itself — analyzing session history, skill library, costs, and architecture to identify improvements, automation opportunities, and system optimizations. Covers generating structured analyst prompts for external (stronger) models to review Hermes's own performance.
version: 1.0.0
license: MIT
tags:
- hermes
- evaluation
- audit
- optimization
- meta-analysis
- systems-review
metadata:
 hermes:
 tags:
 - hermes
 - evaluation
 - audit
 - optimization
 - meta-analysis
 - systems-review
 related_skills:
 - skill-auditor
  - session-artifact-indexing
---
# Hermes Self-Evaluation

Use this skill when the user asks to audit, review, or optimize Hermes's own performance — analyzing session data, skills, configuration, costs, and usage patterns to identify improvements, automation opportunities, and system optimizations.

**Don't use for:** skill content quality grading (use skill-auditor instead), one-off task analysis, or session artifact indexing after a work session (use session-artifact-indexing).

## Overview

The core workflow: gather live evidence about Hermes's state and history → validate each finding against the subsystem's actual semantics and control surface → either produce a direct evidence-backed review or compose a structured analyst prompt for an independent model → verify recommendations before implementation.

External models are useful anomaly detectors and critics, but they are not automatically reliable root-cause analysts. Separate the observed symptom, supported interpretation, confirmed producer/root cause, and proposed change. Before acting on any self-check finding,

## When to Use

Triggers:
- "How can we improve Hermes?"
- "Analyze my sessions and tell me what to optimize"
- "I want to have another model evaluate X"
- "Where do sessions/skills live so I can analyze them?"
- "Do an audit of the system"
- "What's the token cost breakdown?"

## Workflow

### Fast Path: Evaluate a Single Runaway Session

When the user names a specific session and says it was “working” too long, hit a tool-call guardrail, ignored “stop,” or needs the problem evaluated, do **not** build a broad system-audit prompt first. Diagnose the named session directly.

Use for the exact SQL/Python checks. Minimum evidence to collect:

1. Session metadata from `~/.hermes/state.db`: source, title, model, start/end times, message count, tool-call count, token totals, end reason.
2. Role counts and top tool counts.
3. User-message timeline and non-tool assistant replies, especially around compaction/restore and the latest steering instruction.
4. Repeated assistant `tool_call` IDs. Exact repeated `call_id`s are a strong sign of stale tool-call replay after context compaction or gateway restore.
5. Log markers for the session ID: `max_iterations_reached`, `Preflight compression`, `Pre-API compression`, `gateway shutdown`, `Operation interrupted`, `tool-call guardrail`, `idempotent_no_progress`, and transport retry loops.
6. If relevant, check whether any live process from the runaway task is still active before saying it is safe to abandon.

Reporting rule: separate **root cause** from **secondary symptoms**. For example, browser/CUA failures may explain retries, but repeated historical tool-call IDs point to restore/replay contamination. If the user says “stop and evaluate,” stop the operational task immediately and evaluate; do not continue trying to finish the stale task.

### Step 1: Map the Session Store

The canonical session database is `~/.hermes/state.db`. Query its current size and schema live; never hardcode historical counts or gigabytes.

**Key tables:**

```sql
-- sessions: id, source (cli/cron/telegram/tui/api_server/subagent/discord/bluebubbles/speech-bridge),
-- model, input_tokens, output_tokens, reasoning_tokens, cache_read_tokens,
-- cache_write_tokens, message_count, title, started_at, ended_at,
-- estimated_cost_usd, handoff_state, git_branch
CREATE TABLE sessions (...)

-- messages: session_id, role (user/assistant/tool), content (full text),
-- tool_calls, token_count, timestamp, reasoning, finish_reason
CREATE TABLE messages (...)
-- Has FTS5 + trigram full-text search indexes on messages.content
```

**Lifecycle semantics:** `sessions.ended_at IS NULL` means an open DB row. Total retained rows are not active sessions. Gateway routing files map resumable platform conversations; they do not prove a process is currently executing. Review detached sources by age and treat long-lived messaging rows separately. Use the queries above and the interpretation rules in this section.

**Other session data:**
- `~/.hermes/session-log/*.md` — daily Markdown activity logs when the session-log plugin is enabled
- `~/.hermes/sessions/` — gateway routing/session artifacts and optional transcript snapshots; inspect current contents rather than assuming a format or count

### Step 2: Map the Skill Library

- **Default profile:** `~/.hermes/skills/`
- **Profile-specific overrides:** `~/.hermes/profiles/<profile>/skills/`
- Each skill is a directory with `SKILL.md` plus optional `references/`, `templates/`, and `scripts/` directories.

List skills and inspect the live category tree. Never hardcode skill counts or total size: installs, curator actions, and profile changes make those values stale quickly.

### Step 3: Gather Usage Statistics

Run aggregation queries against state.db to get the profile picture:

```sql
-- Sessions by source
SELECT source, COUNT(*) as sessions, SUM(input_tokens + output_tokens) as total_tokens,
 SUM(message_count) as total_msgs, ROUND(SUM(estimated_cost_usd), 2) as cost
FROM sessions GROUP BY source ORDER BY total_tokens DESC;

-- Token cost by model
SELECT model, SUM(input_tokens), SUM(output_tokens),
 SUM(input_tokens + output_tokens) as total
FROM sessions WHERE model IS NOT NULL GROUP BY model ORDER BY total DESC;

-- Most active hours / patterns
SELECT strftime('%H', datetime(started_at, 'unixepoch')) as hour, COUNT(*) as sessions
FROM sessions GROUP BY hour ORDER BY sessions DESC;

-- Longest sessions (high message count)
SELECT id, source, message_count, input_tokens, output_tokens, started_at
FROM sessions ORDER BY message_count DESC LIMIT 20;

-- Repeated session titles (recurring task types)
SELECT title, COUNT(*) as freq FROM sessions
WHERE title IS NOT NULL AND title != '' GROUP BY title ORDER BY freq DESC LIMIT 30;

-- Cron session energy (most expensive cron jobs)
SELECT s.id, s.title, s.message_count, s.input_tokens, s.output_tokens
FROM sessions s WHERE s.source = 'cron'
ORDER BY s.input_tokens + s.output_tokens DESC LIMIT 20;
```

Also collect:
- Total session count and total tokens across all sources
- Current model/provider setup (check config.yaml and .env)
- Cron job list (`cronjob action='list'`)
- Multi-profile architecture notes (default → domain-specific profiles delegation pattern)

### Step 4: Compose the Analyst Prompt

Use the analyst-prompt template structure below as the starting point.

The prompt must be self-contained — the receiving model has no knowledge of this conversation. Include:

1. **Data locations** — exact paths the model would use to query or reference
2. **Usage profile** — session counts, token costs, message volumes per source
3. **Skill library structure** — categories, key skills, per-profile overrides
4. **Business context** — the user's businesses and workflows
5. **Architecture summary** — profiles, model setup, multi-machine layout
6. **Analysis dimensions** — what you want the model to evaluate (automation, skill quality, costs, architecture, UX, system health)
7. **Output format** — priority-ranked findings with evidence and expected impact
8. **Starter queries** — SQL the model can use to deep-dive

### Step 5: Write the Prompt File

Save the composed prompt to a known location so the user can:
- Feed it to another model (Claude, GPT, local Heretic)
- Review and modify it before analyzing
- Re-run the same evaluation later with updated data

Standard location: `Notes/hermes-[audit|evaluation]-prompt-<date>.md`

### Step 6: Deliver

Tell the user:
- Where the prompt lives
- What data it includes (dates, session counts, what was gathered)
- Key stats from the usage profile (most expensive sessions, patterns found)
- Offer to feed it to an external model directly if he wants

## Pitfalls

1. **Prompt too long for the target model.** DeepSeek Flash v4 has a 1M token context window but weaker reasoning. A local 27B Heretic has 128K. If the target model can't handle the full prompt, truncate the oldest data or summarize low-value noise sessions. Know the target model's limits before composing.

2. **Session DB queries are expensive.** 160K messages in a 5.4 GB database means some aggregations take seconds. Don't run heavy queries in a loop — batch them into a single SQL multi-query or collect stats once.

3. **Cost data may be incomplete.** The `estimated_cost_usd` column in sessions only has values for sessions where the billing provider was reachable. Many local-model sessions show $0.00 cost. Note this in the prompt as a caveat rather than asserting "these sessions cost nothing."

4. **Skill library is ~26 items.** Don't enumerate every skill in the prompt body if the target model has a small context window — reference the category tree and let the model query specific categories of interest.

5. **Profiles may share a session store.** Named profiles can write to the same session database; the `source` column distinguishes them. Don't assert clean profile isolation in session data.

6. **The prompt template can get stale.** After major Hermes upgrades or session-schema changes, update the template. Query the live CLI help, config, schema, and docs instead of preserving version-specific assumptions.

7. **A real symptom does not validate the proposed fix.** Verify that the named setting exists, is enabled, and governs the affected subsystem. Examples: checkpoint retention does not control session rows; a retention value does nothing when auto-prune is disabled; staged profile-only plugin enablement is not the same as a globally broken plugin; and an invented convenience key is not a configuration experiment.

8. **Read-only self-checks must stay read-only.** Do not restart, prune, vacuum, consolidate memory, change delivery targets, or enable plugins globally from an unattended audit. Surface exact evidence and the narrow next action.

9. **CLI failures require syntax verification, not folklore.** Run the current command's `--help` and a redacted dry-run. For JSONL session export, include an output target such as `-`: `hermes sessions export - --session-id <ID> --dry-run --redact`.

## Verification

- [ ] state.db exists and queries return results
- [ ] Usage statistics collected and written into the prompt
- [ ] Skill library structure summarized (categories, counts)
- [ ] Prompt references are current (check dates on data samples)
- [ ] Output file written to a known location
- [ ] Reported to the user with key findings summary

## Reference Files

- `references/analyst-prompt-template.md` — the full structured analyst prompt template used as the base for composing evaluation prompts. Update this when the Hermes session schema or architecture changes meaningfully.
- `references/runaway-session-diagnostics.md` — SQL/Python snippets and interpretation notes for diagnosing a specific runaway/restored session, repeated tool-call IDs, compaction contamination, and stop/steer handling.
- `references/evidence-first-self-check-validation.md` — class-level rubric and exact checks for validating session, memory, retention, delivery, plugin-rollout, and CLI-syntax findings before implementing self-check recommendations.
## Public support files

- `references/analyst-prompt-template.md`
- `references/evidence-first-self-check-validation.md`
- `references/runaway-session-diagnostics.md`
