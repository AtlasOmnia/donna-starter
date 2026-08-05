# Electron macOS smoke isolation and hidden-dialog diagnosis

Use this for Electron smoke tests that build successfully but hang before emitting the application-owned result line.

## Isolate Chromium user data correctly

Electron/Chromium switches that own a value should be passed as one argv token. On macOS, this is reliable:

```js
const userDataDir = mkdtempSync(join(tmpdir(), "app-smoke-"));
spawn(electronBinary, [mainScript, `--user-data-dir=${userDataDir}`], {
 env: { ...sanitizedEnv, APP_SMOKE_TEST: "1" },
});
```

Do not use a split pair such as `["--user-data-dir", userDataDir, mainScript]`. Electron can reach the default profile instead of the temporary profile. If that default profile contains safeStorage-backed credentials, an unsigned/development Electron binary may block in a Keychain interaction instead of reaching the smoke hook.

Put the application main script before Chromium switches unless the repository has a tested alternative ordering. Always use a fresh temporary directory and delete it after the test when practical.

## Recognize the hidden-dialog failure mode

Typical symptoms:

- build succeeds;
- Electron remains alive with no stdout/stderr;
- the smoke timeout fires;
- `computer_use` may report an Electron window with zero-size capture;
- a macOS `sample <pid>` shows the main thread inside `-[NSAlert runModal]`;
- unified logs may show Keychain/security activity for the Electron process.

This is evidence of a blocked native modal, not proof that renderer startup or the application logic failed.

Diagnostic sequence:

1. Confirm no stale Electron/smoke process owns the same profile.
2. Reproduce with a unique `--user-data-dir=<path>` token.
3. If still silent, enable Electron logging and sample the process after a bounded wait.
4. Inspect app/System Events windows only to identify the dialog. Do not click permission, password, Keychain, or signing dialogs without explicit user direction.
5. If the isolated-profile run succeeds, patch the smoke launcher and run the real canonical smoke command—not only a manual Electron invocation.

## Acceptance

Require all of the following on the committed SHA:

- the canonical smoke script emits its expected structured result and exits 0;
- the temporary profile is distinct from the user's default Electron profile;
- full validation/build still passes;
- working tree and HEAD remain unchanged across the gate;
- CI repeats the smoke on supported platforms.

A native modal can be transient, but the durable lesson is profile isolation and single-token Chromium switch construction.
