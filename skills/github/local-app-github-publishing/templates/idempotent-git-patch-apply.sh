#!/usr/bin/env bash
set -euo pipefail

# Copy this template into the patch repository and set these defaults for the
# repair being packaged. Callers may override them through the environment.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-${TARGET_REPO:-$HOME/.hermes/hermes-agent}}"
PATCH_FILE="${PATCH_FILE:-$SCRIPT_DIR/patches/repair.patch}"
SENTINEL_FILE="${SENTINEL_FILE:-path/to/affected-file}"
SENTINEL_TEXT="${SENTINEL_TEXT:-replace-with-an-exact-source-sentinel}"
DIFF_SCOPE="${DIFF_SCOPE:-.}"

if ! git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1; then
  echo "ERROR: target is not a Git checkout: $TARGET" >&2
  exit 2
fi

if [[ ! -f "$PATCH_FILE" ]]; then
  echo "ERROR: patch file missing: $PATCH_FILE" >&2
  exit 2
fi

if [[ ! -f "$TARGET/$SENTINEL_FILE" ]]; then
  echo "ERROR: sentinel file missing: $TARGET/$SENTINEL_FILE" >&2
  exit 2
fi

if grep -qF "$SENTINEL_TEXT" "$TARGET/$SENTINEL_FILE"; then
  echo "Repair is already applied."
  exit 0
fi

if ! git -C "$TARGET" apply --check "$PATCH_FILE"; then
  echo "ERROR: patch does not apply cleanly; rebase it against current upstream." >&2
  exit 1
fi

git -C "$TARGET" apply "$PATCH_FILE"
git -C "$TARGET" diff --check -- "$DIFF_SCOPE"

echo "Applied repair to: $TARGET"
