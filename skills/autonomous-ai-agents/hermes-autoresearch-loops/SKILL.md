---
name: hermes-autoresearch-loops
description: 'hermes-autoresearch-loops — Karpathy-style autoresearch loops for Hermes: autonomous propose→test→keep/revert cycles for config tuning, infra hardening, skill improvement, and post-update safety checks.'
version: 1.0.0
---
# Hermes Autoresearch Loops

Karpathy-style autoresearch pattern adapted for our setup: give an agent a concrete environment,
a frozen evaluator, and a scalar metric; let it iterate autonomously via propose→test→keep/revert loops.
Used for config tuning, infra hardening, skill improvement, and post-update safety checks.

## When to use

Trigger on:
- “autoresearch loop” / “Karpathy-style loop”
- “self-improving agent” / “agent experiments overnight”
- “continuous validation after updates”
- “iterate on config/skills/scripts automatically”
- Adapting Codex, Claude, or other agent-loop patterns to Hermes (e.g., “how can I do this Codex setup on Hermes”)
- Any request to set up autonomous improvement on a bounded target with measurable outcomes.

## Core principles (from Karpathy’s 2024–2026 talks)

1) Context engineering:
 - What you put in the context window is your real design surface.
 - Tight, structured AGENTS.md/skills > clever prompt phrasing.
 - Use this skill when optimizing system prompts, skills, or delegation rules via experiments.

2) Autoresearch loop:
 - Agent edits code/config → runs short experiments → checks metric → keeps or reverts → repeats.
 - Human sets direction and constraints only; agent does the grind.

3) Decade of agents (jagged intelligence):
 - Models are strong but brittle; design for partial reliability, not perfection.
 - Enforce verification after external actions; break big tasks into small scopes with clear success criteria.

4) World models:
 - Maintain concise canonical reference docs so agents behave like they understand the environment.
 - Use this skill to iteratively improve those references via feedback loops.

5) Files over apps:
 - Small focused tools/scripts orchestrated by Hermes > monolithic “do everything” prompts.
 - Prefer scripted loops and cron jobs for recurring checks.

## How to set up an autoresearch loop (template)

Use this as the blueprint whenever we implement a new loop.

1) Define target:
 - A concrete, bounded scope only (repo, directory, config subset).
 - Examples in our environment:
 - Dashboard-backend tests and linting.
 - apply-patches.sh robustness after Hermes updates.
 - Model/provider performance comparisons for non-critical tasks.

2) Define metric(s):
 - Must be scalar and unambiguous. Examples:
 - Test pass/fail count.
 - Lint error/warning count.
 - Startup time or latency (e.g., hermes status response).
 - Config alignment check (0 mismatches = good).

3) Define constraints:
 - What the agent is allowed to change (e.g., “only scripts under ~/.hermes/scripts”, “no changes to safety procedures”).
 - What it must never touch without explicit human approval.

4) Implement loop:
 - Use dev profile via delegation for reasoning-heavy loops.
 - Karpathy's actual pattern is NOT cron-based — the agent runs a continuous LOOP FOREVER until manually stopped, not discrete scheduled runs. The human decides start time only; then it iterates autonomously without pausing to ask "should I continue?" Cron jobs are only appropriate when you want bounded windows (e.g., "run 2am-6am") and even then the loop itself is continuous within that window.
 - Each iteration:
 - Propose a small patch (config change, refactor, guardrail).
 - Run evaluator (tests, hermes status, alignment checks).
 - If metric improves/holds and no regressions → keep; else revert.

5) Logging:
 - Log only concise summaries of accepted changes and metrics. Avoid chatty justifications.

## Launching repository improvement loops

Use this pattern when the user names a worker profile and asks for repeated test-and-improve cycles on a code repository:

1. Honor the explicitly named profile; do not silently substitute the generic Dev profile.
2. Inspect the live Git state first. Start only from a clean tree unless the prompt explicitly identifies pre-existing changes that must be preserved.
3. Create a dedicated local branch for the experiment series. Keep accepted iterations as small local commits; never push, tag, publish, or release unless separately authorized.
4. Store controller prompts and loop logs under a local artifact directory such as `.hermes/`, then exclude that directory through `.git/info/exclude`. Do not modify the shared `.gitignore` merely to hide one operator's orchestration artifacts.
 - When using the reusable `hermes-autoresearch` harness, remember its concrete Git semantics: accepted changes are committed locally in the target named by `repo_path`, on whatever branch is currently checked out, with a message such as `autoresearch: accept trial N score=S`. The harness does not create a branch or push.
 - The harness records `runs/experiments.tsv` and `runs/experiments.jsonl`, then stages accepted trials with `git add -A`. Before the first trial, exclude `runs/` in the target repository—prefer `.git/info/exclude` for operator-local runs—so experiment output is not accidentally captured in accepted commits.
5. Treat an iteration duration such as “about five minutes” as a timebox for one hypothesis—not as a fixed sleep. Each iteration should select one problem, define an acceptance condition, test, patch, evaluate, and KEEP or REVERT.
6. Freeze the evaluator before the first edit. Record baseline commands and metrics, then rerun the same release gate for every accepted code change. Focused tests may guide an iteration, but they do not replace the frozen gate.
7. Run the worker as a tracked background Hermes process with completion notification. Explicitly prohibit the child from self-backgrounding or spawning a competing editing agent.
8. Process liveness and exit code are not completion evidence. Verify actual tool activity, a substantive loop log, Git commits/diffs, and evaluator output. If a bounded Hermes session reaches its turn budget, resume the same session against the same branch rather than launching a fresh worker that repeats discovery.
 - Diagnose timeout layers separately: the harness's `command_timeout_seconds` is the hard per-proposal/per-evaluator subprocess deadline; `max_seconds`, Hermes profile gateway/turn settings, terminal-tool timeouts, and an outer controller deadline are independent clocks. A healthy direct model smoke does not prove a repository trial can finish inside the harness deadline.
 - The reusable harness times out the configured proposal wrapper but does not itself guarantee that grandchildren spawned by that wrapper are terminated. A timed-out wrapper can therefore leave an orphaned `hermes --profile … chat` process that continues targeting the campaign checkout and contaminates later trials. Proposal wrappers must launch each agent in its own process group/session, enforce an internal deadline shorter than `command_timeout_seconds`, terminate then kill the whole group on timeout, and the controller must scan for exact campaign descendants before advancing or retrying.
 - Do not turn the profile name into an unnecessary global lock. A Hermes profile may host concurrent independent sessions; serialize writers by exact worktree and shared mutable resources, not merely by profile name. An unrelated writer in another isolated repository is not a checkout collision, while separate profiles still do not make overlapping writers safe in one checkout.
 - For the timeout recovery sequence, process-group wrapper pattern, fresh-ledger relaunch, and profile-versus-worktree concurrency boundary,
 - For review-only workers that enter startup/context-compression churn, first preserve the failed attempt and verify the source tree, then retry with process-scoped isolation (`--safe-mode` or `--ignore-user-config --ignore-rules`), explicit direct provider/model flags, restricted toolsets, and bounded line-range reads. Do not change the profile globally merely to rescue one campaign.
 - Safe-mode file tools may resolve repository-relative artifact paths from the user home rather than the subprocess `cwd`. Pass absolute paths for controller reports, salvage drafts, completion markers, and handoff artifacts.
 - If a worker reaches its turn ceiling after substantive inspection but before contract formatting, preserve its output as a slot-specific salvage source and use a fresh closeout-only session to verify cited ranges and emit the required marker/report. This is a retry of the same logical iteration, not a new hypothesis.
 - Apply the same standard at launch: a running Hermes PID proves only that the controller process started. Do not say the harness is configured, the baseline is complete, or iterations are underway until the expected config/log artifacts exist and show real harness or worker activity. Report launch state precisely: `controller started`, `harness initialized`, `baseline complete`, and `trial N active` are separate milestones.
 - A harness process may exit `0` even though the logical slot failed. Treat `best_score=None`, fewer completed trials than requested, evaluator rejection, a missing exact completion marker, or a task-lost-after-compaction response as an incomplete slot. Preserve the attempt and retry that same logical iteration; do not count it or advance campaign numbering.
 - When the user pastes a finalized campaign prompt as the next message, treat that as authorization to execute it—not as another request to rewrite or summarize it. Perform prerequisite checkout/Git/exclusion checks, launch the named profile through a tracked process, then verify the first substantive milestone before giving a progress report.
9. Keep controller artifacts out of commits, and finish or revert the active experiment before closeout so the branch remains coherent.
10. Do not rely on one agent invocation to remain continuous merely because the prompt says “loop forever.” If it completes one valid experiment and exits, put repetition in an external tracked controller while constraining each invocation to exactly one hypothesis and one clean closeout.
11. When switching the named worker profile, stop and verify the old controller first, then inspect the tree and loop log. The replacement profile must finish or revert any `pending` experiment before proposing another; never let two profiles edit the same working tree concurrently.
12. Cancellation must terminate the **entire campaign process tree**, not merely the parent shell/controller PID. A stopped controller can leave the harness, proposal wrapper, and active `hermes --profile … chat` child orphaned and still editing. Inventory children by target config/repository and exact worker command, stop only that campaign's PIDs, and verify no matching harness/proposal/worker remains. Never kill unrelated work merely because it uses the same profile.
13. After cancellation or profile replacement, reconcile from live evidence before relaunch: inspect accepted commits, TSV/JSONL rows, ignored iteration artifacts, current HEAD, and dirty changes. Preserve accepted gated commits unless the user explicitly requests rollback; finish or revert the one pending transaction. Archive the prior campaign's ignored logs/artifacts, clear the active run logs, and freeze a **new baseline at the retained current HEAD** so the replacement evaluator cannot accept a regression merely because it still compares against the original lower score.
14. Editing a config file does not change a harness process that already loaded it. Stop and verify the old harness before changing `max_trials`, profile commands, budgets, or evaluator inputs; otherwise the in-memory campaign can continue under the old settings while disk appears updated.
15. Treat Git state plus the durable loop log as the cross-profile handoff surface. Start a new session for the replacement profile rather than trying to resume a session owned by another profile.
16. A persistent parent controller does not emit completion notifications after successful child cycles because the parent remains alive. When reporting status, inspect the live controller, recent commits, clean/dirty Git state, and the durable loop log; explain this notification behavior so silence is not mistaken for inactivity. If per-cycle reports are required, add a separate read-only reporting mechanism rather than weakening the continuous controller. Process-supervisor completion alerts can also be stale or misleading when output is redirected; verify the OS PID/process tree and controller log before declaring a controller dead. Prefer keeping stdout attached (for example, pipe through `tee` with `pipefail`) so tracked completion remains observable.

For Office add-ins, include the repository's full tests, type check, production build, manifest validation, proxy/script compilation, and safe host smoke test when available. Separate automated verification from deferred live-host validation rather than claiming host integration from mocks alone.

### Overnight live-host add-in campaigns

When an autoresearch loop drives a live Office add-in while a separate model operates the host application:

1. Use a dedicated disposable workbook/document and an isolated campaign branch. Never point exploratory loops at personal, financial, payroll, claims, or other consequential data.
2. Keep four roles distinct:
 - persistent external controller;
 - application executor model connected to the live add-in bridge;
 - deterministic evaluator that reads host state and frozen command output;
 - bounded repair worker that handles one reproducible defect per invocation.
3. Require the host application, task pane, proxy/companion, machine-awake state, and live bridge/session identifier before the first trial. Treat reconnection as controller-owned lifecycle work: after a rebuild or add-in reload, obtain and verify the new bridge session before resuming.
4. Build a scenario corpus with explicit expected cells, formulas, number formats, tables, charts, comments, errors, and cleanup behavior. Record latency and recovery separately from correctness; do not collapse all evidence into an LLM-written score.
5. The executor and orchestrator must not grade themselves. Re-read the workbook through the bridge, inspect exact tool transcripts, and run the frozen repository gate. Screenshots are supporting evidence, not a substitute for workbook state.
6. Classify failures before editing: bad test expectation, model/executor mistake, bridge/session failure, unsupported host capability, or reproducible product defect. Only the last category opens a repair transaction.
7. A repair iteration may patch only the isolated branch, run focused RED→GREEN evidence plus the complete add-in gate, rebuild, reload the host integration, reconnect, and rerun the failing black-box scenario. KEEP only when both repository gates and live-host reproduction pass; otherwise REVERT.
8. Use bounded fresh worker invocations under the persistent controller. Cloud coding models such as an available Codex Spark route may outperform local models for repair/orchestration; local Qwen-class workers are useful unlimited-runtime fallbacks. Define quota/provider fallback before launch rather than changing models ad hoc mid-transaction.
9. Store concise JSONL/TSV plus a morning Markdown report: scenarios attempted, pass/fail counts, latencies, bridge interruptions, reproduced defects, accepted/reverted commits, deferred host checks, and exact external gates. Never push, publish, release, or deploy from the overnight loop without separate authorization.

For the complete cheap-model campaign controller—including cross-repository profile-slot queuing, the harness first-trial baseline pitfall, ignored completion markers, three-cycle dry-run gating, locked-host downgrade, and frozen test/build/audit evaluation—follow the controller steps in this skill.

### Finite multi-profile, multi-repository campaigns

When the user specifies a fixed iteration count across several profiles and repositories:

- make the total iteration/time arithmetic explicit before launch;
- run one repository/profile block at a time—never concurrent editors on one tree;
- inventory active Hermes children/controllers using the requested profiles **and** map each process to its exact checkout, mutable artifact paths, provider/account, and rate-limit footprint. A profile name alone is not an exclusive slot: unrelated sessions may run concurrently when their repositories and mutable resources are isolated and provider capacity is acceptable. Queue only on a real collision or measured capacity constraint; do not silently subtract unrelated profile uptime from the campaign’s nominal experiment time;
- keep the persistent outer controller profile-neutral (shell/Python or a different orchestrator profile) when the harness proposal command invokes a named worker profile. The controller should launch exactly one bounded proposal worker per campaign worktree at a time, but it need not wait for every unrelated session under that profile to exit. Avoid making the outer controller itself consume the same worker/model route continuously, because that creates needless provider contention and confuses ownership checks;
- start the per-iteration timebox when substantive repository inspection begins, not while waiting for a profile slot or compacting startup context;
- before freezing a command-output evaluator, validate every parser against the real captured output, including ANSI-colored summaries and baseline failures. Compare parsed pass/fail counts with the human-readable gate output, then persist the baseline. A JSON-shaped evaluator result is not trustworthy if its extracted metrics are silently zero or otherwise inconsistent with the underlying command output;
- give every child invocation an external deadline plus a liveness/progress check. A live PID and repeated `compacting context` output are not substantive progress. After a bounded grace period, stop only the affected child, preserve controller state, log the reason, and retry the same slot after the profile becomes free rather than accepting or advancing it;
- when profile rules, memory, plugins, or profile-scoped compression cause repeated startup compaction, preserve the failed attempt and retry the same logical slot with process-scoped isolation. Prefer `--safe-mode`, the smallest sufficient toolsets (usually `terminal,file`), quiet mode, and an explicit user-approved direct provider/model. Use `--ignore-rules` only when retaining the rest of the profile configuration is intentional. Both modes suppress automatic rule injection, so explicitly require repository AGENTS.md and specifications to be read from disk. Probe the exact profile/flags/provider/model with a tiny response before restarting a long block, and keep the substantive timebox separate from the larger startup/finalization deadline. Do not silently invoke a profile's configured compression provider when it conflicts with the user's provider policy.
- when matching an exact CI Node version, prefer an ignored campaign-local Node runtime prepended to `PATH`. Do not wrap the full gate in `npx -p node@VERSION -c` when project scripts may themselves call `npm exec` or `npx`, because the wrapper can create false baseline failures;
- for **review-only** campaigns, adapt the implementation transaction contract: preserve source HEAD/status, write ignored per-iteration artifacts with an exact COMPLETE/BLOCKED terminal heading, independently rerun the frozen gate, and require a consolidated final report. Do not require changed HEAD, commits, or accepted-patch markers when modification was explicitly forbidden;
- make review artifacts **artifact-first**: before broad discovery, each child creates the exact ignored iteration file with every required section as a pending skeleton and updates it continuously; final-synthesis children create both the iteration artifact and consolidated final-report skeleton first. This preserves evidence when context compaction or the turn ceiling interrupts closeout;
- treat review-artifact formatting as controller-owned bookkeeping, not a reason to repeat a completed audit: when exit is zero, the ignored artifact is substantive, the worker reported completion, and baseline HEAD/status remain unchanged, the controller may append a missing canonical heading and record that normalization. If the artifact is missing but the final worker log contains a substantive audit, reconstruct it only after independently validating retained findings against exact current line ranges and confirming the stated gates; label it as controller-canonicalized from that profile's output. Never synthesize findings from a vague or incomplete summary;
- reconcile and commit any pending prior iteration before campaign numbering;
- preserve dirty repositories on dedicated local campaign branches with secret-aware safety checkpoints;
- freeze baselines and treat pre-existing gate failures as recorded invariants that must not worsen;
- treat each logical iteration as one transaction across all retries: capture `iteration_start_head` once before attempt 1 and compare every retry against that immutable baseline; never recalculate the baseline after an earlier attempt may have committed the substantive change;
- require an ignored JSON completion marker plus changed HEAD, exact log heading, and clean tree for the first successful acceptance of an iteration; capture the iteration-start HEAD once before the retry loop and compare every attempt against that immutable baseline—never recompute the baseline after an earlier attempt may have committed;
- treat worker-written completion markers as advisory artifacts, not the authoritative transaction ledger: after each worker exits, the outer controller must verify clean tree, changed HEAD, one exact accepted/reverted heading, and independently rerun the frozen gate; every baseline-passing command must remain passing, while a baseline failure may only keep the same exit or improve to zero; the controller then synthesizes the canonical marker and state record itself, preventing marker omissions/schema drift from causing duplicate hypotheses;
- before deleting or replacing any retry marker, attempt salvage and log why it failed; if the canonical marker is absent, a controller may inspect one exact slot-specific fallback such as `.hermes/iteration-{global_id:03d}-result.json`—never glob arbitrary result files—and must canonicalize it only after counters, evidence, accepted/reverted heading, marker commit equal to current HEAD, and clean-tree checks all agree; on crash/retry recovery, allow salvage without a duplicate commit only when those invariants pass; canonical fields remain authoritative, while a narrowly recognized non-conflicting alias vocabulary may be normalized after verification; reject missing, conflicting, or ambiguous markers and never create a no-op commit merely to satisfy retry bookkeeping;
- persist atomic controller state and per-attempt logs so a long campaign can resume safely;
- when the user removes future scope mid-campaign, stop and verify the exact campaign process tree before editing the controller, reconcile the active transaction, archive removed-scope baseline/state rather than deleting evidence, derive all totals and prompt denominators from the retained repository/profile matrix, regression-test the reduced controller, and verify the resumed child cannot select removed work; see the retained campaign matrix and verify that removed work cannot be selected;
- for review-only iterations, require the worker to create an ignored artifact skeleton before broad inspection and update it continuously; tool-heavy profiles can exhaust their turn budget after producing a useful final summary but before writing the requested artifact;
- allow controller-owned salvage only when the worker exited successfully, the review output is substantive, exact findings are independently traced to current source, baseline HEAD is unchanged, and the production tree is clean; record the salvage explicitly rather than presenting it as worker-written;
- keep `campaign-state.json` controller-owned. If a worker nevertheless appends its own iteration record, deduplicate by iteration number and preserve the controller-verified record so a four-iteration campaign cannot report five completed records;
- checkpoint final verification **after each repository**, not only after the entire campaign: atomically save its frozen gate, spec/quality histories and PASS verdicts, final HEAD/branch, and verification timestamp before advancing. On restart, skip that repository only when the source tree is clean, current HEAD equals the saved final HEAD, the saved gate exists, and both reviews are PASS; any mismatch invalidates the checkpoint and reruns verification. This prevents a later repository BLOCK from discarding earlier PASS evidence or forcing needless repeated reviews;
- timestamp the consolidated final report at actual closeout, after all reviews and repairs—not when the final-verification phase begins. If an unpushed branch undergoes metadata-only identity normalization after review, require identical `HEAD^{tree}` and campaign commit count, rerun the full gate, and update state/report with the reviewed SHA, normalized SHA, invariant proof, exact remote SHA, and separate push/PR/merge/tag/release/deploy status;
- run final read-only reviewers in fresh detached Git worktrees under the campaign artifact directory, with safe mode and only the minimal `terminal,file` toolsets; never aim an untrusted review profile at the campaign branch itself, because it may spawn subagents, modify skills, or create diagnostic tests despite a read-only prompt; record the isolated worktree path/status, keep the source branch clean, and, when the source already has dependencies, expose them through an ignored symlink and smoke-test the isolated checkout rather than installing again;
- define final-review verdict criteria explicitly: BLOCK only for confirmed Critical/Important code defects or violations of tracked specifications/rules. Explicitly deferred live-host validation and an absent optional `AGENTS.md`/rules artifact are evidence gaps to preserve in the report, not invented requirements and not blockers by themselves. Never weaken this distinction to force PASS;
- converge by evidence rather than a fixed number of review cycles: preserve each review log immutably with commit/session/cycle, independently reproduce every real finding RED, verify the repair commit plus frozen gate and live audit output, and review a fresh detached worktree at the repaired HEAD until PASS; repair-agent summaries—including vulnerability counts and claims that other findings are false—are not evidence;
- independently gate every profile block and run final spec/quality review→repair→re-review cycles.

### Transitioning from review to implementation

When a review-only campaign becomes a repair campaign with a named profile:

- Do not send the entire audit and every severity tier to one long worker session. Split work into dependency-ordered phases that can each complete within one fresh context.
- Make each phase a local transaction: focused RED→GREEN evidence, complete gate, diff/untracked-file review, and local commit. Defer push until independent review and repair.
- Inspect the actual commit after every phase. Green tests and a confident worker summary do not prove production code uses the intended source of truth.
- Reject copied registries, lesson maps, policy tables, permission matrices, or version maps when an authoritative catalog exists. Require production imports from the canonical source plus a test that iterates every canonical entry.
- Resume a context-lost session once when it contains useful edits. If repeated compaction leaves a clean tree and no implementation, stop reusing that degraded context and launch a fresh narrower phase.

## Post-update live-runtime regression verification

When an autoresearch or self-check report identifies a Hermes runtime regression—especially context hygiene or compression—separate four states before proposing an update: (1) the upstream defect and fix history, (2) the checked-out source, (3) the already-running process, and (4) live post-restart acceptance. A passing source test does not prove the running gateway has loaded that source, and a restarted gateway does not by itself prove the next live compression event will succeed.

Use this bounded sequence:

1. Read the upstream issue/PR and identify the exact invariant, not just the symptom (for compression: original transcript preservation, session rotation or explicit in-place compaction, and a reduced token/message count when compaction is expected).
2. Inspect the installed version, Git `HEAD`, `origin/main` gap, and the exact source call site. Prefer `git blame`/`git log -S` to establish when the fix entered the checkout.
3. Inspect the live process and logs. Match the failure timestamp to the gateway PID lifetime; a warning from a pre-restart process is not evidence against corrected source.
4. Run the narrow regression suite with the project test environment (`./.venv/bin/pytest ... -q -o addopts=` when available). If the runtime environment cannot collect tests, record the actual blocker and use a working project environment rather than treating a system-Python failure as a product failure.
5. Restart only when explicitly authorized or when an existing supervisor has already restarted the process; then verify the new PID/start time and source load boundary.
6. Do not force `/compress` or manufacture a large production conversation merely to obtain live acceptance. Mark the result `source/test verified; live acceptance pending` and wait for the next natural event, unless a disposable isolated session is available.
7. Do not run `hermes update`, patch production code, or restart the gateway solely because an autoresearch report says a fix is likely upstream. First prove whether the fix is already present and whether the running process is stale; update only when the requested scope authorizes it.

## Reference implementations in this environment

- Post-update autoresearch check (infra safety):
 - Script: ~/.hermes/scripts/post-update-autoresearch-check.sh (user-local — verify it exists)
 - Purpose: After hermes update + apply-patches.sh, verifies:
 - Patches applied cleanly.
 - config.yaml vs .env alignment for provider/model via hermes-config-sync.sh.
 - hermes status has no obvious anomalies.
 - Wired into AGENTS.md as official post-update step (see “Running `hermes update`”).

- Config sync helper:
 - Script: ~/.hermes/scripts/hermes-config-sync.sh (user-local — verify it exists)
 - Purpose: Ensures .env matches config.yaml for HERMES_INFERENCE_PROVIDER and LLM_MODEL.
 - Used both manually (after model/provider switches) and inside the post-update autoresearch check to auto-correct desyncs when safe.

- AGENTS.md context engineering (Phase 0):
 - Tightened profile delegation rules, skill-first policy, verification-after-action rules, anti-collapse memory/skill update rules.
 - Aligns with Karpathy’s “context engineering” and “world model hardening.”

## Private local-model benchmark adapters

When using the public harness to compare models or inference/load settings on a private local server:

- keep the public harness provider-agnostic;
- place endpoint-specific adapters, model inventories, candidate matrices, prompts, settings, and results in a separate local-only repository with no remote by default;
- use a read-only inventory probe and full dry-run campaign before any model load or inference;
- capture the runtime instance identifier returned by model load and unload that exact instance in a `finally` path;
- freeze a quality-first evaluator, retain latency/TTFT/throughput as separate metrics, and avoid early-stop settings when every matrix candidate must run;
- verify both repositories afterward: the private repository clean/no-remote and the public harness clean/unchanged.

## Paired agent/tool-router evaluation

When evaluating dynamic tool routing, treat the autoresearch harness as the experiment controller—not the benchmark itself. Build a frozen evaluator first, then let the harness propose, score, keep, or revert policy changes.

Required evaluation pattern:

1. Use an isolated Hermes test profile, never the production/default profile.
2. Run paired prompts against the same model and profile context:
 - router enabled;
 - full-tool baseline via a process-scoped bypass, not a persistent config edit.
3. Use fresh sessions for each case and record the session IDs.
4. Measure first provider-request input tokens from live Hermes logs. Do not use database `input_tokens` as schema-footprint evidence because that field can reflect cache-adjusted/billable tokens rather than the complete request.
5. Score both prediction and execution:
 - required-toolset recall;
 - exact route precision;
 - actual tool completion;
 - final-answer checks;
 - recovery use and errors;
 - first-request token reduction;
 - latency.
6. Keep a frozen safe-core corpus separate from cost-bearing or interactive tools such as image/video generation, delegation, approvals, and clarification.
7. Keep public evaluator fixtures portable: use placeholders, environment variables, `Path.home()`, or repository-relative commands rather than workstation-specific absolute paths. Ignore raw session/run bundles and publish curated aggregate reports.
8. When a miss still succeeds through `request_toolset`, record it as a routing miss and a recovery success—not a total failure.
9. Rerun the complete fixed corpus after every repair. Synthetic policy tests are useful, but live paired Hermes sessions are the release gate.

## Public trial-contract packaging

When publishing a reusable autoresearch harness that can invoke arbitrary agents:

1. Put portable proposal-agent rules in a public template such as `contracts/trial_contract.md` or `templates/TRIAL_CONTRACT.md`, not in the root `AGENTS.md`. A root `AGENTS.md` governs agents developing the harness checkout; it does not automatically govern agents launched inside a separate target repository.
2. Keep private orchestration policy in this local skill: named profiles, local models/endpoints, context-window tuning, workstation paths, and campaign recovery procedures do not belong in the public contract.
3. The public contract should require exactly one hypothesis, explicit allowed paths, no staging/commit/push by the proposal agent, uncommitted changes left for the evaluator, nonzero exit when blocked, and no second hypothesis in the same trial.
4. Do not claim the harness supplies metadata it does not export. The reusable harness exports `AR_TRIAL`, `AR_PHASE`, `AR_REPO_PATH`, and `AR_PREVIOUS_SCORE`; its configured path allowlist is an enforcement control but is not automatically injected into the agent prompt. A proposal wrapper must receive an explicit allowed-path representation and document that it must mirror `allowlist_relative_paths`.
5. Invoke configurable agent commands without a shell. Prefer a JSON argv prefix such as `AGENT_COMMAND_JSON=["hermes","chat","-q"]`, validate it as a nonempty string array, append the assembled prompt as the final argument, and call `subprocess.run(..., shell=False, cwd=repo_root)`. Propagate the child exit code. Do not use `bash -c "$AGENT_COMMAND"` or interpolate objectives into shell source.
6. Require a nonempty objective and allowed-path input instead of silently inventing defaults. Treat objectives containing spaces, backticks, `$()`, semicolons, or environment-variable syntax as inert prompt data.
7. Verify every documented CLI invocation against the live command help before publishing. For Hermes one-shot prompts, use `hermes chat -q <prompt>`; do not invent subcommands or flags based on another agent CLI.
8. Use TDD for the wrapper. Tests should cover prompt assembly, exact argv behavior, missing objective/scope, malformed or non-string command JSON, shell-metacharacter inertness, child exit-code propagation, and README examples. Run the complete harness suite afterward.
9. Before the first public push, independently inspect the actual diff and documentation in addition to running tests. A mocked wrapper test can pass while the README advertises a nonexistent command, so test success alone is not publication evidence.

## Pitfalls

- For finite campaigns, `max_trials` applies to one harness invocation, not the accumulated campaign. Re-running the harness appends another block to the same logs unless the controller uses a fresh run directory or explicit run ID. Before retrying, reconcile the prior block and preserve it separately; never report the last block as the entire requested campaign.
- Do not place Markdown/backticks or agent prompt bodies inside double-quoted shell assignments. Shell command substitution can execute backticked tokens such as `aria-label`. Store each trial prompt in a file and pass it to Hermes through a safe argv/Python wrapper, or use a single-quoted literal with no interpolation; syntax-check the proposal command before trial 1.
- Verify the harness's comparison semantics before choosing `min_improvement`. If zero allows equality, equal-score trials can be accepted despite an “must improve” contract. Use a positive epsilon/integer threshold and add a fixture proving equal scores revert.
- A keyword-presence evaluator proves only that tokens exist, not that design, performance, or lifecycle behavior improved. Pair static checks with meaningful tests and actual measurements (render profiling, timing, memory/bundle comparison, screenshots/accessibility checks) and label any checklist score honestly.
- Before documenting that a Hermes experiment requires a core patch, verify the live runtime rather than repeating the original design assumption: inspect the valid hook/middleware registries, search the active Hermes checkout for the proposed hook, inspect the update-time patch script, and confirm the Hermes git working tree. Distinguish an optional earlier/preflight optimization from a functional requirement when stock hooks already reduce the provider request and recover tools.
- Don’t let loops touch critical procedures (payroll submission, safety policies) without human approval gates.
- Don’t use loops for open-ended creative tasks; they’re for bounded problems with clear metrics.
- Watch for overfitting to local metrics (e.g., improving test count by removing meaningful tests). Guardrails matter.
- Do not call an evaluation-only trial a proposal failure merely because it produced no Git diff. Accepted no-op trials should log their metrics without attempting an empty commit.
- Avoid brittle answer assertions where several factual phrasings are valid; validate invariant facts or successful grounded tool execution instead.
- Before freezing a conversational-output corpus, validate that every expectation is satisfiable under the output contract. A case that requires three separate source sentences while limiting extraction to two sentences is not a legitimate optimization target. Freeze only after removing or correcting impossible assertions, and record any pre-trial correction explicitly.
- A perfect corpus score is not sufficient adoption evidence. Independently probe nearby counterexamples outside the optimizer's target cases—especially natural equations, URLs/query strings, prose containing delimiters, and truthful provenance labels—because a narrow structured-data fix can satisfy every frozen case while corrupting ordinary language. Repair or reject overbroad candidates before production adoption.
- For cross-model text-selector comparisons, use one fresh model session per hypothesis under an external deterministic controller. Proposal workers edit only exact existing allowlisted files, never create alternate test modules, stage, or commit. The controller owns scalar comparison, complete gates, KEEP commits, REVERT restoration, and model exit-0/no-diff classification. Preserve and inspect blocked diffs: a strict score improvement may still contain brittle hard-coded exceptions, incomplete target coverage, or false provenance.
- `scripts/run_tests.sh` (user-local — verify it exists) discovers file and directory paths in the current parallel runner; `file.py::Class` node IDs can return `No test files to run`. Use the wrapper for the complete affected test file. If a pre-existing unrelated collection defect prevents that and an exact-node fallback is required, run those nodes hermetically with the fully provisioned project `.venv` (not a release venv or a campaign-local partial `uv run` venv), record the wrapper limitation, and keep the complete focused-file wrapper gate wherever it works.
- For URL-cleanup hypotheses, test the exact frozen source strings rather than invented lookalikes. Removing a URL or its hosting scaffold is a transformation, so nonempty resulting speech must use deterministic provenance; a URL-only scaffold should fail closed to the neutral cue rather than emit residue such as `The URL is .`.
- For constrained text-selector campaigns, read for expectation review, direct model-route proof, strict score transactions, counterexample probes, truncated-response recovery, and controller-owned BLOCKED closeout.
- If a policy/plugin boundary prevents controller-side diff reads or tests, read : preserve the dirty handoff, classify acceptance blocked, repair the controlled-tool activation through an authorized route, and never infer a corpus score from worker prose.

## See also

- Karpathy reference doc: Notes/karpathy-teachings-and-hermes-applications.md
 (High-level teachings and their Hermes applications; use this skill to operationalize them.)
- Codex/Claude → Hermes pattern mapping:
 (When someone reads about an agent-loop setup on another platform and wants the Hermes equivalent.)
