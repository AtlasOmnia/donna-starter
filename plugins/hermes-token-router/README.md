# Hermes Tool Router

Experimental standalone Hermes Agent plugin for reducing first-turn tool-schema overhead without repeatedly changing the tool prefix later in the conversation.

> Test on a separate Hermes profile first. Do not install an experimental router directly on a primary profile.

## v0.2 design

- **First-turn routing:** deterministic intent classification runs before schema assembly when Hermes exposes an early hook.
- **Session-sticky surface:** later turns reuse the initial surface instead of reclassifying and shrinking it.
- **Monotonic recovery:** requested toolsets are added permanently for the session.
- **Fail open:** uncertainty, invalid classifier output, missing confidence, timeout, registry mismatch, or unsupported runtime keeps the full tool surface. Protected definitions additionally remain bounded by the immutable host-admission envelope; invalid policy denies new additions rather than broadening.
- **Optional classifier:** external model routing is disabled by default. Deterministic misses fall back immediately with no network call.
- **Dynamic recovery:** `request_toolset` is generated from the live toolset registry and can request multiple toolsets. The registry is used for ordinary compatibility and discoverability only; protected definitions are recovered exclusively from the exact per-agent/session envelope.

## Critical compatibility fact

First-turn token savings work through either an early Hermes surface hook or the stock `pre_llm_call` compatibility path. In current Hermes, `pre_llm_call` runs after the initial preflight estimate but before the actual provider request is assembled and before the loop's request-pressure estimate; mutating `agent.tools` there still reduces the transmitted tool schemas. The tradeoff is that the plugin must recover the live agent through compatibility logic unless Hermes passes it explicitly.

Run diagnostics:

```bash
python diagnostics.py
```

Exit code `0` means a routing path is available before the provider request. Exit code `2` means the current runtime must not claim first-turn savings. The report separately states whether routing happens before the initial preflight estimate.

Automatic execution recovery uses Hermes's generic `tool_request` middleware. When the model emits a registry-known tool that was pruned, the middleware expands its owning toolset before normal validation and dispatch, then the original call continues through ordinary requirement checks and approvals. `request_toolset` remains the visible fallback.

See [docs/compatibility.md](docs/compatibility.md).

## Install on a test profile

```bash
hermes profile create router-test --clone
mkdir -p ~/.hermes/profiles/router-test/plugins
cp -R . ~/.hermes/profiles/router-test/plugins/hermes-token-router
```

Enable the plugin in the test profile, then set `profiles.router-test.enabled: true` in the plugin's `config.yaml`. Start a fresh session after configuration changes.

## Configuration

The safe default is disabled. Important v2 settings:

```yaml
global:
  enabled: false
  floor_toolsets: []
  deterministic_rules_enabled: true
  confidence_threshold: 0.90
  fail_open: true
  classifier:
    enabled: false
```

The router does not read routing_scope, expansion_mode, or shrink_mid_session; first-turn routing, session stickiness, and monotonic recovery are fixed runtime behavior in v0.2, not user-configurable modes.

The classifier remains opt-in because adding a network request before every uncertain main-model call can erase latency gains. When disabled, unresolved deterministic requests keep all tools. Direct DeepSeek is the default hosted classifier; OpenRouter is used only when explicitly selected. A local OpenAI-compatible endpoint can be configured as:

```yaml
classifier:
  enabled: true
  provider: custom
  model: router-local
  base_url: http://127.0.0.1:1234/v1
  api_key_env: null  # or an environment-variable name when authentication is required
```

## Development

The plugin's test suite and synthetic regression corpus (500 records) live in the source repository; they are not bundled with this profile. See the hermes-token-router project for `pytest` and benchmark instructions.

## Current measured schema reduction

Against the live 39-tool Hermes registry, Hermes's own rough request estimator measured:

- `web`: 18,627 → 490 tokens (**97.37% reduction**)
- `file,terminal`: 18,627 → 3,207 tokens (**82.78% reduction**)
- `browser,web`: 18,627 → 3,364 tokens (**81.94% reduction**)

See [`docs/baselines/v0.2-rc1.md`](docs/baselines/v0.2-rc1.md) for commands and caveats. These are estimator results, not provider billing receipts.

## Current release gates

A stable release must demonstrate:

- at least 70% median first-turn schema-token reduction;
- at least 99.5% required-toolset recall and 100% critical-class recall;
- no unrecovered registered-tool failures in E2E testing;
- no task-success regression against the full-tool baseline;
- cache-stable serialized tool schemas after routing or the last expansion.

No quantitative production claim should be made until a versioned live validation report satisfies those gates.

## Rev 6 host-admission and recovery contract

Donna preserves Hermes's final authorization role while enforcing a local no-broadening rule for protected definitions. A protected ceiling is the exact protected surface admitted by the host for one agent/session. A pinned floor is the exact admitted subset that must remain visible. Every pin is protected, but direct-orchestrator protected tools remain optional unless explicitly pinned. Protected definitions retain their complete captured OpenAI schemas and original envelope order; they are never manufactured from the global registry.

Trusted admission metadata is accepted only from the `hermes_token_router_admission` hook keyword and `_hermes_token_router_admission` agent attribute. Its exact version-1 shape is:

```json
{
  "schema_version": 1,
  "protected_toolsets": ["..."],
  "pinned_tool_names": ["..."]
}
```

`MISSING/MISSING` is a valid empty-policy compatibility case. Explicit `None`, booleans, malformed/unknown keys, empty or whitespace-padded identifiers, duplicates, and conflicting channels are invalid. Identifiers are not normalized. The adapter builds one immutable ordered owner snapshot from untouched input, evaluates worker identity once, composes the policy, and binds one result to the agent-attached `RouterState`. Same-session calls reuse that result by identity; disable/re-enable retains it and session end clears it. The process-global legacy state is never capability authority.

A worker is recognized only when both `HERMES_KANBAN_TASK` is nonempty and Hermes reports a dispatcher-owned worker. Complete owner mapping pins every incoming definition owned by the worker toolset. Predicate, registry, or owner uncertainty is `SAFE_NO_PRUNE`. Direct orchestrators can use only their host-admitted protected subset. Specialists, delegated children, inherited non-dispatcher contexts, and cron do not gain worker authority from inherited environment. A valid explicit pin for a present owner-unmapped definition protects that exact name; absent siblings remain denied. No exact four-name policy is hard-coded.

When untouched host provenance is unavailable, an attachable valid-policy call is `NO_AUTHORITY`: it preserves the current surface, denies protected additions, and permits append-only ordinary compatibility. The first ordinary append persists an immutable contamination marker before assignment; later same-session callers may append ordinary definitions but can never capture or promote an envelope. Invalid policy is transient `NO_AUTHORITY_INVALID_POLICY`: it preserves all fields, denies every new addition, performs no owner/definition lookup, creates no clean marker, and retains an existing marker. An unattachable agent is installed-only; capture-invalid input permits no expansion.

Route, visible request, `tool_request` middleware, post-tool recovery, and fallback share deterministic admitted/denied/installed results. Mixed ordinary/protected requests may report ordinary additions plus explicit protected denial. Total protected denial is side-effect-free. Candidate validation precedes coordinated setters, and any partial-assignment failure restores the exact pre-call schemas, order, state fields, counters, fallback/retry markers, and lifecycle-slot identity. Retry is allowed only after exact admitted installation. The empty-message path binds admission before returning and performs no classifier, available-toolset, definition-retrieval, recovery-control, retry, or recapture work. Local synthetic tests are contract evidence only, not live runtime acceptance or production rollout.

## License

MIT.
