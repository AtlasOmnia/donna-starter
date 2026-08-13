---
name: skill-auditor
description: skill-auditor — Use when auditing, reviewing, or grading Hermes skills for quality. Checks trigger phrases, exact commands, pitfalls, verification steps, tool guidance, and shareability. Assigns A-F grade with specific fix suggestions. Run this before publishing a skill or when troubleshooting unreliable skills.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
 hermes:
 tags:
 - skills
 - audit
 - quality
 - grading
 - review
 - best-practices
 related_skills:
 - hermes-agent-skill-authoring
 - hermes-self-evaluation
 - content-style
---
# Skill Auditor — Quality Grading System (A–F)

Audit any Hermes skill file and assign a quality grade based on clarity, completeness, tool guidance, and shareability. Returns specific fix suggestions ranked by impact.

## When to Use

- User asks you to review, audit, or grade a skill
- You're about to create a new skill and want to validate the draft
- A skill is behaving unreliably (agent skips it, calls wrong tools, misses steps)
- User shares a skill file or path for feedback
- You're preparing skills for sharing with others

**Don't use for:** general Hermes troubleshooting, model selection, config review — those have their own skills.

## Grading Criteria

Each skill is scored across **five dimensions**. Points are deducted from 100. The final grade maps to a letter:

- **Grade A (90–100)** — Production-ready. Solid frontmatter, exact commands, real pitfalls, verification steps, consistent structure. Will fire reliably and execute correctly across model sizes.
- **Grade B (80–89)** — Minor gaps. Missing one dimension but still reliable.
- **Grade C (70–79)** — Functional but vague in places. Needs clarification on 1–2 key areas, especially with smaller models.
- **Grade D (60–69)** — Error-prone patterns detected. Incomplete steps or missing critical sections. Will fail silently on model switches.
- **Grade F (<60)** — Broken discovery or execution. Either the description is too vague to fire, or the steps are too incomplete to follow.

### Dimension 1: Frontmatter & Description (max 25 points)

The description is your skill's only chance to be discovered. Hermes sees the one-line description from `available_skills` **before** deciding whether to load SKILL.md at all. If that description is vague, the skill never fires — nothing inside SKILL.md matters if this step fails.

**Full marks (25):** Valid YAML frontmatter with `name` and `description` fields. Description starts with "Use when..." and covers the **trigger class** (not a single task). Specific enough that Hermes can distinguish it from similar skills. ≤ 1024 chars.
- Example A: `Use when debugging Python: test failures, uncaught exceptions, silent bugs. Covers root cause analysis, not just error messages.`
- Example B: `Use when debugging code issues and test failures.` (too broad — could overlap with other skills)

**Partial marks (10–24):** Has frontmatter but description is too generic or overlaps with another skill's scope.
- Problem: "Debug stuff", "debugging", no "Use when..." pattern, description that could match 3+ skills

**Zero marks (<10):** Missing frontmatter entirely, or missing `name`/`description` fields.

**Penalties:**
- Missing frontmatter: -5 pts
- Missing description field: -3 pts
- Description too generic (no "Use when" pattern): -2 pts
- Description overlaps with another skill's scope: -1 pt

### Dimension 2: Exact Commands (max 25 points)

Every step should include the actual command, tool call, or file path — not a description of what to do. Use the **actual registered tool names** from the Hermes toolset (`skill_view`, `skill_manage`, `skills_list`, `write_file`, `search_files`, `terminal`, `read_file`, `patch`) — generic phrasing misleads readers on different setups.

**Full marks (25):** Every numbered step has an exact command or explicit file path with verification condition.
- Example: `search_files(pattern='config', target='files', path='.')` instead of "search for the config"
- Example: `pytest tests/test_module.py::test_name -v` instead of "run the failing test"

**Partial marks (10–24):** Most steps have commands but some are vague.
- Problem: "run the script", "use the appropriate tool", "handle errors appropriately"

**Zero marks (<10):** Steps describe actions without showing how to execute them.

### Dimension 3: Pitfalls Section (max 20 points)

Lists real-world failure scenarios that have actually been observed, with recovery actions.

**Full marks (20):** 2–3 specific pitfalls with concrete recovery steps.
- Example: "PDF is password-protected → use `--password X` flag"
- Example: "LM Studio returns HTTP 400 for gpt-4o → fall back to qwen3.5"

**Partial marks (8–19):** Has pitfalls but they're theoretical or only 1 item.
- Problem: "something might go wrong", "the tool may fail" — no specificity, no recovery

**Zero marks (<8):** No pitfalls section, or purely generic warnings.

### Dimension 4: Verification Steps (max 15 points)

Explicit checks after execution to confirm success before proceeding.

**Full marks (15):** At least one concrete verification step per major action.
- Example: "Verify exit code is 0", "Check file exists at `~/.hermes/skills/<name>/SKILL.md`"
- Example: "Confirm email was sent by checking Sent folder"

**Partial marks (6–14):** Has some verification but incomplete or vague.
- Problem: "make sure it worked" — no way to actually verify

**Zero marks (<6):** No verification steps at all.

### Dimension 5: Structure & Conventions (max 15 points)

Consistent structure makes skills scannable and maintainable. Follows the peer-matched pattern from Hermes core skills.

**Full marks (15):** Has `## Overview` section (what and why), `## When to Use` with bulleted triggers AND counter-triggers ("Don't use for:"), topic-specific body sections, file size 8-15k chars (peer average ~12k). Uses `references/*.md` for large supporting content instead of bloating SKILL.md.

**Partial marks (6–14):** Missing one structural element or inconsistent with peers in the same category.
- Problem: No counter-triggers, no Overview, file > 20k chars without splitting to references

**Zero marks (<6):** No structure at all — just a wall of text with no sections.

**Penalties:**
- Missing Overview section: -2 pts
- Missing When to Use section: -2 pts
- No counter-triggers ("Don't use for"): -1 pt
- File > 20k chars without splitting to references: -2 pts
- Inconsistent with peer skills in same category: -1 pt

## How Skills Actually Work in Hermes

When auditing, keep the three-phase mechanism in mind:

1. **Discovery phase** — Hermes scans the `available_skills` block (the one-line description from each skill's frontmatter). If your description is vague, the router never loads the skill. Nothing inside SKILL.md matters if this step fails.
2. **Loading phase** — The full SKILL.md loads into context. Now structure, commands, and clarity matter.
3. **Execution phase** — The model follows the skill. Vague steps, missing commands, and absent verification cause silent failures, especially on smaller models.

Dimension 1 checks discovery. Dimensions 2-5 check loading and execution.

## Audit Workflow

### Step 0: Prefer class-level umbrellas

If the topic is broad (skill maintenance, config hygiene, verification, authoring), update or extend the umbrella skill for the class rather than creating a one-off session artifact. If the change includes a reusable check or workaround, move the detailed recipe into `references/` and keep the SKILL.md body as the durable overview.

### Step 1: Load the Skill

Read the skill file using `read_file`:

```
read_file(path="~/.hermes/skills/<category>/<name>/SKILL.md")
```

If the user provides a skill name, use `skills_list` to confirm it exists, then `skill_view(name="<name>")`.

For an uninstalled local draft or GitHub staging directory, inspect the supplied `SKILL.md` path directly rather than assuming registry discovery. Do not treat a zero process exit code as proof that `hermes skills inspect ./SKILL.md` succeeded: inspect the command output for an explicit success result. If that Hermes release resolves only registry IDs or URLs, run a direct frontmatter/body validator against the local file, then audit the registered copy after installation with `hermes skills audit <name> --deep`.

If `skill_view` says the skill is not found and the user implies it should exist, do not stop at the installed skill registry. Search the user's vault/project notes for the requested skill/workflow name before concluding it is absent:

```
search_files(pattern="<skill name>|<skill-name>|<title case>", target="content", path="<resolved vault path>", file_glob="*.md")
search_files(pattern="*<keyword>*", target="files", path="<resolved vault path>")
```

When the vault contains a draft or workflow note, report that it is not installed as a Hermes skill and offer to promote it into the appropriate class-level umbrella skill rather than creating a narrow one-off skill.

### Step 2: Check Each Dimension

Systematically evaluate each of the five dimensions against the criteria above. Quote specific lines from the skill as evidence for each score.

### Step 3: Calculate Grade

Sum points across all five dimensions. Map to letter grade.

### Step 4: Generate Fix Suggestions

For every dimension scoring below full marks, provide **one concrete fix** with a before/after example pulled from the actual skill content.

### Step 5: Output Report

Use this exact format:

```
## Skill Audit: <skill-name>

**Grade: X/YZ** — <one-sentence summary>

### Dimension Scores

- Frontmatter & Description: N/25 — <brief assessment, quote evidence>
- Exact Commands: N/25 — <brief assessment, quote evidence>
- Pitfalls Section: N/20 — <brief assessment, quote evidence>
- Verification Steps: N/15 — <brief assessment, quote evidence>
- Structure & Conventions: N/15 — <brief assessment, quote evidence>

### Fix Suggestions (ranked by impact)

1. **[Dimension]** <specific fix with before → after example>
2. **[Dimension]** <specific fix with before → after example>
...

### Related Skills Check

- `related_skills` in frontmatter: <present/missing> — <assessment>
- Overlap with peers: <any duplicate skills found, or "none detected">
```

## Common Pitfalls in Skill Auditing

1. **Auditing against your own expectations, not the rubric.** Stick to the five dimensions. Don't penalize for style preferences — only for missing structural elements.

2. **Calling a skill "too long" without checking content density.** A 15k-char skill with all five dimensions scores higher than a 3k-char skeleton. Length is fine if every line adds signal.

3. **Missing the difference between tool guidance and tool use.** The skill should tell the agent *which* tools to call and *when*. It doesn't need to actually call them during the audit — that's your job as the auditor.

4. **Ignoring shareability.** A skill with hardcoded paths like `~/Documents/` works for one person but breaks for everyone else. Flag this even if the rest is solid.

5. **Making claims about validator limits or tool names without verifying them against actual implementation.** Before asserting "the validator enforces X" or "use tool Y", check the source (`tools/skill_manager_tool.py` for validators, `model_tools.py` for registered tool names). Aspirational claims mislead auditors — if a limit isn't enforced, reframe it as a guideline.

## Verification Checklist

- [ ] Skill file loaded and readable
- [ ] All five dimensions scored with quoted evidence
- [ ] Grade calculated correctly (sum of dimension scores)
- [ ] Fix suggestions include before/after examples from the actual skill
- [ ] Report follows the output format exactly
- [ ] Related skills checked for overlap or missing cross-references
- [ ] If no canonical suite exists for a skill edit, use a temporary `hermes-verify-*.py` script under `/var/folders/...` and clean it up after the run

## Reference Files

- `references/ad-hoc-skill-verification.md` — temporary-script verification pattern for skill edits without a canonical suite.
- `references/public-skill-package-release-gate.md` — standalone GitHub skill-package staging, script safety, privacy review, independent closeout, and immutable pre-push verification.

## One-Shot Recipes

### Quick Audit (user provides skill name)

```
1. skill_view(name="<skill-name>")
2. Evaluate against five dimensions
3. Output grade report
```

### Audit and Fix (user wants immediate improvements)

```
1. skill_view(name="<skill-name>")
2. Evaluate and grade
3. skill_manage(action='patch', name="<skill-name>", old_string="<vague line>", new_string="<exact command>")
4. Re-audit to confirm grade improvement
```

### Batch Audit (user wants all skills reviewed)

```
1. skills_list() — capture the CLI-visible/registered skill set.
2. Independently inventory every SKILL.md under the target skill root; report registered skills and on-disk files as separate counts.
3. Validate every file with Hermes's installed frontmatter/content-size validator, then check duplicate names and concrete relative Markdown links.
4. Grade structural omissions as review signals, not automatic rewrite orders. Do not mass-add boilerplate when it only increases prompt weight.
5. Apply high-confidence fixes only: malformed frontmatter, confirmed broken links, validator size violations, and executable guidance proven stale or incomplete.
6. Re-run the validator across the entire library, run `hermes skills list`, and require zero validator failures before completion.
7. Save before/after machine-readable and Markdown reports plus a rollback backup.
```

### Recovery-safe rules for malformed and oversized skills

- A malformed placeholder is not evidence that a real integration exists. Never invent commands, backends, authentication flows, or generic “route to the relevant helper” instructions merely to make it pass the rubric. If no executable workflow can be verified, preserve it in the rollback backup and remove/archive the invalid entry rather than registering fiction.
- When a skill exceeds Hermes's content-size validator, keep the class-level operational core in `SKILL.md` and move a coherent secondary section into `references/<topic>.md`. Add a concise link from the core, then validate both the reduced size and the relative link.
- Markdown-link checks must distinguish concrete links from examples/templates. Ignore placeholders containing variables such as `{relative-path}`.
- Treat subagent audit summaries as provisional. Read the generated report, inspect every changed file, and independently rerun the full-library validator before reporting success.
- For bulk hygiene runs, trust only the post-fix rescan. If the checker itself was missing or stale, repair that helper first, rerun the audit, and use the new report as the source of truth.
- When normalizing weak openers, strip accidental file-name prefixes before prepending the skill name, and leave already-valid descriptions alone. A fix that compounds a bad prefix is worse than the original smell.
- After deleting snapshot caches or regenerating generated indexes, verify the file state explicitly instead of assuming the command did it.
## Public support files

- `references/ad-hoc-skill-verification.md`
- `references/public-skill-package-release-gate.md`
