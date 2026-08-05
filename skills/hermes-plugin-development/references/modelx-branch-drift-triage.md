# `/modelx` command drift triage

Use this when a slash command appears in docs/feature notes but is not available in active runtime.

## 1) Verify command surfaces in the active checkout

Run in-process checks from the active Hermes `hermes-agent` environment:

- `resolve_command("modelx")` should return a `CommandDef` if available.
- `is_gateway_known_command("modelx")` should usually be `False` for CLI-only commands.
- `resolve_command("switch")` should be `None` when `/modelx` is the active scoped model-switch command.
- `resolve_command("model")` should still be present.

## 2) Verify front-end/TUI route binding

If scoped switching is expected in terminal UI (or user workflow touches TUI), confirm:

- `ui-tui/src/app/slash/commands/session.ts` includes `aliases: ['modelx']` in the model picker command path.

## 3) Verify branch provenance before declaring a regression

Many regressions are feature-branch drift, not runtime breakage.

- Compare with known-feature branch: `fix/modelx-command`.
- Confirm expected commit(s) are in your active branch:
 - `git log --oneline --all --grep='modelx'`
 - `git branch --contains <modelx_feature_commit>`
- Inspect cross-branch diffs for expected files:
 - `hermes_cli/commands.py`
 - `cli.py`
 - `ui-tui/src/app/slash/commands/session.ts`
 - `tests/cli/test_modelx_picker.py`

Only after this parity check should you treat the outcome as a runtime regression.

## 4) Use existing script smoke checks as an assert matrix

`~/.hermes/scripts/post-update-autoresearch-check.sh` (user-local — verify it exists) already has model command assertions; if these fail, the expected files are usually missing or mismatched in the active tree.

- `/modelx` command assertion in the script checks `cli_only` registration + expected gateway state.
- If that assertion fails, do not loop-fix blindly; reconcile the branch first.
