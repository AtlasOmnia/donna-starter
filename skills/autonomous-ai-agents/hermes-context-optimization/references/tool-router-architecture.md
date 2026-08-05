# Hermes Tool Router - Architecture and Status (updated)

## Purpose

Reduce per-turn tool-schema overhead by predicting required toolsets before the first LLM call. The test profile profile narrows tools early, keeps `request_toolset` available as a recovery primitive, and falls back to full tools on errors.

## Current Status

- Plugin installed at: `~/.hermes/plugins/hermes-token-router/`
- Enabled only for test profile; global/default remain disabled.
- Core `agent/turn_context.py` is restored; no persistent Hermes core source patch is required.
- Runtime integration is an experimental plugin-side shim: at plugin registration, it wraps `agent.turn_context.build_turn_context` so routing happens before system prompt, skills prompt, preflight estimate, and tool schema assembly.
- The wrapper now validates the `build_turn_context` signature with `inspect.signature`, logs loudly if incompatible, and falls back safely to normal hooks/full tools.
- Router state is attached to the live agent when available; module globals remain only as last-resort compatibility fallback.

## Registered Surface

`plugin.yaml` provides:

```yaml
provides_hooks:
 - pre_llm_call
 - post_tool_call
provides_tools:
 - request_toolset
```

`pre_agent_init` is not registered; older notes mentioning it are historical.

## Configuration

```yaml
profiles:
 test_profile:
 enabled: true
 floor_toolsets: []
 deterministic_rules_enabled: true
 confidence_threshold: 0.0
 long_message_decline_chars: 12000
 short_message_bypass_chars: 0
 router_model: meta-llama/llama-3.1-8b-instruct
 router_provider: openrouter
global:
 enabled: false
```

## Recovery Model

- `request_toolset` is the reliable model-visible recovery path when a needed capability is missing after pruning.
- `post_tool_call` is best-effort only. Hermes validates tool names before dispatch, so calls to pruned-away tool names may be rejected before `post_tool_call` can run.
- Automatic invalid pruned-tool recovery requires a future core seam in the invalid-tool path, e.g. `on_pruned_tool_call` or a generic pre-error expansion hook.

## Architecture

```text
User message
 -> runtime wrapper around build_turn_context
 -> deterministic rules first
 -> router model only for ambiguous prompts
 -> _apply_predicted_tools mutates agent.tools / valid_tool_names
 -> request_toolset is appended as escape hatch
 -> system prompt / skills prompt / preflight estimate / tool schema assembly
 -> LLM call with narrowed tools
 -> if model needs a missing capability, it should call request_toolset
 -> post_tool_call can expand only after executed tool calls
```

## Pitfalls

1. Runtime wrapper is a shim, not the final contract. It depends on Hermes internals and should eventually be replaced by a small official hook before prompt/tool assembly.
2. Do not use Chat Completions against the Codex backend; Codex uses Responses API format.
3. Escape curly braces in `str.format()` templates.
4. Runtime debug output should use `logger`, not raw `print()`.
5. OpenRouter routing variability means the auxiliary call needs a hard timeout and fail-open behavior.
6. Keep this test profile-only until concurrency, invalid-tool recovery, and module cleanup are proven.

## Testing

```bash
python ~/.hermes/plugins/hermes-token-router/tests/smoke_hardening.py
hermes --profile test_profile chat -q "."
hermes --profile test_profile chat -q "check the hermes subreddit. whats interesting today?"
```

Expected behavior:
- ordinary prompt narrows to `request_toolset` only;
- reddit/web prompts route to web/browser plus `request_toolset`;
- failures restore or keep full tools rather than crashing.