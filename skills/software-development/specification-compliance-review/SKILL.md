---
name: specification-compliance-review
description: specification-compliance-review — Audit partial or passing implementations against an explicit task specification, proving each requirement with code, tests, and execution evidence.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms:
- macos
- linux
- windows
metadata:
 hermes:
 tags:
 - specification
 - compliance
 - code-review
 - testing
 - concurrency
 - verification
 related_skills:
 - grounded-specification
 - test-driven-development
---
# Specification-Compliance Review

## Overview

Use this skill when an implementation is described as partial, passing, or complete and the task is to determine whether it actually satisfies an explicit specification. This is not a generic code review and not a re-run of the test suite. The central question is: **does every normative requirement have both a correct implementation path and a meaningful proof?**

A green build proves syntax, compilation, and perhaps the tested examples. It does not prove race behavior, cancellation semantics, exact backpressure policy, integration parity, or compliance with explicit non-goals.

## Workflow

### 1. Establish the review baseline

Read, in order:

1. The task specification and surrounding plan/release gates.
2. Repository guidance (`AGENTS.md`, README, project instructions).
3. The changed files and their callers.
4. The tests added or claimed as evidence.
5. Git status/diff and recent relevant history.

Create a requirement matrix with one row per normative clause:

| Requirement | Production evidence | Proving test | Execution result | Status |
|---|---|---|---|---|
| Exact behavior | path:lines | test name + fixture | command/output | pass/fail/unknown |

Keep **unknown** distinct from **fail**. A test that could not run is not a passing test.

### 1B. Preflight implementation plans for load-bearing assumptions

When the artifact under review is an implementation plan rather than completed code, identify every external behavior that several downstream tasks assume: server-owned tool execution, plugin loading, request-context propagation, restart/reload ownership, stable host identity, or update/rollback semantics.

Do not let later RED tests encode an unproven API contract. Insert the smallest real-runtime spike before dependent work, capture the exact request/event/context contract, and gate downstream tasks on it. If the plan routes opaque identifiers through model-visible prompt text, require a deterministic metadata/session channel or explicitly stop for the missing platform capability; model copying is not a trusted transport.

Apply the plan's stated threat model before calling a security concern blocking. In particular, do not pretend Origin headers or current-user secret storage defend against hostile code already running as that OS user, and do not move a server-side secret into JavaScript merely to satisfy an authentication requirement.

### 1C. Trusted context and server-owned tool binding

For server-owned agent/plugin integrations, treat any identifier that selects a workbook, document, tenant, user, or session as security-sensitive request context. A UUID embedded in model-visible prompt text is only a hint: the model can omit, alter, replay, or substitute it. Require an out-of-band, server-recognized binding such as request metadata, a trusted header propagated by the gateway, a server-issued capability, or a validated context object. Trace the value through the actual server implementation and plugin handler; do not infer support from client tests or comments.

When a plugin receives a caller-supplied target ID, inspect whether plugin authentication authorizes the whole service rather than the specific target. If so, a wrong-but-valid ID can become cross-workbook or cross-tenant access. Add an adversarial test with two active targets: deliver a valid target A, make the model/plugin attempt target B, and assert the server rejects it or rewrites it to A before any side effect. Tests that only assert the ID appears in a prompt are vacuous for this requirement.

For OpenAI-compatible gateways, inspect the gateway source or run a real request spike to verify which body fields, headers, and tool schemas reach the native agent loop. Caller `tools`/`tool_choice` may be accepted for fingerprinting yet ignored for execution; similarly, custom context fields may be discarded. Record the exact supported transport before designing the client seam.

For localhost-only private deployments, audit proxy topology end-to-end: a loopback listener is not sufficient if its configured upstream host can be remote. Require loopback validation for the upstream as well, or classify the deployment as a separately documented remote mode; never send an injected gateway key over plain HTTP to an arbitrary `API_SERVER_HOST`.

When a review runs alongside another agent or an external process, capture the candidate SHA and review `git show <sha>:<path>` content if the worktree becomes dirty. Do not silently review concurrent edits as part of the candidate, and do not revert them without authorization.

### 2. Decompose the specification

Classify each clause as one or more of:

- functional behavior;
- concurrency or ordering invariant;
- cancellation/timeout behavior;
- integration compatibility;
- explicit scope boundary or non-goal;
- required test coverage;
- build/release gate.

Give special attention to words such as *exactly*, *only*, *latest*, *must*, *never*, *preserve*, *cancellable*, and *no refactor*. These are acceptance criteria, not descriptive prose.

### 3. Inspect implementation and seams

Trace each requirement from its public entry point through state ownership and asynchronous boundaries. For concurrency work, identify:

- who owns the worker/task;
- how pending work is represented;
- how generations/tokens identify stale work;
- who owns and cancels the transport;
- whether cleanup is identity-safe;
- whether stop awaits completion;
- whether callbacks can escape after cancellation;
- whether caller-created tasks can outlive the session.

After an extraction or refactor, compare the old path and new path for behavior parity. Common regressions occur in normalization, language mapping, configuration defaults, error formatting, and interruption handling rather than in the extracted core.

### 4. Audit tests for meaningfulness

A test proves a requirement only when its setup actually creates the required condition and its assertion observes the specified invariant. Reject vacuous coverage such as:

- a race test that releases the first operation before starting the second;
- an “active count” that measures only one callback rather than worker/transport lifetime;
- a timeout test that checks an error callback but not cancellation and eventual worker cleanup;
- a stale-generation test that does not inject a late frame after a new generation begins;
- a latest-wins test that checks the final text but not that the intermediate request was not synthesized;
- a cancellation test that stops after scheduling cancellation without awaiting the old worker.

Review test helper semantics too. An actor, lock, continuation, or deferred cleanup task can make a test appear deterministic while failing to measure the intended interval.

### 5. Verify in increasing strength

Run the smallest useful focused test first, then the complete relevant suite, then a clean build. Also run static searches for forbidden mechanisms or explicit non-goals (for example, semaphore-based blocking, direct credentials, or an unintended framework refactor).

Record command, target, destination, and result. If infrastructure prevents execution, report the exact limitation and downgrade the verification status; do not convert a prior passing claim into independently verified evidence.

### 6. Report findings

Lead with the verdict: **PASS**, **PASS WITH GAPS**, or **FAIL**.

For every finding include:

- severity;
- title;
- exact file and line range;
- requirement violated or left unproved;
- concrete execution scenario;
- why the current test does not catch it;
- smallest corrective direction (without implementing unless asked).

Then include:

- verified-good controls;
- verification commands and real output;
- unverified items and environmental limitations;
- scope/non-goal compliance;
- a short residual-risk summary.

Do not bury a failed acceptance criterion under a long list of passing tests.

## Concurrency-specific checklist

For a single-worker latest-pending pipeline, prove all of the following independently:

- no more than one worker and one transport exist during normal handoff;
- a busy request retains exactly one newest pending request;
- intermediate pending requests are not silently synthesized or sent;
- worker exit cannot strand a request enqueued during handoff;
- old cleanup cannot cancel or clear a newer transport;
- stop invalidates the generation before late callbacks are processed;
- send timeout cancels the transport and reports promptly;
- first-audio timeout cancels a receive that ignores task cancellation;
- stop awaits the old worker when the contract requires it;
- session interruption/output interruption reaches the same cancellation path;
- provider integration preserves prior wire normalization and does not enqueue stale work after reconnect.

## Pitfalls

- **RED evidence must be exact, not just nonzero.** A suite that shows `14 failed` is not meaningful unless every failure proves the corresponding requirement was violated for the right reason. Inspect the first error message, stack, and assertion for each failing test. A test that fails because `_verify_active_hermes_plugin` does not exist (AttributeError) is exact RED — it proves the verify path cannot run at all. A test that fails with an unrelated import error or a vacuous assertion is not meaningful RED. Record the concrete failure messages alongside the count.
- When RED tests are run against a baseline before the fix, verify that the passing tests in that same baseline are not false positives. A passing test in a pre-fix RED run that asserts behavior the baseline does not implement is a false-positive pass, not meaningful GREEN.
- Do not equate “build succeeded” with “specification satisfied.”
- Do not accept a test by name; inspect its synchronization and assertion timing.
- Do not review only the extracted class; inspect every caller and lifecycle edge.
- Do not call a requirement failed solely because a simulator is unavailable; call it unverified, then distinguish any source-level defect separately.
- Do not propose broad fixes before identifying the exact requirement, data flow, and missing proof.
- Do not report speculative security or product concerns as compliance failures unless the specification makes them normative.
- Call out scope drift separately: if changed files include out-of-spec artifacts (for example, scheme metadata, generated project knobs, or tooling configuration) with no explicit task requirement, record them as *out-of-scope configuration drift* rather than silently inheriting them into the implementation path.

## Provider-session safety addendum

For provider-backed audio/TTS sessions, treat these as separate acceptance criteria rather than one generic “cleanup” requirement:

- **Caller-task safety:** track provider-created enqueue tasks that can outlive a callback; stop must cancel and await them, and reconnect must explicitly reset the tracker before accepting new work.
- **Language normalization parity:** normalize language tags at the provider seam (trim, lowercase, map `-`/`_` regional forms to the base language, then apply an allowlisted fallback) before constructing wire requests.
- **Timeout shutdown:** a timeout must complete the caller promptly, cancel the underlying transport, and await cleanup where the lifecycle contract requires it—even if the operation ignores task cancellation.
- **Cleanup-race proof:** gate old transport cleanup, start the new transport first, then release old cleanup; assert the new transport is neither cancelled nor cleared.
- **True global one-active proof:** instrument every transport instance and measure its active interval, not just one worker callback. Assert the maximum across the whole handoff lifecycle is one.

When validating Swift concurrency implementations, compile after each lifecycle change. Actor-isolated helper calls require `await`; deferred tracker updates and fire-and-forget cleanup can make a green-looking test observe the wrong interval. Prefer deterministic `await`-based helper accounting.

A focused iOS verification should use an actually available simulator destination and then run the complete test target. Record the exact destination and distinguish “unverified due to unavailable destination” from a source or test defect. A generic destination such as `generic/platform=iOS` is valid for compilation but not for XCTest execution; discover a concrete simulator with `xcodebuild -project <project> -scheme <scheme> -showdestinations` (or `xcrun simctl list devices available`) and rerun tests against that destination. If `xcrun` reports it cannot find `simctl`, re-point command-line tooling with `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer` (or the active Xcode bundle path) and retry discovery before declaring the test layer unverified. If no concrete destination is available, report tests as unverified rather than treating a different device as equivalent.

When validating compile-time release/debug policy, do not rewrite both policy tests to assert the current configuration. Keep configuration-specific assertions honest: use separate Debug and Release build/test invocations, or expose a pure injectable policy factory for unit tests while retaining `#if DEBUG` as the production compile-time gate. A test named for Release must not pass merely because it was compiled in Debug.

## Milestone acceptance versus whole-product completion

When development is staged, never promote a milestone-level PASS into a whole-product verdict. A tested native launch, clean Git synchronization, or verified shortcut proves only that the accepted artifact runs; it does not prove that later milestones, prototype controls, user-reachable CRUD, settings, packaging, or persistence paths exist.

Before declaring a milestone-built product complete:

1. Inventory every normative specification clause and meaningful prototype control.
2. Trace each through UI, controller, native/backend seam, persistence, relaunch, tests, and native evidence.
3. Report milestone acceptance and whole-product acceptance separately.
4. Treat user-confirmed expectations that resolve specification ambiguity as explicit requirements.
5. If the user chooses phased execution, produce only the requested bounded phase and stop at its gate; do not resend the entire campaign.

## Support files

- `references/spec-compliance-review.md` — reusable requirement matrix, adversarial test audit, and async pipeline race patterns.
- `references/amended-commit-rereview.md` — spec rereview of an amended commit: prior-finding disposition table, delta baselines, native closeout gate as separate verification layer.
- `references/milestone-vs-product-completeness.md` — distinguish accepted milestone scope from whole-product completeness and structure bounded phase handoffs.
- `references/typescript-validator-adversarial-review.md` — hidden-own-property, cap-proof, deterministic-ordering, and content-free-error probes for `unknown`-input validators.
- `references/load-bearing-assumption-spikes.md` — pre-implementation plan review: turn unproven runtime/API assumptions into gated spikes and apply explicit threat-model boundaries.
- `references/cross-repository-contract-reconciliation.md` — reconcile producer/consumer health, auth, lifecycle, ownership, and script contracts; reject dead test helpers and wrapper-exit acceptance.
- `references/start-stop-generation-race.md` — session-specific pattern for rejecting queued provider/audio callbacks from stale lifecycle generations.
- `references/late-callback-generation-gating.md` — session-specific pattern for rejecting queued provider/audio callbacks from stale lifecycle generations.
- `references/ios-simulator-triage.md` — concrete destination discovery + simctl/toolchain triage flow for simulator-based verification.

- Treat instrumentation scope as part of the requirement: a counter around individual `send()` calls does not prove a transport- or worker-lifetime invariant. For a true one-active proof, enter when each transport/worker is created, leave only after its receive loop and cleanup have completed, and assert the maximum across the entire handoff.
- When a test claims to prove cancellation-resistant cleanup, inspect the fake transport's cancellation semantics and wait for both cancellation and worker completion. A test that only observes an error callback or a single cancellation flag can miss leaked work.
- Before running project-specific verification, confirm the project root and target path from repository guidance or discovery. If a command fails because it was launched from the wrong directory, retry from the actual project directory and report the corrected command/result rather than treating the first failure as an implementation limitation.
- Distinguish source correctness from proof completeness: a lifecycle helper may look race-safe in code while still requiring direct adversarial tests for add-during-stop, reset-after-stop, self-removal, and delayed cleanup.

## Provider enqueue-task adversarial pattern

When a provider uses a task bag to bridge a synchronous callback into an async pipeline, review the bag as a lifecycle component rather than as incidental bookkeeping. The proof should cover the linearization point of `add` versus `stop`: once stopping begins, a later add must be rejected atomically; a task already accepted must be cancelled and awaited; reset must create a clean generation. An actor is usually the clearest ownership model because the stop/add/reset decisions serialize naturally without manually reasoning about a lock around task creation.

For transport pipelines, cleanup belongs before worker completion. Do not clear the current transport or release the worker slot before `cancel()` has returned; otherwise a handoff can construct a second transport while the first is still alive. The strongest regression test gates the old transport's cancellation, starts enqueue for the next request, asserts no second transport has been created, opens the cleanup gate, then asserts the next transport becomes active and the global maximum active lifetime is one.

## Integration-review lessons from iOS provider pipelines

For a provider extraction that passes focused concurrency tests, perform one final caller-seam audit before declaring approval:

1. Trace every lifecycle requirement back through the public provider and ViewModel, not only the extracted pipeline. In particular, verify that output interruption, session stop, provider failure, and audio-engine shutdown all reach the same cancellation path when the specification requires it.
2. Distinguish **implemented and tested**, **implemented but untested**, and **not wired**. A green pipeline suite proves the seam in isolation; it does not prove that the production integration emits or consumes the relevant event.
3. Check project hygiene as part of integration quality: duplicate/unreferenced source files, generated project drift, and untracked artifacts should be reported even when the build succeeds. A passing Xcode build can still include an accidental duplicate file outside the target.
4. Run both the generic unsigned device build and the actual simulator test destination, recording the exact destination and test count. Treat static searches such as `DispatchSemaphore` and secret-pattern scans as separate evidence, not as substitutes for runtime tests.

When a broad requirement such as “output interruption cancels TTS” has no provider event path, report it as an unproven integration gap unless source tracing demonstrates a concrete defect. Do not overstate a gap as a failing acceptance criterion without an observable execution path.

## Session review template: iOS mode/job clarity + localization-harness audits

For iOS translator-style reviews where the feature spans consumer-job UX, localization catalogs, and lifecycle behavior, follow this sequence before final verdict:

1. Read `ios/AGENTS.md` plus the relevant feature doc (`README`, `OPERATOR_GUIDANCE`, and any active `.md` plan for the feature).
2. Confirm the review scope from git: current branch, recent commits (for example, the feature head commit and any immediate follow-up), and `git status` cleanliness.
3. Inspect `ConsumerOnboarding`, `LiveInterpreterView`, `TranslatorViewModel`, localization catalog(s), and their tests together; never review one file family in isolation.
4. Add a requirement matrix row for each normative promise in onboarding copy, routing, direction selection, persistence, and release policy.
5. Run at least one targeted test set for changed contracts and one broader integration test set (same toolchain/simulator session) and report exact counts.
6. For iOS simulator evidence, use a concrete destination and include the exact destination string in the evidence.

If a concrete simulator destination is unavailable, explicitly report that subset as `unverified (environmental)` and continue with source-level proof for the remaining requirements.

### Specific pitfalls for this domain

- A passing full test suite alone does **not** prove every user-facing onboarding promise. Confirm semantic gaps in the matrix:
 - onboarding routing (welcome → consent → permission → job select → route guidance → session)
 - persistence restore after relaunch
 - policy/availability affordance in Release-visible flows
 - reset safety while a session is starting/stopping
- Treat simulator-only audio HAL warnings as non-fatal noise unless assertions are failing; report separately as “environmental noise” so they do not become false negatives.
- For localization/catalog work, ensure `Localizable.xcstrings` changes preserve parity and that the completeness suite is run with the updated catalog.
- In review findings, separate **implemented-but-untested** from confirmed defects and from **not-wired** integration paths.

Record this as a short post-review note in (or equivalent) with:

- tested commands + outcome,
- matrix snapshot,
- top 3 unproven items (if any),
- and any repo-config or generated-file risks that remain.

## Consumer onboarding and UX review addendum

For onboarding plus consumer-facing UX changes, audit the feature as a complete launch-to-first-session path rather than approving the coordinator and unit tests in isolation. Build a matrix for each normative UX promise and trace it through persistence, app-root routing, the completed consumer surface, and the ViewModel/provider seam.

Prove separately:

- **Launch routing:** first launch enters onboarding; completed launch enters the consumer surface; reset is reachable from an actual user control, not only an uncalled coordinator method.
- **State persistence:** consent, selected job, and any required configuration survive relaunch or are deliberately re-established. A local `@State` selection applied once is not persistence.
- **Consent enforcement:** collecting and storing consent is insufficient; session start must either require the consent state or receive an explicit capability/configuration derived from it. Check restored-completed paths, not only the happy-path onboarding test.
- **Job-to-session continuity:** the selected consumer job must remain legible and actionable after onboarding. If the post-onboarding screen exposes raw mode/provider/audio controls instead, report the consumer UX seam as incomplete even when mapping tests pass.
- **Release policy wiring:** a policy/helper test proves nothing if production views and session-start logic never consult the policy. For `#if DEBUG` requirements, inspect the compiled source path and also search the release-visible view for advanced controls, provider selectors, credentials, models, and tuning controls.
- **Single authority for service availability:** do not duplicate policy facts as UI-only booleans (for example, `showsAdvancedSettings` or a separate `isAvailable` flag). Keep the service capability in `FeaturePolicy` and make start affordances, status/error presentation, and session-start validation derive from `canStartTranslation`/`serviceState`. Compile-time `#if DEBUG` should remain reserved for removing advanced controls from Release, not for creating a second availability authority.
- **Configuration-specific test compilation:** a Release app build can pass while Release XCTest compilation fails if tests use `@testable import` and the app module is built without `-enable-testing`. Treat this as a test-target configuration issue: verify Release policy behavior with a production Release build plus source/static inspection, or provide a pure injectable policy factory/test seam. Do not weaken the Release app’s optimization or infer Release behavior from a Debug-only test run.
- **Service availability behavior:** if release is expected to show an unavailable/not-configured service, verify the start affordance, error state, and provider validation agree. Do not accept a helper that reports `.notConfigured` while the UI still offers a misleading Start action.
- **Permission recovery:** denial must have a concrete recovery path, and returning from Settings or retrying must be traced through the real app lifecycle. A rationale/link test alone does not prove recheck behavior.
- **Live-configuration protection:** if a mapping API rejects changes while live, include an adversarial test that establishes the live state and asserts every relevant field remains unchanged; a pre-session mapping test is not sufficient.

Classify each item as **implemented and tested**, **implemented but untested**, **not wired**, or **confirmed failure**. This prevents overcalling a missing proof as a source defect while still exposing dead policy objects and inaccessible recovery controls.

When the requested simulator/device is unavailable, enumerate actual destinations, rerun on a compatible available destination, and record both the failed attempted destination and the successful exact destination. Do not stop at the first destination error or silently treat a different device as equivalent.

## Integration lessons for SwiftUI consumer flows

For SwiftUI consumer flows that combine persisted onboarding, job selection, release policy, and a live ViewModel, treat these as four separate seams and prove each one:

1. **Persistence after onboarding:** A persistence test that only covers onboarding completion is incomplete. Exercise a job change from the completed state, verify the backing store changes, then construct a fresh coordinator from that same store and verify the selected job is restored.
2. **Live ViewModel protection:** Do not prove live rejection with a pure configuration helper alone. Give the ViewModel an injectable/test-only initial live status, call the real `configureForJob` seam, and assert every relevant field (selected job, mode, direction, input route, output route) is unchanged.
3. **Authoritative release policy:** A policy object is authoritative only when production start logic gates on a capability such as `canStartTranslation`, rather than an incidental UI flag such as `showsAdvancedSettings`. Keep Debug and Release values semantically distinct (`developerConfigured` versus `notConfigured`) and test the compile-time branches honestly.
4. **Release affordance:** If Release cannot start the service, remove or replace every Start action in the compiled Release view. A disabled-looking or misleading Start button is not compliant; expose a non-actionable unavailable state and ensure the error/service state agrees with the UI.
5. **Binding side effects:** When a SwiftUI Picker changes a consumer job, apply the ViewModel mapping first and persist only after an `.applied` result. A live rejection must leave both runtime configuration and durable selection unchanged.

The focused suite should be followed by both Debug and Release generic-device builds and a concrete simulator test run. A successful Release build is necessary to prove `#if DEBUG` UI exclusion, while simulator tests prove runtime integration in the available configuration; neither replaces the other.

**Release test-target caveat:** If tests use `@testable import`, a Release app build may succeed while Release XCTest compilation fails because the app module was built without `-enable-testing`. Treat this as a test-configuration defect, not evidence that the production Release app is broken. Either configure the testable Release app/test target deliberately, or verify Release policy with a production Release build plus static/source inspection and run runtime XCTest coverage in Debug. Record the exact limitation rather than claiming Release tests passed.

**Reset/lifecycle seam:** Any production reset control that returns the app to onboarding or clears persisted session configuration must also account for an active ViewModel/provider/audio session. Trace reset through the real app root and lifecycle owner; guard reset while live or stop and await the session before changing onboarding state. The reset affordance should be serialized or disabled while shutdown is in progress so repeated taps cannot race teardown. A coordinator-only persistence reset test is insufficient if live work can continue after the UI returns to onboarding. Add an integration-level regression test or, when hardware/provider execution is unavailable, a lifecycle-focused unit test that proves the reset path awaits an idempotent stop operation before clearing state.

**Consent ownership seam:** Consent must have one authoritative owner across onboarding, persistence, and session startup. Do not keep a separate view-local `@State` copy that is only copied into the coordinator on Continue; bind the control directly to the coordinator's published consent and persist changes through the coordinator. Session startup must read the authoritative consent state, including after relaunch/restored-completed routing. Tests should cover toggle/persistence ownership and the restored-completed path, not only the initial onboarding happy path.

**Readability without testability regression:** When cleaning up onboarding code, prefer explicit multiline switches, bindings, and lifecycle helpers over compressed one-line declarations. Preserve compile-time Debug/Release policy boundaries and verify the generated build commands: `ENABLE_TESTABILITY` should remain Debug-only unless the task explicitly requires a separately configured Release test target. A successful Release app build is not Release XCTest evidence; record physical-device signing or simulator availability limitations separately from source correctness.

## Deterministic start-vs-stop/reset race proof

For any async session lifecycle where `start` can suspend before ownership is published (permission, authorization, provider connect, engine startup), treat pending start as a separate lifecycle phase from an already-live session. An `isLive` check alone is insufficient because a suspended start may observe idle state and resume after reset.

**Late-callback gating is a separate requirement.** Generation checks only at suspension boundaries do not protect against provider/audio callbacks that were queued before stop and execute afterward. Every callback closure installed for a session must capture that session's generation or identity, and the handler must discard the event unless it still matches the current generation/owner. Audit status, error, transcript, audio-output, interruption, and route callbacks independently. A stale provider event must not overwrite a newer session's status/error/transcript or send audio through the newer engine. The regression test should enqueue or hold a stale callback, stop the session, start a new generation, deliver the old callback, and assert the new session state and output remain unchanged.

Require a monotonically increasing session generation/token owned by the lifecycle owner:

1. Increment and capture a generation at the beginning of each accepted start.
2. Invalidate the generation before stop/reset teardown begins, not after awaiting cleanup.
3. Re-check the captured generation after every suspension point that can acquire or publish ownership.
4. Before assigning provider/audio ownership, starting the engine, changing live status, or reporting a start error, reject stale generations.
5. Stale continuations must clean only their local resources; they must not clear or stop resources belonging to a newer generation.
6. Keep the dependency injectable so tests can suspend permission/connect deterministically without hardware or network timing.

The regression test must hold the first start at a real async boundary, invoke stop/reset while it is suspended, verify the lifecycle returns to idle, release the boundary, await the original start, and assert that no provider/audio session is resurrected and no stale error/status overwrites the reset state. A test that only calls stop after start has completed does not prove this race.

## Bounded JavaScript/TypeScript schema-validator reviews

For recursive validators that accept `unknown` JavaScript values, audit the runtime object model separately from the JSON-schema logic:

- **Closed-object enforcement must cover all own properties.** `Object.keys()` sees only enumerable string keys. A non-enumerable own field can therefore bypass `additionalProperties: false` and branch-specific cross-outcome rejection. Test an inspect plan with a hidden `operations`/`verification` field and a nested object with a hidden unknown field. Use `Object.getOwnPropertyNames()` (and an explicit policy for symbols) when the validator promises closed objects; align required-field checks with the same own-property policy.
- **Plain-object semantics need an explicit boundary.** Decide whether null-prototype dictionaries are accepted as plain objects and test that decision. Reject inherited/class-instance fields without accidentally rejecting valid dictionary inputs unless the contract explicitly requires `Object.prototype`.
- **Caps need adversarial proof, not just source branches.** For `maxErrors`, create more failures than the cap and assert the returned array is bounded and deterministic. For `maxDepth`, exercise the deepest representable/schema-resolved path or a controlled recursive schema/reference fixture; a code branch with no triggering test is not proof.
- **Deterministic ordering must be locale-independent.** Avoid default `localeCompare()` for canonical error ordering; use a direct code-unit comparator or another explicitly locale-independent order, and include non-ASCII property/path cases.
- **Keep content-free errors bounded.** Error paths should identify the structural location without echoing values, formulas, secrets, or attacker-controlled oversized field names. Add adversarial tests for unknown keys and wrapper values.

## Release verification boundary

When the user explicitly accepts a **Release verification boundary**, record it narrowly and do not overclaim it. A successful Release generic-device/app build proves the production Release compilation path and `#if DEBUG` exclusion; it does **not** prove Release XCTest execution when `ENABLE_TESTABILITY=NO`, nor does it prove runtime lifecycle behavior. Run Debug XCTest on a concrete simulator for runtime evidence, run Debug and Release generic-device builds separately, and report the exact boundary in the verdict.

For onboarding/reset work, an awaited `stopSession()` is only sufficient if it covers all in-flight lifecycle phases. Audit the start path for suspension points before provider/audio ownership is assigned. A reset can observe `isLive == false` while `startSession()` is awaiting permission, provider connection, or engine startup, then the suspended start may resume after onboarding state has been cleared and recreate a session. Require an explicit start/stop generation or lifecycle gate: reset/stop must invalidate the pending start before awaiting cleanup, and the start path must re-check that generation before assigning ownership or starting audio. Add an adversarial test that suspends start during connection, invokes reset/stop, releases the connection, and asserts no provider/audio session is resurrected.

Keep this distinct from a normal “stop awaits provider cleanup” test: that test covers an already-owned live session, while the pending-start race covers work that has not yet been published into `isLive` ownership.

## Bounded renderer security, accessibility, and code-quality reviews

For a read-only review of concurrent Electron/React renderer work, capture the exact candidate and inspect changed names/focused diffs before broad source reads. Review untracked files explicitly. Trace every renderer readiness/consent/preflight boolean through preload and IPC to the final model, filesystem, network, or mutation sink: a renderer gate is UX, not authorization. Require a main-process re-check immediately before powerful work when the requirement is security-sensitive or the renderer state can become stale.

Treat text-only and optional-voice flows as complete user journeys, not state flags. A callback that prepares a packet and writes “ready” to a transcript does not prove a usable lesson; verify that the packet is rendered, learner input is accepted, progression/persistence is wired, and the path is reachable without the optional voice dependency. For async preflight/cancellation, construct the stale-result scenario (cancel old run, start new run, deliver old result) and require generation/request identity checks around every state update, not just cleanup of a request ref.

For accessibility, inspect the rendered path for route-entry focus, focus restoration, keyboard reachability, live status/error announcements, reduced-motion behavior, and approximately 44px actionable targets. Classify evidence honestly: static markup and pure helper tests prove structure/logic only; they do not prove clicks, bridge wiring, IPC authority, focus behavior, or races. A test script named `test:a11y` is not accessibility proof unless it exercises the relevant interaction semantics.

## Desktop tray/controller integration reviews

For WinForms, Qt, or similar background tray-controller candidates, review the production artifact and the UI-independent command seam separately. A passing cross-platform command suite does not prove the Windows UI is wired, renders the required fields, or exercises the production factory.

Use this checklist:

- **Interrupted-candidate baseline:** capture the current `HEAD`, `git status`, changed/untracked paths, and the authoritative task plan before judging scope. If the worktree is dirty or another agent may still be writing, keep the candidate boundary explicit and do not silently include later edits. Session history can locate the plan, but the plan/source files remain the evidence.
- **Production entry point:** verify the application output type is executable, `Program` creates exactly one tray context, and the default factory loads the manifest and constructs the real classifier/supervisor. A source-level `Program` call is useful evidence, but it is not a behavioral test.
- **Conditional compilation seam:** when tests remain cross-platform, inspect which files are linked into the test project and which WinForms sections are excluded by compilation symbols. Tests covering only the UI-independent portion cannot prove tray menus, status-window controls, disposal, or default wiring.
- **Status-model completeness:** every required visible value must have a real model field and a production data source. A label named “registration,” “gateway,” or “capability count” that is populated from a generic status string or hard-coded `Unavailable` is a confirmed compliance gap, not merely weak test coverage.
- **No-op provider detection:** trace the default constructor chain. Empty/null provider implementations may make injected unit tests pass while the shipped app always reports `Failed`/`Unavailable`; classify that as a production integration defect when the task promises operational status.
- **Diagnostics privacy:** distinguish character scrubbing/truncation from a fixed allowlist. Trace arbitrary classifier/supervisor `Code` and `Message` values into copied diagnostics and rendered error labels. Require adversarial tests that inject a secret/path into each channel and assert omission, not just a fixture test that places secrets in an unused manifest field.
- **Pending-action UX:** controller single-flight rejection and UI disabling are separate requirements. Track the actual tray/menu action controls and subscribe them to pending state; a `PendingChanged` event with no menu subscriber, or local action variables that cannot later be disabled, leaves the UI requirement unproved.
- **Verification boundary:** if the review is explicitly read-only, do not build or run tests; report execution as unverified. Separate confirmed source defects from missing Windows/manual evidence and from helper-only test coverage.

### Electron process-supervisor lifecycle addendum

For Electron tray apps that spawn and supervise child processes (plugin/agent launchers, PowerShell wrappers), apply the tray/controller checklist above plus these process-lifecycle gates:

- **Tested-but-unwired helper detection:** a passing unit test on a helper (bounded retry, queue, classifier) proves nothing unless production code calls it. Grep every production module for the helper import and for the lifecycle events it is supposed to emit (`retry-scheduled`, etc.). A `retries` counter that stays 0 forever plus a `runWithBoundedRetries` imported nowhere is dead code with green tests — report as a wiring gap, naming the dead event/import.
- **Inert persisted settings:** for every persisted setting rendered in the UI, trace the consume path in the main process. A `keepRunningInBackground` checkbox that is stored and rendered but never read means close-to-tray is unconditional and the setting is dead configuration. Check the read side, not just save/render.
- **Single-flight spawn guard:** `start()` must reject or atomically supersede when a child record already exists for that id. An unchecked second `spawn()` overwrites the children map and orphans the first child — it stays alive in the driver's handle map, is invisible to `stopManaged()`, and is never cleaned up. Test with a capturing driver: call start twice, assert `spawn` ran once (or the first record is stopped) and no orphan handle remains after stop.
- **Late probe result after stop/restart (stale generation):** an async `start()` that captures state before `await probe()` and applies `health-updated` against that captured state after stop/restart can throw the transition guard (e.g. `invalid transition from STOPPED to READY`) or paint ERROR over a clean STOPPED. Require generation/epoch gating on probe results; the regression test holds the probe, calls stop, releases the probe, asserts the final state is unchanged.
- **Awaited quit teardown:** `before-quit` firing `void supervisor.stopManaged()` executes only the synchronous prefix of the async loop — with N children, only the first stop runs before process exit. Require an awaited teardown seam (or synchronous stop calls) and assert every spawned handle is stopped before exit. On Windows, killing a `powershell.exe` wrapper does not kill the plugin it launched; state tree-teardown scope explicitly.
- **Windows-native acceptance boundary:** packaging targets (NSIS) and `setLoginItemSettings` wiring in source are not Windows-native acceptance. If the README defers tray/login/installer checks to a Windows host, classify that contract row as unverified (environmental), not failed — but require at least a documented smoke checklist or script so the deferral is actionable.
- **Read-only evidence boundary:** `npm test` and `tsc --noEmit` are non-mutating and safe in read-only reviews; `npm run build`/`package` rewrite gitignored generated dirs (`dist/`, `release/`) — skip them and report the boundary, or run only with explicit permission.

## Electron packaging and release-readiness reviews

For non-Electron installer packaging (PowerShell side-by-side version contracts, manifest/hash validation, atomic pointer publication, rollback/reapply safety)

For Electron packaging commits, treat the packaged application—not the source tree—as the artifact under specification review. Build a requirement matrix covering identity, platform targets, clean-checkout icons, stable `userData`, OS credential storage, license/SBOM scope, signing/notarization, packaged smoke, architecture selection, installer lifecycle, and CI artifact publication.

Apply these gates:

- Reconcile `package.json` with the lockfile root and packaging tests. A dependency moved between `dependencies` and `devDependencies` without a regenerated lockfile is a clean-install blocker; a test asserting the wrong placement is an immediate canonical-suite failure.
- Trace license and SBOM scope to the shipped runtime. `--production` and `--omit dev` omit Electron when Electron is a devDependency, even though electron-builder bundles the Electron runtime. Require Electron/runtime notices in both outputs and fail closed if generation fails.
- Start from the committed tree. Ignored generated icons, license outputs, SBOMs, or unpacked app directories are not evidence that a clean CI checkout can package successfully. Verify each CI OS can create every icon required by its builder configuration.
- Treat signing/notarization as an executable conditional path, not documentation. Check hardened runtime, certificate inputs, Apple notarization inputs, and actual GitHub Actions secret-to-environment mappings. A comment naming `CSC_*`/`APPLE_*` variables is not wiring.
- Require packaged smoke to fail when its executable is missing, select the host-compatible macOS architecture, and clean up on timeout. Smoke should prove startup, preload, root UI, teardown, and credential/user-data isolation; source-string tests only prove structure.
- Do not accept docs as proof of install/upgrade/uninstall isolation. Exercise installer lifecycle or classify that gate as unverified. For `upload-artifact@v4`, require unique names across matrix jobs or a deliberate merge job.

### Additional Electron acceptance traps

For a final read-only packaging acceptance review, add these checks rather than trusting structural tests or a green local run:

- **Clean-checkout generated outputs:** if a packaging generator writes into an ignored directory such as `third-party-licenses/`, prove it creates the directory itself. An imported-but-unused `mkdirSync` and a locally pre-existing ignored directory are not evidence; use `git ls-tree`/a clean-tree mental model and inspect the first write path.
- **Exact runtime identity in every claiming artifact:** require an exact component name or package URL for shipped Electron in the SBOM *and* license inventory. A fuzzy `includes("electron")` assertion can pass on `electron-to-chromium` while the actual `electron` runtime is absent. The generator itself should fail closed, not rely only on a test. Re-run each generator to an isolated temporary output when repository writes are forbidden, then inspect the component list.
- **Dependency-scope fidelity:** compare the package-manager manifest's scoped direct `devDependencies` against the inventory classifier without stripping `@scope/`. Check both direct scoped packages and transitive scope claims. CycloneDX output that includes all dev dependencies does not automatically contain usable `scope` metadata; do not describe it as scoped or shipped-runtime inventory unless the generated component fields prove that claim. If the inventory is intentionally overinclusive, label it explicitly as a full installed-dependency inventory.
- **Process-tree teardown on every smoke path:** “parent process exited” is not equivalent to “Electron and Chromium helpers exited.” Trace source smoke, unpacked CI smoke, and installed-installer smoke independently. Before deleting externally-owned `userData`, wait for or positively verify every helper; after force-killing a helper, wait/re-poll before deletion. Detection without kill/reap is not cleanup, and a later leak scan after deletion is too late.
- **Documentation must use the same path and identity contract as production:** compare manual smoke examples with the runtime validator and packaging output. Documentation must launch the actual installed executable rather than an installer, select or label the host architecture, and describe the real credential artifact (`safeStorage`-encrypted file plus OS key material) rather than inventing an app-specific Keychain entry.

When concurrent edits appear during the review, preserve the candidate SHA and use `git show <sha>:<path>` for the verdict; report later worktree drift separately rather than silently including it.

## Desktop speech-bridge / TTS lifecycle review addendum

For Electron speech bridges that combine a renderer session state machine, a main-process provider WebSocket, preload IPC, streaming PCM playback, and browser fallback, review the whole lifecycle rather than approving the transport class in isolation:

- **Final-event gating:** after a Hermes final clears the active turn but before playback completes, a second STT final can bypass an `activeTurn`-only dedupe guard. Accept finals only in the intended listening state, or route them through an explicit barge-in transition; test a final callback during `speaking` without a VAD callback.
- **Pending-start exact ownership:** an epoch guard prevents stale publication but does not by itself clean resources allocated after stop. Require main-process pending-start invalidation plus renderer-side exact cleanup for any late returned session ID, listener, or transcription generation. A stale attempt must never use broad cancellation that can hit a newer owner.
- **Awaited teardown:** a synchronous queue `cancel()` that invokes an async provider cancellation without awaiting it does not prove lifecycle safety. Trace `session.stop()` → queue → provider → preload → main → WebSocket, and require an awaited shutdown seam when stop must mean no old transport remains.
- **Transport-close proof:** awaiting an IPC cancellation promise is still insufficient if the main-process handler only calls `WebSocket.close()` and returns. `close()` may leave the old socket in `CLOSING`; ownership must remain held until `onclose` (or a bounded close timeout) before a new stream can be created. Test with a fake socket whose `close()` does not immediately become `CLOSED`; assert that handoff cannot create the next transport while the old one is closing.
- **Fallback boundary across both paths:** a `streamedBytes === 0` guard proves only the incremental path. Audit the legacy/full-buffer path separately: if playback has been handed to the audio backend and then rejects, do not replay the full utterance through browser fallback. Track the first scheduled/started playback boundary and add an adversarial post-start playback-failure test.
- **Exact stream identity:** streaming start/next/cancel must carry and validate both generation and request ID. Old cancellation must not cancel a newer stream, and a new start must invalidate the prior pending reader before creating another transport.
- **Bound before decode:** for base64 audio, validate canonical syntax and encoded-size bounds before decoding. A decoded-size check after `Buffer.from(..., "base64")` still permits oversized allocation and accepts malformed input as audio.
- **IPC error boundary:** provider-level catches are insufficient if the preload bridge exposes raw main-process rejection messages. Test failure propagation through the actual IPC handler and redact operational/provider details at the privileged boundary.
- **Fallback boundary:** browser fallback is allowed only before the first successfully scheduled audio chunk. Once any audio has been handed to playback, fail the utterance rather than replaying the complete text through a second provider.
- **Playback telemetry semantics:** do not emit `synthesis_complete` at Web Speech `start`; use a semantically correct completion boundary or omit the event for providers that do not expose it. Telemetry must remain metadata-only, bounded, and content-free.
- **Test meaningfulness:** structural regex tests and provider-only fakes do not prove Electron IPC authorization, window-close cleanup, pending cancellation, or renderer-to-main race behavior. Add adversarial tests at the actual seam, especially stop during `nextEvent`, final-during-speaking, stale cancel after restart, malformed/oversized audio, and handler-level error redaction.

 For final candidate-review traps covering exact duplicate finals, pending-start ownership, awaited TTS shutdown, pre-decode base64 bounds, and browser telemetry boundaries, For dirty read-only Electron multi-provider audio reviews, see for exact provider headers, cross-provider backpressure, aggregate SSE/PCM bounds, terminal reader cancellation, stream/full-buffer cancellation parity, and meaningful adversarial test coverage.

## Phase-1 fixture-corpus and plan-contract reviews

When reviewing an implementation plan whose Phase 1 deliverable is a synthetic fixture corpus plus hygiene tests, treat the corpus contract as the artifact under review—not as a runtime parser implementation.

1. Capture the candidate SHA, parent SHA, branch/status, and exact changed paths before reading semantics. If the worktree is dirty, use `git show <candidate>:<path>` for candidate evidence and report later drift separately.
2. Read the repository guidance and canonical schema/tool definitions before judging fixture semantics. Distinguish a future `WorkbookPlan` contract from the current direct tool schema; do not reject a fixture solely because a planned normalized operation intentionally differs from today's adapter name or argument nesting.
3. Build a coverage matrix from the normative list: exact fixture count, every named failure/acceptance class, both transports, metadata fields, provenance, sensitive-data hygiene, and explicit non-goals. Verify representative fixtures semantically, not only by filename or `failureClass`.
4. For accepted transport fixtures, inspect the envelope shape and nested payload. A transport enum alone is not proof that an “accepted XML fallback” or OpenAI tool-call case actually represents the claimed envelope. Flag contradictory descriptions/notes and cases that combine more drift than their description admits.
5. Inspect the loader's test meaningfulness. `JSON.parse` in `beforeAll` is valid evidence for fixture JSON validity, but structural corpus tests must not be presented as proof of parser/kernel execution. Check for `.skip`/`.todo`, vacuous assertions, and inventory filters that could omit in-scope artifacts.
6. Recompute the committed manifest independently from raw fixture bytes: exact sorted file list, each SHA-256, and the aggregate algorithm. Confirm the manifest has no timestamp or forbidden transport and no extra/missing entries.
7. Treat TDD recovery evidence separately from final green evidence. A controlled mutation should make the old candidate fail a contract assertion, and the candidate must then pass focused/full tests plus static/type/diff gates. If dependencies are unavailable in the review environment, do not install or fabricate a rerun; use supplied controller output and independently verify deterministic static/hash evidence, labeling local execution unverified.

### Independent Phase-1 code/test-quality gate

After specification compliance passes, run a separate quality review before approving a fixture corpus. Keep this review distinct from deferred Phase-5 runtime behavior, but do not treat "hygiene-only" as permission for semantically vague fixtures or vacuous structural tests:

1. Inspect accepted transport fixtures beyond their enum labels. An OpenAI case must expose the expected `tool_calls`/function envelope and a parseable plan payload; an XML/native fallback case must contain either the actual XML/native envelope or a clearly documented structured representation whose shape is asserted. A field named `xml_fallback` alone is not proof of XML transport. The OpenAI test must actually parse the argument string and assert the accepted normalized-plan shape; checking only `typeof function.arguments === "string"` leaves malformed accepted payloads unproved. Scope parseability assertions to accepted cases so intentionally malformed/rejected fixtures remain meaningful.
2. Run an adversarial transport mutation independently of the manifest: replace an accepted OpenAI argument string with malformed JSON and replace an XML/native wrapper with an arbitrary object while preserving metadata. The structural tests must fail for the semantic reason, not only because a committed hash changed; a mutation that requires a deliberate manifest update is still useful for evaluating whether the corpus assertions catch the underlying drift.
2. Reconcile each fixture's description, failure class, expected disposition, and nested payload. A case must not claim a tool-name drift while only changing properties, or claim correct properties while using an alias. Do not combine multiple drift classes unless the description explicitly says so.
3. Ensure hygiene tests are JSON-aware. Regexes such as `/token[=:]/` do not match ordinary JSON keys like `"token":"..."`; check quoted keys and values deliberately. Validate metadata types and relationships, including accepted disposition versus `failureClass: null`, rather than checking only property presence. Treat a `toHaveProperty`-only check as insufficient even when the current corpus is valid: a controlled metadata mutation (for example, changing an accepted fixture's `failureClass` from `null` to a known rejected class) must be expected to fail without relying on a manifest hash mismatch. If the production test does not enforce these relations, report the gap against the exact test lines; do not silently treat valid current data as proof of fail-closed hygiene.
4. Hash the actual bytes used by the manifest. Read fixture files as `Buffer` values for SHA-256 and separately decode them for JSON parsing; hashing a decoded UTF-8 string does not literally protect raw bytes.
5. Test meaningful structural invariants without claiming parser/kernel execution: envelope shape, nested argument syntax where applicable, required plan fields, and the intended malformed/accepted distinction. A non-null `modelOutput` object plus a matching manifest hash is insufficient.
6. Report controller-supplied RED/GREEN and full-suite evidence separately from independently executed static/hash/diff checks. In a read-only review, do not modify fixtures or regenerate the manifest to make a test pass.

## Candidate-bounded decisive final reviews

When reviewing a named candidate commit in a read-only session, establish and preserve the review boundary before judging behavior:

1. Capture `HEAD`, candidate SHA, parent SHA, branch/status, and changed paths before running tests or other tooling. Verify the candidate object directly; a later commit, concurrent agent, or generated dependency directory can change the worktree during review. If `HEAD` moves, do not silently switch candidates: continue with `git show <candidate>:<path>` / object-based scripts and report the boundary drift.
2. Treat `git status` as evidence, not as permission to clean up. Never delete an untracked `node_modules`, generated output, or another agent's artifact during a read-only review. Distinguish tracked-tree/index cleanliness from untracked environmental drift, and report when the requested clean-before/after condition could not be established.
3. Read repository guidance, the candidate diff, changed production files, their callers, and the relevant tests. Do not silently review generated `dist/` output or later edits as candidate evidence.
4. For fixture-corpus repairs, reconcile each fixture's prose and payload against the actual canonical schema at the production direct-tool seam and, separately, any future normalized plan contract. Do not infer that a model-visible tool name is canonical from a normalized operation name: for example, a planned `create_table` operation does not make a direct `insert_table` schema alias canonical. A fixture claiming one isolated drift must not silently combine tool-name drift with property drift; cite the schema and fixture lines and classify the contradiction as an open finding.
5. For async transport teardown, trace the complete ownership chain: request start → active transport registry → terminal/cancel path → socket close/onclose or bounded close timeout → caller/IPC Promise. Prove that replacement construction waits for the old ownership release, that stale callbacks are detached/ignored, and that terminal delivery cannot precede the required teardown boundary.
6. Check both streaming and legacy/full-buffer paths; do not infer parity from one implementation. Include exact-generation cancellation, completion/error/cancel single-settlement, pending-start supersession, timeout shutdown, and pre-first-audio fallback behavior in the matrix.
7. If the user explicitly forbids build/test execution, remain read-only: use source, diff, static checks, and test inspection as evidence, label runtime verification unexecuted, and do not claim tests pass.
8. For any API-backed create/write followed by read-back verification, audit the post-side-effect error boundary separately from ordinary request failure. The created identity must be captured before verification, and transport, decode, malformed-shape, mismatch, and local-persistence failures after the write must converge on a created-unverified result that preserves the returned identity. Do not assume catching the client’s usual `RuntimeError` covers `JSONDecodeError`, invalid UTF-8, `null`, list-shaped, or otherwise malformed successful responses. Add adversarial seam tests for at least one transport failure and one malformed successful response; assert both the distinct status/exit contract and identity output, with no automatic retry.
9. For a decisive final verdict, report only `PASS` or actionable `HIGH`/`MEDIUM` findings with exact file:line ranges. Omit style and low-severity observations. Keep the summary concise while naming the unverified execution boundary.

## Multi-provider Electron audio review lessons

When reviewing a multi-provider Electron voice feature, audit the direct/full-buffer TTS IPC path separately from the renderer streaming path. A coordinator may internally track `{generation, requestId}` while the public `tts:cancel` API still accepts only `generation`; that is not exact identity safety. Trace `synthesize → collect → cancel → transport teardown` end to end, and add a same-generation stale-cancel test where request A cannot cancel newer request B.

Treat provider setup-frame sends as a distinct start failure path. `socket.send()` in `onopen` can throw synchronously before the session is marked ready; it must immediately enter the normal redacted fail/close/settle path. A start timeout technically bounds the promise but is not prompt lifecycle correctness. Test setup-send failure separately from post-ready audio-send failure for every realtime provider.

Renderer credential-status booleans are UX preflight only, never authoritative authorization or readiness. If the selected provider can change or its credential can disappear after the renderer check, require an authoritative main-process preflight before allocating session resources. Trace the missing-credential error through preload and the renderer state machine; fixed IPC redaction must still leave a clear actionable state rather than silently returning to listening. Add a negative test for each selected provider with no credential.

For SSE/parser bounds, reject an oversized incoming decoded transport chunk before concatenating it into parser state. Checking `Buffer.byteLength(buffer)` only after `buffer += chunk` permits a transient allocation beyond the declared bound. Test both aggregate multi-chunk overflow and a single oversized chunk.

User-facing labels containing “fallback” require a semantic audit whenever automatic provider fallback is forbidden. Rename compatibility display/audio-mode labels so they cannot be mistaken for a secondary provider or browser voice path, and add a source/UI regression assertion for the forbidden wording.

### Cross-provider TTS handoff gate

When the main process caches one TTS session but permits the selected provider to change, inspect the provider-switch branch separately from same-provider replacement. A synchronous `dispose()` that launches asynchronous WebSocket close or HTTP reader cancellation without returning an awaited promise does not release transport ownership. The replacement provider must not be constructed until the old transport has reached its close/reader-cancellation boundary; otherwise a delayed close can leave two active transports and stale callbacks during handoff. Require a delayed-close fake test that starts provider A, holds teardown, requests provider B, asserts B is not constructed, releases A, then asserts B starts.

**Pending cancellation is a separate handoff invariant.** A transition queue that serializes `start` and `dispose` does not automatically make `cancel` safe. If provider A is still disposing and provider B's start is queued, a direct `cancel(B)` may inspect A as the current owner, become a no-op, and allow B to be constructed after cancellation. Track pending request identity and either serialize cancellation with the transition or atomically invalidate the queued start before teardown completes. Add an adversarial test that holds A teardown, queues B, cancels B, verifies B is never constructed or started, then releases A.

**Pre-reader HTTP ownership must be tracked.** Aborting a fetch and returning from disposal when no body reader exists does not prove the old request is gone. Retain the pending `open()`/fetch promise and, if a response arrives after supersession, await or explicitly bound body-reader cancellation before releasing the transport slot. Otherwise the replacement can start while the old fetch later installs a reader. Reader cancellation itself also needs a deliberate liveness policy: either await it with a tested bounded timeout or document why it is guaranteed to settle; an unbounded await can permanently block provider handoff.

**Coordinator cancellation must interrupt provider start, not only transport teardown.** A bounded `dispose()`/`cancel()` is insufficient when a serialized provider coordinator is awaiting `session.startStream()`: if that start awaits a non-cooperative HTTP open promise, the coordinator transition remains blocked forever and the queued cancellation/dispose operation never runs. Review the start/cancel interleaving at the coordinator boundary, including cancellation before the lifecycle publishes its active request. Require one of: a start promise that settles on cancellation, an explicit cancellation race owned by the coordinator, or a deliberately non-blocking start with late-response cleanup. A direct lifecycle test that proves disposal returns while `start()` remains pending does not prove production handoff safety.

**Final non-cooperative HTTP review gate.** Verify separately that the coordinator's serialized transition covers provider selection/teardown but does not await the provider's non-cooperative start; that pending request identity is registered before the first suspension and atomically invalidated by exact cancellation; and that the provider lifecycle bounds both open settlement and reader cancellation. Trace the late-response path after the bound: it must cancel an uninstalled body/reader, reject stale sink callbacks by stream identity, and avoid installing a replacement-owned reader. For queued-completion cancellation, inspect the lifecycle directly—not only the outer coordinator—and require cancellation to discard queued PCM and terminal completion while preserving a newer exact identity. Use deferred open/reader fakes and a delayed provider handoff; fixed sleeps or a test that only checks the cancellation flag are insufficient.

**Terminal cancellation parity must be checked across transports.** If a provider can queue audio before publishing completion, exact cancellation after completion must discard queued audio and suppress the terminal event, matching the established transport contract. Do not rely only on an outer coordinator’s cancelled-request guard; test the provider session/lifecycle directly as well, because direct or future callers can otherwise observe stale PCM after cancellation.

Before finalizing:

- [ ] Every normative clause has a matrix row.
- [ ] Every claimed pass cites production evidence and a meaningful test.
- [ ] Test helpers were inspected for vacuous synchronization.
- [ ] Integration parity was checked at the caller seam, including interruption and failure paths.
- [ ] Consumer onboarding was traced through persistence, app-root routing, completed UX, consent enforcement, and reset reachability.
- [ ] Release/debug policy was verified at the actual UI/session seam, not only by helper tests.
- [ ] Persisted post-onboarding mutations were tested across a fresh coordinator instance.
- [ ] Live ViewModel integration was tested against real state mutation/rejection, not only pure mapping helpers.
- [ ] Release builds were inspected for non-actionable unavailable affordances when the service is not configured.
- [ ] Implemented-but-untested and not-wired behavior are distinguished from confirmed failures.
- [ ] Untracked, duplicate, or unreferenced changed artifacts were checked.
- [ ] Build/test limitations are explicit, including exact fallback destinations.
- [ ] Findings have exact paths/lines and concrete scenarios.
- [ ] Verdict is clear and appears before details.
## Public support files

- `references/amended-commit-rereview.md`
- `references/cross-repository-contract-reconciliation.md`
- `references/ios-simulator-triage.md`
- `references/late-callback-generation-gating.md`
- `references/load-bearing-assumption-spikes.md`
- `references/milestone-vs-product-completeness.md`
- `references/spec-compliance-review.md`
- `references/start-stop-generation-race.md`
- `references/typescript-validator-adversarial-review.md`
