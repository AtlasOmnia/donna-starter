# Multiplex Gateway Plugins with Profile-Guarded Native Prefetch

Use when one Hermes gateway multiplexes many profiles and a latency-critical read-only integration should activate for only one profile.

## Discovery versus activation

In a multiplexed gateway, the plugin manager can be process-global even though request execution temporarily switches to a profile-scoped Hermes home. A plugin placed only under `~/.hermes/profiles/<name>/plugins/` may never be discovered if discovery happened from the global home at process startup.

Separate the concerns:

- **Discovery:** install the plugin in a directory the process-global manager scans, commonly `~/.hermes/plugins/<name>/`.
- **Activation:** enforce the target profile inside every hook invocation using the request-scoped Hermes home.

Never assume “stored under a profile” proves “loaded for that profile,” and never let globally discovered mean globally active.

## Safe profile guard

Inside the hook:

1. Call the runtime’s canonical `get_hermes_home()` while the request profile scope is active.
2. Resolve the path and infer the profile only from a canonical `.../profiles/<name>` segment.
3. Return without mutation if the target profile does not match.
4. Fail disabled when identity is missing or ambiguous.

Do not rely solely on `HERMES_PROFILE`; multiplexed `--profile` execution may not set it consistently. Do not choose the first enabled profile from config order.

## Deterministic read-only prefetch

For a latency-critical lookup:

- Register a narrow native tool schema.
- In `pre_llm_call`, detect only explicit read-only intent.
- Dispatch the real tool with `ctx.dispatch_tool()` and inject a bounded result into current-turn context.
- Route the turn so the model does not redundantly call skills or terminal tools.
- Emit privacy-safe `prefetch started/completed` logs because hook-dispatched tools do not appear as model-authored tool-call lines.

Use a strict mutation denylist. Words such as add, book, cancel, create, delete, move, reschedule, schedule, or update should bypass read-only prefetch. Avoid loose substrings that collide with ordinary words; test word boundaries and phrases.

For date-relative requests, resolve local-day windows deterministically before dispatch. Preserve the canonical global credential/token location without copying secrets into profile config or prompt text.

## Regression matrix

Test at minimum:

- target profile + read-only lookup → exactly one dispatch;
- non-target profile + same prompt → zero dispatches;
- target profile + mutation intent → zero prefetches;
- unrelated prompt → zero prefetches;
- explicit today/tomorrow → bounded local-time arguments;
- handler subprocess failure/timeout → bounded, redacted failure without secret leakage;
- profile identity unavailable → disabled behavior;
- live multiplex gateway restart → plugin discovered once, target hook fires, sibling profile remains unchanged.

## Live latency proof

Record separately:

1. native prefetch start/end;
2. router/classifier time, if any;
3. main-model latency;
4. terminal metadata/render latency;
5. complete HTTP/SSE turn duration.

A fast native handler alone does not prove a fast voice turn. Require one handler dispatch, one main-model call, no skill/setup/token-probe/terminal detour, and deterministic terminal metadata. Keep provider-routing changes out of this acceptance unless explicitly authorized.

## Restart ownership

A gateway cannot reliably restart itself and continue its own verification. Use an external launchd/service owner or one-shot helper to restart, health-check, and relaunch dependent UI. Persist a machine-readable marker/report so the controlling chat can be interrupted without losing evidence. Never click credentials or permission prompts during this path.
