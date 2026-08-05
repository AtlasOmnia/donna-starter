# Hook state across copied execution contexts

Use this when a plugin captures trusted metadata in `pre_tool_call` and consumes or clears it in the tool handler or `post_tool_call`.

## Failure mode

Hermes can snapshot the parent execution context with `contextvars.copy_context()` and execute the handler/post-hook in a copied worker context. A `ContextVar.Token` belongs to the exact context where it was created. Passing that token through another `ContextVar` and calling `token.reset()` from the copied worker raises:

```text
ValueError: <Token ...> was created in a different Context
```

Catching only `LookupError` or `RuntimeError` misses this. Worse, Hermes may isolate the post-hook exception, so the tool call succeeds while the parent retains a deep-copied payload and trusted metadata.

## Durable design rules

- Never transport a `ContextVar.Token` across a copied context.
- Do not treat a successful tool result as proof that post-hook cleanup succeeded.
- Prefer a bounded one-shot holder whose claim/consume/clear operations are context-independent and synchronized. Key it only by trusted server-owned identity, not model arguments.
- Make consumption atomic and fail closed on absent, stale, mismatched, duplicate, or already-consumed state.
- Bound count, byte retention, and age; clear terminal state on every success/failure path.
- Keep independently useful duplicate-turn/idempotency fences separate from temporary payload retention.
- If a `ContextVar` is still useful for request-local lookup, store an immutable holder/key rather than a cross-context reset token, and explicitly clear both parent and worker-visible references.

## Required regression

Exercise the production topology, not only a same-context unit test:

1. Run the pre-hook in a parent context.
2. Create a copied context with `contextvars.copy_context()` or Hermes' live context-propagation helper.
3. Run handler and post-hook in the copied worker context.
4. Assert no exception and exactly one downstream dispatch.
5. Assert no usable plan/payload/trusted metadata remains in either parent or worker after completion.
6. Run concurrent sessions/turns and prove isolation.
7. Prove a second call for one trusted turn is blocked before mutation.
8. Probe exception paths and confirm cleanup remains terminal and content-free.

Also inspect the live Hermes execution path that invokes the hooks; same-context tests can be fully green while production cleanup is broken.