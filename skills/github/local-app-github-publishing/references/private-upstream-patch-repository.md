# Private upstream patch repositories

Use this pattern when a local repair to a fast-moving upstream project must be applied now, survive updates, and be preserved privately without copying the whole upstream repository.

## Deliverable shape

Create a small private repository containing:

- `README.md` — behavior, scope, upstream links, and apply instructions
- `BASELINE` — upstream repository and exact reviewed commit
- `patches/<repair>.patch` — source and regression-test diff only
- `apply.sh` — idempotent, fail-closed patch installer
- `VERIFY.md` — exact checks run and honest limits of live validation
- optional `UPSTREAM-REVIEW.md` — why competing PRs were accepted, rejected, or adapted

Do not include dependency folders, packaged apps, credentials, local configuration, or the full upstream checkout.

## Choose the repair before packaging it

1. Define the invariant at the consequential boundary. For UI state bugs, trace state through the actual API/RPC request rather than stopping at the displayed label.
2. Fetch competing PR heads into namespaced remote refs and compare each against current main.
3. Apply candidates in detached temporary worktrees. A clean cherry-pick is not proof of correctness; a candidate can pass its own tests while leaving an immediate-action race.
4. Prefer a small current-main adaptation when old PRs have useful semantics but stale architecture.
5. Add a regression test for the outgoing request or persisted write. Preserve explicit user intent, and consume one-shot state only after the side effect succeeds.
6. Run focused tests, typecheck/lint/format, the relevant full suite, and a build or live smoke when packaging is affected.

## Generate and validate the patch

Generate the diff from an explicit file list so unrelated dirty recovery patches cannot enter the artifact:

```bash
git diff -- path/one path/two path/to/tests > repair.patch
```

When a tool captures `git diff` output and another tool writes it, explicitly ensure the file ends with `\n`. Missing the final newline can produce `git apply: corrupt patch at line N` even though the visible hunk looks complete.

Validate the artifact in a clean detached worktree:

```bash
git worktree add --detach /tmp/repair-check HEAD
./apply.sh /tmp/repair-check
git -C /tmp/repair-check diff --check
git -C /tmp/repair-check diff --stat
./apply.sh /tmp/repair-check   # must report already applied
git worktree remove --force /tmp/repair-check
```

Unified diffs contain blank context lines represented as a single leading space. A patch repository's own `git diff --cached --check` can therefore flag valid patch context as trailing whitespace. Do not strip those context markers. Add:

```gitattributes
*.patch -whitespace
*.diff -whitespace
```

Source-tree `git diff --check` remains mandatory.

## Worktree-safe idempotent installer

Do not test `[[ -d "$TARGET/.git" ]]`; linked worktrees store `.git` as a file. Use Git itself:

```bash
if ! git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1; then
  echo "ERROR: not a Git checkout: $TARGET" >&2
  exit 2
fi
```

The installer should:

1. Locate its patch relative to `BASH_SOURCE[0]`.
2. Detect an exact source sentinel and exit successfully if already applied.
3. Run `git apply --check` before writing.
4. Run `git apply` only after the check passes.
5. Run `git diff --check` on the affected source area.
6. Fail with a rebase/manual-merge message when upstream drift prevents a clean apply.

Keep the one-shot state consumption after the successful side effect. Clearing it while merely constructing request parameters loses the user's explicit choice when creation fails.

## Recovery-harness integration

A cumulative `apply-patches.sh` may contain several independent repairs. Inspect every block before running it on the live checkout: validating one new block can legitimately reapply older pending patches and broaden the dirty tree. Prefer testing the new patch directly in a clean worktree first. If the real cumulative harness is executed, inspect and report every resulting file, not just the new repair.

Store the patch at a stable path, add an idempotent sentinel block to the recovery harness, run `bash -n`, and verify a second execution reports every repair as already applied.

## Verify update automation from live state

Do not infer automatic recovery from an update guide alone. Inspect the live invocation chain:

- active Git hooks such as `.git/hooks/post-checkout` and `.git/hooks/post-merge` (a similarly named `.disabled-*` file is not active)
- the updater implementation or wrapper
- LaunchAgents/systemd/Task Scheduler entries
- user crontab or scheduled jobs

State the trigger precisely. For example, a `post-checkout` hook may reapply patches only when a fast-forward update changes the checked-out revision and only while the hook and patch script remain executable. Require visible `Applied` or `already applied` output after an update and retain a documented manual fallback.

Source recovery and binary deployment are separate. Reapplying TypeScript/Python source does not rebuild or reinstall a packaged Electron, macOS, Windows, or mobile app. Verify whether the update path rebuilds the artifact; if it does not, document or automate that second stage independently.

## Local Electron packaging on macOS

Source verification and local packaging are separate gates. For a local-only build when normal certificate signing is unavailable or not intended:

```bash
CSC_IDENTITY_AUTO_DISCOVERY=false npm run builder -- --dir --mac
codesign --deep --force --sign - \
  --entitlements electron/entitlements.mac.plist \
  release/mac-arm64/App.app
codesign --verify --deep --strict --verbose=2 release/mac-arm64/App.app
```

Label the result accurately: ad-hoc signing is suitable for local validation, not distribution. Hash the packaged and installed payload (for Electron, commonly `Contents/Resources/app.asar`) and require exact equality. Launch with isolated user data for a smoke test; if isolation omits auth, report expected authorization failures as a smoke-test limitation rather than claiming authenticated end-to-end behavior.

## Private first-push gate

Before the initial commit:

- run a source-only credential and personal-path scan
- verify the patch applies in a clean worktree
- set the established repository-local noreply identity
- stage and run `git diff --cached --check` with the patch attributes above
- create with explicit `--private`
- verify local HEAD equals `git ls-remote origin refs/heads/main`
- verify GitHub reports `isPrivate: true`, `visibility: PRIVATE`, and the expected default branch
- read back at least one remote file through the GitHub API

Private visibility reduces exposure; it does not replace secret scanning or commit-metadata review.
