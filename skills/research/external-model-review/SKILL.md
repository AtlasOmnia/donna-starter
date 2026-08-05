---
name: external-model-review
description: external-model-review — Run reproducible independent reviews of plans, architectures, major content, and release candidates through named external models; preserve provenance, verify findings against source, and amend artifacts safely.
version: 1.0.1
license: MIT
platforms:
- macos
- windows
metadata:
 hermes:
 tags:
 - review
 - critic
 - openrouter
 - provenance
 - plans
 - architecture
 - verification
 related_skills:
 - multi-model-brainstorming
 - grounded-specification
 - plan
---
# External Model Review

## When to use

Use this skill when the user asks a named external model or provider to:

- critique an implementation plan, architecture, specification, major article, README, or release candidate;
- pressure-test a consequential decision;
- provide an independent spec/security/quality pass;
- review something through OpenRouter, Claude, Gemini, Fable, or another specific model;
- revise the original artifact after the critic pass.

This is a review workflow, not general brainstorming. Load `multi-model-brainstorming` instead when the goal is divergent idea generation across several models.

## Core rule

The external model is an independent critic, not an authority. Preserve its exact output, then verify every material finding against the source artifact, repository, and authoritative platform documentation before changing anything.

## Workflow

### 1. Establish the review target

- Read the complete canonical artifact.
- Capture the relevant source/repository evidence and constraints.
- State whether the request is critique-only or critique-plus-amendment. If the user says “revise,” amend the canonical artifact after verification while preserving the original in the review artifacts.

### 2. Discover and pin the model

- Query the provider’s live model catalog for the exact current ID.
- Prefer a pinned model/version over a moving `latest` alias when reproducibility matters.
- Never infer availability or version from memory.
- Preflight credentials without printing them.

### 3. Build a rigorous critic prompt

Require:

- a decisive verdict;
- blocking findings with severity;
- concrete corrections and closure tests;
- architecture/trust-boundary analysis;
- migration, compatibility, rollback, performance, accessibility, privacy, and live-acceptance review where relevant;
- explicit separation of facts evident from the supplied material versus model judgment;
- no claims that files were saved or external actions occurred.

### 4. Preserve provenance

Save:

- exact prompt;
- credential-free request payload;
- raw provider response;
- rendered critique;
- requested/returned model IDs;
- provider permaslug/version and route when available;
- response ID and finish reason;
- token usage and reported cost;
- checksums for provider artifacts.

A non-empty answer with a terminal finish reason is required. If truncated, preserve the partial response and run a narrowly scoped continuation with separate provenance. Aggregate prompt/completion/total tokens and reported cost across every call rather than reporting only the first response. After adding finding-verification and review-summary artifacts, regenerate the checksum manifest and verify every listed artifact; a checksum set created before closeout files exist is incomplete.

A reviewer that reads the target and surfaces a source-supported defect but stalls, times out, or exits before a verdict is **not PASS**. Preserve the partial transcript and independently verify the finding. If valid, repair it through one bounded writer, then launch a fresh changed-files-first review against the new exact SHA. Do not repeatedly resume a large degraded review context just to obtain a ceremonial verdict; one narrow continuation is the limit, after which replace the reviewer.

Checksum success proves byte integrity, not report truth. Verify relative-path manifests from their artifact directory, parse every JSON file, recompute hashes quoted inside reports/metrics, structurally compare the submitted schema/tool payload with the preserved artifact, and reconcile model/finish/tool-call/usage/cost fields against the raw response. If the delegated package contains stale internal claims, preserve it unchanged and add a separately checksummed controller correction overlay.

### 5. Source-verify every finding

Classify each blocking finding as:

- **ACCEPT** — supported by source evidence;
- **PARTIALLY ACCEPT** — valid underlying risk, but some claim is already handled, overstated, or mechanism-dependent;
- **REJECT** — contradicted by source or authoritative documentation.

Record exact file/line or primary-source evidence. For security and orchestration reviews, also verify the live deployment principal boundary and failure semantics before accepting recommendations about ACLs, sandboxes, profile isolation, or fail-closed hooks; logical profiles may share one OS user, and blocking-hook exceptions may be caught by the framework. Use the framework's exception handling. Do not reproduce an existing security control merely because the critic failed to notice it; add regression coverage for the new surface instead.

### 6. Amend the canonical artifact

When amendment is requested:

- preserve the original in the exact critic prompt/raw artifacts;
- add a revision-basis note linking the review directory;
- translate accepted findings into tasks, tests, state rules, gates, and rollback boundaries;
- retain sound architecture rather than redesigning for activity’s sake;
- place feasibility spikes before production work when a platform assumption is unproven;
- build replacement paths before irreversible migration or secret deletion;
- keep every commit boundary green;
- run a stale-assumption search after editing.

### 7. Verify and report

Verify:

- revised artifact exists and is internally consistent;
- stale rejected assumptions are absent;
- review artifacts contain no credentials;
- model/version/finish/usage/cost are recorded;
- no source or release action occurred beyond the requested scope;
- live branch, HEAD, and complete status are re-read after the critic exits—a disjoint read-only critic can coexist with an authorized source controller, so the implementation baseline may advance even when the critic made no out-of-scope changes.

Report the verdict, accepted/partial/rejected counts, key amendments, artifact paths, and whether implementation can begin or must start with a feasibility gate.

## Planning-specific quality checks

For implementation plans, explicitly inspect:

- global state versus operation-level permission overlays;
- transitional-state deadlines and precedence;
- cross-context cancellation protocols (`AbortSignal` is not a wire format);
- component version skew and capability negotiation;
- legacy-user cohorts;
- irreversible migration ordering;
- measured cold/warm readiness budgets;
- rollback independent of slow app/store rollout;
- green tests at every commit boundary;
- live native acceptance rather than source-only confidence.

## Pitfalls

- Using a moving alias when a pinned model is available.
- Saving only rendered prose and losing raw response/usage/cost.
- Accepting a critic’s source claim without inspection.
- Treating every finding as equally valid.
- Amending the plan but leaving stale state names or old sequencing elsewhere.
- Deleting insecure legacy data before a replacement and guided repair path exist.
- Adding a duplicate security check instead of reusing and regression-testing the existing guard.
- Calling a response complete when `finish_reason` indicates truncation.

## Detailed references

- See when a named provider/model must amend a large artifact through a tracked Hermes run. It covers disjoint writer surfaces, runtime route proof, bounded patch contracts, partial streamed tool-call recovery, same-session retry limits, and artifact readback gates.

For large amendments, prefer bounded section replacements or a model-authored amendment patch over one enormous streamed `write_file` call. If a partial mutating tool call is dropped after a stream-idle timeout, verify the artifact remained unchanged and resume the same pinned-model session once with narrower output; never launch an overlapping writer or assume the incomplete call executed.
