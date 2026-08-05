# macOS Ollama model inventory and complete uninstall

Use this when auditing whether Ollama consumes local model storage or when the user explicitly asks to uninstall Ollama on a Mac.

## Inventory before claiming models exist

Check all three surfaces:

1. `ollama list` for the runtime's registered models;
2. allocated storage under `~/.ollama/models`, especially `models/blobs` and `models/manifests`;
3. large files under standard Ollama roots, because a missing or stale registry does not prove blobs are absent.

Also inspect `~/Library/Application Support/Ollama`, but distinguish small Electron/UI caches from actual model blobs. Report allocated bytes rather than treating an empty directory as a model installation.

## Complete uninstall checklist

With explicit uninstall authorization:

1. Inspect and stop the Ollama GUI/server processes.
2. Identify the actual `.app` location; do not assume `/Applications/Ollama.app`.
3. Inspect the CLI path with `command -v`, `stat`, and `readlink`. The CLI may be a root-owned symlink into an app bundle located elsewhere.
4. Check Homebrew formula/cask ownership, installer receipts, launch agents, and launch daemons before choosing removal commands.
5. Remove only identified Ollama assets:
 - the Ollama application bundle;
 - `~/.ollama` after confirming any models are intentionally included in the uninstall;
 - Ollama Application Support, caches, preferences, and saved state;
 - Ollama-specific launch items;
 - the CLI or package through its owning installer/package manager.
6. Verify no Ollama process remains, the app/data paths are absent, and `command -v ollama` no longer resolves.

## Administrator boundary

A root-owned CLI symlink may remain after the user-owned app and data are removed. Do not claim full completion while it still resolves.

When privileged removal is the only remaining gate:

1. Attempt noninteractive privileged removal only when already authorized.
2. If macOS requires authentication, initiate the credential gate rather than defaulting to instructions for the user to copy: first try a native `do shell script ... with administrator privileges` prompt.
3. If the native authorization dialog rejects or fails, open a visible Terminal tab containing the exact bounded `sudo rm -f <verified-path>` command. The user enters the administrator password directly; the assistant never reads, requests in chat, stores, or types it.
4. After authorization, independently verify that the link is absent, `command -v ollama` returns nothing, no process remains, and the app/data paths are absent.

A dangling symlink consumes negligible storage but still matters for a clean uninstall and can mislead later diagnostics. Start closeout with **Yes** or **No**, separating any credential gate from defects.
