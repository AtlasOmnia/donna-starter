# Start/Stop Generation Race Reference

## Problem

A lifecycle can report `idle` while `start()` is suspended at microphone permission, provider connection, or engine startup. A later continuation can then publish provider/audio ownership after reset, resurrecting a session or overwriting reset state.

## Minimal deterministic proof

1. Inject the permission or connect dependency.
2. Suspend the first start using a checked continuation or actor gate.
3. Wait until the start is definitely suspended.
4. Call and await `stop()`/`reset()`.
5. Assert idle/non-live state before releasing the gate.
6. Release the gate and await the original start task.
7. Assert that no provider/audio resource was created or retained, and no stale status/error escaped.

Do not use sleeps or rely on real permission/network timing. Do not release the gate before stop/reset; that produces a vacuous race test.

## Implementation invariant

The lifecycle owner increments a monotonically increasing generation when accepting start and invalidates it synchronously at the beginning of stop/reset. The start continuation captures its generation and checks it after every relevant `await` and immediately before resource publication. If stale, it disposes only resources created by that continuation. It must not clear shared fields, stop a newer provider, or mutate the current status.

## Swift pattern

Use injectable closures such as:

```swift
init(permission: @escaping () async -> Bool = requestPermission) { ... }
```

For tests, hold the closure with `withCheckedContinuation`, fulfill an expectation when reached, perform `await viewModel.stopSession()`, then resume the continuation and `await startTask.value`. Keep the test `@MainActor` when the lifecycle owner is main-actor isolated.

## Review checklist

- Is pending start represented separately from live ownership?
- Is the token invalidated before teardown awaits provider cleanup?
- Are checks present after permission, connect, and engine-start boundaries?
- Does stale cleanup use local references rather than shared `provider`/`audioEngine` fields?
- Does the test await both stop and the original start task?
- Does it assert absence of resurrection, not merely `status == idle` at an intermediate point?
