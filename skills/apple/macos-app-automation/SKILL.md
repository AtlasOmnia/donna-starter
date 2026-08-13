---
name: macos-app-automation
description: macos-app-automation — Automate native macOS apps with AppleScript, URL schemes, System Events, and Hermes computer-use fallbacks; includes TCC/Automation permission troubleshooting.
version: 1.0.0
platforms:
- macos
metadata:
 hermes:
 tags:
 - macos
 - applescript
 - automation
 - tcc
 - native-apps
 category: apple
---
# macOS App Automation

Use this skill when the user asks whether Hermes can control a native macOS app, or asks you to verify, configure, or troubleshoot AppleScript/Automation access for an app.

## Preferred automation ladder

1. AppleScript dictionary / app scripting API
 - Best for structured app data and repeatable operations.
 - Verify with the app's bundle ID, version, and scripting dictionary before promising coverage.
2. App URL scheme
 - Good for quick-add or deep-link actions when documented by the app.
3. System Events / Accessibility scripting
 - Useful for menu items and UI operations not exposed in the app dictionary.
4. Hermes `computer_use`
 - Last-resort GUI operation for UI-only features. Capture first, click by element index, verify after state changes.
 - If the wrapper reports that its cua-driver session ended, recover the same session before concluding GUI control is blocked. If Hermes has already rejected repeated identical calls, change the wrapper call signature or continue through direct `cua-driver call` operations rather than retrying the same arguments.
 - Do not turn an internal wrapper guardrail into the user-facing result. Recover through the direct driver path first; if a real blocker remains, report it in task language with the evidence that distinguishes it (for example, asleep display versus locked login screen).
 - On an unattended Mac, wake a black/asleep display non-destructively and recapture before diagnosing capture failure. A visible login/password screen is a credential gate: never type, request, infer, or bypass the password, and never claim a click reached an app behind the lock screen without verified state change.
 - After the user unlocks the Mac for a long unattended native-app workflow, start a tracked `/usr/bin/caffeinate -dimsu` process immediately and stop it during cleanup; `caffeinate -u -t 2` wakes only and does not prevent a later relock.
 - Electron/webview drawers can retain off-screen controls in the accessibility tree with zero- or one-pixel bounds. Programmatic `set_value` by accessible label may still work, but never use an off-screen element as a human handoff target—especially for credentials. Scroll the exact row into view, recapture, require visible nonzero bounds, focus the intended field, and verify the adjacent action before asking the user to paste or confirm. After Save, recapture neighboring ordinary fields such as Endpoint and Model to catch a paste that landed in the wrong control without echoing its value.
 - Treat a modal dismissal as coordinate-invalidating: perform one click, recapture, and only then choose the next target. Never batch raw coordinate clicks across a dialog close.
 - See `references/cua-session-recovery.md` for deterministic session revival, black-capture diagnosis, lock-screen handling, repeated-call-guard fallback, and modal-safe clicking.

Do not describe a theoretical capability as confirmed until you have run at least one live probe.

## Desktop shortcuts and custom icons

When the user asks for a Desktop shortcut to a packaged macOS app:

1. Verify the real installed target separately from Spotlight results. Inspect `/Applications` directly (for example, `find /Applications -maxdepth 1`) and use `mdfind` only to explain duplicate indexed build artifacts; never treat every `mdfind` result as an installed copy.
2. Freeze the installed target by bundle ID, version, and final executable hash. Do not launch an old candidate from a development volume when the request is for the installed build.
3. Do not modify the signed installed bundle merely to change its icon. Replacing `Contents/Resources/*.icns` changes the bundle’s recorded code-signing hashes and requires a new build/signing/verification cycle.
4. A plain symlink is adequate for a functional shortcut, but it inherits the target app icon and is awkward to customize reliably in Finder. For a custom icon, replace the symlink with a small real launcher `.app` on the Desktop. The launcher should contain its own `.icns`, a distinct bundle ID, and a minimal AppleScript or native executable that opens the verified installed target.
5. Build a valid multi-size `.icns` with `/usr/bin/iconutil` from an iconset containing 1x/2x sizes (16, 32, 128, 256, 512). Set `CFBundleIconFile` on the launcher and mark the launcher custom-icon flag when needed (`SetFile -a C`). Keep the source PNG and `.icns` as user-visible deliverables only when requested.
6. Verify the launcher independently: inspect `Info.plist`, confirm the icon resource exists, open the Desktop launcher, verify the exact installed target process appears, then quit the test instance and confirm no test-instance process remains. Never modify the installed target during icon work.

Command-level recipe: `references/desktop-launcher-icon-workflow.md`.

## Verification workflow

1. Locate the app and bundle ID:

 ```bash
 osascript -e 'id of application "App Name"'
 mdfind "kMDItemDisplayName == 'App Name.app'"
 ```

2. Verify simple AppleScript access:

 ```bash
 osascript -e 'tell application "App Name" to get version'
 ```

3. Inspect the scripting dictionary:

 ```bash
 sdef /Applications/App\ Name.app
 ```

 If `sdef` fails because active developer directory is CommandLineTools, look for an app-bundled dictionary instead:

 ```bash
 find /Applications/App\ Name.app -name '*.sdef' -print
 ```

 Then read/parse that file directly.

4. Test an object-level read with a short timeout:

 ```bash
 osascript -e 'tell application "App Name" to count of documents'
 ```

5. Only after object reads work, test create/update/delete with a clearly temporary item and verify it is removed.

## Apple Mail and multi-account mailbox automation

When Hermes is running on a Mac and the requested mailbox account is already configured in Apple Mail, consider Mail's AppleScript interface before adding direct IMAP credentials. This is especially important when a CLI client such as Himalaya covers only one account but Apple Mail also contains Google, Microsoft, or other accounts.

### Account-coverage rule

1. Inventory the accounts visible to the primary mail tool before searching.
2. A successful search of one account/folder proves absence only from that scope—not from “email” generally.
3. If the expected account is absent from Himalaya, inspect Apple Mail’s configured accounts before concluding that a message is missing.
4. Report the scope explicitly: account, folder, and date window searched.

### Reliable Apple Mail search ladder

1. Confirm Mail’s configured account names with a bounded object read.
2. Prefer the account’s Inbox for recent-message searches. A direct probe such as `count of messages of mailbox "INBOX" of account "Google"` can work even when Gmail’s displayed `All Mail` mailbox cannot be addressed literally.
3. Search sender, subject, and site/domain variants separately rather than forcing one fragile compound predicate. Return only bounded metadata first: message ID, subject, sender, received date, and read status.
4. If a displayed mailbox name returns Apple event `-1728`, stop repeating the same named lookup. Iterate the mailbox objects from `every mailbox of account ...` and run lightweight subject/sender predicates against each object; Gmail labels can be visible by name yet not directly addressable as `mailbox "All Mail" of account ...`. For a large Gmail label, first enumerate mailbox names in order, probe a candidate by ordinal (`mailbox N of account "Google"`), and require its returned `name` to match before searching it. The ordinal is a runtime-discovered object handle, never a hardcoded permanent mailbox number.
5. Use `computer_use` only after confirming Mail has an on-screen window. A running Mail process can have zero capturable windows; create or reveal a message viewer through Mail’s scripting API before retrying GUI capture. If no capturable window is available, continue with bounded AppleScript object queries rather than declaring GUI control impossible.
6. Avoid account-wide `content contains ...` scans until the search is narrowed by mailbox and date; broad body searches can time out. An empty successful AppleScript result means no match in that exact scope, not no message globally.
7. If AppleScript times out or TCC blocks even bounded object access, follow the TCC diagnostic path below; do not translate that into “the email is not present.”

For Google Search Console/indexing notices, useful independent probes include:

- sender: `Google`, `search-console`, `sc-noreply`
- subject: `index`, `indexing`, `pages`, `Search Console`, `new reason`
- the exact site/domain, when known

When a matching notification is found, read the actual message body before diagnosing the website. Separate Google’s reported symptom (for example, blocked by robots, duplicate canonical, redirect, 404, or discovered-not-indexed) from any inference about the current live site.

Reference: `references/apple-mail-multi-account-search.md` contains the concise failure-to-GUI fallback recipe and indexing-notice search terms.

Decision rule:

- Prefer AppleScript for a Mac-local workflow that can rely on the signed-in Mail app. It avoids storing an iCloud app-specific password in Hermes and works with Mail's existing account configuration.
- Prefer Himalaya or another IMAP/SMTP client for headless, server-based, or cross-platform operation. This is mailbox management, not the Hermes Email gateway adapter.

Apple Mail's scripting surface can support structured mailbox operations such as reading and searching messages, creating drafts, sending or replying, moving messages between mailboxes, changing flags, and deleting messages. Before promising a specific operation, inspect Mail's live scripting dictionary and run a bounded read-only probe from the same execution identity Hermes will use.

Operational guardrails:

1. Confirm the intended iCloud account and mailbox are already present and synchronized in Mail.
2. Grant Automation access to Mail for the actual controller, such as Terminal, Python, or Hermes. Approval for one controller does not cover the others.
3. Start with read, search, and draft operations. Require human approval for sending and deletion until the workflow has been tested against a dedicated mailbox or folder.
4. Verify mutations by reading the resulting message or mailbox state back from Mail.
5. If AppleScript is unsuitable, use iCloud's standard IMAP/SMTP path with an Apple app-specific password. Do not request or store the normal Apple Account password.

## macOS TCC / Automation pitfall

Simple AppleScript commands can succeed while deeper object operations hang. This often means macOS TCC Automation permission is waiting on or blocking the real execution path, not that the app is unscriptable.

Signs:

- `get version` works.
- `count of lists`, `make new ...`, `show ...`, or object property reads time out.
- System logs show `TCCAccessRequestIndirect` or `Prompting for access to indirect object <Target App> by <execution identity>`. The identity can be a Python interpreter, Terminal, an SSH wrapper, or another launcher—not necessarily `osascript` itself.

Check the target-specific TCC decision path first, then broaden to the app process if needed:

```bash
log show --last 10m \
 --predicate 'process == "tccd" AND eventMessage CONTAINS[c] "Target App"' \
 --style compact

log show --last 5m --predicate 'process == "AppProcessName"' --style compact | tail -80
```

Fix:

- Ask the user to grant Automation permission in System Settings → Privacy & Security → Automation for the exact execution identity named by TCC.
- If the item is not visible, trigger the prompt from the same execution context with a bounded object-level command, then have him approve it. If he explicitly authorizes remote approval for that permission class, capture the exact prompt, click only **Allow**, and verify the result.
- Choose the final controller before the unattended run. Terminal, Python/Hermes, and other launchers receive separate TCC decisions; approving one does not approve the others.
- Launching the command through a Terminal `.command` file changes the execution identity to Terminal; it can be useful when Terminal is the intended durable controller, but it does **not** bypass TCC. Terminal must still be approved for the target app.
- After approval, rerun a short read-only object probe before any mutation. If it still times out, inspect for an app-owned modal before treating TCC as unresolved; error reporters, recovery prompts, protected-document alerts, and security dialogs can block AppleEvents after permission is already granted.

Never save the conclusion as “AppleScript does not work.” Save the fix: grant Automation permission for the actual execution identity and verify with a bounded read probe.

## AppleScript performance: bulk property fetch

Large object collections (thousands of items, e.g. Apple Notes) break two common patterns:

- `repeat with n in <collection> ... <prop> of n` does one AppleEvent round-trip per item and times out (180s+) at a few thousand items.
- `whose <prop> ≥ value` filters can throw `Access not allowed (-1723)` for some properties (validated: Notes `creation date`).

Fix: fetch the property for the whole collection in ONE AppleEvent, then compare locally:

```applescript
tell application "Notes"
 set d to current date
 set hours of d to 0
 set minutes of d to 0
 set seconds of d to 0
 set dl to creation date of every note of default account
 set c to 0
 repeat with x in dl
 if x ≥ d then set c to c + 1
 end repeat
 return c
end tell
```

Parallel bulk lists (`every note of ...` + `creation date of every note ...`) let you pair titles with properties without per-item AppleEvents. This same shape applies to Mail messages, Contacts, and any collection-backed app dictionary.

TCC also denies direct `sqlite3` opens of protected app containers: `NoteStore.sqlite` fails with `authorization denied`, including the `file:...?mode=ro` URI form. Raw byte reads via `strings` still work; do not build a query path on sqlite3 for a protected store.

Reference: `references/notes-creation-date-count.md` — validated "how many notes since X" recipe with title+time listing.

## Safari native browser verification

When a user explicitly asks for Safari testing, do not substitute Chrome at Safari-sized dimensions. Use native Safari through this ladder:

1. Open the live URL without raising the window: `open -g -a Safari 'https://…'`.
2. Prefer Selenium with `/usr/bin/safaridriver` for viewport screenshots and DOM geometry.
3. Use Safari Apple Events `do JavaScript` only when WebDriver is unavailable.
4. Required Safari settings:
 - Safari → Settings → Advanced → Show features for web developers.
 - Safari → Settings → Developer → Allow Remote Automation.
 - Safari → Settings → Developer → Allow JavaScript from Apple Events.
5. If WebDriver still reports Remote Automation disabled, the user must run `sudo safaridriver --enable`; never type their administrator password.
6. Fully quit and reopen Safari after permission changes. Existing Safari processes can retain the old disabled state.
7. Verify each permission independently:
 - WebDriver: create a short `webdriver.Safari()` session and read `innerWidth`.
 - Apple Events: `tell application "Safari" to do JavaScript "document.title" in front document`.
8. If `computer_use` returns a zero-size Safari capture, switch to Safari WebDriver/Apple Events rather than concluding Safari is untestable.

Surface the exact permission error. Never claim a native Safari pass from Chromium screenshots.

### Safari responsive/full-page acceptance details

Safari WebDriver accepts exact window widths that can map directly to exact `innerWidth` values (verified on Safari 26.5.2); browser chrome reduces height. Always calibrate by reading `[innerWidth, innerHeight, outerWidth, outerHeight]` after `set_window_size()` rather than assuming this remains true across releases.

For full-page evidence, measure `document.documentElement.scrollHeight`, grow the Safari window to `scrollHeight + a browser-chrome allowance`, re-read `innerHeight` and `scrollHeight`, and grow once more if needed before calling `save_screenshot()`. Safari screenshots may be Retina-scaled, so interpret image pixels separately from CSS pixels.

Treat the screenshot pixels—not `save_screenshot() == True`—as the evidence. Safari WebDriver can return a successful but all-black PNG, especially after extreme window resizing or when a session is reused across desktop and mobile sizes. Validate every PNG visually or with a luminance check, retry each viewport class in a fresh Safari session, and keep native Safari geometry results separate from any Playwright/Chromium visual fallback. See `references/safari-screenshot-evidence.md` for the evidence ladder and exact-viewport fallback recipe.

A strong native Safari matrix combines exact widths (typically 375, 390, 1024, 1280, 1440) with:

- visible-element `getBoundingClientRect()` containment checks, not only document `scrollWidth`;
- browser-specific component geometry, such as equality of outer-button and inset-label rectangles;
- H1, metadata, schema, image-load, form-count, and navigation checks;
- native full-page screenshots and contact sheets;
- live interaction tests for forms and drill-down menus.

Weebly forms can contain hidden duplicate inputs that Safari WebDriver refuses to `clear()` or click. Filter to displayed/enabled controls first. If native element interaction remains blocked, set only visible controls with JavaScript, dispatch bubbling `input` and `change` events, call `form.requestSubmit()`, and require the live thank-you confirmation before passing.

For animated mobile menus, click the hamburger, wait, click the submenu parent, wait again, then inspect visible links. Clicking both synchronously can leave only the top-level menu visible and create a false failure. For a clean post-menu screenshot, do not trust the second click alone: wait until the toggle reports `aria-expanded="false"` **and** the navigation is no longer displayed, then allow a short render-settle interval before capture. Otherwise Safari can successfully save a screenshot from the closing transition with the menu still covering the hero.

## Things 3 notes

Things 3 on the user's Mac exposes a useful AppleScript surface:

- App: `/Applications/Things3.app`
- Bundle ID: `com.culturedcode.ThingsMac`
- Dictionary: `/Applications/Things3.app/Contents/Resources/Things.sdef`
- Objects: lists, areas, projects, to dos, selected to dos, tags, contacts.
- Commands/properties include make, delete, duplicate, move, schedule, show, edit, quick entry, parse quicksilver input, status, notes, due date, activation date, completion/cancellation dates, tag names, project, area, and contact.

If Things object commands time out but version reads work, diagnose TCC Automation permission before falling back to GUI automation.

## macOS memory and process cleanup

Reference: `references/macos-memory-process-cleanup.md` covers live memory-pressure audits, per-application RSS aggregation, distinguishing required services from orphaned workers, graceful app shutdown, exact-process verification, command-line self-match pitfalls, and Docker engine checks.

## Chrome native messaging hosts

Reference: `references/chrome-native-messaging-hosts.md` covers macOS Chrome manifest installation, Chrome-vs-Chrome-for-Testing manifest paths, GUI PATH/absolute-Node handling, streaming native-message framing without EOF deadlocks, safe PID ownership, idle-shutdown verification, live MCP/browser testing, and cleanup. Use it whenever a Chrome extension launches a local Node gateway or helper.

## Terminal.app window cleanup

Reference: `references/terminal-frozen-last-login.md` captures the frozen-new-window / stuck-"Last login" recovery pattern and a safe `.zshrc` + `.hushlogin` fix.

When the user wants Terminal windows closed but not the active Hermes/TUI session, do not quit Terminal.app wholesale.

Preferred sequence:

1. Identify which Terminal-backed TTYs are safe to close from the shell side.
 - Use `ps` to map `Terminal -> login -pf -> shell -> child processes`.
 - Preserve the Hermes/TUI TTY and any window still running meaningful foreground work.
2. Try terminating the idle shell/login pair first.
 - HUP or TERM the leaf shell and its parent `login -pf` for the target TTY.
 - Re-check `ps` to confirm the target TTY disappeared.
3. If the process tree is gone but the empty Terminal window remains open, use Accessibility/System Events to close only that window.
 - `tell application "System Events" to tell process "Terminal" to get name of every window`
 - Then click `button 1 of window "<name>"` for the specific leftover window(s).
4. Avoid `tell application "Terminal" to get count windows` or `name of every window` when Terminal is hung or partially blocked; those direct Apple Events can time out even when Accessibility access still works.
5. Verify only the intended Terminal window remains before reporting success.
6. If a newly opened Terminal window shows `Last login...` and then appears frozen, inspect the target TTY with `stty -a < /dev/ttysNNN`.
 - A common failure mode is inherited broken line discipline such as `-echo` or `-icanon`.
 - Immediate recovery for the current stuck window: `stty sane < /dev/ttysNNN`.
 - Durable fix for future shells: add a guarded startup repair to `~/.zshrc`:
 ```zsh
 if [[ -t 0 ]]; then
 case "$(stty -a 2>/dev/null)" in
 *"-echo"*|*"-icanon"*) stty sane 2>/dev/null ;;
 esac
 fi
 ```
 - If the visible annoyance is the banner itself, create `~/.hushlogin` to suppress `Last login...`; that removes the distracting symptom but does not replace the TTY-state fix.

This is the right fallback pattern when direct Terminal AppleScript hangs but GUI-level Accessibility remains responsive.

## Tauri native app-bundle acceptance

Reference: `references/tauri-native-app-bundle-isolation.md` covers raw Mach-O versus `.app` launch semantics, WebKit blank-window diagnosis, explicit `--bundles app` builds, byte-identity verification, disposable-HOME prerequisites, unified-log/process sampling, and the evidence needed before native acceptance. Load it when a macOS Tauri process creates a window but its webview is blank or inaccessible.

## Electron desktop smoke testing

Reference: `references/electron-smoke-isolation.md` covers isolated Chromium user-data arguments, silent macOS Keychain/native-modal hangs, `sample`-based diagnosis, safe dialog handling, and committed-SHA smoke acceptance. Load it when an Electron build succeeds but the smoke process stays alive without emitting its application-owned result.

## iCloud/File Provider dataless files

Reference: `references/icloud-dataless-files.md` covers diagnosing `dataless` placeholders, recursively requesting materialization with Foundation, polling actual readability, rerunning a local job from scratch, and verifying Git pushes. Use it when a Desktop/Documents repository exists but reads fail with `Resource deadlock avoided`, Git cannot recognize `.git`, or a script exits suspiciously without producing output.

## Safety

- Do not type or request secrets through AppleScript or GUI automation.
- Do not click permission dialogs yourself unless the user explicitly instructs you to; ask him to approve macOS privacy prompts.
- For destructive app commands such as emptying trash, deleting records, payments, or submissions, confirm scope before executing.
## Public support files

- `references/apple-mail-multi-account-search.md`
- `references/chrome-native-messaging-hosts.md`
- `references/chromium-file-upload-fallback.md`
- `references/cua-session-recovery.md`
- `references/desktop-launcher-icon-workflow.md`
- `references/electron-smoke-isolation.md`
- `references/icloud-dataless-files.md`
- `references/macos-memory-process-cleanup.md`
- `references/notes-creation-date-count.md`
- `references/safari-screenshot-evidence.md`
- `references/tauri-native-app-bundle-isolation.md`
- `references/terminal-frozen-last-login.md`
