# Amended-Commit Spec Rereview Pattern

## When to use

The candidate under review is an existing commit that was amended to repair findings from a prior specification review. You are performing a **rereview** — not a first review — and must:

1. Verify the incremental diff from the previously reviewed commit to the amended target.
2. Confirm each prior finding's disposition.
3. Verify all original requirements remain satisfied despite any new changes.
4. Check for new findings introduced by the amendment delta.
5. Incorporate any findings from native/separate execution gates.

## Establishing the delta

Before judging the amended candidate, establish **three** baselines:

| Baseline | What to verify |
|----------|----------------|
| Parent → target (full) | `git diff <parent>..<target>` — the build-from-scratch delta. Confirm it changes only the permitted bounded files. |
| Prior review → target (incremental) | `git diff <prior-reviewed-sha>..<target>` — the amendment delta. This should be smaller than the full diff. |
| Worktree cleanliness | `git status --short` — must be empty for the candidate to be final. |

When the prior review found a defect in a specific test file (e.g., F-001 in CRLF test), verify the incremental diff changes **only that test file** — or carries production changes that are strictly additive (hardening, bugfix) and not scope-creep.

## Prior finding disposition table

For every F-`N` finding from the prior review, produce:

| Field | Content |
|-------|---------|
| **F-`N`** | Short title |
| Source | Prior review commit SHA |
| Severity | CRITICAL / HIGH / IMPORTANT |
| Location | Exact file:lines from prior review |
| Issue | One-paragraph summary of what was wrong |
| Repair | What the amended target changed to fix it |
| Verification | How the amendment's fix is confirmed in the diff |
| Status | CLOSED / RESOLVED / CARRIED FORWARD |

If a prior finding was marked `RESOLVED` in an intermediate rereview but the target adds new production code, re-verify the fix is still present and not regressed.

## New findings from the amendment delta

When the incremental diff from the prior reviewed commit to the target adds production code (bugfixes, hardening) beyond the test-only repair, inspect each change as a potential new finding:

- **Binary mode fix:** A text-mode `fdopen("w")` changed to `fdopen("wb")` is a Windows CRLF correctness fix. Verify it has a regression test, a known pre-fix native failure log entry, and that the fix doesn't break POSIX paths.
- **UTF-8 decode fix:** Removing `text=True` from `subprocess.run` to capture bytes and calling `.decode("utf-8")` explicitly is cross-platform safe. Verify the regression test covers the non-ASCII glyph that triggered the bug.
- **Environment isolation fix:** Adding `PYTHONDONTWRITEBYTECODE=1` to the subprocess env prevents self-defeating mutations. Verify the regression captures `env` kwargs and asserts the variable.
- **ACL hardening:** Adding `harden_secret_acl()` calls in an existing `install_or_sync` path is additive. Verify the regression tests confirm ACL stability after repeat verification.

## Requirement re-verification

After the prior findings are disposed, re-verify every original requirement from the first review. The amendment delta may not change production behavior for a given requirement, in which case the prior conclusion carries forward. Document this explicitly:

> *Unchanged production evidence from `<prior-sha>`, carried forward:*

Include the specific evidence (path:lines) as a reading trace so a future reviewer does not need to re-derive it.

## Native closeout gate as separate verification layer

When the amended commit was verified against a disposable native (Windows, macOS, etc.) environment, record the gate results as a separate row in the requirement matrix. This is stronger than unit test evidence:

| Gate | Result |
|------|--------|
| Key file byte invariant | 64 hex chars + LF = 65 bytes |
| Canonical verify | return code 0 |
| Repeat verify (no mutation) | return code 0 |
| ACL stability after verify | unchanged |
| Untrusted ACL rejection | return code 2 |
| File reparse rejection | return code 2 |
| Directory junction rejection | return code 2 |
| Parent junction rejection | return code 2 |

Each gate should cite the native evidence log file and line numbers.

## Deployment HOLD-blocker resolution verification

When the deployment phase itself (not the spec review) produced a HOLD report with specific blockers, the amendment may need to fix those blockers rather than (or in addition to) fixing spec-review findings. This changes the review baseline:

1. **The effective baseline is the HOLD report's pinned state**, not just the prior spec review's parent SHA. The HOLD report records what is already live (e.g., installed version `0.2.4` with specific file hashes). The amendment must prove the new candidate can be deployed alongside that live state, not just that it builds from a clean checkout.

2. **Produce a blocker-closure matrix**, one row per HOLD blocker, with the same Severity → Location → Issue → Repair → Verification → Status layout as the prior-finding disposition table. A blocker that is fully addressed by the amendment should show `CLOSED`; a blocker outside the commit's scope should show `NOT_IN_SCOPE` with the reason.

3. **For side-by-side versioning additions**, verify:
   - The version contract (`bridge-version.json` or equivalent) declares a distinct candidate version different from the live retained version.
   - The installer reads the contract before destination construction and freezes the candidate version dynamically (no hardcoded version).
   - The switch/validator checks every retained bundle by marker, manifest hash, and per-file SHA-256 — not only by version string.
   - The retained version directory is never overwritten (no `-Force` copy, no same-version directory collision).
   - Any legacy extra-file allowance (e.g., `__pycache__/*.pyc`) is version-scoped (`$ExpectedVersion -ceq '0.2.4'`) and path-bounded (`^runtime\\__pycache__\\[^\\]+\\.pyc$`), with no allowance for the candidate version.

4. **Atomic pointer switching**: the switch script must use `[IO.File]::Replace` for atomic NTFS replacement with a pre-existing backup, roll back on failure, and have no lifecycle side effects (no `Start-Process`, no port claims, no gateway interaction). Temporary and backup files must be cleaned up in a `finally` clause bounded by `Assert-ContainedPath`.

5. **Live immutability proof**: the native cycle must prove the live production root and pointer were never modified — file count, byte/hash snapshot, and gateway PID/creation/health must be captured before, during, and after the disposable cycle.

## Commit-amendment delta verification

When the approved commit (`1e9a810`) was amended in place to produce the final commit (`f7d8dee`), there is no direct `git diff <approved>..<final>` because the approved SHA no longer exists in the DAG. Verify preservation structurally instead:

1. **Produce the parent-to-approved diff** (from the prior review record) and the **parent-to-final diff** side by side.
2. Confirm the production change lines (the bounded diff from the parent) are byte-for-byte identical between the two diffs. The amendment should only add packaging/additional files — the production change that was reviewed and approved must not be altered.
3. For the new files, verify they are bounded to the described scope (version contract, switch script, installer modifications, status script modifications, contract tests, documentation). No unrelated source, gateway, or publication path should be included.
4. Confirm the parent SHA is identical between the approved and final commits (the amendment did not rebase onto a different parent).

If structural comparison is impractical, verify that the parent-to-final diff shows the exact same production lines as the prior review record, plus only the permitted bounded additions.

## HOLD-blocker specific verdict structure

- **PASS** — all HOLD blockers within scope are CLOSED, the original approved production change is preserved, all requirements satisfied, native gate passed.
- **PASS WITH GAPS** — all HOLD blockers within scope are CLOSED, the original change is preserved, all requirements satisfied, but native gate was not run or had environmental limitations that prevented executing the full deploy cycle.
- **REQUEST_CHANGES** — one or more in-scope HOLD blockers remain unresolved, the original production change was altered, or a new finding exists in the packaging additions.

Always note which HOLD blockers are `NOT_IN_SCOPE` of the current commit so the next phase can be directed accurately.

## Verdict structure

- **PASS** — all prior findings resolved, no new findings, all requirements satisfied, native gate passed.
- **PASS WITH GAPS** — all prior findings resolved, no new findings, all requirements satisfied, but native gate was not run or had environmental limitations.
- **REQUEST_CHANGES** — one or more prior findings remain unresolved, or a new finding exists in the amendment delta.
