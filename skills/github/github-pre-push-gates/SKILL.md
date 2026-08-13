---
name: github-pre-push-gates
description: 'github-pre-push-gates — Pre-push quality gates: immutable verification, privacy scanning, independent closeout review, and clean publication from divergent local history.'
version: 1.1.1
metadata:
 hermes:
 tags:
 - GitHub
 - Publication
 - Security
 - Privacy
 - Git
 related_skills:
 - github-pr-workflow
 - github-auth
 - github-code-review
---
# Pre-Push Quality Gates

Before pushing a branch to a shared remote, run through these gates. They prevent pushing credentials, PII, private history, or a broken tree. The skill covers the pre-PR quality phase — use `github-pr-workflow` for the PR lifecycle itself.

## Dependency audit interpretation

- The standard production gate is `npm audit --omit=dev --audit-level=high`, but a zero result there does not clear a vulnerable developer toolchain. Run the full audit too when the repository ships or executes from source.
- Separate lockfile evidence from installed-tree evidence. `npm audit --package-lock-only` can pass while stale `node_modules` still reports old versions; use a clean `npm ci` in CI and then run ordinary `npm audit` before declaring the dependency fix verified.
- If a patched transitive version requires an override, verify every resolved package path and exercise tests/build/validation. Do not use `npm audit fix --force` without reviewing proposed major downgrades and behavior changes.

## Workflow overview

```text
[code complete] → [immutable verification] → [privacy scan] → [reviewer] → [push + SHA verify] → [PR]
```

Each gate is optional by severity — skip when the scope doesn't warrant it, but never skip the privacy scan when pushing to a shared/public remote.

### Multi-agent candidate freeze

Before any final gate or read-only review, verify that no write-capable agent still owns the checkout **or can advance the branch from an orchestrator/sibling worktree**. A clean status alone is insufficient: interrupted parent agents can leave delegated workers alive, continuation controllers can auto-start the next task, and `command | tee log` can mask an agent failure unless the shell uses `set -o pipefail`. Freeze the exact SHA across gates and recheck HEAD/status/writers after every long command. For process checks, shared-ref/worktree freezes, dirty-tree fingerprints, safe interrupted-writer recovery, and synthetic secret-fixture classification,

If later work keeps advancing the live development branch, publish the approved ancestor from a detached non-cloud worktree instead of resetting or force-pushing the moving checkout. Re-run immutable gates, privacy scanning, and exact-SHA review there, then push the immutable SHA with an explicit refspec (see §4 for the full frozen-worktree procedure).

If the checkout is under iCloud Drive, OneDrive, Dropbox, or another placeholder-backed sync root, move recovery to a non-cloud development directory before resuming. `Resource deadlock avoided`, unreadable Git refs/objects, zero-block placeholders, and conflict copies such as `file 2.ts` invalidate normal Git evidence. Hydrate placeholders before reading, preserve dirty-tree state, and verify the destination before resuming.

---

## 1. Immutable Verification Gate

Run the full test suite, then **verify the working tree and commit SHA did not change**. This catches regenerated lockfiles, build artifacts, or side-effect file writes that could invalidate your pass:

```bash
set -e
sha=$(git rev-parse HEAD)
test -z "$(git status --porcelain)"
npm test
npx tsc --noEmit
npm run build
npm run validate
git diff --check
# ... any other project-specific gates ...
npm audit --audit-level=high --omit=dev
test -z "$(git status --porcelain)"
test "$sha" = "$(git rev-parse HEAD)"
printf 'IMMUTABLE_GATE=PASS sha=%s\n' "$sha"
```

**Pitfalls:**
- Run this AFTER you've finalized what you want to push, not before.
- If `git status` shows a change after the test suite, investigate — the tree is not reproducible.
- A SHA mismatch means something (npm regenerate, schema generation, etc.) wrote to the tree during testing. Fix the root cause: either commit the generated file, or add it to `.gitignore`.
- Treat command transport and command output as two independent signals. If a wrapper reports a nonzero exit while stdout contains a final `PASS` marker—or reports zero while an inner gate failed—do not choose the convenient result. Run a minimal standalone reconciliation that verifies the exact SHA, empty porcelain, committed-range `diff --check`, and lock/writer state, with an explicit final exit code. Record the first run as contradictory transport evidence, not a pass or product failure.

### Static-site theme and contrast gate

When a release changes a website's palette, theme, gradients, or component backgrounds, responsive geometry is not sufficient accessibility evidence.

1. Probe **focus-only UI** explicitly—especially skip links, menus, dialogs, and controls hidden until keyboard focus. A palette token that passes against white may fail when used as the focused element's background.
2. Calculate contrast from the **actual computed foreground/background pair in the rendered state**, not from variable names or the page background. Tab to the element in a browser and read `getComputedStyle()` after focus.
3. Check gradient controls at their weakest endpoint. For normal-size text require at least 4.5:1; for qualifying large text require at least 3:1.
4. Re-run the exact-candidate independent review after any contrast repair because amending the commit invalidates the previous verdict.
5. Keep a deterministic browser assertion in the immutable gate when practical; report the measured ratio and colors so a future palette change cannot silently regress it.

A useful Playwright pattern is: load the page, press `Tab`, assert the active element is the expected skip link, parse its computed `color` and `backgroundColor`, calculate WCAG relative luminance, and require `ratio >= 4.5`.

For `background-clip: text` / `-webkit-background-clip: text` headings, add a visual glyph-paint gate: DOM containment and `scrollWidth` can pass while the bottom of a gradient line is visibly shaved off. Prefer a small bottom paint allowance on the gradient span (for example `padding-bottom: 0.08em`) over globally loosening every heading’s line-height. Verify computed padding, `overflow: visible`, and screenshot appearance at the exact reported width plus mobile/desktop Chromium and WebKit widths; confirm the allowance does not introduce an uneven gap below the headline.

### Agent-produced commit acceptance

A background process exit code is not an engineering verdict. An agent can exit `0` after returning `HOLD`, exhausting turns, leaving a dirty candidate, or failing to commit. Before accepting an agent-produced commit:

1. Read the complete final report and distinguish `PASS`, `HOLD`, and native/runtime gaps.
2. Inspect live Git state independently: `HEAD`, porcelain status, staged/unstaged/untracked paths, locks, and every worktree.
3. Verify the raw commit object with `git cat-file commit <sha>` plus explicit `%H/%P/%T/%an/%ae/%cn/%ce` formatting. Do not rely only on a wrapper-rendered identity line.
4. Compare the exact changed-path set against the authorized scope and confirm the parent is the frozen baseline.
5. Run committed-range whitespace with two separate revision arguments, for example `git diff --check "$parent" "$sha"`. Do not build a revision expression with control characters or a visually ambiguous separator.
6. Re-run meaningful focused/full tests and the build from the committed tree, then assert the SHA and porcelain are unchanged.
7. Check remote containment separately; a local commit can be accepted without being pushed, but never imply publication from local evidence.
8. If a report says a writer is still active, inspect current process command lines/CWDs and Git locks. A stale summary is not proof of a live writer; conversely, a clean tree is not proof that an orchestrator cannot advance the branch.

For producer/consumer changes across repositories, acceptance also requires field-by-field reconciliation using the producer's minimal exact payload. See `specification-compliance-review` and ; green convenience fixtures do not prove interoperability.

---

## 2. Pre-Push Privacy and Secrets Scan

Scan the committed tree for credentials, local paths, private artifacts, and whitespace issues. Run **after** the immutable gate so the tree is final.

### 2a. Committed credential scan

Check for API keys, tokens, private keys in the tracked tree:

```bash
PAT='AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|xox[baprs]-[A-Za-z0-9-]{20,}'
test -z "$(git grep -IlE "$PAT" HEAD -- . || true)"
```

### 2b. Local and internal identifier scan

Check for machine-specific paths, private IP addresses, employer email addresses, and internal assistant/agent/profile persona names:

```bash
test -z "$(git grep -IlE '<user-home>/[^/]|10\.0\.0\.[0-9]|@[a-zA-Z]+\.com' HEAD -- . || true)"
test -z "$(git grep -IlEi '<profile-name-1>|<profile-name-2>|<internal-worker-name>' HEAD -- . || true)"
```

Build the profile/persona inventory from the user's actual private environment; generic terms such as `router-test`, `test-profile`, `alpha`, and `beta` are safe fixture names. Scan the **whole candidate tree**, current public default branch, every active PR head, and PR metadata—not only added lines. Profile names can be inherited from `main` or remain exposed on sibling draft branches even when the current diff is clean.

Keep legitimate public author attribution separate from profile-name privacy. A copyright holder or package author is not automatically an internal profile identifier. Also distinguish current-tree cleanup from history purge: removing a name in a new commit does not erase it from reachable Git history, and history rewriting requires separate explicit authorization.

Adjust patterns for the user's environment.

### 2c. Artifact directory scan

Check for tracked internal artifact directories:

```bash
test -z "$(git ls-tree -r --name-only HEAD .hermes .vscode __pycache__ .DS_Store 2>/dev/null || true)"
```

### 2d. Commit-range diff scan

Only lines **added** by this branch (not inherited from main). This avoids false positives from pre-existing public values:

```bash
git diff --check origin/main..HEAD

python3 -c '
import subprocess, re, sys
raw = subprocess.check_output(["git","diff","--unified=0","origin/main..HEAD"])
patterns = {
 "credential": re.compile(rb"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN.*PRIVATE KEY-----"),
 "local_path": re.compile(rb"<user-home>/[^/]|10\.0\.0\.[0-9]"),
}
hits = []
for line in raw.splitlines():
 if line.startswith(b"+") and not line.startswith(b"+++"):
 for kind, pat in patterns.items():
 if pat.search(line):
 hits.append((kind, line[:120].decode(errors="replace")))
if hits:
 for kind, text in hits:
 print(kind, text)
 sys.exit(9)
'
```

### 2e. Reachable-history and metadata scan

For a new public repository or a branch whose existing history will become reachable, scanning `HEAD` is insufficient. Inspect every reachable commit and ref—not only the current tree:

- enumerate `git rev-list --all` and scan the blobs reachable from each revision;
- inspect author/committer names and emails with `git log --all --format=...`;
- inspect branch/tag refs and run `git fsck --full`;
- flag unexpected binary blobs, logs, databases, screenshots, exports, or deleted secrets still present in history;
- verify the intended public/noreply commit identity.

A clean current tree does not erase private data from prior commits. If reachable history is unsafe, publish from a new clean history rather than merely deleting the file in a later commit.

---

## 3. Independent Closeout Review

For significant branches (new feature, cross-repo work, security hardening), run a separate read-only agent as a second opinion:

```bash
hermes --profile <name> --yolo chat --provider <provider> --model <model> --max-turns <N> \
 -q 'READ-ONLY final binary check of exact clean commit <SHA> in <path>. ...'
```

**Rules:**
- The reviewer must inspect without editing, staging, committing, or pushing anything.
- A dispatched or still-running background review is not a PASS. Do not push until the reviewer returns a verdict on the final candidate diff; if the diff changes after review, review the replacement diff again.
- Supply the exact SHA and verify both tree cleanliness and commit identity.
- When the reviewer runs under another Hermes profile, remember that configs, plugins, memory providers, skills, and credentials are profile-isolated. The reviewer's local status is not evidence about the target profile. Either run the live check with `hermes --profile <target> ...` or provide verified target-profile output as authoritative context.
- If the target is a staging directory rather than a Git repository, say so explicitly and do not let the reviewer turn expected missing Git metadata into a product defect.
- Require a full sentence and `file:line` for every **HOLD**. A bare line number or unexplained verdict is not actionable; retrieve the review transcript or rerun with a tighter prompt.
- A **HOLD** return means either concrete defects or procedural issues (tool budget exhaustion is not a hold — re-run with more turns).
- Write the verdict report to a timestamped file on the user's Desktop when a durable external review artifact is required.
- For large cross-boundary branches, use specification, security/privacy, and code-quality reviewers as distinct axes. Let all finish before one consolidated repair pass; any evidence-backed BLOCKER/HIGH is HOLD even if another reviewer says PASS. Re-review the replacement SHA on each axis that previously held.

### Electron and large-diff closeout

For Electron/filesystem features, a passing bridge test does not prove product completeness: trace the production UI route through preload, privileged IPC, and the service, and treat an unreachable user-facing feature as blocking. Review canonical-path, symlink, and TOCTOU behavior across write, rollback, extraction, reveal, and deletion—not only the nominal import call.

For packaged Electron release manifests and scanners, follow the release checklist. It covers built-vs-packaged proof, macOS framework symlinks without dereferencing, regular-entry type checks before hashing, canonical manifest paths, global caps, binary allowlists, literal-backslash spoofing, and idempotent manifest regeneration.

For large branches, partition evidence by risk surface rather than asking one bounded reviewer to ingest the entire diff. Context exhaustion is an incomplete review, never approval. An evidence-backed BLOCKER/HIGH from specification or security review overrides a generic quality PASS until repaired, and every replacement SHA must be re-reviewed.

For multi-skill/tool collection repositories, see for layout, raw-install URL, companion-asset, CI-path, and first-release checks.

---

## 4. Publishing from Divergent Local History

When local history diverged significantly from `origin/main` (dozens of commits of internal/campaign/prototype work), **do not push the raw history**. Expose a clean single commit.

### 4a. Preserve private history

```bash
git branch local/archive/<topic>-$(date +%Y%m%d)
```

### 4b. Create a clean squash commit

```bash
git reset --hard origin/main
git merge --squash local/archive/<topic>-$(date +%Y%m%d)
```

### 4c. Clean up artifacts from the staged squash

Remove private artifacts, campaign docs, and generated files from staging:

```bash
git rm --cached -r .hermes docs/autoresearch-*.md .vscode 2>/dev/null || true
rm -f docs/autoresearch-*.md
```

### 4d. Resolve conflicts properly

Real three-way conflicts mean remote `main` accumulated changes during your local work. Resolve with care:
- For code files (agent.ts, tools.ts): prefer the archive's proven implementation when it is the superset
- For configuration files (plugin schemas, YAML): prefer the archive's companion-aware version
- For lockfiles (`package-lock.json`): regenerate via `npm install` and stage the result
- For test files testing a superseded implementation: `git rm --cached` them rather than forcing incompatible tests into the publication commit

### 4e. Run verification on the squash

```bash
npm test
npx tsc --noEmit
npm run build
npm run validate
git diff --check origin/main..HEAD
test "$(git rev-list --count origin/main..HEAD)" = 1
test -z "$(git status --porcelain)"
```

**This reset-and-squash pattern is for publication only — it rewrites commit metadata.**
**Do not use it on a branch others are collaborating on.**

### 4f. Publishing a shallow clone to an empty remote

An ordinary shallow clone cannot always be pushed to a brand-new empty repository. Its boundary commit still names a parent object that the clone does not have, so GitHub may reject both normal and `--no-thin` pushes with `remote unpack failed` / `did not receive expected object <sha>`.

Do not unshallow a multi-gigabyte upstream repository merely to publish one private feature branch. Build a complete, self-contained two-commit graph instead:

1. Create a new root commit with `git commit-tree` using the shallow boundary commit's tree but no parent.
2. Create the feature commit with the verified feature tree and the new root as its parent.
3. Preserve the intended noreply author/committer identity explicitly.
4. Reset only the disposable publication checkout to the replacement feature commit.
5. Verify `git rev-list --count HEAD` is `2`, `git fsck --full` is clean, the feature's stable patch ID matches the reviewed commit, and the tree is clean.
6. Re-run the affected immutable tests, privacy scan, and exact-SHA independent review because the publication commit SHA changed.
7. Push with `git push --no-thin`, then compare local, `git ls-remote`, and GitHub API SHAs.

Keep the original development checkout untouched. Use this only for a new empty publication repository where preserving all upstream ancestry is unnecessary; do not rewrite a shared branch or conceal contributor history.

---

## 5. Push, Public Verification, and CI Closure

```bash
git push -u origin <branch>
remote_sha=$(git ls-remote --heads origin "refs/heads/<branch>" | cut -f1)
test "$remote_sha" = "$(git rev-parse HEAD)"
printf 'PUSH_VERIFIED branch=%s sha=%s\n' "<branch>" "$remote_sha"
```

Before retrying a failed exact-SHA run, distinguish a product failure from GitHub infrastructure and billing limits. Inspect every job's timestamps and step count: failures in seconds with `steps: []` did not execute repository code. Check GitHub Status, `gh api rate_limit`, and—especially for private repositories—Billing → Usage → Actions. Exhausted hosted-runner minutes with no paid budget is separate from REST API limits. Do not launch repeated reruns while usage is exhausted or Actions/API service is degraded; wait for the cause to clear, then rerun the same SHA once.

For a new public repository, the push is only the transport step. Verify public visibility and the repository API SHA, fetch the public page and raw install URL, test a fresh HTTPS clone, and wait for the exact commit's CI run with `gh run watch <run-id> --exit-status`. Inspect annotations even when CI succeeds; if a supported dependency or GitHub Action is deprecated, update it and repeat every affected gate on the replacement commit.

For packaging or matrix workflows, top-level `success` is insufficient evidence: inspect every required job and critical step, then enumerate uploaded artifacts through the Actions API and record each artifact's name, size, and expiry state. Confirm both build and packaged-smoke steps passed on every promised platform.

When a matrix run fails, diagnose the **exact current-SHA job log** rather than the checks-table summary. Normalize policy-scan paths across Windows/POSIX, release database/file handles on constructor failure, avoid experimental built-in module mocks when real fixtures or injected seams suffice, synchronize timing tests on request-start signals, and explicitly provision locked desktop runtimes when their packages have no lifecycle installer.

If every independent job fails almost immediately with `steps: []`, verify the provider status before changing code. That pattern is CI infrastructure evidence, especially when Actions and API services are degraded. Rerun the same exact-SHA workflow after recovery and inspect attempt-specific jobs; any job with substantive executed steps is a real candidate failure until diagnosed. Prefer a bounded exact-SHA retry monitor that exits on substantive failure over no-op commits made only to retrigger CI.

### Public repository rename closure

Treat a public repository rename as a coordinated migration rather than a GitHub setting change:

1. Confirm the target slug is available.
2. Search the tracked tree for the old slug and display name; update README titles, raw-install URLs, clone commands, directory examples, and public terminology before committing.
3. Re-run tests, validation, clean-tree checks, and the reachable-history privacy scan on the replacement commit.
4. Rename with `gh repo rename <new-slug> --repo <owner>/<old-slug> --yes`.
5. Immediately set `origin` to the new URL and update the GitHub description; do not rely on GitHub's redirect as the permanent configuration.
6. Push and verify local, `git ls-remote`, and GitHub API SHAs match.
7. Rename the local checkout directory only after the remote rename and push succeed, then continue from the new path.
8. Fetch the new public page and raw-install URL, test a fresh unauthenticated HTTPS clone, wait for CI on the exact replacement commit, and confirm the current tracked tree has no stale old slug or display name.

For mixed public collections, choose a broad class-level name that is distinct from any existing product or website. A label such as “Custom Pack” can cover skills, plugins, integrations, scripts, and utilities without implying they are all one formal tool type.

---

### Direct-upload static-site release closure

For static sites whose production host uses manual/direct upload rather than Git-connected builds, a verified Git push is not deployment evidence. Build a minimal archive from the exact committed public assets—excluding `.git`, local artifacts, and unrelated repository files—and include every runtime dependency introduced by the release, including client JavaScript, JSON/data files, and nested assets. Inspect the archive manifest while counting files separately from directory entries, upload it as a production deployment, and require the host UI to confirm the expected expanded file count before submission.

After host-side success, compare live bytes or hashes against the committed files and probe at least one **new release sentinel**—a newly added script, JSON endpoint, or distinctive marker—on both the custom and provider domains with cache-busting queries. A missing data path that returns the old `index.html` through SPA fallback is evidence that the new archive is absent, not a successful JSON response. Run a bounded propagation poll before declaring the deployment stale, but trust public readback over a dashboard that merely looks published. Then rerun the reported visual defect at the exact viewport plus the normal browser matrix.

When browser automation must populate a hidden file input, prefer CDP `DOM.setFileInputFiles` over the native chooser. If ordinary node IDs are invalid across stateless CDP calls, obtain the input's stable `backendDOMNodeId` from a full DOM or accessibility snapshot and address it by backend ID. Read back the archive name, expanded file list/count, and enabled deploy button before clicking. If the controllable dashboard reaches a login/Turnstile gate, test for an already-authorized CLI/API session without exposing tokens; otherwise stop at the human authentication gate rather than claiming publication or asking the user to perform the upload manually.

## 6. Multi-Repo Batch Coordination

When publishing the same pattern across multiple repositories (e.g., porting a library component):

1. Create a tracking list: repo → branch → SHA → approval status
2. Gate each repo independently — one failure does not block the others
3. Use separate profile/session for each repo's independent closeout reviewer
4. After all pass, push each from a clean status check, not sequentially
5. Log each push with SHA verification in the same conversation

---

## Related

| Skill | Coverage |
|-------|----------|
| `github-pr-workflow` | PR creation, CI monitoring, merging |
| `github-auth` | GitHub token setup, SSH key config |
| `github-code-review` | PR code review workflow |
## Public support files

- `scripts/ci-retry-monitor.py`
