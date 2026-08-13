# Specification-Compliance Review Reference

## Requirement matrix

Use one row per normative clause, not one row per feature:

| ID | Normative clause | Code path | Test setup | Assertion | Execution | Verdict |
|---|---|---|---|---|---|---|
| C-01 | Exactly one active worker/transport | `path:lines` | Name + relevant gate | What is observed | Command/result | Pass/fail/unknown |

For a claimed pass, require all three: implementation path, test that creates the condition, and real execution output.

## Adversarial test audit

When a test claims to prove a race or lifecycle invariant, ask:

1. What operation is deliberately held open?
2. At what exact point is the competing operation started?
3. Is the old operation released before or after the new resource is installed?
4. Does the assertion observe the interval where both could overlap?
5. Is cleanup awaited, or merely scheduled in a detached/deferred task?
6. Could the helper itself serialize away the race?

A test named `delayedOldCleanupCannotCancelSecondTransport` is not meaningful if the first cancellation gate is opened before the second request installs its transport. A test named `oneActive` is not enough if its tracker counts only send callbacks and not worker/transport lifetime.

## Async pipeline proof obligations

For an actor-backed latest-pending worker, inspect these transitions:

- `enqueue`: replace one pending item; do not start another worker when one exists.
- worker exit: clear worker/token atomically with observing pending work, so handoff cannot strand the newest item.
- transport install: return an identity handle.
- cleanup: clear state only if the handle still matches; never clear a newer transport.
- stop: increment generation and mark stopping before cancellation; cancel transport; cancel and await worker; then allow a new generation.
- receive/audio callback: check generation both before processing and immediately before delivery.
- timeout: settle the caller’s race once, cancel the operation and transport, and ensure the eventual worker cannot leak an error or frame.

## Integration parity checks

After replacing synchronous provider code with an async pipeline, compare the old and new paths for:

- language normalization (`en-US` vs `en`, invalid fallback behavior);
- model and voice defaults;
- sample rate/channels/audio format;
- error message detail and request IDs;
- stop and interruption callers;
- session-generation ownership;
- unstructured tasks that may outlive `stop()` or `connect()`.

A helper left in the provider but no longer called is a review signal: either the new path has unintentionally dropped behavior, or dead code should be removed and covered by an explicit parity test.

## Evidence wording

Prefer precise statements:

- “The source-level identity guard is present, but the regression test does not create delayed cleanup after the second transport is installed.”
- “The generic unsigned device build passed; simulator tests were not independently rerun because no concrete simulator destination was available.”
- “This is a compliance gap, not a compile failure.”

Avoid claiming a test passed when the command was not run in the current review.
