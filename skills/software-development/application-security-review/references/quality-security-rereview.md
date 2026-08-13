# Quality/Security Rereview — Independent Verification of Prior Findings

## When to use

- The user asks you to independently rereview a commit or patch that remediates prior code-review or security-review findings.
- You receive a commit SHA and a prior review report containing specific findings (F-001, F-002, etc.) to be dispositioned.

## Workflow

### 0. Establish review lineage

Some rereviews are of a **second or later revision** of a fix — a commit that amends a previously-reviewed base commit to address deployment blockers or additional review feedback. Before assessing individual findings, determine the review lineage:

1. Is there a **prior rereview** that already approved an earlier commit in the same lineage?
2. Is there a **deployment HOLD report** that identifies blockers for the earlier commit?
3. What is the **delta** from the prior review target to the new commit? (`git diff <prior_sha>..<new_sha>`)
4. Did the prior review's scope change? (new files added? existing files unchanged?)
5. **Is the delta test-only?** If the delta is 100% test changes (confirm with `git diff <prior_sha>..<new_sha> --stat`, and verify production files are byte-identical with a hash check), treat it specially: the production code is pre-cleared at full depth, and the review focuses entirely on whether the test changes correctly cover the blockers/HOLD items without introducing new platform-specific issues.

Treat prior-reviewed code paths as **pre-cleared** — only assess the incremental change against the blockers/HOLD items. Explicitly list which files changed in the delta vs which are unchanged from the prior target.

### 0b. Delta-class signals for structural assessment

When assessing a delta (whether it amends a prior review target or not), classify it into one of these delta classes and adjust assessment depth accordingly:

| Delta class | Characteristics | Assessment focus |
|---|---|---|
| **Production-only** | Only production files change; test file hashes unchanged | Trace every changed path through tests for vacuous coverage |
| **Test-only** | Only test files change; all production file hashes identical between commits | Verify each test change correctly addresses the blocker/HOLD; no accidental platform assumptions (silent skips, POSIX-only constructions on Windows) |
| **Mixed** | Both production and test files change | Full-depth review of production changes; skim-mapped test changes for coverage |

**For production-file identity proof**, capture deterministic hashes (MD5 or SHA-256) of every production file at both the prior target and the new commit. Report unmodified files explicitly:

```
| File | MD5 @ prior_sha | MD5 @ new_sha | Change? |
|---|---|---|---|
| src/register.py | abc123... | abc123... | ❌ None |
| scripts/launcher.ps1 | def456... | def456... | ❌ None |
| tests/test_register.py | ghi789... | jkl012... | ✅ Changed |
```

This makes the "no production weakening" claim independently verifiable without re-running diffs.

### 0c. HOLD-to-fix mapping

When a **deployment HOLD report** identifies specific blockers (e.g. exact test failures on a target platform), build a mapping table that connects each HOLD item to the fix in the delta. This forces explicit, item-by-item verification rather than a gestalt "the delta fixes the HOLD" claim:

| # | HOLD item | Fix mechanism | Verification |
|---|---|---|---|
| 1 | `stat.S_IMODE` on Windows returned 0o666, not 0o600 | Branched assertion: `assert_private_file_contract` calls `verify_secret_acl` on Windows | Code and test assertion confirmed branch is `os.name != "nt"` |
| 2 | Injected `_PosixObjectSeam` on Windows | Replaced with `_IdentitySwapObjectSeam` that delegates to active seam via `__getattr__` | Code confirmed seam works with both POSIX and Windows |
| ... | | | |

Each HOLD item must be either **RESOLVED** (fix verified in code/tests), **PERSISTED** (not addressed), or **DEFERRED** (acknowledged as out of scope).

### 1. Gather sources

Read in parallel:

- Repository guidance (`AGENTS.md`, README, project notes)
- The **original quality/security review** report containing the findings to be verified
- Any **prior rereview** report (if the commit is a second revision)
- Any **deployment HOLD report** that identifies blockers for the earlier commit
- The **implementation summary** (if one exists) — including RED/GREEN evidence and any **native closeout logs**
- The **exact commit diff** (`git diff <parent>..<commit>`) across all changed files
- The **delta from prior review target** (`git diff <prior_sha>..<new_sha>`) to scope the incremental change
- The affected files in full context where needed
- The implementation brief/plan that drove the work

### 2. Establish the baseline

Record in the report:

- Repository path
- Exact commit SHA and parent SHA
- Commit subject
- Review mode (read-only? diagnostic commands permitted? tests executable?)
- Sources read

### 3. Decompose each finding

For every finding in the original report:

| Field | What to record |
|---|---|
| Finding ID | e.g. F-001 |
| Original severity | HIGH / MEDIUM / LOW |
| Original complaint | Summarize the defect as described in the original report |
| Remediation in commit | What changed in the code — cite exact functions, classes, lines |
| Evidence | What the diff, tests, and native logs show about the fix |
| Target state | Is the fix complete, partial, or absent? |

### 4. Assess remediation depth

For each finding, verify all of:

**TOCTOU and object identity (F-001 class):**
- Are pathname checks bound to the opened object? (lstat → open + fstat → compare identity → read → re-lstat)
- Is O_NOFOLLOW or equivalent required (not optional)?
- On Windows: is `CreateFileW` with `FILE_FLAG_OPEN_REPARSE_POINT` used instead of Python path operations?
- Are directory identities retained in guards and rechecked at each critical operation?
- Are ancestor directories validated, not only the final leaf?
- Does the consumer (launcher, service startup) still re-read by naked pathname after verification?

**Platform-neutral identity-swap seam pattern (TOCTOU test infrastructure):**
When TOCTOU tests use a seam to inject identity mismatches (simulating a race where a file is replaced between probe and open), verify the seam itself is platform-neutral — not hardcoded to a POSIX-only class:

| Anti-pattern (POSIX-only) | Platform-neutral (preferred) |
|---|---|
| `class IdentitySwapSeam(module._PosixObjectSeam)` | `_IdentitySwapObjectSeam(module, module._OBJECT_SEAM, target)` |
| Overrides `before_open` to swap the file | Injects identity mismatch through `read_regular_bytes` by temporarily patching `delegate.path_identity` |
| Only works on Linux/macOS | Delegates to whichever seam is active via `__getattr__` |
| Fails on Windows before reaching identity assertion | Works with both `_PosixObjectSeam` and `_WindowsNativeObjectSeam` |

The platform-neutral pattern:
1. Accepts the *active module seam* as a delegate (`_IdentitySwapObjectSeam(module, delegate, target)`)
2. Uses `__getattr__` to forward all methods not explicitly defined to the delegate
3. In `read_regular_bytes`, temporarily replaces `delegate.path_identity` with an injector version that increments the file index on the target path
4. Calls through to the delegate's own `read_regular_bytes`, which internally calls `self.path_identity(...)` — now hitting the injected version
5. Restores the original delegate method in `finally`

This proves the TOCTOU gate works on both POSIX and Windows, not just on the developer's platform.

**Key/canonical validation (F-002 class):**
- Is the key format exact: length, charset, trailing newline, no stripping?
- Is there a minimum entropy check to reject degenerate all-same-char keys?
- Are ACLs/permissions verified before content is read?
- Do error messages avoid printing the key?

**Active-plugin verification (F-003 class):**
- Does the verifier query the Hermes runtime (not just disk) for plugin enabled status?
- Does it check the toolset is active, not only the plugin ID?
- Is the query strictly read-only (no enable/sync/write_private/subprocess mutation)?
- Is `PYTHONDONTWRITEBYTECODE` set to prevent side-effect file creation?

**Test and regression coverage (F-004 class):**
- Are source-position ordering assertions present (not just substring presence)?
- Does the nonmutation test snapshot complete file trees (bytes, mode, identity, timestamps)?
- Are symlink/junction/reparse tests mandatory (fail on creation failure, not silently skip)?
- Are deterministic identity-swap tests present using a seam or monkeypatch?
- **Are identity-swap seams platform-neutral?** (see pattern above — a POSIX-only seam that fails on Windows is a regression-coverage gap, not regression coverage)
- Do tests cover at least: linked files, noncanonical keys (9+ variants), permissive ACLs, disabled plugin, content drift, malformed markers, non-loopback config, missing files, CRLF normalization?
- **For Windows permissive-ACL tests:** does the adversary use `icacls /grant *S-1-1-0:R` (Everyone Read) instead of POSIX-only `chmod(0o755)`? A `chmod` on Windows has no meaningful ACL effect — the test must create a genuine Windows adversary.
- **For POSIX mode assertions on Windows:** does the test branch on `os.name != "nt"`? On Windows, `stat.S_IMODE` always returns `0o666` for regular files — an unguarded `assert mode == 0o600` will fail. Use a helper that calls `verify_secret_acl` on Windows instead.

### 5. Broad assessment

Beyond the specific findings, assess:

- **Correctness:** Does the verifier accept what it should and reject everything else? Are edge cases handled (empty dirs, oversized files, unicode, concurrent writers)?
- **Security (TOCTOU):** Are there any pathname-based gaps between verification and use?
- **Subprocess behavior:** Are subprocess calls read-only? Are timeouts set? Is output captured as bytes (not text-mode)?
- **Maintainability:** Are the helper functions small and single-responsibility? Is the seam pattern clear for platform divergence?
- **Evidence integrity:** Does the native evidence match the claimed behavior? Are RED-to-GREEN transitions documented?

### 6. Edge-case matrix

Build a compact table of edge cases and whether each is handled:

| Edge case | Handled? |
|---|---|
| Key with exactly N unique hex chars | Y/N |
| Config body > 64 KiB | Y/N |
| Ancestor directory replaced mid-verify | Y/N |
| Plugin enabled then disabled before verify | Y/N |
| launcher path with spaces | Y/N |
| CLI not installed | Y/N |
| `tools list` in unexpected format | Y/N |

### 6b. Assessment dimensions for transactional state migration

When the delta adds a **supported migration path** for existing state (e.g. legacy CRLF→LF key canonicalization, configuration file upgrade, credential format migration), assess every dimension of the migration independently:

**Credential semantics:**
- Is the semantic value preserved unchanged? Only the representation (line ending, encoding) should change.
- Are error messages content-free? The credential value must never appear in stdout, stderr, or log output.
- Is the generation path itself canonical? (binary write to prevent translation, fsync, atomic replace)

**Exact legacy-shape gate:**
- What legacy formats are accepted for migration? List each explicitly (e.g. "64 hex + CRLF = 66 bytes").
- Are all other variants rejected? Test uppercase, weak/repeated, short, long, trailing whitespace, wrong newline sequences, non-UTF-8 byte values.
- Is the gate fail-closed: unrecognized shape → raise RuntimeError, not silent skip?

**TOCTOU during migration:**
- Triple identity verification: pre-migration (lstat/path_identity), on opened handle (fstat/GetFileInformationByHandle), post-replacement (lstat).
- Does the migration check that the target identity matches the expected identity *before* replacement?
- Does replacement verify the replaced file identity matches the replacement identity?
- Are identity checks present at every critical read and write boundary, not only the initial probe?

**Link/reparse rejection:**
- Is every file touched by the migration checked for link/reparse status before reading, opening, and writing?
- On POSIX: O_NOFOLLOW required; on Windows: `FILE_FLAG_OPEN_REPARSE_POINT` prevents kernel-level following.
- Can a symlink placed on the target path between probe and replace bypass the gate?

**Backup confidentiality:**
- Is the backup written to a private, same-directory location (hidden name, random suffix)?
- Are the same byte-level permissions/ACLs applied to the backup as the original?
- Is the backup read back and verified byte-for-byte before the migration proceeds?
- Is the backup lifecycle managed: cleaned up on commit, consumed by rollback, or cleaned up on error?

**Atomic replacement:**
- Is `os.replace` (rename-based, atomic on same filesystem) used instead of write-in-place, truncate-and-write, or copy-then-delete?
- Is the temp file created in the same directory (same filesystem mount)?
- Is there an identity gap between verify and replace? (bounded but covered by post-replace identity check)

**Windows DACL preservation:**
- Are Windows security descriptors captured (via `GetFileSecurityW` / `ConvertSecurityDescriptorToStringSecurityDescriptorW`) before replacement?
- Is the DACL protection flag (PROTECTED vs UNPROTECTED/auto-inherited) preserved? The SDDL string `"D:P"` vs `"D:PAI"` must be parsed and the correct flag passed to `SetNamedSecurityInfoW`.
- Are identity checks performed before and after capture/restore to detect mid-operation ACL tampering?
- Is the `_metadata_equal` helper designed to skip raw descriptor bytes (which may differ due to internal representation) while still comparing the SDDL string?

**Rollback on every downstream failure:**
- Is the migration transaction held open across the full sync lifecycle (stage, replace, config write, enable)?
- Does every exception path trigger rollback? (outer try/except in the orchestrator, inner try/except in the migration preparer)
- Does rollback verify:
  - current identity matches the canonical identity (the one set after migration),
  - backup identity is unchanged,
  - restored bytes match the original raw bytes (with allowance for the original ±1 byte width),
  - restored ACL/metadata matches the original?
- Can a rollback failure be distinguished from the original failure? (chain exceptions: `raise RuntimeError("... failed") from original_exc`)

**Error non-disclosure:**
- Do no credential values appear in error messages, stdout, or log output?
- Are migration-specific error messages content-free (e.g. "Word bridge key file is not canonical", never the key value)?
- When errors chain (rollback fails on top of original failure), is the original error preserved without leaking additional state?

**Verify non-mutation:**
- Does the read-only verify path NOT invoke any migration helpers?
- Is the migration path strictly limited to the explicit install/sync path?
- Is there a test that monkeypatches migration helpers to raise AssertionError during verify?

### 7. Report structure

#### Standard: single-revision review

```
# HW-XXX Quality and Security Rereview — commit <SHA>

## Review identity

- Repository
- Exact commit
- Exact parent
- Commit subject
- Review mode

## Sources read

## Exact delta

| File | Description of changes |

## Original findings disposition

### F-001 (SEVERITY) — <title>
- Original finding: <quote>
- Remediation in commit: <what changed>
- Evidence: <diff citations, native output, test names>
- Assessment: REPAIRED / PARTIALLY REPAIRED / NOT REPAIRED

### F-002 ...

## Comprehensive assessment

- Correctness
- Security (TOCTOU, object identity, ACLs)
- Subprocess behavior
- Tests and coverage
- Maintainability

## Edge-case assessment

| Edge case | Handled |

## Positive review results

## Verdict

APPROVED / REQUEST_CHANGES

## Report metadata
```

#### Alternative: delta-rereview of an amended/second-revision commit

When the commit is a second revision that amends a previously-reviewed base, replace "Original findings disposition" with a **commit ancestry** section plus **assessment dimensions** organized by migration or delta category:

```
# HW-XXX Quality and Security Rereview — commit <SHA>

## Review identity

— standard fields —

## Commit ancestry

```
<sha> fix: ...                        ← HEAD (review target)
<sha> fix: ...                        ← prior review target (e.g. base-5f19ec4)
<sha> Bind office bridge browser...   ← common parent
```

## Prior findings disposition

All findings from the prior review were assessed as REPAIRED in the prior rereview.
See [prior rereview](<path>). Only the incremental change is assessed here.

## Migration delta (<prior_sha>..<new_sha>)

| File | Δ | Description |
|---|---|---|
| src/a.py | +N/−M | New migration helpers, modified sync path |
| src/test_a.py | +N | New tests for migration |
| src/unchanged.py | 0 | Preserved byte-for-byte from prior target |

## Detailed review dimensions

### 1. Credential semantics (dimension description)
...

### 2. Exact legacy-shape gate
...

### 3. TOCTOU during migration
...

... (one section per dimension) ...

## Remaining edge-case analysis

| Edge case | Handled | Notes |
|---|---|---|

## Verdict

APPROVED / REQUEST_CHANGES
```

### 8. Disposition language

| Status | When |
|---|---|
| **REPAIRED** | Every aspect of the original finding is demonstrably fixed in the commit, with evidence and tests. |
| **PARTIALLY REPAIRED** | Some aspects covered, some still open or unverified. List remaining gaps. |
| **NOT REPAIRED** | The finding was not addressed at all, or the claimed fix does not work. |

### 9b. Native platform evidence verification

When evidence from a **separate platform** (e.g. JARVIS/Windows remote verification, disposable fixture on a native machine) is presented, incorporate it as a distinct verification layer:

1. **Classify the evidence source:**
   - Disposable fixture (isolated temp directory, no production state touched)
   - Live state inspection (read-only probes against production installation)
   - Mutation test (write/readback/restore within a disposable fixture)

2. **Document fix cycles:** If the native evidence records an initial failure and a corrected re-run (e.g. Windows DACL auto-inheritance flag divergence), note the fix cycle explicitly. A fix cycle that required a code change and was re-verified is positive evidence of thoroughness, not a weakness.

3. **Evidence fields to capture:**
   - Did the migration preserve the original ACL/permissions? (`aclPreservedOnMigration: true`)
   - Was the backup exact and private? (`backupExactBytes: true`, `backupPrivate: true`)
   - Was a race/identity swap detected? (`identitySwapRejected: true`)
   - Were linked/malformed inputs rejected? (`linkedKeyRejected: true`, `malformedRejected: true`)
   - Was rollback exact and complete? (`rollbackExactOriginalBytes: true`, `rollbackAclPreserved: true`)

4. **Separate from unit tests:** Do not conflate "native fixture verified" with "unit tests pass." Report them as independent layers. Native evidence can cover Windows-specific behavior (DACL inheritance, reparse tags, effective access checks) that unit tests on a POSIX host cannot.

### 10. Verdict

- **APPROVED** — all findings repaired, no new issues of equal or greater severity.
- **REQUEST_CHANGES** — one or more high-severity findings not repaired, or new high-severity issues exist.

## Pitfalls

- Do not accept a green build as proof of finding remediation. Inspect the actual code path and test.
- Do not rely on the test name alone; inspect the test fixture, setup, assertions, and seam.
- Do not equate "verified on one platform" with "verified on all platforms" — Windows reparse/ACL behavior is distinct from POSIX.
- Do not silently accept a test that can skip on failure (`pytest.skip()`, `pytest.xfail()`, `os.symlink` fallback). Require mandatory tests for platform-specific behavior.
- Do not conflate "the right source order now" with "the regression test proves the ordering invariant." Source-level checks for `indexOf` + `.GreaterThan` are needed.
- Do not claim a finding is fixed based on a non-representative test fixture (e.g. a POSIX-only test for a Windows-specific reparse finding).
- **Delta-review drift:** When reviewing a second-revision commit, do not re-review the code paths already approved in the prior review unless the new delta touches them. Compute the delta from the prior review target, not just from the original parent, and explicitly list which files are unchanged.
- **Prior-review-as-shortcut:** An approved prior rereview does not automatically forgive the new commit's entire delta. Assess only the incremental change, but assess it at full depth — a HOLD report may identify blockers that the prior review did not consider.
- **Native evidence is not proof of absence:** A native fixture that passes all migration checks proves the migration works on that fixture. It does not prove the migration handles every adversarial input on every platform. Cross-reference native evidence with the unit-test matrix to find gaps.
- **Test-only delta platform assumptions:** A commit that only changes test files is still assessable. Verify every changed test assertion branches on `os.name != "nt"` where the behavior diverges (POSIX mode checks, symlink creation, chmod semantics). A test that silently relies on POSIX-only infrastructure (e.g. inheriting from `_PosixObjectSeam`, calling `chmod(0o755)` as an adversary, asserting `stat.S_IMODE == 0o600` on all platforms) is a deployment blocker in disguise — it passes on the developer's machine and fails on the target platform.
