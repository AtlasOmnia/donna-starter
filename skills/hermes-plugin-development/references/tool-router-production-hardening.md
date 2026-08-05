# Tool-router production hardening

Use this reference when building or validating a Hermes plugin that prunes tool schemas.

## Safe architecture

1. Route once before the first provider request in a live agent process.
2. Keep the selected surface stable for that session/process.
3. Expand toolsets monotonically; never shrink after the initial route.
4. Keep a compact, live-registry-generated `request_toolset` tool visible.
5. Fail open to the full surface on uncertainty, malformed classifier output, timeout, registry mismatch, or profile ambiguity.
6. Store mutable state on the agent and key any compatibility agent cache by `session_id`; release cached references on `on_session_end`.

A resumed CLI session starts a new process and therefore creates fresh in-memory router state. Gateway/TUI sessions retained in one process can preserve the sticky surface.

## Hook timing on current Hermes

`pre_turn_context_build` is version-dependent and may not exist in the live `VALID_HOOKS` registry. Never advertise or register an unavailable hook unconditionally; this creates startup warnings.

Current stock `pre_llm_call` is still useful: it runs after the earliest preflight work but before the actual provider request and the conversation loop's later request-pressure estimate. Mutating `agent.tools` there reduces transmitted first-turn schemas, though it cannot undo the earlier preflight work. Diagnostics should report these separately:

- first-turn provider-request savings available
- preflight routing available

Check live hook/middleware registries instead of trusting version strings.

## Automatic recovery without a router-specific core hook

Hermes `tool_request` middleware runs before normal tool validation and dispatch. When the model emits a registry-known but pruned tool:

1. Resolve the live agent by `session_id`.
2. Confirm the tool is registered but absent from `valid_tool_names`.
3. Resolve its owning toolset through public registry APIs.
4. Expand that toolset on the agent.
5. Return the unchanged args to middleware.
6. Let ordinary requirement checks, approvals, validation, and execution continue.

Do not recover hallucinated or unregistered names. Keep `request_toolset` as the visible fallback.

## Profile gating

Never activate the first enabled profile by insertion order when identity is unknown. Resolve profile identity in this order:

1. Explicit `HERMES_PROFILE` / `HERMES_ACTIVE_PROFILE`.
2. Canonical `HERMES_HOME` path inference (`.../profiles/<name>`).
3. Safe disabled/default behavior.

For the user's router experiments, use a dedicated isolated test profile. Snapshot the installed plugin and its config before deployment; keep global/default routing disabled.

## Classifier policy

Deterministic-first routing should be the default. External classification is opt-in.

- Require structured JSON with explicit numeric confidence.
- Missing, malformed, nonfinite, out-of-range, low-confidence, or unknown-toolset results fail open.
- Direct DeepSeek or a local OpenAI-compatible endpoint are preferred defaults for the user; OpenRouter is used only when explicitly requested.
- Enforce a short hard deadline (about 1.2 seconds for routing).

Do not implement the deadline using `with ThreadPoolExecutor(...)`: timing out `future.result()` can still block while the context manager waits for executor shutdown. A daemon worker plus bounded queue lets the caller return at the deadline without joining the worker.

## Registry and packaging

- Use public registry methods (`get_registered_toolset_names`, `get_tool_names_for_toolset`, `get_entry`, `get_definitions`). Avoid `_snapshot_entries()`.
- Do **not** freeze recovery toolset names into a JSON-schema `enum` during plugin registration. Plugin registration can occur before the full tool registry is populated, producing a stale enum (for example, exposing only `spotify`). Accept string names, provide canonical examples in the description, and validate each requested name against the live registry inside the handler.
- For pip packaging, expose `[project.entry-points."hermes_agent.plugins"]` and verify the built wheel contains `__init__.py`, `config.yaml`, `plugin.yaml`, and entry-point metadata.
- Install the wheel into an isolated environment and verify the entry point through `importlib.metadata.entry_points()`.

## Intent-collision pitfall: browser schemas are not desktop control

Treat webpage automation and native desktop control as separate classes:

- `browser`: navigate URLs, click web elements, submit forms, inspect page DOM.
- `computer_use`: capture/control native app windows such as Safari, Chrome, Finder, or another desktop application.
- `vision`: analyze an already-supplied screenshot or image.

A prompt such as “Capture the Safari window and tell me what is open” must route to `computer_use`, not `browser + web`. Otherwise the model sees browser schemas, concludes desktop control is unavailable, and refuses instead of calling the correct tool. Add high-precision desktop intent patterns for `computer-use`, `desktop control`, `capture <app> window`, `<app> window`, and `capture screen/desktop/window`; evaluate them before generic screenshot/image and browser rules.

Live validation must distinguish router success from downstream tool state. If logs show `predicted_toolsets=['computer_use']` and the model executes `computer_use`, routing succeeded even when cua-driver later reports that the requested app window is not visible or an approval is denied. Capture the downstream failure separately; do not misclassify it as a routing regression.

## Verification sequence

1. Unit tests for conceptual collisions, minimum toolsets, profile resolution, session isolation, monotonic expansion, malformed confidence, hard timeout, and browser-vs-desktop-vs-vision intent separation.
2. Middleware test proving a registered pruned tool expands before validation.
3. `py_compile`, full pytest, Ruff, benchmark corpus, and `git diff --check`.
4. Build sdist/wheel and perform an isolated import/entry-point check.
5. Use Hermes's own `agent.model_metadata.estimate_request_tokens_rough`, not character estimates, against the live registry.
6. Deploy only to test profile after making a timestamped snapshot.
7. Run live test profile probes:
 - conceptual/no-tool request
 - web request with real tool execution
 - file/terminal request
 - native desktop request such as “Capture the Safari window” and verify `computer_use` is exposed and called
8. Verify logs show predicted toolsets, narrowed tool counts, API input tokens, cache reuse, and no router-specific errors. Compare the exact user prompt to the route decision; do not infer success from the final prose alone.

A known-good live validation showed conceptual routing to only `request_toolset`, web routing to three tools with successful `web_search`, file routing with successful `read_file`, and Safari-window routing to `computer_use` followed by real cua-driver calls. Treat exact token counts and downstream desktop-window visibility as environment-dependent; preserve the method, not the number.
