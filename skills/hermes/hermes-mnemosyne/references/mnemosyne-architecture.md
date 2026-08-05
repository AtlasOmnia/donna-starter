# Mnemosyne Architecture & Internals

Deep-dive reference compiled while investigating a failed nightly consolidation cron job.

## Provider Lifecycle

### Initialization
- `MnemosyneMemoryProvider.__init__()` sets `_skip_contexts = {"cron", "flush", "subagent", "background", "skill_loop"}`
- `initialize(agent_context=...)` checks `if self._agent_context in self._skip_contexts` — if true, skips beam creation entirely
- `_skip_contexts` can be overridden via `MNEMOSYNE_SKIP_CONTEXTS` env var (comma-separated, empty string = skip nothing) or config.yaml `memory.skip_contexts`

### Sync and Auto-Sleep
- Every turn: `sync_turn()` saves user/assistant content to working memory
- Every 10 turns (when `auto_sleep` enabled): checks `get_working_stats()["total"] > sleep_threshold`
- If threshold exceeded: calls `sleep_all_sessions()` in non-blocking thread
- On session end: `on_session_end()` runs sleep with `SESSION_END_SLEEP_TIMEOUT_SECONDS` (default 15s)

### Tool Injection
- Current package/distribution: `mnemosyne-memory`
- Provider implementation: `hermes_memory_provider/__init__.py`
- Tools are exposed by the provider and injected via `agent/memory_manager.py::inject_memory_provider_tools()`
- Tools are NOT part of any named toolset — they're provider-injected, not toolset-gated

## Sleep/Consolidation Internals

### `sleep()` (single session)
1. Query working_memory where `session_id = current` AND `timestamp < cutoff` AND `consolidated_at IS NULL`
2. Limit to `SLEEP_BATCH_SIZE` (default 5000, env: `MNEMOSYNE_SLEEP_BATCH`)
3. Atomic claim: UPDATE `consolidated_at` WHERE `consolidated_at IS NULL` (prevents duplicate work)
4. Group claimed rows by source, send to LLM for summarization
5. Write episodic_summary with source rows marked as consolidated (NOT deleted — originals remain recallable)
6. Falls back to AAAK encoding if LLM unavailable

### `sleep_all_sessions()` (multi-session)
1. Query `SELECT session_id, COUNT(*) FROM working_memory WHERE timestamp < cutoff AND consolidated_at IS NULL GROUP BY session_id`
2. For each session_id with eligible rows, create a `BeamMemory(session_id=...)` and call `sleep()`
3. Aggregates results across all sessions

### LLM Path Priority
1. Host LLM (if `MNEMOSYNE_HOST_LLM_ENABLED=true` and backend registered) — uses Hermes' model
2. Remote API (if `MNEMOSYNE_LLM_BASE_URL` set) — makes HTTP calls to configured endpoint
3. Local GGUF model (if downloaded to `~/.hermes/mnemosyne/models/`) — llama-cpp or ctransformers
4. AAAK encoding (deterministic compression, no LLM needed) — always available as fallback

## Tool Schemas (19 total)

| Tool | Purpose |
|---|---|
| `mnemosyne_remember` | Store durable memory |
| `mnemosyne_recall` | Hybrid vector+FTS5 search |
| `mnemosyne_sleep` | Consolidation cycle |
| `mnemosyne_stats` | Working/episodic counts |
| `mnemosyne_get` | Retrieve by ID |
| `mnemosyne_update` | Update content/importance |
| `mnemosyne_forget` | Delete by ID |
| `mnemosyne_invalidate` | Mark expired/superseded |
| `mnemosyne_validate` | Attest/update/invalidate/delete with collaborative ownership |
| `mnemosyne_shared_remember` | Cross-agent surface memory |
| `mnemosyne_shared_recall` | Search shared surface |
| `mnemosyne_shared_forget` | Delete shared surface |
| `mnemosyne_shared_stats` | Shared surface stats |
| `mnemosyne_triple_add` | Add fact triple to KG |
| `mnemosyne_triple_query` | Query knowledge graph |
| `mnemosyne_remember_canonical` | Single-source-of-truth self-fact |
| `mnemosyne_recall_canonical` | Read canonical self-facts |
| `mnemosyne_import` | Import from file/provider |
| `mnemosyne_export` | Export to JSON |
| `mnemosyne_diagnose` | PII-safe diagnostics |
| `mnemosyne_graph_query` | Multi-hop graph traversal |
| `mnemosyne_graph_link` | Declare semantic edge |
| `mnemosyne_scratchpad_write` | Temporary note |
| `mnemosyne_scratchpad_read` | Read scratchpad |
| `mnemosyne_scratchpad_clear` | Clear scratchpad |

## Key Files

| Path | What |
|---|---|
| `~/.hermes/mnemosyne/data/mnemosyne.db` | Main database |
| `~/.hermes/mnemosyne/models/` | Local GGUF model cache |
| `~/.hermes/plugins/mnemosyne/` | Provider symlink → pip package |
| `venv/lib/.../hermes_memory_provider/__init__.py` | Provider implementation + tool schemas |
| `venv/lib/.../hermes_memory_provider/hermes_llm_adapter.py` | Host LLM adapter |
| `venv/lib/.../mnemosyne/core/beam.py` | BeamMemory engine |
| `venv/lib/.../mnemosyne/core/memory.py` | Mnemosyne class |
| `venv/lib/.../mnemosyne/core/local_llm.py` | LLM integration for sleep |
| `venv/lib/.../mnemosyne/cli.py` | Standalone CLI |

## Current State

- Database: 420MB, 44,057 working memories, 15,744 episodic
- Provider: mnemosyne (active)
- Auto-sleep: enabled, threshold 50
- Host LLM: enabled
- Remote API: `http://127.0.0.1:1234/v1` (Mac LM Studio, Qwen2.5-VL-7B) — slow for batch consolidation
- No local GGUF model downloaded
- `_skip_contexts`: default (cron, flush, subagent, background, skill_loop)
