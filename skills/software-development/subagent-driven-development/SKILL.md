---
name: subagent-driven-development
description: subagent-driven-development — Execute plans via delegate_task subagents (2-stage review).
version: 1.2.5
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms:
- linux
- macos
- windows
metadata:
 hermes:
 tags:
 - delegation
 - subagent
 - implementation
 - workflow
 - parallel
 related_skills:
 - writing-plans
 - requesting-code-review
 - test-driven-development
---
# Subagent-Driven Development

## Overview

Execute implementation plans by dispatching fresh subagents per task with systematic two-stage review.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration.

## When to Use

Use this skill when:
- You have an implementation plan (from writing-plans skill or user requirements)
- Tasks are mostly independent
- Quality and spec compliance are important
- You want automated review between tasks

**vs. manual execution:**
- Fresh context per task (no confusion from accumulated state)
- Automated review process catches issues early
- Consistent quality checks across all tasks
- Subagents can ask questions before starting work

## The Process

### 1. Read, Parse, and Preflight the Plan

Read the plan file. Before dispatching implementation, audit it for internal contradictions and claims that cannot simultaneously hold—especially low-latency streaming versus authoritative final-channel precedence, bounded shutdown versus retained worker ownership, retry claims versus partial-stream replay safety, and install/public-link claims for artifacts not yet published. Correct the execution contract or explicitly document the tradeoff before production code begins.

For plans with streamed irreversible side effects (TTS, media, notifications, progressive writes), load during preflight.

Extract ALL tasks with their full text and context upfront. Create a todo list:

```python
# Read the plan
read_file("docs/plans/feature-plan.md")

# Create todo list with all tasks
todo([
 {"id": "task-1", "content": "Create User model with email field", "status": "pending"},
 {"id": "task-2", "content": "Add password hashing utility", "status": "pending"},
 {"id": "task-3", "content": "Create login endpoint", "status": "pending"},
])
```

**Key:** Read the plan ONCE. Extract everything. Don't make subagents read the plan file — provide the full task text directly in context.

### 2. Worker Transaction Contract

Before every implementation dispatch, reduce the assignment to:

- **One invariant:** one observable behavior that must become true.
- **Bounded files:** the exact writable file set; everything else is read-only.
- **One RED→GREEN gate:** the exact focused test command and expected failing reason before implementation.
- **One checkpoint:** a local commit or verified artifact after focused and relevant regression gates pass.
- **Boundaries:** no push, release, credentials, unrelated cleanup, self-backgrounding, or skill/memory curation.

The controller owns acceptance. Exit code `0` and a worker summary prove only transport completion; inspect the live files/diff, rerun the named focused test and canonical gate, and verify the checkpoint.

Resume an incomplete worker once. If the resumed pass remains incomplete, preserve and verify valid live-tree work, then start a fresh narrower worker for only the remaining invariant. Do not keep feeding a degraded context.

Disposable implementation workers must not spend a post-task turn reviewing or updating skills. Disable the worker/profile skill nudge (`skills.creation_nudge_interval: 0`) when the execution surface supports it; curate reusable learning only from the controller after verified acceptance.

### 3. Per-Task Workflow

For EACH task in the plan:

#### Step 1: Dispatch Implementer Subagent

Use `delegate_task` with complete context:

```python
delegate_task(
 goal="Implement Task 1: Create User model with email and password_hash fields",
 context="""
 TASK FROM PLAN:
 - Create: src/models/user.py
 - Add User class with email (str) and password_hash (str) fields
 - Use bcrypt for password hashing
 - Include __repr__ for debugging

 FOLLOW TDD:
 1. Write failing test in tests/models/test_user.py
 2. Run: pytest tests/models/test_user.py -v (verify FAIL)
 3. Write minimal implementation
 4. Run: pytest tests/models/test_user.py -v (verify PASS)
 5. Run: pytest tests/ -q (verify no regressions)
 6. Commit: git add -A && git commit -m "feat: add User model with password hashing"

 PROJECT CONTEXT:
 - Python 3.11, Flask app in src/app.py
 - Existing models in src/models/
 - Tests use pytest, run from project root
 - bcrypt already in requirements.txt
 """,
 toolsets=['terminal', 'file']
)
```

#### Step 2: Dispatch Spec Compliance Reviewer

After the implementer completes, verify against the original spec:

```python
delegate_task(
 goal="Review if implementation matches the spec from the plan",
 context="""
 ORIGINAL TASK SPEC:
 - Create src/models/user.py with User class
 - Fields: email (str), password_hash (str)
 - Use bcrypt for password hashing
 - Include __repr__

 CHECK:
 - [ ] All requirements from spec implemented?
 - [ ] File paths match spec?
 - [ ] Function signatures match spec?
 - [ ] Behavior matches expected?
 - [ ] Nothing extra added (no scope creep)?

 OUTPUT: PASS or list of specific spec gaps to fix.
 """,
 toolsets=['file']
)
```

**If spec issues found:** Fix gaps, then re-run spec review. Continue only when spec-compliant.

#### Step 3: Dispatch Code Quality Reviewer

After spec compliance passes:

```python
delegate_task(
 goal="Review code quality for Task 1 implementation",
 context="""
 FILES TO REVIEW:
 - src/models/user.py
 - tests/models/test_user.py

 CHECK:
 - [ ] Follows project conventions and style?
 - [ ] Proper error handling?
 - [ ] Clear variable/function names?
 - [ ] Adequate test coverage?
 - [ ] No obvious bugs or missed edge cases?
 - [ ] No security issues?

 OUTPUT FORMAT:
 - Critical Issues: [must fix before proceeding]
 - Important Issues: [should fix]
 - Minor Issues: [optional]
 - Verdict: APPROVED or REQUEST_CHANGES
 """,
 toolsets=['file']
)
```

**If quality issues found:** Fix issues, re-review. Continue only when approved.

#### Step 4: Mark Complete

```python
todo([{"id": "task-1", "content": "Create User model with email field", "status": "completed"}], merge=True)
```

### 4. Final Review

After ALL tasks are complete, dispatch a final integration reviewer:

```python
delegate_task(
 goal="Review the entire implementation for consistency and integration issues",
 context="""
 All tasks from the plan are complete. Review the full implementation:
 - Do all components work together?
 - Any inconsistencies between tasks?
 - All tests passing?
 - Ready for merge?
 """,
 toolsets=['terminal', 'file']
)
```

### 5. Verify and Commit

```bash
# Run full test suite
pytest tests/ -q

# Review all changes
git diff --stat

# Final commit if needed
git add -A && git commit -m "feat: complete [feature name] implementation"
```

## Task Granularity

**Each task = 2-5 minutes of focused work.**

**Too big:**
- "Implement user authentication system"

**Right size:**
- "Create User model with email and password fields"
- "Add password hashing function"
- "Create login endpoint"
- "Add JWT token generation"
- "Create registration endpoint"

## Red Flags — Never Do These

- Start implementation without a plan
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed critical/important issues
- Dispatch multiple implementation subagents for tasks that touch the same files
- Make subagent read the plan file (provide full text in context instead)
- Skip scene-setting context (subagent needs to understand where the task fits)
- Ignore subagent questions (answer before letting them proceed)
- Accept "close enough" on spec compliance
- Skip review loops (reviewer found issues → implementer fixes → review again)
- Let implementer self-review replace actual review (both are needed)
- **Start code quality review before spec compliance is PASS** (wrong order)
- Move to next task while either review has open issues

## Handling Issues

### If Subagent Asks Questions

- Answer clearly and completely
- Provide additional context if needed
- Don't rush them into implementation

### If Reviewer Finds Issues

- Implementer subagent (or a new one) fixes them
- Reviewer reviews again
- Repeat until approved
- Don't skip the re-review

### If Subagent Fails a Task

- Dispatch a new fix subagent with specific instructions about what went wrong
- Don't try to fix manually in the controller session (context pollution)
- Inspect the live tree before redispatching; preserve valid partial work and separate agent-created generated junk from intentional source changes. After a timeout, inspect recent commits, the staged index, and unstaged/untracked files separately—a worker may have committed a valid slice before starting later scratch work.
- Resume the same session once when it merely returned a progress placeholder. If the resumed context again spends its budget on inspection without a RED→GREEN deliverable, stop feeding the degraded context.
- Split the mission into invariant-level vertical phases, each with a bounded read set, focused TDD, a local commit, and independent controller gates. Do not stack a new phase on a dirty or failing tree, and do not push until independent review is complete.
- When the code is already green but the worker repeatedly stops before commit, switch to a **closeout-only transaction** instead of replaying the implementation prompt: controller-verifies the dirty diff and gates, then a fresh tiny worker may only review, stage the enumerated files, commit, and prove a clean tree. This preserves context budget and prevents a finished patch from being re-audited into another timeout.
- If a worker leaves a parser-red partial patch, recover syntax from the live file and pre-change diff before redispatching. Run the parser/compiler immediately, then inspect the whole diff for adjacent behavior accidentally deleted during broad replacements (IPC/provider handler loss is a common example). Preserve valid edits; do not trust the worker's prose description of corruption.
- During a dirty repair, use `git diff <remote> --check` to include uncommitted fixes. `git diff --check <remote>...HEAD` checks only the committed range and can continue reporting a defect already fixed in the working tree. After commit, rerun the three-dot committed-range check.

### Verify the Working Tree, Not the Summary

Subagent completion summaries are claims, not evidence. Before advancing any gate:

1. Re-read every file the agent says it changed and inspect the actual diff.
2. Run the focused test yourself, then the relevant full suite/build.
3. Confirm configuration sources and generated artifacts remain synchronized.
4. Search for legacy symbols the task claimed to remove.
5. Check that requested tests actually exist; passing counts can conceal unchanged or mistargeted coverage.
6. For every new behavior, distinguish **registration/schema tests** from **behavioral tests**. Schema presence proves only that a tool or endpoint is advertised; it does not prove parsing, host-API calls, fallback semantics, error handling, or output correctness. Require behavioral tests for the risky path and named edge cases before accepting an implementer's “tests added” claim.
7. For data transformations, verify write dimensions and returned metadata are derived from the final filtered/normalized data, not the original input shape. This catches silent over-wide/over-tall writes after blank-row removal, filtering, deduplication, or normalization.
8. For deferred/batched host APIs such as Office.js, inspect installed type definitions and review the full load → sync → read/mutate sequence. A successful compile does not prove that client-object state was loaded when accessed. Treat latency plans that collapse synchronization as potentially contradictory with payload caps: loading full values before learning dimensions may reduce round-trips while defeating truncation and increasing bridge cost. Prefer a locally estimable fast path plus a metadata-first fallback, and require tests that assert exact loaded properties as well as sync counts.
9. After every repair/amend cycle, re-read commit messages and release notes. Remove stale test counts, contradicted behavior claims, and obsolete implementation details before push/tag/release.
10. Audit new/untracked files separately from the diff. Do not delete an unexplained user-owned duplicate merely because a reviewer calls it stale. If generated project discovery could accidentally compile it, exclude the exact path in the project source manifest and report it for later user disposition.
11. For database table rebuilds, verify schema semantics as well as row preservation: primary keys/autoincrement, NOT NULL/defaults, unique indexes, foreign-key targets/actions, new insert behavior, `foreign_key_check`, and forced-failure rollback. Generic reconstruction from column metadata often drops constraints; prefer explicit canonical DDL for a fixed table set.
12. Treat “tests passed” and “committed” in a child summary as untrusted until the controller reruns the focused gate, checks `git status`, reads the actual commit/diff, and confirms the claimed SHA exists. A clean process exit with no commit, a dirty tree, partial gates, or an inaccurate ahead-count is an incomplete phase.
13. Review idempotency for semantic conflicts, not only duplicate counts. Exact retries may no-op, but a reused identity with different ownership or payload must reject atomically. Do not implement retry safety by globally deduplicating legitimate records from different transactions (for example, identical review text from separate sessions).
14. Verify new tests are executed by the canonical repository gate, not merely compiled or run manually. Inspect explicit package-script/workflow test lists, add the new test there, and prove its success marker appears during the full validation command.
15. For Electron/web renderer changes, audit runtime boundaries separately from Node tests. APIs such as `Buffer` may exist in the test runner but not the packaged browser context; use browser-native UTF-8 primitives and test multibyte limits without Node globals.
16. For privileged IPC writes, review the entire envelope: exact top-level and nested key allowlists, UTF-8 byte caps, identifier validation, canonical ownership/catalog checks, immutable retry semantics, and rejection of fabricated fallback identities. A valid inner object does not make an unbounded or secret-bearing outer envelope safe.
17. For main-process-derived assessment/progression, verify semantics beyond type safety: pending-only rules must be unconditional, evidence maps by authoritative IDs, each competency keeps its own threshold, concept IDs are not inferred from competency IDs, prerequisite reads occur inside the write transaction, and identical pending retries remain stable after surrounding progress changes..
18. For provider/network hardening, inspect both the reusable bounded-read helper and every call site. Stream-count bytes, distrust `Content-Length`, cancel on declared and streamed overflow, keep error-body limits small, and ensure retry aggregates never retain raw provider bodies. Build redaction fixtures dynamically so transport masking cannot make tests tautological.
19. For Electron/React accessibility work, verify runtime lifecycle rather than accepting ARIA presence alone. New tests must run in the canonical script; focus-trap callbacks must be stable; cleanup must restore the actual prior element; `aria-current` and `aria-pressed` must match their real semantics; screen-reader utilities, focus outlines, 44px targets, and reduced-motion rules must exist in CSS. Separate visible product branding from persisted compatibility identifiers.
20. Never patch secret-bearing source from redacted tool output or a child summary. Read the live file and run the parser first: masked Authorization syntax may be display-only, or the worker may have written the mask back into source. For Electron rebrands, treat `app.setName()` as a storage-path change until proven otherwise; prefer `productName`/window titles unless an explicit user-data migration is tested.
21. Configure the repository-local public Git identity **before the first publishable commit**, then audit author and committer identities for every commit ahead of the remote before push. If the series is still unpushed, rewrite only that local series; never discover identity leakage after publishing.
22. If the explicitly named worker remains unavailable after bounded cooldown retries, freeze scope. The controller may perform only mechanical parser recovery or commit closeout after inspecting the live diff; it must rerun focused and canonical gates and obtain independent review before push. Do not turn an availability fallback into unsupervised feature development.
23. A green implementation is not release-ready until a semantic review traces product claims through production wiring. Check for legacy authority bypasses, canonical profile/policy binding, provenance surviving cache eviction, UI-reachable retries, queued/one-shot state flowing through claim → authoritative prompt/runtime use → exactly-once consume (with release on failed startup), persistent preferences actually reaching policy generation, deletion recomputation, export/privacy schema agreement, course-specific behavior, prerequisite UX, and packaged-artifact verification..
24. Convert every worker claim such as “production-path,” “end-to-end,” “streaming,” “cancellation,” or “canonical gate” into a claim-to-test trace: identify the production entry point invoked, controlled failure/interleaving, assertion that proves the invariant, and package/workflow command that runs it. Reject helper-only timer tests labeled as hung-call coverage, direct sanitizer tests labeled as provider-path coverage, fake relay objects labeled as socket-level streaming proof, tests that reproduce filtering logic instead of invoking production code, and tautologies such as `expect(true)` / `or True`. When fake timers drive rejected promises, require the test to attach rejection handling before time advances; a runner that reports passing tests plus unhandled rejections is failed. If the same resumed worker twice reports nonexistent coverage, preserve valid changes but start a fresh narrow repair transaction rather than resuming the degraded context again.
25. Treat a worker's own “deferred” list as part of its verdict. If it defers production entry-point wiring, lifecycle integration, canonical test registration, independent review, or commit closeout, the task is incomplete regardless of exit code or passing component tests. Start a fresh narrow repair against the named gaps instead of accepting the foundation as finished.
26. Verify every promised external artifact by reading it back. A claimed report path, generated schema, screenshot, or review file that does not exist is not evidence; recover authoritative content from the process/session log when possible, write the artifact outside the repository if appropriate, and label that provenance.

A green build proves compilation, not concurrency, security, protocol, lifecycle, parser correctness, or host-API behavior. Review whether each test establishes its named invariant. Reject fixed timing sleeps for synchronization, per-instance counters presented as global concurrency proof, sorted values used to “prove” semantic ordering, tests that duplicate the implementation without invoking production code, schema-only tests presented as feature coverage, and other tautological assertions.

When a subagent times out, inspect the working tree before redispatching. Timeouts often leave useful partial edits. Preserve valid work, run focused verification, and give the next agent only the remaining gaps rather than restarting blindly.

### Nested-background completion trap

A delegated Hermes process may invoke `/background` or otherwise spawn its own worker, then exit successfully with a progress placeholder such as “background task running.” Treat that as **incomplete**, even when the outer process exits `0`.

1. Capture the returned Hermes `session_id`.
2. Resume that exact session using the CLI form accepted by the installed Hermes version. For current subcommand-based CLIs, use `hermes --resume <session_id> -p <profile> chat -q "<instruction>"`; placing `-q` directly after the global flags can be parsed as an invalid command. If Hermes prints a resume command, validate its syntax against `hermes --help` before launching rather than assuming generated guidance matches the installed parser.
3. Instruct it to inspect the live working tree/background task, resume stalled work directly, and remain attached until the original deliverable is finished, verified, and committed.
4. Reject repeated progress placeholders; require the full requested completion report.
5. Independently inspect the working tree and rerun verification after the resumed agent reports completion.

### Context-compaction and repeated-placeholder recovery

A resumed session is not always the right recovery. If the same Hermes session has already compacted away the task, a resume may inherit the damaged context and spend another turn budget re-inspecting without editing.

1. Resume the exact session once when it contains useful state or a nested-background task.
2. If that resume again returns a placeholder or inspection-only summary, stop resuming it.

Repeated pre-API compaction telemetry is itself an escalation signal. **At the second consecutive compaction without a committed RED→GREEN slice, the controller must stop the worker and inspect the live tree.** Do this even if file modification times are still advancing: continued edits do not prove retained task understanding, and allowing dozens or hundreds of compressions converts useful partial work into a corruption risk. Preserve valid edits, recover syntax mechanically if needed, and start a fresh narrower transaction.

For Office companion/plugin ports, split each repository into bounded transactions rather than one monolithic prompt: (1) protocol/companion + focused tests, (2) plugin/schema/task-pane wiring + focused tests, (3) lifecycle/docs/full gates/local commit. Do not ask one worker to implement the entire bridge, independently review itself, run every platform gate, and commit after a long shared-context run.

If a named worker reaches this threshold, do not merely “monitor it because it is still changing files.” Stop it, record its session/process and dirty-tree state, and hand only the remaining failing invariant to a fresh worker.

3. Verify the repository directly, preserve useful partial edits/logs, and start a fresh **narrow transaction** with a bounded file surface, one RED-capable focused test, one invariant, explicit gates, and a local commit/artifact finish contract.
4. Split again if the worker still compacts before implementation. Separate store migrations from renderer/IPC wiring, build-layout migrations from feature behavior, and analysis from closeout formatting.
5. Do not advance while the current phase is dirty or red.
6. Tests must derive expectations from the authoritative source of truth. Reject tests that merely reproduce a newly copied policy/catalog and therefore prove the duplicate rather than integration correctness.
7. For large native-app plans, do not delegate baseline + all implementation + review + screenshots + commit + push as one transaction. Use at least three bounded transactions: implementation/RED→GREEN, independent review/repair, then controller-owned verification and closeout. A worker that spends its iteration budget waiting on a long `xcodebuild` or simulator run is not making useful implementation progress.
8. If a delegated test command remains alive with near-zero CPU after its named tests have started, inspect the live process and test log from the controller. Preserve the log, terminate only the stuck test process, then rerun a narrower test class or method. Do not keep resuming a compressed worker merely to wait on the same hung native test.
9. Keep the final push controller-owned whenever practical. Before push, independently verify the actual commit, public author/committer identity, ahead range, clean diff checks, and the exact remaining untracked files. A worker summary saying “ready to push” is not a push.

Detailed recovery recipe: see the recovery steps in this skill.

### Read-only audit hygiene

A “read-only” audit can still mutate repositories indirectly if the agent runs `npm install` or another dependency resolver. Before accepting an audit:

1. Compare `git status` before and after.
2. Treat lockfile rewrites, generated directories, and dependency metadata as unintended unless the task explicitly authorized them.
3. Preserve the requested plan/report artifact, but restore only the clearly audit-created mutation after inspecting its diff.
4. Prefer existing dependencies, manifest reads, static inspection, and already-available test commands for audits; do not install merely to gather evidence.

For race-sensitive code, require deterministic barriers/continuations and test the exact interleaving: old cleanup after new resource installation, enqueue during worker exit, cancellation-resistant operations, and old/new generation isolation. Repeat specification review until PASS before starting code-quality review.

## Efficiency Notes

**Why fresh subagent per task:**
- Prevents context pollution from accumulated state
- Each subagent gets clean, focused context
- No confusion from prior tasks' code or reasoning

**Why two-stage review:**
- Spec review catches under/over-building early
- Quality review ensures the implementation is well-built
- Catches issues before they compound across tasks

**Cost trade-off:**
- More subagent invocations (implementer + 2 reviewers per task)
- But catches issues early (cheaper than debugging compounded problems later)

## Integration with Other Skills

### With writing-plans

This skill EXECUTES plans created by the writing-plans skill:
1. User requirements → writing-plans → implementation plan
2. Implementation plan → subagent-driven-development → working code

### With test-driven-development

Implementer subagents should follow TDD:
1. Write failing test first
2. Implement minimal code
3. Verify test passes
4. Commit

Include TDD instructions in every implementer context.

### With requesting-code-review

The two-stage review process IS the code review. For final integration review, use the requesting-code-review skill's review dimensions.

### With a systematic debugging approach

If a subagent encounters bugs during implementation:
1. Follow a systematic debugging process
2. Find root cause before fixing
3. Write regression test
4. Resume implementation

## Example Workflow

```
[Read plan: docs/plans/auth-feature.md]
[Create todo list with 5 tasks]

--- Task 1: Create User model ---
[Dispatch implementer subagent]
 Implementer: "Should email be unique?"
 You: "Yes, email must be unique"
 Implementer: Implemented, 3/3 tests passing, committed.

[Dispatch spec reviewer]
 Spec reviewer: ✅ PASS — all requirements met

[Dispatch quality reviewer]
 Quality reviewer: ✅ APPROVED — clean code, good tests

[Mark Task 1 complete]

--- Task 2: Password hashing ---
[Dispatch implementer subagent]
 Implementer: No questions, implemented, 5/5 tests passing.

[Dispatch spec reviewer]
 Spec reviewer: ❌ Missing: password strength validation (spec says "min 8 chars")

[Implementer fixes]
 Implementer: Added validation, 7/7 tests passing.

[Dispatch spec reviewer again]
 Spec reviewer: ✅ PASS

[Dispatch quality reviewer]
 Quality reviewer: Important: Magic number 8, extract to constant
 Implementer: Extracted MIN_PASSWORD_LENGTH constant
 Quality reviewer: ✅ APPROVED

[Mark Task 2 complete]

... (continue for all tasks)

[After all tasks: dispatch final integration reviewer]
[Run full test suite: all passing]
[Done!]
```

## Remember

```
Fresh subagent per task
Two-stage review every time
Spec compliance FIRST
Code quality SECOND
Never skip reviews
Catch issues early
```

**Quality is not an accident. It's the result of systematic process.**

## Further reading (load when relevant)

When the orchestration involves significant context usage, long review loops, or complex validation checkpoints, load these references for the specific discipline:

- Split monolithic named-profile runs into context-bounded vertical transactions; recover partial dirty trees; stop repeated exact terminal calls; prevent concurrent writers; safely remove a runtime while preserving only genuine compatibility identifiers; clean stale emitted artifacts; and harden GUI smoke/schema-migration gates against false-positive success. Load when a profile worker starts repeated compression, times out before commit, triggers a repeated-command guardrail, performs a cross-layer runtime removal, or a smoke test reports success despite runtime handler/database errors.
- Four-tier context degradation model (PEAK / GOOD / DEGRADING / POOR), read-depth rules that scale with context window size, and early warning signs of silent degradation. Load when a run will clearly consume significant context (multi-phase plans, many subagents, large artifacts).
- The four canonical gate types (Pre-flight, Revision, Escalation, Abort) with behavior, recovery, and examples. Load when designing or reviewing any workflow that has validation checkpoints — use the vocabulary explicitly so each gate has defined entry, failure behavior, and resumption rules.
- Deterministic controller checks for timeout races, task cancellation, worker handoff, identity-safe cleanup, generation isolation, and misleading concurrency tests. Load whenever delegated work touches actors, async resources, or lifecycle state machines.
- Protocol-precedence, incremental parsing, worker ownership, streaming retry, marketability-claim, and release-closeout gates for TTS/media/notification/progressive-write plans.
- Coherent checklist for TypeScript/Electron `rootDir` expansions: emitted-layout changes, package/dev/smoke/preload/test path updates, `__dirname` revalidation, generated-artifact cleanup, and authoritative integration tests.
- Isolate Electron smoke user data and credential access, prevent orphaned GUI children, establish product-specific development storage, and register newly added application subtrees in canonical cross-platform CI.
- Renderer/runtime-boundary, UTF-8, privileged IPC envelope, immutable retry, canonical test-registration, and controller-acceptance checklist.
- Streamed response byte caps, overflow cancellation, small error-body limits, sanitized retry aggregates, and transport-safe secret-redaction tests.
- Focus-trap lifecycle, ARIA state semantics, canonical test execution, CSS keyboard/reduced-motion gates, and visible-branding vs compatibility-identifier rules.
- Bounded named-worker outage fallback, parser-first recovery from redacted edits, mechanical closeout limits, and pre-push public Git identity auditing.
- Three-way independent review and production-wiring checks for authority bypasses, profile binding, provenance, retries, deletion-derived state, privacy/export claims, and packaged artifacts.

Both general workflow references are adapted from gsd-build/get-shit-done (MIT © 2025 Lex Christopherson).
