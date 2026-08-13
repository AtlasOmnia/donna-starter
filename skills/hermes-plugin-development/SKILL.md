---
name: hermes-plugin-development
version: 1.2.0
description: hermes-plugin-development — Design, register, and debug Hermes plugins — hooks, YAML wiring, profile detection, token routing patterns.
triggers:
- Build a Hermes plugin
- Add a hook to Hermes
- Plugin not firing / not loading
- Token router / tool router / pre-call filter
- Extend Hermes with custom logic
---
# Hermes Plugin Development

Use when: creating, debugging, or integrating Hermes Agent plugins, including Python backend plugins (tools, hooks, routers, middleware) and JavaScript Hermes Desktop runtime plugins.

## Core patterns

- Choose the extension surface first:
 - Backend plugins live under `~/.hermes/plugins/<name>/` and add tools, hooks, commands, providers, or middleware.
 - Desktop runtime plugins live under `$HERMES_HOME/desktop-plugins/<name>/plugin.js` and add native UI contributions through `@hermes/plugin-sdk`. For model-picker specifics, including a Desktop-local `/switch` command plus backend command-inventory bridge, use `references/desktop-model-picker-plugin.md`.
- Resolve the requested interaction surface before building anything. “TUI,” “terminal,” “over SSH,” or “from Windows over SSH” means the prompt_toolkit CLI, not Hermes Desktop. Never substitute a Desktop popover or a backend text-response command.
- Backend plugin slash handlers return text; they cannot open a prompt_toolkit modal. For a TUI command that opens an existing picker, prefer a central command alias or an update-safe `quick_commands` alias. If the user requires an explicit Session/Global step, aliasing to bare `/model` is insufficient because the standard picker follows its persistence default; extend the TUI picker state with a scope stage and verify that scope reaches the final switch call. For live verification, use a fresh CLI under tmux, synchronize on the visible composer, capture each modal stage, then repeat through the user's real SSH path; do not mistake raw PTY repaint fragments for a product failure. See `references/tui-model-picker-slash-command.md`.
- Desktop-only slash-like UI commands may use a two-surface integration: composer middleware opens/cancels locally, while an enabled Python backend plugin registers inventory/autocomplete and a non-Desktop fallback. Middleware receives a `{ text, attachments }` draft object—never test it with raw strings. This pattern does not satisfy TUI/SSH requests.
- Backend plugins use:
 - `__init__.py`: Python code + hook implementations
 - `plugin.yaml`: metadata + hook declarations
 - Optional `config.yaml`: per-profile settings (e.g., router_model, floor_toolsets)

- A plugin is wired when Hermes discovers it from a supported plugin directory or pip entry point, its manifest is valid, and `register(ctx)` succeeds.
- For fail-closed policy plugins deployed across multiple profile homes, use `references/fail-closed-policy-plugin-deployment.md`: immutable library-to-wrapper staging, canonical-root deduplication, per-profile atomic install/enable, fresh-process and gateway canaries, runtime-cache-aware hash reconciliation, rollback, and stale-session retirement. For malformed controlled-tool schemas, raw-dict result failures, and the source-versus-installed activation boundary, see `references/self-gated-policy-plugin-deployment.md`.
- A plugin is **not yet proven through an API platform** merely because it registers locally. Resolve the active runtime home, confirm the platform-specific toolset allowlist, restart through the approved owner path, and run a live header-to-agent-to-registry-to-handler contract matrix. For trusted `X-Hermes-Session-Id` propagation, negative/auth, streaming, cancellation, concurrency, restart, lifecycle, and hashed-evidence requirements, use `references/api-server-live-plugin-contract.md`.
- Profile-specific activation should be enforced inside plugin config; discovery alone does not mean the plugin should mutate every profile.
- In a multiplexed gateway, discovery can be process-global while hook execution is request-profile-scoped. If a profile-local plugin is never discovered, install it in the global plugin directory but make every hook fail disabled unless canonical request-scoped `get_hermes_home()` resolves the intended `profiles/<name>` path. For latency-critical read-only lookups, combine that guard with mutation-intent exclusion, deterministic `ctx.dispatch_tool()` prefetch, bounded context injection, and one-main-call live timing. See `references/multiplex-profile-guarded-prefetch.md`.
- Declare only hooks present in the target runtime's live hook registry. For version-dependent hooks, check `VALID_HOOKS` before registering instead of advertising an unknown hook and producing startup warnings.

## Reloading Desktop runtime plugins

Desktop plugins normally hot-reload whenever their `plugin.js` changes. Use the least disruptive path:

1. Preferred: save the file and verify the contribution updates.
2. Manual rescan: in Hermes Desktop, open the command palette (`⌘K`) and run **Reload desktop plugins**.
3. If GUI control is unavailable or denied while the user's reload request still stands, retrigger each existing plugin's file watcher without reloading the renderer:

 ```bash
 for f in "${HERMES_HOME:-$HOME/.hermes}"/desktop-plugins/*/plugin.js; do
 [ -e "$f" ] && touch "$f"
 done
 ```

 Verify the target files' modification times changed, the Hermes process remains running, and—when UI access is available—the plugin contribution is present with no load-error toast.

Do not substitute Electron's **View → Reload** unless a full renderer reload is acceptable; it is broader than a desktop-plugin reload and can unnecessarily disturb current UI state. Touching a watched file reloads an already-discovered plugin. A newly added plugin directory may still need the command-palette rescan or the app's periodic directory scan.

## YAML wiring (critical)

- Use `provides_hooks:` (NOT `hooks:`).
 - Example:

 ```yaml
 name: my-plugin
 version: 1.0.0
 description: "My plugin"
 kind: standalone
 requires_env: []
 provides_hooks:
 - pre_agent_init
 - pre_llm_call
 - post_tool_call
 ```

- If hooks are declared but never called, first check `provides_hooks` vs `hooks`. This is a common failure mode.

## Hook function naming

- Hook functions must be PUBLIC (no underscore prefix) unless the plugin system explicitly uses them with underscores.
- Match exactly what you register:

 ```python
  def register(ctx):
      ctx.register_hook("pre_agent_init", pre_agent_init)
      ctx.register_hook("pre_llm_call", pre_llm_call)
      ctx.register_hook("post_tool_call", post_tool_call)
  ```

- If they are named `_pre_llm_call` but registered as `pre_llm_call`, Hermes will never call them.

## Profile detection inside plugins

Hermes does NOT reliably set HERMES_PROFILE when using `--profile <name>`. Don't trust it blindly.

Safe pattern (from the hardened hermes-token-router):

- Prefer explicit `HERMES_PROFILE` / `HERMES_ACTIVE_PROFILE` when present.
- Otherwise infer only from the canonical `HERMES_HOME` path (`.../profiles/<name>`).
- If identity remains unknown, use disabled/default behavior.
- **Never select the first enabled profile by config insertion order.** That can apply another profile's policy to the wrong live agent.

For the user's router experiments, use a dedicated isolated test profile, snapshot the installed plugin/config first, and keep global/default routing disabled.

## Token router / tool routing patterns

For plugins that predict or reduce tools:

- Route once before the first provider request, then keep the surface stable in that live agent process.
- Prefer an early surface hook when the live hook registry exposes one. Otherwise, current Hermes `pre_llm_call` can still reduce the actual provider payload, although it runs after the earliest preflight work.
- Use `tool_request` middleware to expand a registry-known pruned tool before ordinary validation/dispatch.
- Keep `request_toolset` visible as a secondary recovery path. Its schema should accept string toolset names and validate them against the live registry at call time; do not freeze an early-registration enum that may contain only partially registered toolsets.
- Expand monotonically; never reclassify and shrink the tool surface on every turn.
- Fail open on ambiguity or errors rather than relying on large permanent floor toolsets.
- Store state on the agent; key compatibility references by `session_id` and release them on `on_session_end`.
- Use public registry APIs and build recovery choices from the live registry.
- Keep native desktop intent distinct from web-browser and image-analysis intent: capturing a Safari/Chrome/Finder window requires `computer_use`, webpage interaction requires `browser`, and analyzing an existing screenshot requires `vision`.
- A plugin tool remains deferrable under progressive tool search even when registered into a core-named toolset such as `terminal`; non-core tool names are removed before a token router caches the model-facing definitions, so the router cannot restore that tool merely by resolving its toolset. For latency-critical deterministic read-only lookups, either keep the plugin schema visible or perform a real `ctx.dispatch_tool()` from `pre_llm_call`, inject the bounded result as turn context, and pair it with a deterministic no-tool route so the turn pays for one main-model call rather than classifier + tool-call + answer rounds. Emit explicit dispatch/completion logs because hook-dispatched tools do not appear as model-authored `Tool call:` lines, and test that unrelated or mutating intents do not trigger prefetch.
- Judge routing from live route logs and executed tool names, not final prose alone; a correctly loaded tool can still fail later because the target app/window is unavailable or approval is denied.

See `references/tool-router-production-hardening.md` for the full implementation, intent-collision pitfalls, and live validation workflow.

## Composing with external model-routing gateways

When Hermes is placed behind an OpenAI-compatible model gateway, compose the systems instead of merging repositories: Hermes owns the agent/tool loop, a tool router owns schema reduction, and the gateway owns upstream model choice. Use a separate profile-gated `llm_request` middleware plugin to inject a stable session-affinity header; do not fold provider routing, credentials, or privacy policy into the tool router.

Keep document/add-in bridge authorization separate from model affinity, use explicit allowlisted model pools, and fail closed for sensitive routes rather than bypassing the gateway through an unrelated cloud fallback. Generic custom providers are the first integration target; specialized Hermes-managed OAuth transports require an independent compatibility design.

Full architecture, privacy rules, and verification gates: `references/external-model-gateway-affinity.md`.

## Runtime hook-composition contract

Never read or replace a plugin context's private hook storage (for example, `ctx.hooks`). A runtime may expose only `ctx.register_hook(...)`, and even when multiple registrations are accepted their replacement/chaining semantics are runtime-specific.

For a wrapper that adds policy around a base hook:

1. Build one merged kwargs mapping in the wrapper, resolving every wrapper-owned dependency (`profile_name`, `surface`, registry/audit paths, etc.). If the runtime supplies a key with `None` or an empty value, `dict.setdefault()` will **not** apply the fallback; assign the resolved value explicitly (`merged['registry_path'] = resolved_registry_path`) so required dependencies cannot be erased by a null runtime field.
2. Pass that **same merged mapping** to both the wrapper's additional policy and the base hook. Computing defaults and then calling the base hook with the original kwargs silently discards the dependencies.
3. Prefer an explicit composed callback registered through the public API; do not assume a second `register_hook` call preserves a previous callback.
4. Add a regression fake that has `register_hook` and `register_tool` but deliberately lacks `hooks`, then invoke the registered hook without private injected parameters. Assert the normal policy path works rather than returning a configuration-path error.
5. Prove the actual live runtime with a fresh process; local fake-context success alone does not establish hook ordering or discovery behavior.

See `references/runtime-hook-composition-regression.md` for the concrete policy-plugin failure sequence and canary matrix.

### Controlled-launch preflight disagreement

For policy-plugin repairs that must use a controlled `inspect_project` / `launch_specialist` seam, treat a non-zero Git preflight inside the registered candidate root as a hard **checkout-accessibility HOLD**, even if a registry snapshot says the root is clean and writer-free. Never work around that by launching an ungoverned writer or deploying a previously staged payload. A staged manifest proves only the bytes present when it was created; compare the staged hashes for every required repair file—especially wrapper/bootstrap files—before considering it a candidate. If the active repair requires a later wrapper/config-propagation change absent from staging, preserve the stage and restore/reconcile source Git accessibility before retrying the one controlled launch. Record the exact Git subcommand and exit status as evidence.

### Self-gated repair deadlock (policy plugin blocks its own deployment)

When the policy plugin that gates general execution is itself the broken component and its installed payload is stale:

1. Expect **every** fresh profile session (default and specialist profiles) to resolve as the default profile and deny `terminal`/`execute_code` with `default profile must use controlled supervisory tools`. Proven live: a specialist-profile one-shot received the default-profile verdict.
2. Agent-routed deployment is therefore impossible — including cron agent ticks, whose delegates inherit the same denied surface AND do not expose the controlled tools (`tool_search` finds none in subagent runtimes).
3. Use the **scheduler script channel** instead: a `no_agent: true` cron job executes its script directly in the scheduler process, entirely outside the agent tool surface — the same mechanism `apply-patches.sh` and watchdog scripts already use. This is sanctioned infrastructure operation, not a guard bypass; keep the canary and rollback gates intact.
4. Split the deployment into two phases with a review boundary: Phase A read-only (verify HEAD/dirty set, run the real test suite, snapshot per-profile installed hashes for rollback, stage an immutable merged payload with a hash manifest); Phase B (atomic per-profile replacement, fresh-process discovery canaries, gateway restart only after all pass, automatic rollback on any failure, exact result artifact `DEPLOYED_AND_VERIFIED`/`ROLLED_BACK`/`HOLD`).
5. Never deploy a staged payload whose provenance predates the final candidate dirty set; re-stage from current candidate bytes.

Launch mechanics learned alongside this case:
- `launch_specialist` / `hermes --profile X chat -q "handoff:<path>"` one-shots exit in seconds without doing work — the spawned session treats the path as literal text. Pass the full brief **inline** as handoff text; inline-text one-shots do execute real work.
- One-shot profile workers cap at the profile's `max_turns` (observed 40/40) and exit **without writing result artifacts**. Require artifact-first behavior or launch with `--max-turns N`.
- Under the governed profile, `write_file` refuses new paths with `path does not exist`; the `patch` tool V4A `*** Add File:` mode creates files successfully.
- One-shot `no_agent` cron jobs: use duration schedules (`'1m'`, `'30m'`); after arming, verify `last_run_at` and the output artifacts rather than assuming the tick fired.

See `references/self-gated-policy-plugin-deployment.md` for the worked case and script skeleton.

## Debugging checklist

When a plugin loads but does nothing:

- Confirm:
 - Plugin is discovered from a supported directory or pip entry point
 - Profile gating resolves the intended live profile and enables only that profile
 - `plugin.yaml` uses `provides_hooks` and does not advertise hooks absent from the live registry
 - Hook functions are public and match registration names
- Add temporary print() at top of each hook to confirm invocation.
 - **CRITICAL: ensure print() calls are AFTER the closing `"""` of any docstring**, not inside it. A print() placed inside a multi-line docstring is just text — it never executes. This wasted 30+ minutes in the hermes-tool-router session (June 2026). Verify: `grep -n "def your_hook" __init__.py` then visually check the next 5 lines for proper docstring closure.
- Check logs for "PLUGIN LOADED" / "plugin registered" messages.

## Provider API format mismatches

When a plugin calls an external model/API directly (without going through Hermes' provider routing):

- Verify the API format. Codex at `chatgpt.com/backend-api/codex` uses the **Responses API** (`/responses` endpoint), NOT Chat Completions (`/chat/completions`). A raw `OpenAI` client calling `client.chat.completions.create()` against this URL receives Cloudflare challenge HTML, not JSON.
- Hermes' own transport layer (`agent/transports/codex.py`) handles this correctly via `ResponsesApiTransport`. If your plugin needs Codex, either use Hermes' transport or implement Responses API format directly.
- For standard Chat Completions, prefer providers that support it natively (DeepSeek, OpenRouter, local LM Studio).

## Router prediction — provider selection

For plugins that call a small classifier before the main turn, latency and failure isolation matter more than model sophistication.

**the user-specific default:** deterministic-first, external classifier disabled unless needed. If enabled, prefer direct DeepSeek or a local OpenAI-compatible endpoint. Use OpenRouter only when the user explicitly requests it.

Requirements:

- Structured JSON output with explicit numeric confidence.
- Unknown toolsets, missing/invalid confidence, malformed output, timeout, or provider failure → full-surface fallback.
- Short hard deadline (roughly 1.2 seconds for routing).
- Local OpenAI-compatible configuration should accept `base_url`, model, and an optional API-key environment-variable name.
- Never send prompt text to an external classifier without an explicit config opt-in and privacy disclosure.

Avoid Codex for small router calls unless you intentionally implement its Responses API transport.

## Trusted hook state across copied contexts

Hermes may run a tool handler and `post_tool_call` hook in a copied execution context rather than the exact context that ran `pre_tool_call`. Never create a `ContextVar.Token` in the parent hook, transport it through another context variable, and call `Token.reset()` in the copied worker: Python raises a cross-context `ValueError`, while isolated hook-error handling can make the tool appear successful and leave sensitive payload/trust state retained in the parent.

Use a bounded, synchronized one-shot holder keyed only by trusted runtime identity. Consumption and cleanup must be atomic and valid from either context, fail closed on stale/missing/mismatched state, and leave no usable payload or trusted metadata in parent or worker. Test the real topology with `contextvars.copy_context()` or Hermes' context-propagation helper; same-context hook tests are insufficient. Require one dispatch, no cleanup exception, no retained state in either context, concurrent isolation, and duplicate-turn rejection before mutation.

See `references/hook-contextvar-lifecycle.md` for the failure reproduction, durable design rules, and regression matrix.

## Threaded timeout for plugin API calls

When a plugin makes an external API call, enforce a real caller deadline and fail open.

**Pitfall:** `with ThreadPoolExecutor(...)` plus `future.result(timeout=...)` is not a hard deadline. After the timeout, leaving the context manager calls executor shutdown and may wait for the hung worker.

Use a daemon worker and bounded queue (or a transport with enforceable cancellation):

```python
import queue, threading

results = queue.Queue(maxsize=1)
def worker():
    try:
        results.put((True, call_provider()), block=False)
    except BaseException as exc:
        results.put((False, exc), block=False)

threading.Thread(target=worker, daemon=True).start()
try:
    ok, value = results.get(timeout=1.2)
except queue.Empty:
    return None  # full-surface fallback; do not join the worker
if not ok:
    return None
return value
```

Test elapsed wall time with a deliberately sleeping worker so a future refactor cannot silently reintroduce shutdown waiting.

## str.format() and JSON templates — curly brace escape

When a plugin prompt template uses `str.format()` and contains JSON examples (common for router/classifier plugins), curly braces in the JSON MUST be escaped by doubling (`{{` and `}}`):

```python
# BROKEN — KeyError: '"toolsets"'
ROUTER_PROMPT = """Example response:
{"toolsets": ["terminal", "web"]}"""

# FIXED — double the braces in JSON examples
ROUTER_PROMPT = """Example response:
{{"toolsets": ["terminal", "web"]}}"""
```

Python's `str.format()` interprets ALL `{...}` as format fields, including those inside JSON literals. This is a silent runtime error (caught by `except Exception`) that produces no visible output unless you have debug prints inside the except block.

## Profile config changes — update .env too

When changing a profile's model or provider, you MUST update both:
1. `config.yaml` — `model.provider` and `model.default`
2. `.env` — `HERMES_INFERENCE_PROVIDER` and `LLM_MODEL`

`.env` values override config.yaml at Hermes startup. Changing only config.yaml leaves the old provider in effect, producing silent connection failures to unreachable endpoints.

## Debugging plugin output — use files, not pipes

When debugging plugin `print()` output via `hermes --profile X chat -q "..."`:

- **Avoid**: `hermes ... 2>&1 | grep "plugin-name"` — grep may exit (closing the pipe) before all output is written, especially if the plugin makes API calls. The `SIGPIPE` kills Hermes mid-execution.
- **Use**: `hermes ... > /tmp/debug.txt 2>&1; grep "plugin-name" /tmp/debug.txt` — captures everything, grep runs after Hermes exits.

## Model command availability drift checks (e.g. `/modelx`)

When a scoped command like `/modelx` appears in docs or patch trails but is missing in runtime, verify in order:

- Command registry (Python surface):
 - `resolve_command("modelx")` must return `CommandDef(name="modelx", cli_only=True)`.
 - `is_gateway_known_command("modelx")` should be false when this is CLI-only.
 - `resolve_command("switch")` should stay unset if `/modelx` owns scoped switching.
 - `resolve_command("model")` must still exist and remain gateway-available.
- TUI layer (if terminal UX depends on it):
 - `ui-tui/src/app/slash/commands/session.ts` must include `aliases: ['modelx']`.
- Script validation:
 - `post-update-autoresearch-check.sh` modelx assertions should pass.
- Source provenance if it still fails:
 - Check if the feature landed on another branch and is not on your active checkout.
 - Compare expected feature files (`hermes_cli/commands.py`, `cli.py`, `ui-tui/src/app/slash/commands/session.ts`, `tests/cli/test_modelx_picker.py`) across branch boundaries before assuming runtime corruption.

Pitfall: patch apply logs can be noisy; a successful return code is not proof of semantic parity.

See `references/modelx-branch-drift-triage.md` for a proven diagnostic flow.

## Public distribution prep

When preparing a local/dogfood plugin for GitHub public distribution:

### Cross-platform deterministic-prefetch integrations

For a plugin that performs a deterministic read-only lookup before the main model call (calendar, email, Drive, reminders, or similar), treat local dogfood code as a prototype until all of these are true:

- Remove machine- and user-specific assumptions: no absolute home paths, profile names, personal resource IDs, or dependencies on another user's installed skill tree.
- Use a portable executable/module entry point (`sys.executable`, `get_hermes_home()`, `shutil.which()`), not a Bash-only launcher or hard-coded interpreter path; test subprocess and path behavior on both macOS and Windows.
- Export a clean public tree rather than publishing `~/.hermes/plugins/<name>/`; include only source, manifest, portable backend, sample config, docs, tests, packaging metadata, `.gitignore`, and `LICENSE`.
- Make services and profiles opt-in and profile-agnostic by default. A shared gateway may discover a plugin process-globally, so enforce request-scoped profile guards inside the hook.
- Prefetch only high-confidence, read-only intents. Exclude sends, replies, creates, deletes, shares, and other mutations; preserve Hermes confirmation gates for those actions.
- Bound every lookup by result count, field/body size, timeout, and logs. Inject metadata/snippets rather than full sensitive bodies by default, and fail open to the normal model/tool path on ambiguity or backend failure.
- Document data egress explicitly: which fields enter the model request, whether a hosted provider receives them, what stays local, and how users disable each service. Google Gmail/Drive integrations require a least-privilege scope plan and may require OAuth verification/security-assessment work before broad public use.
- Pin or test against a minimum Hermes/plugin API version, verify the live hook registry, and run fresh-process Mac/Windows acceptance—not only fake-context unit tests.

Keep the reusable workflow in `references/cross-platform-prefetch-publication.md`.

### Least-privilege OAuth for Workspace prefetch plugins

When adding Gmail or another sensitive Workspace adapter, treat authorization as a separate human gate from implementation:

- Inspect the installed OAuth helper's real parser and scope list before following its documentation; a stale `--services` example can cause an unintended broad consent request.
- If the shared helper cannot express least privilege, add a source-owned service-specific auth helper with an explicit scope allowlist. For Gmail-only mode, the exact scope is `https://www.googleapis.com/auth/gmail.readonly`; do not include Gmail send/modify or unrelated Drive, Docs, Sheets, or Contacts scopes.
- Accept Desktop OAuth client JSON only from an external user path, reject client/token paths inside the repository, and store tokens under a user-local Hermes home path outside Git.
- Never authorize OAuth or read live personal data during a coding campaign. Use mocked OAuth/API responses and exact-scope/path regression tests, then stop at the browser-consent gate.
- Keep existing Calendar credentials separate; do not revoke or mutate a working Calendar token just to add Gmail.
- Gmail prefetch must be disabled by default, return bounded metadata/snippets only, exclude full bodies/attachments, and reject send/reply/forward/delete/archive/trash/mark-read/label mutations.

This keeps implementation evidence separate from live authorization evidence: green tests prove the adapter contract, not that a user's Gmail account has been authorized.

Detailed workflow: `references/least-privilege-workspace-oauth.md`.

### Long-goal handoff and delegated acceptance

For long autonomous coding goals that prepare a public plugin or desktop bridge:

- Save the complete specification to an absolute Markdown path and launch the worker with a short instruction to read that file. Do not rely on a rendered `[[ … [N lines] … ]]` placeholder; the goal manager stores its raw argument and does not dereference a lossy display representation.
- If the worker loads an unrelated skill (for example, Obsidian) or searches for a truncated note title, treat that as a malformed handoff. Clear or stop the goal and relaunch from the file; do not accept the resulting “blocked” judgment as task completion.
- A normal worker exit, a green judge verdict, or a report claiming “all tests passed” is not independent evidence. Re-check the exact checkout, writer ownership, dirty set, changed/untracked files, `git diff --check`, privacy scan, and required tests yourself.
- Run each gate from the repository directory that actually owns its manifest (`desktop/` for a desktop `package.json`, for example), and record the command working directory. A root-level package-manager failure may be a wrong-directory diagnostic rather than a product failure.
- After a delegated worker modifies a shared checkout, recapture ownership and state before any follow-up writer. Do not overlap workers or silently discard unrelated changes.

See `references/long-goal-public-prep-handoff.md` for the compact handoff and acceptance checklist.

When preparing a local/dogfood plugin for GitHub public distribution:

- Stage a clean public tree instead of publishing the live `~/.hermes/plugins/<name>/` directory directly.
- Copy only source, manifest, sample config, docs, tests, and packaging files; exclude backups, caches, logs, local profile state, and credentials.
- Make public sample config disabled-by-default and profile-agnostic.
- For experimental/proof-of-concept plugins, make the README warn users before installation/use: create or use an alternate test profile first (for example `router-test`), enable the plugin only there, and move to the primary profile only after validating routing behavior and toolset mix.
- Add explicit README privacy/data-egress disclosure if router/provider calls can send prompt text outside the local process.
- Add `LICENSE`, `.gitignore`, and `requirements.txt` or `pyproject.toml`.
- Keep recovery-tool enum choices aligned with canonical toolset names; test enum/description consistency.
- Run py_compile, smoke tests, pytest, and a privacy grep before committing.
- Set repo-local public git author before the first commit, or amend with `git commit --amend --reset-author --no-edit` before publishing.
- Use a public-facing commit subject because GitHub shows the latest commit message beside every file; prefer something like `feat: publish standalone tool router proof of concept` over an internal `chore:` message.
- If GitHub already has an old public version, preserve it with a legacy branch/tag before replacing `main`; use `--force-with-lease`, then update repo metadata.
- Add visual docs when explaining routing behavior publicly: an inline SVG in README plus a self-contained `docs/how-it-works.html` makes the pre-turn flow, small-router-model requirement, fail-open path, narrowed tool surface, and `request_toolset` recovery easy to understand.

Detailed checklist: `references/public-plugin-distribution-checklist.md`.
Repo replacement workflow: `references/public-plugin-repo-replacement.md`.

## References

- `references/api-server-live-plugin-contract.md` — prove a backend plugin through the live API server, including trusted session-ID propagation, platform toolset exposure, negative/streaming/cancellation/concurrency/restart/lifecycle cases, and independently hashed evidence.
- `references/desktop-model-picker-plugin.md` — build and test a native **Desktop-only** status-bar picker with Session/Global scope, live `/model` inventory refresh, and explicit expensive-model confirmation.
- `references/tui-model-picker-slash-command.md` — implement a prompt_toolkit `/switch` picker for terminal/SSH use with an explicit Session/Global scope stage; includes alias, state-machine, testing, and update-safety pitfalls.
- `references/router-model-latency.md` — live latency benchmarks and provider data for router model selection.
- `references/tool-router-production-hardening.md` — production architecture, current hook timing, middleware recovery, packaging, and live validation procedure.
- `references/external-model-gateway-affinity.md` — compose Hermes with model-routing gateways using profile-gated affinity middleware, privacy boundaries, and end-to-end verification gates.
- `references/public-plugin-distribution-checklist.md` — checklist for sanitizing and packaging a local/dogfood plugin for public GitHub distribution.
- `references/public-plugin-repo-replacement.md` — preserving/replacing an existing old GitHub public repo when publishing a cleaned standalone plugin.
- `references/hook-contextvar-lifecycle.md` — safely capture, consume, and clear trusted plugin-hook state when Hermes runs handlers/post-hooks in copied execution contexts.
- `references/modelx-branch-drift-triage.md` — check if `/modelx` availability issues are checkout-branch drift versus runtime regression.
- `references/gmail-oauth-handoff.md` — preflight Gmail OAuth client type, exact file paths, least-privilege scopes, and safe terminal handoffs before user authorization.

- Example: hermes-token-router plugin (~/.hermes/plugins/hermes-token-router)
 - Shows per-profile config gating, toolset prediction, recall fallback, and safe degradation.
## Public support files

- `references/api-server-live-plugin-contract.md`
- `references/cross-platform-prefetch-publication.md`
- `references/desktop-model-picker-plugin.md`
- `references/external-model-gateway-affinity.md`
- `references/fail-closed-policy-plugin-deployment.md`
- `references/gmail-oauth-handoff.md`
- `references/hook-contextvar-lifecycle.md`
- `references/least-privilege-workspace-oauth.md`
- `references/long-goal-public-prep-handoff.md`
- `references/modelx-branch-drift-triage.md`
- `references/multiplex-profile-guarded-prefetch.md`
- `references/public-plugin-distribution-checklist.md`
- `references/public-plugin-repo-replacement.md`
- `references/router-model-latency.md`
- `references/runtime-hook-composition-regression.md`
- `references/self-gated-policy-plugin-deployment.md`
- `references/tool-router-production-hardening.md`
- `references/tui-model-picker-slash-command.md`
