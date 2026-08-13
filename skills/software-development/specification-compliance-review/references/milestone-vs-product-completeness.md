# Milestone Acceptance vs Product Completion

Use this when a tested desktop build is described as “operational,” “accepted,” or “complete,” but the product was developed in milestones or from a working prototype.

## Core distinction

A milestone can be fully accepted while the product remains incomplete. Native launch, clean synchronization, and green tests prove only the candidate’s implemented scope. They do not prove parity with the original product specification or prototype.

## Audit sequence

1. Freeze the exact candidate SHA and identify which milestone(s) it claims.
2. Read the complete behavioral specification and visual/interaction prototype.
3. Inventory every visible prototype control and every normative specification clause.
4. Trace each item through the production path:
   UI → controller/state → platform adapter → privileged/native command → persistence/platform effect → relaunch → test → native evidence.
5. Classify each item as:
   - COMPLETE AND VERIFIED
   - PRESENT BUT DEFECTIVE
   - PLACEHOLDER
   - ABSENT
   - EXTERNAL GATE
6. Keep milestone acceptance and whole-product acceptance as separate verdicts.
7. If implementation will proceed in batches, finish the read-only matrix first and stop. Each later batch should consume a bounded subset of matrix IDs and return updated evidence for those IDs.

## Common traps

- A shortcut launching the expected executable proves path correctness, not feature completeness.
- A database table or type does not prove user-reachable CRUD.
- Prototype-only controls must be distinguished from normative requirements, but user-confirmed expectations become explicit requirements.
- A backend path with no production UI is not complete.
- A rendered control with no persisted/native behavior is a placeholder.
- A test named after a feature is not evidence until its setup and assertions reach the production seam.
- “External gate” is reserved for genuine credentials, signing, payment, permission, publishing, or unavailable physical interaction—not unfinished engineering.
- Default behavior matters: an idle animation may correctly stop in an event-driven mode, while the continuous option can still be missing.

## Batch handoff format

For a phase prompt, include:

- authoritative checkout, baseline SHA, spec, and prototype;
- explicit read/write boundary for the phase;
- exact included requirement IDs;
- pre-write writer/worktree checks when mutation is allowed;
- RED-capable tests and native acceptance for the batch;
- data-protection and publication boundaries;
- output artifact path and verification;
- a hard stop after the requested phase.

Do not send the entire remaining campaign when the user asks for one phase. Provide only that bounded phase with enough context to run independently.

## Reporting language

Prefer:

- “The shortcut is correct; the installed milestone is incomplete against the full product plan.”
- “Milestone 2 acceptance: PASS. Whole-product acceptance: FAIL/NOT YET REVIEWED.”

Avoid:

- “Operational” or “complete” without naming the accepted scope.
- Treating synchronized clean trees as product-completeness evidence.
