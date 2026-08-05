# Runtime Hook-Composition Regression

## Trigger

Use when a backend plugin loads under a fake context but fails in fresh Hermes discovery with errors involving `PluginContext`, private hook maps, missing configuration paths, or unexpectedly replaced pre-tool hooks.

## Durable failure pattern

A wrapper first delegated tool registration to a base adapter, then attempted to capture the installed hook through `ctx.hooks['pre_tool_call']`. The real runtime exposed `register_hook()` but no `hooks` attribute, so plugin discovery failed before controlled tools were available.

Replacing that private-map access with a second public hook registration allowed discovery, but exposed a second seam: the wrapper computed fixed registry/audit paths while delegating to the base callback with the original runtime kwargs. Fresh live calls therefore lacked the paths and failed policy evaluation. The reusable lesson is that *configuration injection and hook composition are one contract*.

## Regression matrix

1. **No-private-context test** — context fake has `register_hook` and `register_tool`, but no `hooks`; package-level `register(ctx)` succeeds.
2. **Default propagation test** — call registered pre-tool hook without `profile_name`, `surface`, registry, or audit kwargs; it must use wrapper defaults and reach normal policy evaluation.
3. **Security composition test** — a mixed registered-root request remains blocked with the expected reason code, while a permitted single-root read follows the base policy.
4. **Tool result contract** — controlled-tool missing paths return a JSON string containing `INVALID_TOOL_ARGUMENT`, never an exception or raw Python dict.
5. **Fresh-process canary** — invoke Hermes in a new process and verify plugin discovery plus a harmless controlled read. Local tests cannot prove actual hook registration/chaining semantics.

## Deployment boundary

Treat candidate source, profile-local payload, and already-running process modules as distinct artifacts. Stage immutable bytes, atomically replace one already-enabled profile first, hash-check the payload excluding generated cache files, then run a fresh-process canary. Do not restart a gateway or roll the payload to other profiles until the single-profile evidence is complete.

## Anti-patterns

- Reading or mutating `ctx.hooks`.
- Assuming repeated `register_hook` calls chain rather than replace.
- Calculating fallback values and forwarding the unmodified kwargs to the next callback.
- Declaring a repair complete after a unit fake passes without fresh runtime discovery.
