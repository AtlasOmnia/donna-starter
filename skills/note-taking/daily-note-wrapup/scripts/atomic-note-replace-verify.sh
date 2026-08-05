#!/bin/bash
# Atomically replace a daily note, protect it from a stale one-shot writer,
# and prove its bytes remain stable both while locked and after unlock.
set -euo pipefail

if [[ $# -lt 2 || $# -gt 4 ]]; then
  echo "Usage: $0 <intended-note> <target-note> [locked-seconds=30] [unlocked-seconds=20]" >&2
  exit 64
fi

SOURCE="$1"
TARGET="$2"
LOCKED_SECONDS="${3:-30}"
UNLOCKED_SECONDS="${4:-20}"
INTERVAL=5

[[ -f "$SOURCE" ]] || { echo "Intended note not found: $SOURCE" >&2; exit 66; }
[[ "$(uname -s)" == "Darwin" ]] || { echo "This recovery script requires macOS chflags." >&2; exit 69; }
[[ "$LOCKED_SECONDS" =~ ^[0-9]+$ && "$UNLOCKED_SECONDS" =~ ^[0-9]+$ ]] || {
  echo "Hold durations must be non-negative whole seconds." >&2
  exit 64
}

TARGET_DIR="$(dirname "$TARGET")"
TARGET_BASE="$(basename "$TARGET")"
mkdir -p "$TARGET_DIR"
STAGED="$(mktemp "$TARGET_DIR/.${TARGET_BASE}.hermes-wrapup.XXXXXX")"
PROTECTED=0

cleanup() {
  if [[ "$PROTECTED" -eq 1 && -e "$TARGET" ]]; then
    chflags nouchg "$TARGET" 2>/dev/null || true
  fi
  rm -f "$STAGED"
}
trap cleanup EXIT INT TERM

cp "$SOURCE" "$STAGED"
EXPECTED="$(shasum -a 256 "$STAGED" | cut -d' ' -f1)"
mv -f "$STAGED" "$TARGET"
chflags uchg "$TARGET"
PROTECTED=1

verify_hash() {
  local phase="$1" elapsed="$2" actual
  actual="$(shasum -a 256 "$TARGET" | cut -d' ' -f1)"
  if [[ "$actual" != "$EXPECTED" ]]; then
    echo "$phase verification failed after ${elapsed}s: expected $EXPECTED, found $actual" >&2
    exit 1
  fi
  echo "$phase-check-${elapsed}s=ok"
}

elapsed=0
verify_hash locked "$elapsed"
while (( elapsed < LOCKED_SECONDS )); do
  step=$(( LOCKED_SECONDS - elapsed < INTERVAL ? LOCKED_SECONDS - elapsed : INTERVAL ))
  sleep "$step"
  elapsed=$(( elapsed + step ))
  verify_hash locked "$elapsed"
done

chflags nouchg "$TARGET"
PROTECTED=0
elapsed=0
verify_hash unlocked "$elapsed"
while (( elapsed < UNLOCKED_SECONDS )); do
  step=$(( UNLOCKED_SECONDS - elapsed < INTERVAL ? UNLOCKED_SECONDS - elapsed : INTERVAL ))
  sleep "$step"
  elapsed=$(( elapsed + step ))
  verify_hash unlocked "$elapsed"
done

FLAGS="$(stat -f '%Sf' "$TARGET")"
if [[ "$FLAGS" == *uchg* ]]; then
  echo "Immutable flag still set on target." >&2
  exit 1
fi

echo "atomic-note-replace=verified"
echo "sha256=$EXPECTED"
