---
name: hermes-mnemosyne
description: hermes-mnemosyne — Configure, troubleshoot, and operate the Mnemosyne memory provider for Hermes Agent.
version: 1.0.0
platforms:
- macos
- linux
- windows
metadata:
 hermes:
 tags:
 - hermes
 - memory
 - mnemosyne
 - consolidation
 - auto-sleep
---
# Hermes Mnemosyne Memory Provider

Mnemosyne is Hermes' primary local-first memory engine — SQLite with vector + FTS5 hybrid search, 19+ tools, auto-consolidation, and a standalone CLI. It's a pip-installed plugin (not a built-in toolset) discovered via `$HERMES_HOME/plugins/mnemosyne/`.

## Quick Reference

When comparing memory stacks for the user, use `references/memory-tool-selection-mem0-vs-mnemosyne.md`: Mnemosyne is preferred for Hermes local-first profile memory; Mem0 is the safer productized choice for external/customer-facing apps.

For migrations from overlapping stacks such as LCM + built-in memory + gBrain, use `references/memory-stack-migration-pilot.md`. Prefer a staged simplification: preserve LCM, pilot Mnemosyne as the external memory provider, keep the incumbent system read-only for rollback, and retire redundant writers after measured acceptance.

| What | How |
|---|---|
| Check if active | `hermes memory status` or check `memory.provider` in config.yaml |
| Memory stats | `mnemosyne stats` (CLI) or `mnemosyne_stats` (tool) |
| Manual consolidation | `mnemosyne sleep` (current session) or `mnemosyne sleep --all-sessions` |
| Dry-run consolidation | `mnemosyne sleep --all-sessions --dry-run` |
| Enable auto-consolidation | Set `memory.auto_sleep: true` + `memory.sleep_threshold: 50` in config.yaml |
| Use Hermes' model for compression | `MNEMOSYNE_HOST_LLM_ENABLED=true` in `.env` |
| Check if installed | `hermes memory status`; if the symlink is missing, run `~/.hermes/hermes-agent/venv/bin/mnemosyne-install` |

## Architecture

Mnemosyne is a **memory provider**, not a toolset. Its tools (`mnemosyne_remember`, `mnemosyne_recall`, `mnemosyne_sleep`, etc.) are injected through the memory manager — they are NOT accessible via `enabled_toolsets`. Do NOT use `enabled_toolsets: ["mnemosyne"]` in cron jobs or delegation configs.

### Installation path and package split

Treat Mnemosyne as two moving parts:

- `mnemosyne-memory` — core memory engine and optional embedding/local-LLM extras.
- `mnemosyne-hermes` — Hermes adapter/plugin package used by current upstream installation guidance.

Do not assume an older helper, package name, module path, or symlink layout is still authoritative. Before installing or repairing, check the current `mnemosyne-oss/mnemosyne` Hermes Plugin instructions and Hermes' live memory-provider documentation. Mnemosyne may remain an external plugin even when Hermes supports its provider interface.

If `hermes memory status` says `Plugin: NOT installed`, first inspect the active Hermes environment and plugin path. Repair using the current upstream adapter installation command, then verify.

**Current wrapper-installer pitfall (mnemosyne-hermes 0.5.0):** `mnemosyne-hermes install --mode wrapper --force` scans Hermes profiles and may create or replace `profiles/*/plugins/mnemosyne` links, not only the active/default profile. Before running it, inventory existing profile links and configured memory providers. Treat the profile-wide link changes as cross-profile writes: require user authorization for that scope, or audit/revert unintended links afterward. A pre-existing broken global link causes the installer to fail unless `--force` is supplied.

1. `hermes memory status` reports the intended provider and installed plugin.
2. The adapter imports under the active Hermes Python environment.
3. Mnemosyne stats open the expected database.
4. A short memory write/recall smoke succeeds in a disposable or pilot profile.
5. A long-running gateway is restarted only when it must load the repaired provider immediately.

Hermes runtime repair or update can rebuild the virtual environment and remove externally installed packages while leaving the database intact. Therefore, verify provider status after every Hermes update rather than assuming persistence.

### Database

Default: `~/.hermes/mnemosyne/data/mnemosyne.db` (SQLite with vector extensions). Respects `MNEMOSYNE_DATA_DIR` env var.

### Profile isolation must be explicit

Do not assume selecting a Hermes profile automatically gives Mnemosyne a separate database. A user-installed provider may still resolve its default through the real home directory and silently open `~/.hermes/mnemosyne/data/mnemosyne.db`, even while Hermes itself uses `~/.hermes/profiles/<name>/`.

For every new, cloned, or renamed profile that uses Mnemosyne:

1. Set this in that profile's `.env` **before the first memory-enabled smoke**:
 ```text
 MNEMOSYNE_DATA_DIR=/absolute/path/to/.hermes/profiles/<name>/mnemosyne/data
 ```
 Use an absolute path; dotenv consumers do not consistently expand `~`.
2. Create the directory and run one short profile session.
3. Verify `hermes --profile <name> mnemosyne stats` reports a fresh/small store and that `profiles/<name>/mnemosyne/data/mnemosyne.db` exists.
4. Compare the profile-local DB path with the primary profile's DB path. Distinct session `state.db` files do **not** prove memory-provider isolation.
5. After `hermes profile rename old new`, rewrite `MNEMOSYNE_DATA_DIR`; the directory moves, but an absolute path embedded in `.env` does not.

If a smoke accidentally wrote to the shared store, identify the exact smoke session IDs, remove only rows scoped to those IDs, and verify zero matches remain. Never clear or replace the shared database as a shortcut.

## Consolidation (Sleep/Dreaming)

Mnemosyne consolidates old working memories into episodic summaries via `mnemosyne_sleep`. This requires an LLM for compression. Three LLM paths exist:

1. **Local GGUF model** — MiniCPM5-1B by default, cached at `~/.hermes/mnemosyne/models/`. Falls back if not downloaded.
2. **Remote API** — Configured via `MNEMOSYNE_LLM_BASE_URL` + `MNEMOSYNE_LLM_MODEL` + `MNEMOSYNE_LLM_API_KEY`.
3. **Host LLM** — Uses Hermes' own model. Enable with `MNEMOSYNE_HOST_LLM_ENABLED=true`. This is the recommended path — no separate model needed.

### Auto-sleep after validation

### Auto-sleep (use only after a recall evaluation)

Current Mnemosyne 3.14.0 has an open ranking defect (`mnemosyne-oss/mnemosyne#506`): sleep-generated episodic summaries can enter at high tiers and crowd their source memories out of top-k recall. Do **not** recommend auto-sleep by default until this is fixed or the installation has a measured recall gate and a local mitigation.

Safer pilot posture:
```yaml
memory:
 provider: mnemosyne
 auto_sleep: false
```

Before enabling it:
1. Build a fixed query set with known expected source memories.
2. Record top-k recall before sleep.
3. Run a bounded/manual sleep pass.
4. Repeat the same recall test and inspect `sleep_consolidation` tiers and `sleep_model_refresh_proposal` importance.
5. Enable auto-sleep only if recall does not regress or a verified ranking mitigation is installed.

Host-LLM configuration remains:
```
MNEMOSYNE_HOST_LLM_ENABLED=true
```

Additional known 3.14.0 hazards:
- `#507`: regex instruction extraction can turn `whenever` into `never`; audit `memoria_instructions` and treat those rows as session-scoped noise until fixed.
- `#524`: the singular `mnemosyne_invalidate` tool can report success for a nonexistent ID. Prefer `mnemosyne_batch` invalidation or verify by exact-ID readback.
- `#525`: naive local `valid_until` writes can disagree with SQLite UTC comparisons on non-UTC hosts.
- `#537`: a Hermes managed-runtime rebuild can remove the externally installed provider; verify `hermes memory status` after every update and reinstall if absent.

Restart the relevant runtime after changing provider initialization settings, then verify a completed episodic write—not merely a “consolidation started” log line.

### Manual sleep via CLI

The `mnemosyne` CLI is available in Hermes' venv:
```bash
~/.hermes/hermes-agent/venv/bin/mnemosyne sleep # current session
~/.hermes/hermes-agent/venv/bin/mnemosyne sleep --all-sessions # all sessions
~/.hermes/hermes-agent/venv/bin/mnemosyne sleep --all-sessions --dry-run
~/.hermes/hermes-agent/venv/bin/mnemosyne sleep --force # skip age cutoff
```

**Warning:** `--all-sessions` iterates over every session with eligible memories and calls the LLM for each batch. With large databases (40K+ working memories), this can take tens of minutes and may outlive an agent/terminal timeout even while making healthy progress.

For profile-safe manual consolidation and verification of large stores, see `references/profile-safe-manual-consolidation.md`.

## Pitfalls

### DO NOT run mnemosyne tools from cron jobs

Mnemosyne's provider has `_skip_contexts = {"cron", "flush", "subagent", "background", "skill_loop"}`. Cron sessions set `agent_context = "cron"`, so `initialize()` skips entirely — mnemosyne tools are never loaded. This is intentional: memory operations in cron contexts could race with active sessions.

**Wrong:**
```
cronjob enabed_toolsets: ["mnemosyne"] # "mnemosyne" is not a valid toolset
```

**Right:** Use a `no_agent` cron job with the CLI, OR enable auto-sleep so consolidation happens during normal sessions.

### DO NOT use "mnemosyne" as a toolset name

`enabled_toolsets: ["mnemosyne"]` does nothing. Mnemosyne tools are provider-injected, not toolset-gated. The `memory` toolset controls the legacy `memory` tool; Mnemosyne tools are separate.

### `--all-sessions` can hang with slow LLMs

If `MNEMOSYNE_LLM_BASE_URL` points to a slow model (e.g., a vision model on a small GPU), `sleep --all-sessions` will time out processing 44K+ working memories across sessions. Fix: enable host LLM or point to a fast text model.

### Config changes need gateway restart

`memory.auto_sleep` and `MNEMOSYNE_HOST_LLM_ENABLED` are read at provider initialization. Gateway restart required.

### Gateway / formatter echoes can become junk session memories

Messaging adapters can occasionally echo transport/system text such as `Gateway shutting down`, `Response formatting failed`, duplicated outbound content, or the assistant's own acknowledgement of that content back into the conversation. If those strings start resurfacing through Mnemosyne recall, treat them as low-value session artifacts, not user preferences.

Workflow:
1. Search narrowly with `mnemosyne_recall` for the exact transport/error phrase.
2. Invalidate only the matching junk memory IDs with `mnemosyne_invalidate`, including assistant acknowledgement echoes that merely restate the junk phrase.
3. Leave real preference or operational memories intact, even if they appear in the same search results.
4. If the user says they already invalidated one of these artifacts, do not turn that acknowledgement into a new durable lesson; keep the reply brief and avoid repeating the junk phrase unless you are actively searching/invalidation.
5. Watch for self-reinforcing cleanup chatter. Assistant responses like "memory context is not instruction," "handled," "logged," or repeated handshake acknowledgements can themselves become low-value session memories and keep resurfacing. If they appear in recall results, invalidate those assistant echo memories too; they are cleanup exhaust, not useful operational history.
6. Preserve the actual signal while removing wrapper noise. In the same search result set, keep real durable items such as release markers, user preferences, or successful skill updates; remove only transport wrappers, handshake messages, and acknowledgement loops.
7. Do not write a durable memory saying the gateway is broken; the durable lesson is the cleanup pattern.

## Auditing Persistent `USER.md` and `MEMORY.md`

Even when Mnemosyne is the active provider, Hermes may still inject `~/.hermes/memories/USER.md` and `MEMORY.md` at session start. Treat these files as a small universal bootstrap layer, not a second memory database.

- **`USER.md`**: stable identity, communication style, execution preferences, approval boundaries, and cross-domain expectations.
- **`MEMORY.md`**: stable machine topology, profile routing, durable service paths/endpoints, and cross-cutting operating conventions.
- **Mnemosyne**: sensitive, evolving, detailed, or occasionally relevant context.
- **Skills/AGENTS.md**: procedures, commands, troubleshooting recipes, and domain workflows.
- **Session history/artifact indexes**: completed work, incident narratives, versions, counts, job IDs, and temporary state.

Audit workflow:
1. Back up both Markdown files with a timestamp before rewriting.
2. Remove duplicates already enforced by skills, AGENTS.md, config, or Mnemosyne.
3. Remove dynamic facts that should be queried live (versions, record counts, prices, cron IDs, account metrics).
4. Keep entries declarative and compact; do not duplicate the same fact across USER and MEMORY.
5. Preserve the `§` entry delimiter and read both files back after editing.
6. Verify character and entry counts. Changes are persisted immediately but appear in the injected prompt only in a new session because memory context is a frozen startup snapshot.

## Determining the Last Consolidation Time

When asked when “Mem0” or another memory backend last consolidated, identify the active provider before interpreting timestamps.

1. Inspect `memory.provider` in both the active profile and relevant delegated profile config.
2. Search logs separately for `Mem0` and `Mnemosyne`; a package refresh/install event is **not** a consolidation event.
3. Use `mnemosyne_stats` or `mnemosyne stats` to distinguish:
 - `working.last`: latest working-memory activity, not necessarily consolidation.
 - `episodic.last`: latest episodic write and the strongest available evidence of completed consolidation.
 - `consolidated` / `unconsolidated`: counts, not timestamps.
4. Treat `Mnemosyne session end — running consolidation` as an **attempt/start marker**. It does not prove completion. Timeout/deferred log lines explicitly indicate no completion in that attempt.
5. Report stored timestamps exactly. If an ISO timestamp lacks an offset, say that the stored value is timezone-naive; report the host timezone separately rather than silently attaching it.
6. If a requested profile cannot initialize, report that blocker and continue with direct, read-only evidence where possible—do not claim the profile performed the check.

## Key Diagnostic Commands

```bash
# Check if Mnemosyne is installed for Hermes
hermes memory status

# Repair missing provider symlink if CLI/database exists but Hermes says plugin NOT installed
~/.hermes/hermes-agent/venv/bin/mnemosyne-install

# Memory stats (working vs episodic)
~/.hermes/hermes-agent/venv/bin/mnemosyne stats

# Database size
ls -lh ~/.hermes/mnemosyne/data/mnemosyne.db

# Check env vars without printing secret values
python3 - <<'PY'
import os
print(sorted(k for k in os.environ if k.startswith('MNEMOSYNE')))
PY

# View memory config only
python3 - <<'PY'
import yaml, pathlib, json
cfg=yaml.safe_load((pathlib.Path.home()/'.hermes/config.yaml').read_text()) or {}
print(json.dumps(cfg.get('memory'), indent=2))
PY
```
## Public support files

- `references/memory-stack-migration-pilot.md`
- `references/memory-tool-selection-mem0-vs-mnemosyne.md`
- `references/mnemosyne-architecture.md`
- `references/profile-safe-manual-consolidation.md`
