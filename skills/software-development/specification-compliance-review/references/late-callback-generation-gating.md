# Late-callback generation gating

## Lesson

A start/stop generation check around `await permission()` or `await provider.connect()` prevents stale continuations from publishing ownership, but it does not prevent callbacks already queued by the stale provider from running after stop or after a newer session starts.

## Review pattern

For every callback installed during session start—provider events, audio output, status, error, transcript, interruption, route, and engine callbacks:

1. Capture the session generation or an equivalent owner identity when installing the closure.
2. At callback delivery, hop to the lifecycle owner and reject the event unless the captured identity still matches the current owner.
3. Ensure rejected callbacks cannot mutate status/error/transcript, clear newer resources, or route audio to a newer engine.
4. Test the adversarial order: hold a stale callback, stop generation N, start generation N+1, deliver the old callback, and assert generation N+1 remains unchanged.

## Evidence standard

A test that only asserts the old `start()` task eventually returns to `.idle` proves pending-start cancellation but not stale event isolation. Use a fake provider with an exposed `onEvent` callback and assert the new session's status, error, transcript, and audio sink are unchanged after late delivery.
