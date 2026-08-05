# Tauri Native App-Bundle Isolation and Blank-Window Diagnosis

Use this when a macOS Tauri binary starts but its webview is blank, dark, or exposes no in-app accessibility elements.

## Core distinction

A successful raw Mach-O launch is not valid native-app acceptance. A Tauri executable launched directly from `src-tauri/target/release/<name>` can create an AppKit window while lacking the `.app` bundle identity and runtime context WebKit expects.

Typical evidence:

- window exists but canvas is blank or dark;
- no webview controls appear in the AX tree;
- unified logs mention a missing main bundle identifier;
- WebKit child processes report sandbox, LaunchServices, TCC, CoreServices, SkyLight, or IPC failures;
- the Rust/AppKit main loop is healthy, so the process is alive rather than crashed.

## Correct launch contract

1. Build the macOS application container explicitly when bundling is disabled by default:
 ```bash
 export PATH="$HOME/.cargo/bin:$PATH"
 npm run tauri -- build --bundles app
 ```
2. Locate the executable inside:
 ```text
 src-tauri/target/release/bundle/macos/<Product>.app/Contents/MacOS/<executable>
 ```
3. Verify before acceptance:
 - Git SHA/tree/status;
 - `CFBundleIdentifier` and `CFBundleExecutable` from `Contents/Info.plist`;
 - SHA-256 equality between the accepted raw release executable and the bundled executable;
 - architecture and full path.
4. For disposable-HOME testing, create the HOME and standard subdirectories **before** launch:
 ```bash
 mkdir -p "$HOME_ROOT/Library/Application Support" \
 "$HOME_ROOT/Library/Caches" \
 "$HOME_ROOT/Library/Preferences"
 env HOME="$HOME_ROOT" "/path/Product.app/Contents/MacOS/executable"
 ```
5. Do not use `open` when the acceptance contract depends on a custom HOME; LaunchServices does not reliably preserve that injected environment.
6. Bind evidence to the executable path/hash, bundle ID, PID, full command, HOME, app-data path, native window title/bounds, and timestamp.

## Diagnostic ladder

1. Capture the app window and AX tree.
2. Confirm parent and WebKit GPU/network/content processes are alive.
3. Inspect unified logs for parent and exact WebKit child PIDs from launch time.
4. Sample the parent process to distinguish a healthy event loop from a hang.
5. Read the frontend entrypoint: if it renders a loading shell before native invokes, a completely empty page indicates that the frontend asset/script did not execute, not merely a database failure.
6. If needed, enable `WebKitDeveloperExtras` only under the disposable HOME and relaunch; do not alter the user's normal app preferences.
7. Change one launch prerequisite at a time and recapture.

## Late-module startup race

A production bundle can load its module after `DOMContentLoaded` has already fired even when development mode does not. A bootstrap that only registers a new `DOMContentLoaded` listener then never runs.

Use a small independently tested startup gate:

- if `document.readyState === "loading"`, attach one `{ once: true }` listener;
- otherwise start immediately;
- protect startup with an exactly-once flag;
- surface/log rejected boot promises;
- make a missing root element a truthful error rather than a silent return.

Prove the race before fixing it with bounded telemetry recording `readyState`, whether `DOMContentLoaded` was observed, module-import completion, and their order. Remove all probe entrypoints and processes before final gates.

## Background occlusion versus a genuinely blank DOM

On macOS, a WKWebView window driven entirely in the background can be reported as `occluded=1`. WebKit may reach first visually non-empty layout and meaningful paint, then freeze/suspend the layer tree. `computer_use` and direct window captures can consequently show a white canvas with an empty AX tree even though the DOM is rendered.

Do not accept meaningful-paint logs alone, and do not diagnose a product blank screen from background pixels alone. Use this non-foreground discriminator when raising the app is not authorized:

1. Build a temporary diagnostic variant from the exact accepted commit.
2. After `boot()` resolves and again after a bounded delay, report through `document.title` or a no-secret local evidence file:
 - `readyState` and location;
 - root and product-shell selector presence;
 - body text/HTML length and root child count;
 - key `getBoundingClientRect()` values;
 - computed `display`, `visibility`, and `opacity`;
 - caught boot errors.
3. Bind the diagnostic bundle to the accepted source/package hashes and record the small diagnostic delta.
4. Classify **rendered behind occlusion** only when real product selectors exist with nonzero geometry and visible computed styles. A database initialized or WebKit meaningful-paint milestone is insufficient by itself.
5. Revert every probe, remove diagnostic processes/HOME/TMP roots, and require the repository to return to the exact clean accepted commit.
6. Collect a foreground screenshot later when permitted, but do not steal focus from an unattended user merely to satisfy visual evidence.

## Acceptance rule

- Raw-binary blank-window evidence is a controller/setup failure, not a product verdict.
- A bundled launch is still not a pass until actionable nonblank UI is proven either by foreground pixels or by the strict post-boot DOM/layout probe above.
- Treat ad-hoc `spctl` rejection truthfully: it is expected for an unnotarized local bundle and is separate from a successful deep/strict `codesign` check.
- Preserve failed diagnostic evidence, but create a fresh evidence root and HOME for the final workflow matrix.
- Close only exact campaign-owned PIDs and verify WebKit descendants disappear before relaunch or handoff.
- In multi-profile campaigns, the supervisory profile may verify this diagnosis and prepare the handoff, but bundling, relaunch, product debugging, and native workflow acceptance remain with the product-owning profile.
