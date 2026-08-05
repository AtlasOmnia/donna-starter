---
name: coding-worktree-recovery
description: coding-worktree-recovery — Safely recover and continue interrupted or overlapping coding-agent work in a dirty Git checkout, including concurrent-writer arbitration, macOS cloud-synced/dataless checkout recovery, bounded handoff, and verified closeout.
version: 1.1.3
platforms:
- macos
- linux
- windows
metadata:
 hermes:
 tags:
 - git
 - worktree
 - coding-agents
 - recovery
 - concurrency
 category: software-development
---
# Coding Worktree Recovery

Use this skill when coding-agent work is interrupted, an agent exits without a clean commit, multiple controllers target the same checkout, or the checkout produces inconsistent file/Git behavior.

This skill is about preserving valid work and restoring one trustworthy writer. It does not authorize pushing, merging, publishing, or destructive cleanup.

## Core invariants

1. **One checkout, one writer.** Read-only reviewers may overlap; write-capable agents may not.
2. **The live filesystem is authoritative.** Agent summaries and successful process exits are evidence leads, not proof.
3. **Never clean another writer's work.** Do not reset, stash, checkout, delete, or overwrite unexplained changes.
4. **Commits are checkpoints, not completion.** Re-run controller gates after the final commit.
5. **Mechanical status and reasoning are separate.** A deterministic watchdog may report process/Git state; acceptance still requires a controller review.

## Recovery workflow

### 1. Freeze new writers

- Do not launch another implementation agent yet.
- Enumerate all live coding/Hermes processes whose full command references the checkout.
- Record PID, parent PID, process group, start time, elapsed time, and command.
- Inspect child processes as well as tool-managed process handles; an interrupted parent can leave an orphan writer.
- Trace workers back to long-lived TUI/gateway controllers. Killing only a visible `hermes ... chat` PID is insufficient when its controller can respawn or resume another worker.
- Match writers by exact command semantics (for example, `hermes ... chat` plus checkout), not by broad words such as `hermes`, model names, or the checkout path; broad matching misclassifies `tsserver` and other read-only services.
- If a stale TUI or messaging controller repeatedly respawns workers, preserve the user session while stopping its already-spawned worker/monitor process groups. Trace the exact originating conversation before transferring ownership.
- Do not assume `/stop` cancels prior task-owned background work. It may correctly report no active task while a previously launched worker survives or its completion notification triggers a successor. When that happens, send an explicit plain-language cancellation instruction into the exact originating conversation, require acknowledgement, and independently verify that no new generation appears. Do not suspend the production messaging gateway for this purpose.

### 2. Arbitrate ownership

- Classify every surviving process by its full command and repository scope: write-capable controller/worker, strictly read-only reviewer, repository service, language server, or unrelated campaign. A Hermes process is not automatically a writer.
- Keep the earliest legitimate writer if it is still making bounded progress.
- Stop later duplicate writers and their child processes.
- Do not launch a duplicate review merely because the fresh controller cannot see the old tool-process handle. An interrupted parent can leave a read-only reviewer alive under its OS PID; recover its profile/session result instead.
- A living read-only reviewer may overlap controller-run deterministic gates only when no writer survives and the reviewer prompt forbids generators, installs, builds, tests, staging, commits, and edits.
- If a worker has undergone repeated context compaction without a committed RED→GREEN slice, terminate it and preserve the tree for a fresh handoff.
- After stopping a writer, verify the process and descendants are gone before touching the checkout.

### 2A. Distinguish process liveness from forward progress

A live PID, recent log timestamp, active research child, or expanding diff proves execution activity—not convergence. When the user asks whether work has stalled, lead with the task gate: state `Task N passed` or `Task N incomplete`, then report process liveness separately.

Classify a worker as **running but nonconverging** when the same acceptance gate remains RED through the initial pass plus one bounded resume while mechanisms and diff size keep changing. At that threshold:

1. Preserve the exact dirty diff and latest authoritative RED artifact outside the repository.
2. Stop the obsolete writer generation and any watcher/launcher that can revive it; verify the full process group is gone.
3. Re-run the smallest focused gate against the preserved tree to establish the replacement worker's true starting failure.
4. Create a fresh dirty-tree handoff naming the baseline HEAD, complete changed-file allowlist, preserved patch hash, exact remaining blocker, required acceptance artifact, and forbidden operations.
5. Launch the requested replacement model as a fresh sole writer and verify the live provider/model command plus absence of the retired generation.

Do not answer “not stalled” merely because the process is alive. For the full evidence matrix and status wording, use `shared-worktree-agent-orchestration/.

### 3. Inventory the checkout

Capture:

- absolute root, branch, HEAD, remotes, local Git identity;
- `git status --short --branch`;
- changed and untracked paths;
- diff statistics and `git diff --check`;
- active build/test processes;
- any unexpected duplicate files.

Do not assume a prior clean preflight is still current.

#### Unclear dirty checkout: isolate instead of commandeering

If the canonical checkout is dirty with unrelated work and no current writer can be positively identified, do not write into it merely because the requested files are currently clean. Preserve the dirty tree and create a fresh worktree from the verified HEAD under a unique path, recording the base SHA and branch. Verify the new worktree is clean before launching one writer. Finish and validate the bounded change there; leave integration/cherry-pick/merge to an explicit later gate. This prevents an interrupted or dormant controller from losing ownership of unrelated WIP.

### Restored checkout relocation

When a session is redirected from an old checkout to a restored repository root, recover the intended project/remote, branch, and full HEAD from the originating session or durable handoff before selecting anything. Require an exact match and independently verify complete state plus writer ownership. If no destination checkout matches—or the expected commit is absent from all destination object databases—select none and fail closed rather than continuing at the old path or choosing a similar sibling. Read-only relocation scanners whose command text mentions the path are not writers without corroborating write semantics. Follow for the full enumeration, manifest/object check, ownership classification, and reporting contract.

If the missing checkout was clean and a verified private bare remote contains the exact branch ref and commit, reconstruct a standalone destination through a unique same-volume partial clone using `--no-hardlinks --single-branch --branch`; verify exact HEAD/branch, complete clean status, `git fsck`, internal Git common-dir, absent object alternates, and no writer before atomically renaming it to the final path. Re-read the retired checkout afterward to prove it stayed unchanged. Repository-local ignored plans may be absent from the clone, so rebuild remaining work from external evidence/session history and recheck historical blockers live. Follow for this clean-checkout path.

If no complete archive exists but a verified private bare remote contains the exact committed baseline and durable session evidence contains the complete dirty overlay, use the recovery procedure. Reconstruct only from exact patches/file bodies, require recorded hashes where available, preserve staged/unstaged/untracked classification, and fail closed on any mismatch rather than consulting a prohibited checkout.

### 3A. Integrate an accepted change into a dirty live service checkout

When an accepted commit must land in a running gateway/service without disturbing unrelated dirty work, use a bounded semantic integration transaction:

1. Before editing, record HEAD/branch, full porcelain inventory, affected-path hashes, service PID/command, supervisor label, and writer evidence. Archive every affected live path under a timestamped report directory and write a SHA-256 manifest for both archive and live copies.
2. Derive the accepted delta from `parent → child`; do not treat the accepted child file as a replacement template. Three-way merge each affected path against the live file, parent, and accepted child. If live code diverged, preserve live-only behavior and transplant only the accepted behavior. Record conflict resolutions and any compatibility seam explicitly.
3. Verify scope after every edit: compare unrelated porcelain entries to the preflight inventory, run `git diff --check` on tracked files, scan untracked files for trailing whitespace, compile the changed modules, and run focused tests for source, API, and finalization boundaries. Save raw test logs and counts.
4. Immediately before restart, repeat the writer and inventory checks. A clean test result does not authorize restart if another write-capable process can still mutate the checkout.
5. Restart through an external supervisor boundary. A command launched from inside the supervised gateway can be terminated by the gateway itself; use the project’s external gateway-restart command or a separate shell/controller. Verify the new PID, supervisor state, two health checks, and startup-log scan.
6. Produce a verifiable report containing commit IDs, scoped paths, backup hashes, merge disposition, exact commands/results, restart evidence, health responses, and any blocker. Never claim restart completion from an issued command alone.

### 4. Diagnose storage integrity

On macOS, check for cloud/File Provider placeholders when reads fail, dependencies repeatedly corrupt, or Git reports `Resource deadlock avoided`:

```bash
stat -f '%N | %z bytes | flags=%Sf' <paths>
```

If source, Git metadata, or dependency executables are `compressed,dataless`, stop using that checkout as a writer surface. Follow macOS cloud-synced checkout recovery.

### 5. Preserve and transfer work

#### Selecting a restored checkout after repository relocation

When an existing session is redirected from an old checkout to a restored repository root, select the replacement only if the **candidate worktree itself** matches the recorded project lineage, branch, and exact HEAD. A shared object database containing the expected commit, or a sibling worktree listing the expected branch at the old path, is not a match.

After a scheduled chat reset, recover the predecessor by the same messaging thread/topic before using broad keyword search; otherwise a different project that merely mentioned the archive root can be mistaken for the active repository. Extract the expected project + branch + full HEAD and last complete status from that predecessor. If the user then asks for the remaining plan or phases, reconcile the authoritative plan against that same-thread verified boundary and report only the unfinished execution order plus closure gates.

Inspect restoration manifests when available, then verify the candidate's Git root, branch, HEAD, complete staged/unstaged/untracked/stash/lock state, worktree registration, and live writer/open-file ownership. If only a sibling feature worktree was restored while the canonical branch remains elsewhere, report **no checkout selected** and stop rather than switching branches, creating a detached substitute, or commandeering the sibling.

- Establish a stable non-synced checkout at the exact last verified commit.
- Recover dirty files into staging first; verify byte counts/hashes before overlay.
- Overlay only inventoried source/test/config paths.
- Exclude `.git`, dependencies, build output, credentials, and generated artifacts.
- Compare unexpected `name 2.*` files against canonical files. Delete only a proven stale agent-created duplicate; preserve unique edits.
- If the latest work is in a divergent dirty checkout on another machine, a branch bundle alone is insufficient: preserve the exact branch, binary tracked diff, untracked allowlist, metadata, and hashes before reconciliation. Use the cross-machine-connectivity skill’s workflow and reconcile only in a new isolated worktree.

When local update-safe patches (e.g. `apply-patches.sh` artifacts) fail on upstream drift after checkout relocation, use for the split-patch, manual-context-fix, and content-based-detection workflow that preserves unrelated work.

For the READ-ONLY twin of that workflow — reconciling a stale patch against a checkout without touching the tree (does it apply, is the mechanism already upstream, minimal port plan) — use the reconciliation reference. It covers blob-hash pre-image verification from the diff's `index` line, exact patch provenance via `git log --all --find-object=<post-blob>` (pins the patch to the feature-branch tip, with `git diff --stat main...branch` line-count matching as completeness proof), `git apply --check --verbose` as a hunk-level applicability probe, upstream archaeology across unmerged PR branches (`git log --all -S`, `git branch -a --contains`, `git merge-base --is-ancestor`), port-readiness checks (dependency signatures, exported-but-uncalled helpers, RED baseline), partial apply via `git apply --exclude=<drifted-test-path>` (test files drift faster than code — re-anchor, don't discard), and call-site completeness checks. Never reset/stash/edit during reconciliation; `git apply --check`, `git show`, and `git diff <pre-blob> HEAD:<path>` are the safe tools.

### 6. Run handoff gates

Before delegating again:

- verify the stable checkout path, branch, HEAD, and dirty inventory;
- reinstall dependencies cleanly if the old dependency tree was unreliable;
- run at least focused tests, typecheck, and diff checks;
- explicitly authorize the new worker to own the inventoried dirty paths;
- tell it not to delegate or self-background when concurrency caused the recovery.

#### RED evidence on an inherited dirty tree

Do not create RED chronology by stashing the inherited dirty tree, even temporarily. A stash/pop cycle violates preservation provenance and can silently omit untracked work, alter staged state, or leave a hidden stash behind.

Use one of these instead:

- run the already-failing focused gate and preserve its raw log;
- add the focused expected-RED test directly, record the exact diff fingerprint, run it RED, then implement GREEN;
- use a temporary `git archive` or copied fixture surface for controlled mutation when the live inherited tree must remain untouched.

When an inherited fix contains multiple mechanisms and passes without a trustworthy explanation, minimize it outside the live tree with a four-way differential: exact parent, A only, B only, and A+B. Preserve logs, keep the smallest load-bearing variant, run canonical gates, commit a clean checkpoint, then remove only the disposable worktree you created.

When a canonical gate is contaminated by host disk pressure, a stale generic interpreter, or different POSIX/Windows open-handle semantics, isolate the runner rather than weakening product behavior. After repeated broad-controller exhaustion, split deterministic and native acceptance by platform.

At closeout, inspect `git stash list`, staged state, unstaged state, and untracked files. A worker claim that RED was “captured through stash/pop” is a reconciliation trigger, not acceptable proof. Verify the live tree still contains the complete authorized diff before committing.

When the writer is launched through `hermes --profile <name> chat`, treat a response such as “background task running” as a handoff—not completion. The profile CLI can exit cleanly and then cancel its asynchronous child during CLI shutdown, leaving a partial dirty tree. For recovery slices, explicitly prohibit `delegate_task` and self-backgrounding so the profile process remains the writer through tests and checkpoint commit. If delegation is required, keep the owning controller process alive until the child result is persisted, then verify the live tree and commit rather than trusting exit code 0.

For interrupted synthetic fixture corpora, transport-envelope validation, real manifest hashing, secret-field hygiene, controlled-mutation RED recovery, and isolated-worktree dependency reuse, follow fixture-corpus recovery gates.

### Explicit worker-model switch during recovery

When the user explicitly changes the implementation model while an interrupted checkout is dirty:

1. Enumerate live writers by full command, including parents, children, pipeline shells, and orphaned profile processes. Do not trust a missing Hermes process handle.
2. If another model is still writing the same checkout, stop that writer and its descendants before launching the requested replacement. Verify no matching process remains.
3. Preserve the dirty tree. Inventory tracked edits, staged state, and untracked artifacts; inspect untracked files before deleting anything.
4. Delete only proven agent-generated scratch (for example, a temporary inspection script or dependency symlink whose command/path and contents establish provenance). Hand the exact cleanup allowlist to the new worker.
5. Run the smallest focused compile/test against the partial tree. Give the replacement the exact surviving failure, allowed files, current HEAD, and known-good partial edits instead of replaying the broad original mission.
6. Launch the requested model as the sole writer and verify the runtime provider/model from the live command or agent log.

A user-requested model change is an ownership transfer, not permission for overlapping writers or a reset of valid partial work.

### 7. Complete in bounded slices

Require:

- strict RED → GREEN → REFACTOR evidence;
- production-path tests registered in canonical validation;
- one coherent commit per bounded repair/feature slice;
- no push unless separately authorized;
- independent spec review before quality/security/accessibility review when required.

#### Parallel acceleration without extra writers

When the user asks to “use agents” or hurry work in one checkout, parallelize **analysis**, not writes:

- Keep exactly one implementation/repair writer.
- Launch at most one bounded specification reviewer and one bounded quality/security/accessibility reviewer.
- Before dispatch, inspect live process commands and suppress duplicate reviewers already covering the same dimension.
- Review prompts must prohibit installs, builds, tests, generators, staging, commits, and subdelegation; those actions can mutate ignored artifacts even when source edits are forbidden.
- Give reviewers the baseline SHA, changed-file list, narrow symbols/invariants, severity threshold, and compact verdict format. Tell them not to dump full diffs or broad files.
- Treat context exhaustion, compression-only exits, or a review with no decisive verdict as **no review**. Exclude it from the decision record and replace it once with a narrower or larger-context reviewer.
- Reviewer findings may accelerate the next repair transaction, but do not feed a moving live diff into another writer. Wait for the current writer to stop or checkpoint before applying findings.

### 8. Controller acceptance

#### Desktop candidate/package identity binding

For desktop applications, source acceptance does not automatically transfer to an external `.app`/installer. Before native acceptance, bind and record the exact source HEAD/tree, package path, executable hash, bundle metadata, signature/resource-envelope result, and build interval. Reject or mark HOLD when an evidence manifest names an older source SHA, a package executable hash changes without a new binding record, or the designated package differs from the freshly built artifact. Treat repository `target/` output, a designated evidence package, and previously signed copies as separate candidates; never combine test or native evidence across those identities. A clean checkout and green source tests do not close package binding, signature validity, or native UI acceptance.

Independently verify:

- exact commit SHA and author/committer;
- clean tree;
- focused and canonical tests;
- build/smoke/audits/diff checks;
- no secrets, PII, local paths, generated artifacts, or scope creep;
- no surviving writer in the checkout.

#### Evidence inheritance across test-only checkpoints

A test-only commit may leave the runtime artifact byte-identical, but that alone does not authorize inheriting a prior native-acceptance verdict.

1. Rebuild and prove the candidate runtime artifact hash is identical to the artifact named by the earlier acceptance evidence.
2. Inspect the earlier evidence root itself—not only its summary—and require every artifact in the governing contract: per-workflow ledger, executable/PID/window identity, isolated data roots, screenshots with hashes/dimensions/nonblank analysis, relaunch proof, personal-data readback, and cleanup.
3. If the earlier evidence is incomplete or contains only fixture/database preparation, reject the inherited PASS and run native acceptance. Never upgrade setup evidence into execution evidence.
4. If the evidence is complete and the runtime artifact hash is identical, write an explicit inheritance record binding the new source SHA/tree to the unchanged artifact and the complete earlier evidence manifest.
5. Before advancing the next platform, independently sample/read the referenced artifacts and recompute their hashes; controller exit code and self-reported PASS are not proof.

If a later task starts automatically, confirm it begins only after the prior task's clean verified checkpoint.

### Iteration-limit closeout

When an agent reaches a turn/tool/context ceiling, distinguish incomplete implementation from completed implementation with missing mechanical closeout. Never accept exit code 0 or a self-reported PASS by itself. Re-read the durable log, inspect the live checkout, reconcile any file-mutation verifier warning against each claimed path, rerun the originally requested authoritative gates (not a worker-selected narrower substitute), prove candidate-fingerprint stability, compare dirty and staged scope to an explicit allowlist, and verify the resulting commit object, identity, parent, scope, clean tree, locks, writers, and listeners. Passing tests do not replace semantic inspection of security invariants named in the task.

A rejected local checkpoint is not an accepted boundary. Keep accepted ancestors immutable; amend a rejected local commit only when the required logical topology explicitly demands it and the user/controller authorizes the amendment. Otherwise use a follow-up repair commit or HOLD.

After a timeout or interruption, compile the smallest focused surface before launching a replacement. Compiler errors often identify the exact interrupted seam: missing interfaces, stale signatures, unfinished fakes, or literal patch markers. Repair one vertical slice and rerun its focused gate before assigning the next slice. For macOS Tauri filesystem-watcher work, use : inject an event sink around the real notify/reconciliation engine instead of constructing a Tauri event loop on a Rust test thread or using unsafe runtime transmutation. After two timeout generations on one broad prompt, decomposition is mandatory; merely increasing `--max-turns` is not recovery. If repeated controllers consume their budget on preflight and never execute the acceptance transaction, precompute and verify the dynamic inputs first (current process/listener owners, wrapper hashes, fresh evidence path, rollback), then launch a controller whose only job is one transaction attempt plus evidence preservation. Keep each failed generation immutable and never rerun within the same evidence directory.

A normal exit with `Response remained truncated`, max iterations, rendered diff fragments, or a file-mutation-verifier warning is not evidence that edits landed. Inspect the exact session tool calls and live tree. Resume once only when the context remains bounded; after two oversized/truncated generations without a trustworthy checkpoint, preserve the tree and switch to a fresh narrow worker/model with exact defects and a file allowlist.

When an accepted candidate is mixed with an unrelated dirty slice that breaks the checkout-wide build, prove the candidate against a temporary `git archive HEAD` tree with only its allowlisted files overlaid. Then stage and commit only that exact scope while leaving the unrelated slice intact. Follow dirty-tree candidate isolation for the complete procedure.

Use a tracked background process with completion notification for genuinely long bounded work. Exit code 0 with an explicit report that review, privacy checks, native acceptance, or commit remain unfinished is an incomplete dirty handoff—not completion. Preserve external evidence ledgers by appending; if one was truncated, record that fact and reconstruct only from retained evidence.

Follow iteration-limit closeout for the classification decision, exact-scope staging procedure, raw identity verification when output is redacted, and final report boundaries. See iterative timeout recovery for the compile-first, one-slice handoff procedure and repeated-failure strategy change.

When a controller exits while a child may have committed, or the user explicitly says to stop the active phase, use controller exit and explicit phase stop. Reconcile controller health separately from repository progress; on stop, terminate the exact controller/worker tree, preserve accepted commits or bounded dirty work, verify the post-stop Git/process boundary, and never auto-resume. A prompt requested for another session must be regenerated or verified against that final boundary and include an explicit phase stop point.

## Scheduled status updates

When the user requests periodic updates:

- prefer a deterministic script that reads live PID/Git/log state;
- make it silent after detecting the expected completed commit and clean tree;
- include branch/HEAD, latest commit subject, dirty counts, worker state, log freshness, and push state;
- update the script's checkout path after any recovery relocation;
- do not let a successful worker exit alone mark completion.

## Native desktop candidate closeout

For an interrupted desktop-app acceptance campaign, keep package identity and native interaction as separate gates. A clean checkout, successful build, valid ad-hoc signature, and matching executable hash do not prove functional-beta readiness. Before accepting a candidate, launch the exact bound bundle executable directly in isolated state and require a native capture with visible, nonzero-bounds controls plus executed scenario evidence. A window that exists but renders a blank canvas with zero accessible elements is a concrete HOLD, not a pass or an unknown that can be inferred away.

When a controller reaches the native gate and its GUI calls time out or are denied, treat that as missing evidence—not as a product pass and not as permission to keep the same exhausted session looping. Independently recapture once from the supervising session, preserve the exact candidate and blocker root, terminate any orphaned isolated app process, verify no writer/app residue remains, and record the blocker with package/source hashes and the SQLite checks that were actually completed. Resume only with a fresh, narrower controller if the native path is still actionable; otherwise return HOLD and list the precise next gate.

## Pitfalls

- Starting a replacement worker before checking live process commands.
- Trusting only Hermes process handles; orphan child agents may remain.
- Suspending or stopping a visible TUI controller does not stop child shells and Hermes workers already launched through the TUI or gateway. Enumerate process groups, parent chains, and repository-referencing commands across both controller surfaces; terminate only the exact child groups, then verify no writer can still advance the checkout.
- Persistent terminal sessions can retain an interrupted `trap cleanup EXIT` and cleanup function. A later command may silently remove a temporary dependency symlink mid-test even when no cleanup process is visible. Before recovery gates, run `trap - EXIT` and `unset -f cleanup 2>/dev/null || true`, verify the dependency path before each suite boundary, and reconcile the exact failing log when a module disappears.
- Repeatedly running `npm ci` in a cloud-synced checkout instead of relocating it.
- Treating nominal file size as proof that dataless bytes are available.
- Running recursive `lsof +D` or full `git status -uall` against a large/File Provider checkout during ownership preflight; these scans can stall and obscure the actual handoff. Prefer bounded low-level Git checks, a filtered process scan, and `lsof` against `.git/index.lock` only.
- Treating a large `git diff-files` inventory as confirmed content loss before refreshing the index. Preserve first, then use `git update-index --refresh` and compare staged/unstaged content; stale stat-cache entries can collapse without changing source bytes.
- Restoring `.git/info/exclude` or `.gitignore` from guesswork without proving intended content and zero tracked diff.
- Reporting a helper-only implementation as a complete shipped UI workflow.
- Allowing an automatic next-task worker to overlap final review repairs from the prior task.

For interrupted-worker commit discovery, one-resume dirty recovery, persistent cleanup traps, detached exact-SHA verification worktrees, and Mac→private-local-Git→Windows synchronization order, follow the recovery steps in this skill.
