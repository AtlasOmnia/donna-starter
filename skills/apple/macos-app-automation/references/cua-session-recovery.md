# cua-driver session recovery for macOS GUI automation

Use this when Hermes `computer_use` reports that the underlying cua-driver session has ended, especially during a native-app or TCC permission workflow.

## Recovery sequence

1. Run the local daemon health/repair helper if available:

 ```bash
 the ensure-cua-driver-daemon helper (user-local, in ~/.hermes/scripts)
 ```

 A healthy daemon does not automatically revive the wrapper's named session.

2. Recover the **exact session ID from the error** through cua-driver's direct CLI. Pipe JSON on stdin:

 ```bash
 printf '%s' '{"session":"<session-id-from-error>","capture_scope":"desktop"}' \
 | cua-driver call start_session
 ```

 Require a response showing `active: true` and `revived: true` (or an already-active equivalent).

3. Do not immediately repeat a wrapper call that has already failed with the exact same arguments. Hermes may block it as `repeated_exact_failure_block` before it reaches the now-healthy driver. Instead choose one:

 - change the wrapper signature materially, such as capturing the specific app instead of `app="screen"`, or switching from `mode="som"` to `mode="ax"`;
 - use direct cua-driver calls for the remaining bounded operation.

4. For direct CLI fallback, inspect schemas rather than guessing:

 ```bash
 cua-driver describe get_desktop_state --json
 cua-driver describe get_window_state --json
 cua-driver describe click --json
 ```

 Then invoke each tool by piping its JSON input to `cua-driver call <tool>`.

5. Preserve the normal GUI verification loop:

 - capture desktop/window state;
 - identify the exact target control;
 - act once;
 - capture again and verify the state changed;
 - end the named session when finished.

 Treat every modal dismissal as a coordinate-invalidating state change. Never batch two raw coordinate clicks across a dialog close in one shell call: the second click can fall through into the newly exposed application and mutate or trigger an unrelated control. Recapture after **each** modal or permission-button click, even when the next target looked obvious in the prior screenshot.

## Black capture: distinguish sleep from lock

A completely black macOS screenshot is not enough evidence that screen capture failed. First inspect the image deterministically (for example, confirm whether every pixel is black), then wake the display without unlocking it:

```bash
caffeinate -u -t 2
screencapture -x /tmp/macos-awake.png
```

Interpret the new capture:

- Normal desktop: continue the capture → act → verify loop.
- Login/password screen: the Mac is locked. This is a credential boundary, not a computer-use failure. Do not type, request, infer, or bypass the user's password.
- Still black: run the normal cua-driver health/permissions diagnostics and change capture scope before concluding anything about the tool.

`caffeinate -u -t 2` is a wake probe, not a session inhibitor. When the user has explicitly unlocked the Mac for a long unattended native-app workflow, immediately start a tracked `/usr/bin/caffeinate -dimsu` background process and retain its handle for cleanup. Do this before TCC prompting or workbook work, not after the desktop relocks. It keeps an already-unlocked session awake but cannot and must not bypass the login screen.

A specific application window can sometimes still be inspected while the display is locked:

```bash
screencapture -x -l <window-id> /tmp/window.png
```

This is useful for diagnosis only. It does **not** prove that a background or foreground click can cross the lock screen. Never report success unless the post-action window/state proves the intended control changed or disappeared.

## Short-lived direct sessions

If a direct cua-driver session expires between separate shell calls, start the session and perform the immediately dependent action in one shell invocation. Use a fresh stable session ID if reviving the stale wrapper-owned ID continues to expire. This is a lifecycle workaround, not evidence that cua-driver is unavailable.

## Recover an off-Space window before pixel actions

An app may have a healthy process and real top-level window while wrapper capture reports “no on-screen window.” Before relaunching it:

1. Call direct `cua-driver list_windows` without `on_screen_only`, filter by the exact PID, and distinguish the titled product window from 30-pixel menu-bar records.
2. Start a fresh window-scoped direct session with that PID/window ID and capture with `get_window_state` plus `screenshot_out_file`.
3. Pixel clicks cannot reliably anchor while `is_on_screen: false`. Use the native **Window** menu item for the target window (AX action commonly `makeKeyAndOrderFront`) through an element-index click.
4. Re-run `list_windows` and require `is_on_screen: true` before retrying the pixel action.
5. For nested webview scrollers, target a wheel event inside the scrollable panel; escalate only when background delivery reports `background_unavailable` or recommends foreground.

Do not create multiple app instances just because the first window is on another Space. Reconcile to one production process first, then recover its exact window.

## User-facing reporting rule

Do not answer the user with raw wrapper text such as a repeated-call guardrail. That is implementation detail, not the task result. Recover through the direct CLI path first. If recovery exposes a real boundary—such as a locked login screen—state that boundary in one sentence, say what was verified, and offer only the viable next route.

## Permission-dialog safety

Never approve a macOS privacy or Automation prompt merely because it appears. Proceed only when the user explicitly authorizes approving that specific permission. His authorization can be remote (for example, when he is away from the Mac), but it must identify the intended prompt or permission class.

When approval is authorized, verify the result with a bounded read-only app probe before performing mutations. For Excel, an example is reading the app version, workbook count, and active workbook name with a short AppleEvent timeout.

## Pitfall

A healthy daemon plus a successfully revived direct session does not clear Hermes' repeated-identical-call guard. Treat that guard as a call-shape issue: change strategy instead of reporting that computer control remains unavailable.

## Scope-mismatch after revival

A revived session inherits the `capture_scope` from the original `start_session` call (typically `"desktop"`). If you then call the wrapper's `computer_use(action="capture", app="<AppName>", mode="som")`, the wrapper sends `get_window_state` which is disabled for a desktop-scope session, producing:

 capture failed: cua-driver get_window_state failed: window-scope tool 'get_window_state' is disabled while session '<id>' is in desktop scope

**Recovery ladder:**

1. Pass `mode="ax"` to the wrapper capture — AX mode is scope-agnostic and works with desktop scope:
 ```
 computer_use(action="capture", app="<AppName>", mode="ax")
 ```
2. If AX mode returns the tree you need, continue driving via element indices through the wrapper.
3. If you need a screenshot, switch to direct cua-driver CLI with the correct window scope:
 ```bash
 printf '%s' '{"session":"<id>","pid":<pid>,"window_id":<wid>,"max_elements":500}' | cua-driver call get_window_state
 ```
4. Or restart the session with window scope:
 ```bash
 printf '%s' '{"session":"<id>","capture_scope":"window","pid":<pid>,"window_id":<wid>}' | cua-driver call start_session
 ```

**Pitfall:** The `mode` switch on the wrapper is not a session-scope change. If the revived session is in desktop scope, `mode="som"` and `mode="vision"` both fail because they require a `get_window_state` that the desktop scope blocks. Only `mode="ax"` works through the wrapper, or you go direct.

**Pitfall:** The wrapper may refuse to switch back to window scope even after the session is revived (`session_policy_conflict`). When this happens, end all cua-driver sessions (`cua-driver call end_session` for each), then restart with the desired scope. Never fight the policy — drain and restart.

## Vision-guided desktop-coordinate click fallback

When the `computer_use` wrapper is completely stuck (wrapper guardrail `same_tool_failure_halt` after 4 identical failures, or session scope can't be changed), and you need to click a visible on-screen control, use this fallback:

1. **Wake the display if needed:** `caffeinate -u -t 2` then verify with `screencapture -x /tmp/test.png`. If still black, the display is physically off or locked — stop and report the boundary.

2. **Bring the app to front:** `open -a "App Name"` or `osascript -e 'tell app "App Name" to activate'`. Do not use `tell application "System Events" to set frontmost to true` unless TCC Automation permission is already granted for the calling identity.

3. **Capture a native screenshot:** `screencapture -x /tmp/app-screenshot.png`. This bypasses cua-driver entirely.

4. **Get pixel coordinates from vision:** Use `vision_analyze` on the screenshot to ask for exact pixel coordinates of the target control.

5. **Revive the desktop-scope session** (use the error's session ID): `printf '%s' '{"session":"<id>","capture_scope":"desktop"}' | cua-driver call start_session`.

6. **Click by desktop pixel coords:** `printf '%s' '{"session":"<id>","scope":"desktop","x":<x>,"y":<y>}' | cua-driver call click`. Desktop-scope pixel clicks always return `"effect":"unverifiable"` — that is normal. Verify via follow-up screencapture + vision.

7. **Verify and iterate:** `sleep 1 && screencapture -x /tmp/after-click.png && vision_analyze`. If the control didn't activate, try slightly different coordinates (±10px) or double-click. Electron/Chromium controls (gear icons, webview buttons) sometimes need a broader targeting grid.

**Pitfall:** Do not confuse `mode="ax"` wrapper capture with vision-guided pixel clicking — they are separate fallback paths. AX mode works when elements are in the tree but screenshots aren't available; vision-guided pixel clicking works when the screen is renderable but AX actions are unverifiable or the wrapper is stuck. Choose the path that matches the current failure, not both at once.

**Pitfall:** The `same_tool_failure_halt` guardrail fires after the wrapper fails 4 times with identical arguments in one turn. It does not mean cua-driver is broken — it means the wrapper won't retry unchanged. **The guardrail persists even after session revival** — the wrapper caches the rejection internally. The only reliable path after the guardrail fires: end all cua-driver sessions, then use ONLY direct `cua-driver call` CLI commands for the rest of the turn. Do not attempt any more wrapper calls in the same turn, even with different arguments — go fully direct.