# Chrome Native Messaging Hosts on macOS

Use this reference when adding or troubleshooting a Chrome extension native host that launches a local Node service.

## Required installation shape

Google Chrome reads per-user host manifests from:

```text
~/Library/Application Support/Google/Chrome/NativeMessagingHosts/<host-name>.json
```

Chrome for Testing uses a different product directory:

```text
~/Library/Application Support/Google/ChromeForTesting/NativeMessagingHosts/<host-name>.json
```

With a custom `--user-data-dir`, put the test manifest in that profile's `NativeMessagingHosts/` directory. Chromium has its own product path as well. Verify the authoritative Chrome native-messaging documentation rather than assuming all Chrome-family builds share one location.

A manifest must contain:

- stable `name`
- `description`
- absolute executable `path`
- `type: "stdio"`
- exact `allowed_origins` entry: `chrome-extension://<32-char-id>/`

Chrome extension IDs are exactly 32 lowercase characters in `a` through `p`. Do not commit a private unpacked-extension ID; pass it to the installer at runtime.

Write JSON as UTF-8 without BOM. Prefer atomic temporary-file + rename installation so Chrome never reads partial JSON.

## Keep generated launchers outside Git

Chrome launched from Finder/Dock does not necessarily inherit the interactive shell PATH. A wrapper that runs bare `node` can pass terminal tests and fail only when Chrome invokes it.

Preferred fix:

1. At install time, capture the absolute Node executable (`process.execPath`).
2. Generate a user-local executable launcher beside the native-host manifest.
3. Point the manifest at that generated launcher.
4. Quote both the Node path and target script path safely, including spaces and single quotes.
5. Never rewrite a tracked repository wrapper with a machine-specific path.
6. Make dry-run genuinely read-only.
7. Test that installation leaves the repository template byte-identical.

## Native messaging protocol: do not wait for EOF

Chrome sends a length-prefixed frame and waits for the response while keeping the native host's stdin open. A host that buffers stdin until the `end` event deadlocks: Chrome waits for output while the host waits for Chrome to close stdin.

Implement a streaming frame parser:

1. Append each `data` chunk to a buffer.
2. When at least four bytes exist, read the native-endian payload length.
3. Wait until the entire frame is buffered.
4. Parse and answer immediately without waiting for EOF.
5. Continue parsing additional frames from the remaining buffer.
6. Serialize responses in request order.

Regression test: write one complete frame into a `PassThrough` stream **without calling `end()`** and require a framed response within a short timeout. Existing tests that call `child.stdin.end()` can conceal the deadlock.

## Launch the service without shell PATH assumptions

Capturing an absolute Node path in the launcher is not enough if the native host then spawns bare `npm`. GUI Chrome's environment may lack npm too.

On macOS, prefer:

```text
<absolute process.execPath> <absolute repo>/src/gateway/server.js
```

Use the existing Windows `cmd.exe /c npm run ...` path only where required for compatibility. Unit-test the launch-command builder for both macOS and Windows.

## Process lifecycle verification

A start script that backgrounds `npm run ...` may record the npm/shell wrapper PID while the real Node server survives as a child. Unit tests using a fake process can miss this.

- Prefer launching the actual Node server process directly.
- After health becomes ready, identify and record the PID owning the listener; verify command and cwd belong to the expected repository.
- Stop only a positively identified PID; never use broad `pkill node` or kill by port alone.
- Verify both the PID and listening socket are gone.
- Treat a missing subscriber endpoint/HTTP 404 as “not available yet” when `/health` is healthy.

## Idle-shutdown testing pitfall

If every HTTP request updates gateway activity, repeatedly polling `/health` prevents idle shutdown and produces a false failure. To test idle shutdown:

1. Disconnect the subscriber.
2. Verify `hasSubscriber: false` once.
3. Make no gateway requests for the idle interval plus margin.
4. Perform one final health/socket check.
5. Then restart through native messaging and verify subscriber reconnection.

## Live extension verification

Current branded Google Chrome builds may ignore command-line `--load-extension`. For automated live testing, install Google Chrome for Testing with `@puppeteer/browsers`, launch it with an isolated profile and CDP port, and use its product/profile-specific native-host manifest directory.

Do not guess which service worker is the extension: query each target's `chrome.runtime.getManifest()` and match the extension name/permissions. Built-in extensions can otherwise be mistaken for the target.

Minimum live proof:

- `chrome.runtime.sendNativeMessage()` starts the host and returns a healthy gateway status.
- Side panel reports Gateway OK and Subscriber Connected.
- MCP `tools/list` returns the canonical count.
- One harmless call such as `chrome.tabs.list` returns real tabs.
- Disconnect, verify idle shutdown without polling, restart, and reconnect.
- Remove temporary profiles, test manifests, downloaded test browser, and positively identified gateway processes afterward.

## Test matrix

- Manifest validation, no-BOM serialization, atomic overwrite
- Absolute generated launcher path and exact allowed origin
- Executable permissions; spaces and single quotes
- Dry-run writes nothing; tracked template remains unchanged
- Streaming framed round trip without stdin EOF
- PATH-independent gateway launch and preserved Windows launch command
- Fresh start → healthy → 404 subscriber status → safe stop
- Listener and PID absent after stop
- Platform-gated macOS shell tests so canonical `npm test` remains valid on Windows
- Full unit suite and smoke test
- Live native start, subscriber connection, MCP tool count, browser call, idle shutdown, and reconnect

## Documentation checklist

Document Chrome reload/restart, manifest verification, Node/PATH troubleshooting, log location, manual lifecycle fallback, exact generated-artifact uninstall, and preserved Windows Registry/PowerShell instructions.
