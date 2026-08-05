# External model gateways with Hermes

Use this pattern when composing Hermes with an OpenAI-compatible model-routing gateway such as Plano. Do not merge the gateway, Hermes core, and application add-ins into one repository.

## Boundaries

- Hermes remains the agent loop and tool executor.
- A tool-surface router remains responsible only for pruning/recovering tool schemas.
- The external gateway remains responsible for upstream model selection, provider credentials, model fallbacks, observability, and affinity storage.
- Application add-ins (Excel, Word, etc.) continue talking to Hermes; they do not call the model gateway directly in native `hermes-agent` mode.

## Update-safe affinity integration

Hermes exposes `llm_request` middleware, which may return `{"request": {...}}` to rewrite provider kwargs before transmission. A standalone profile-gated plugin can inject:

```python
headers = dict(request.get("extra_headers") or {})
headers["X-Model-Affinity"] = stable_affinity_id
request["extra_headers"] = headers
return {"request": request, "reason": "model-affinity"}
```

Derive `stable_affinity_id` from a namespaced hash of the trusted Hermes profile and `session_id`; do not expose or log raw document/session identifiers. Activate only when provider/base URL matches the configured gateway. Preserve existing headers and do nothing for direct providers.

Keep this plugin separate from the tool router. Tool routing and model routing have different failure, privacy, and cache semantics.

## Provider constraints

Start with generic OpenAI-compatible Chat Completions through a `custom:<name>` provider pointed at the gateway. Direct API-key and local providers are suitable first targets. Hermes-managed OAuth transports such as `openai-codex` use specialized authentication and Responses behavior; do not assume a generic gateway can inherit those credentials. Treat OAuth passthrough as a separate transport project.

## Privacy and fallback rules

- Bind the gateway to loopback for local use.
- Keep upstream keys in the gateway's secret environment, never in an Office task pane or workbook.
- Use explicit allowlisted model pools per data class.
- Sensitive routes should be local/private and fail closed; never silently fall back to arbitrary cloud models.
- If the gateway is unavailable, avoid a Hermes fallback that bypasses gateway privacy policy.
- Configure deterministic safe defaults; reject or test any gateway behavior that randomly selects an unknown model.

## Verification gates

1. Basic and streaming responses through the custom provider.
2. Single and parallel tool calls preserve tool IDs, argument JSON, and continuation order.
3. Affinity is stable across a full tool loop, distinct across sessions, and consumed rather than forwarded upstream.
4. Tool-surface routing still preserves profile-local/dynamic tools and recovers registered pruned tools.
5. Failure injection: gateway down, primary model failure, affinity expiry, malformed tool call, and session reset.
6. Privacy test with synthetic sensitive data proving only approved endpoints receive content.
7. Measure real latency, transmitted schema tokens, selected model, and cost before rollout.

For Office add-ins, keep bridge/session authorization independent of model affinity. The bridge ID selects the live document; the affinity value selects the model. A hashed derivative may be used, but the gateway must never become trusted to route document tool calls.