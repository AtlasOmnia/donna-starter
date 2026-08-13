---
description: content-style — Writing content for r/hermesagent and similar communities — workshop posts, definitive model-variant guides, research-heavy megathreads, and community update posts.
name: content-style
---
# Content Style: r/hermesagent & Community Posts

## Overview

Writing Reddit-native content that sounds human, avoids AI tells, and delivers value through structure and specificity. Applies to workshop posts, definitive model guides, research megathreads, and community FYI/update posts.

## Hook Patterns

Lead with one of these:
1. **Contradiction** — "Everyone says X but Y is actually true"
2. **Specific number** — "The 3 tools I use daily"
3. **Pain point** — "If you're doing X, stop"
4. **Before/after** — "Before: Y. After: Z"
5. **Question** — "Why does X still suck?"

## Writing Principles

- Hook first, details second
- Lead with what people actually care about
- Concrete over abstract: specific examples beat general advice
- One idea per paragraph
- End on a clear takeaway

### Product-name disambiguation before drafting

For “How would you describe X on Reddit?” requests, lock the exact product identity before importing features or architecture:

1. Treat likely voice-dictation homophones (`box`/`Vox`, `Voz`/`Vox`) as ambiguous names, not permission to substitute the nearest familiar project.
2. Search for the exact spelling and check whether it is an external product, a renamed product, or one of the user’s similarly named apps.
3. Describe only features supported by that product’s source material. Do not transfer one voice-learning product's capabilities to another merely because they share a category.
4. If the user corrects the name, acknowledge it briefly and rewrite from the corrected identity; do not preserve assumptions from the earlier draft.

### Plain-language Reddit product explainer

Use this compact order for a comment-sized explanation:

1. **What it is** — one sentence in ordinary language.
2. **What the user does** — the concrete interaction.
3. **How it works** — only the essential mechanism, without architecture dumping.
4. **Why it is different** — one comparison readers immediately understand.

Keep a short Reddit comment short unless the user asks for a full post. Avoid marketing copy such as “revolutionary,” unsupported privacy claims, or a polished feature list that has not been verified.

## What to Avoid

- Long intros that bury the lead
- Bullet-point dumps without through-line
- Writing for peers instead of audience
- Ending with "any questions?"
- Self-deprecation as escape hatch

## Tone

- Direct, not performative
- Confident but not arrogant
- One clear sentence beats three hedged ones
- No "I think" / "I believe" filler
- No trailing questions

## Anti-AI Sounding Replies

For social media replies that should sound human:

- Use contractions freely
- Keep sentence length uneven
- Include minor colloquialisms or fragments
- Avoid perfectly balanced paragraphs
- Skip transition words like "additionally", "furthermore"
- Use lowercase for emphasis instead of formatting
- One genuine opinion > five hedged observations
- Natural "honestly" or "look" is fine

## Answering Beginner Hermes Reliability Questions

When a Reddit user asks whether Hermes can be forced to obey instructions, whether gates can be ignored, or how memory avoids degradation:

1. **Lead with the honest limit:** natural-language instructions to a probabilistic model are soft controls and cannot guarantee perfect compliance.
2. **Separate instructions from enforcement:** prompt rules can be missed; deterministic runtime controls can block a specific action path. Never imply a gate protects routes it does not cover.
3. **Use the correct confidence gradient:** prompt/SOUL/skill guidance → verifier or judge → tool restrictions and approvals → OS/container/filesystem boundaries. Only the last category can make some violations mechanically impossible.
4. **Treat claims of completion as unverified:** recommend observable evidence such as tool output, file readback, screenshots, tests, or independent review.
5. **Explain memory by storage role:** bounded built-in memory for durable facts, skills for procedures, and `session_search` for on-demand historical detail.
6. **Preserve key nuances:** memory overflow errors rather than silently evicting entries; exact duplicates are deduplicated as a successful no-op; writes persist immediately while the system-prompt snapshot remains frozen until the next session.
7. **Keep it novice-readable:** explain the model first, then the Hermes mechanisms. Avoid dumping config commands unless the reader asks how to enable them.
8. **Separate storage roles explicitly:** user preferences belong in `USER.md`; compact stable environment facts belong in `MEMORY.md`; procedures belong in skills; project or machine operating rules belong in `HERMES.md` / `.hermes.md` / `AGENTS.md`; actual transport belongs in SSH config or a deterministic integration.
9. **Do not describe memory as the source of truth for live machine identity:** recommend live verification (`hostname`, `pwd`, and, when relevant, `uname` or an explicit remote-host check) before remote work.
10. **When explaining a reliable remote-agent setup, describe the layered pattern:** durable memory points to the canonical runbook; the runbook holds detailed scope, routes, and recovery; a connector performs the transport; returned tool output proves success. Do not imply that a model should reconstruct a complete SSH/API recipe from remembered prose.

### Machine identity and remote-execution reliability

When a beginner reports that Hermes forgets which computer it is on, chooses the wrong SSH route, or keeps rediscovering an installed tool, treat this as a configuration-and-verification question first, not simply an external-memory question.

Explain the practical split:
- `USER.md` is for identity and preferences, not infrastructure topology.
- `MEMORY.md` may hold a short stable pointer such as the machine role and the location of the authoritative runbook, but it is bounded and session-snapshotted.
- `HERMES.md`, `.hermes.md`, or `AGENTS.md` should contain the readable machine map and operating rules for the relevant working directory.
- `~/.ssh/config` should contain host aliases, ports, usernames, and key selection; never put private keys or secrets in memory/context files.
- A dedicated skill should define the procedure: verify the current host, use the named alias, verify the remote host after connecting, avoid improvised multi-hop routing, and stop on ambiguity.
- When a native connector exists, prefer it over asking the model to assemble transport details manually.

Use a plain-language example when useful:
> Memory tells Hermes where the runbook is. The runbook explains the machines. SSH config or a native connector performs the connection. `hostname` and the returned tool output prove which machine was actually reached.

Current sourced details and reusable wording checks are in `references/hermes-instruction-compliance-memory.md`. Re-check the live Hermes docs before publishing version-sensitive defaults.

## Post Templates

### Workshop Post (copy-paste prompt)

```
[HOOK — one sentence that makes someone stop scrolling]

[SETUP — 2-3 sentences max, get to the point fast]

[CONTENT — concrete details, specific numbers, real examples]

[TAKEAWAY — clear takeaway or next step]
```

### Audit/Diagnostic Post (pain-point → framework → runnable prompt)

```
[IDENTIFY PROBLEM — quote top community complaints]

[EXPLAIN ROOT CAUSE — what's actually going wrong]

[THE FRAMEWORK — grading criteria or dimensions that matter]

[RUNNABLE PROMPT — copy-paste prompt anyone can use immediately]

[REAL EXAMPLES — before/after showing bad vs. fixed]

[TAKEAWAY — one-sentence summary]
```

### Community Update / FYI Post

For infrastructure, moderation tooling, process changes, community operations.

```
[HOOK — what you did. No preamble]

[CONTEXT — one paragraph on scope and independence]

[WHAT CHANGED — bullet list, one fact per bullet]

[THE SYSTEM — how it works, numbered steps if workflow]

[GUARDRAIL — what it CAN'T do — this matters more than what it does]

[WHY THIS MATTERS — the pattern, not the pipeline, one concrete example]

[FEEDBACK LOOP — how readers can report issues, specific]
```

FYI Post rules:
- Lead with action, not greeting (no "Quick update" or "Hey everyone")
- Headers are blunt: "What changed" not "Here's what I updated"
- The guardrail matters more than the workflow
- One concrete example beats three paragraphs of philosophy
- End with specific ask, not vague invitation

### Non-Technical Explainer Post (translate a technical release for a general audience)

For "explain this announcement/release/feature for non-technical people" requests — most commonly translating a terse technical tweet or changelog line into a Reddit-native post.

```
[TITLE — plain-language benefit or removed pain point, not the feature name]

[HOOK — one line, no preamble]

[THE PROBLEM THIS SOLVES — plain-language grounding of why this mattered BEFORE the change.
 Define any load-bearing term inline the first time it appears (parenthetical gloss), never after.]

[WHAT CHANGED — 2-4 bullets, one fact per bullet, attribute claims to the source
 ("Nous says...", "the announcement claims...") rather than inventing an evidence
 framing the source didn't use]

[HOW IT WORKS, IN PLAIN TERMS — one analogy, see selection rules below]

[WHAT IT CAN'T DO — the guardrail. This deflates hype and is often the most
 trustworthy section; don't skip it]

[WHY IT MATTERS — the new idea only. If this repeats the "what changed" bullets,
 cut the repeat and lead with the angle that's actually new (e.g. a "hidden tax"
 framing) ]

[CLOSING — a takeaway or a specific ask ("if you run X, curious whether you
 notice Y"), never just a bare source link]

Source: [link]
```

**Analogy selection — test every candidate against two independent criteria, not just "does this feel clever":**

1. **Audience accessibility.** Does understanding the analogy require background the *stated audience* doesn't have? An analogy that name-drops an internals feature of a tool (e.g. `git notes`, a specific API's internal cache eviction policy) fails this even when the underlying subject is a dev-heavy subreddit — plenty of working practitioners have never touched the specific internal feature you're citing. If you have to write "if you've ever used X, you already understand this," that sentence is a tell the analogy just excluded everyone who hasn't used X. Prefer universal, everyday analogies (a librarian who knows which section to search instead of shelving everything up front, a restaurant menu vs. asking the waiter what's off-menu, phone contacts you look up instead of memorizing) — they carry zero technical prerequisite.
2. **Mechanism fidelity.** The analogy must actually map the mechanism being explained, not just the vague shape of it. Check specifically for: threshold/adaptive behavior (does the analogy have a "still fine below X, changes above X" property if the real system does?), active vs. passive retrieval (does the analogy's information get actively searched-for on demand, or does it just passively sit there waiting to be noticed — these are different mechanisms and picking the wrong one misleads the reader), and discovery direction (does the analogy's "something advertises its own existence" direction match the real system, or is it backwards?). An analogy can pass the accessibility test and still fail this one — verify both before finalizing, don't stop at "sounds clean."

When you catch an analogy problem via self-review or a critic pass, treat the fix as a stylistic/subjective decision and bring the tradeoff back to the user (e.g. via `clarify`) rather than silently swapping it — the user may want the technical analogy anyway for a dev-heavy audience, or may want it demoted to a secondary aside rather than dropped.

**Jargon-grounding pass (run before calling a draft done):** scan for every technical noun introduced without a plain-language gloss on first use — common misses: "tokens," "context window" (fine once, redundant if defined twice — keep the first, cut the second), protocol/product names the source assumes familiarity with (e.g. "MCP"), and engineering shorthand like "out-of-band" when a plain-English equivalent ("off to the side") already exists elsewhere in the draft. Either define inline in a parenthetical or cut the term entirely if it's not load-bearing.

**Critic-verification pitfall (do not skip):** an independent critic pass (Fable, cross-model audit, etc.) can flag a claim as "invented" or "not in the source" when it actually IS in the source — always re-read the exact primary-source text yourself before applying a critic's factual-accuracy fix. A critic pass once claimed a draft’s "internal test" language was fabricated when it was quoted from the source; re-reading the primary text resolved it." Applying that fix blind would have introduced an inaccuracy the critic invented while trying to catch one. Treat every critic finding as a hypothesis to verify against the primary source, not a fact to apply — this applies to ALL critic passes in this skill (the chosen critic model, OpenRouter, delegate_task audits), not just explainer posts.

### Security-incident sticky / mod note

When a credible security report initially looks like spam or implies Hermes itself caused an attack, keep the sticky short and separate the layers:

1. **Source status:** say the source was vetted and whether it is a legitimate company/publication.
2. **Mechanism:** explain that Hermes was used as an agent harness when that is the evidence; do not call Hermes the malware, exploit, or attacker.
3. **Guardrail:** state what the report does *not* show—no Hermes vulnerability, no evidence ordinary users were compromised, or no proof of initial access—only when verified.
4. **Evidence limit:** distinguish independently corroborated infrastructure/sample behavior from private vendor captures and unconfirmed victim attribution.
5. **Analogy:** one plain comparison such as “someone used Python or Metasploit” is enough.

Preferred wording is “parts of the technical evidence independently check out,” not “the story is confirmed,” when the victim or government has not publicly acknowledged it. YOLO/approval bypass proves commands could run without approval; it does not prove no human supplied objectives or watched the session. Avoid repeating the sensational headline in the clarification.

Use either a 2–4 paragraph sticky post or a single compact mod comment. The goal is to reassure readers the link is not spam while preventing the clarification from becoming brand defense.

## Content Planning: Audit Before You Write

Before drafting, verify demand signal:

**Demand signals:**
- Comment count on related threads (25+ = hot, 7-15 = viable, <5 = niche)
- Explicit "I want to learn X" requests
- Repeated pain phrases across multiple posts
- Top posts by month: sort by top/month, scan for topic

**What fails:** Templates without workflow context. A grading rubric alone gets upvotes but no comments. Pair the tool with concrete usage.

**What works:** Posts that solve explicit pain points with copy-paste content AND map to community complaints.

## Research-Heavy Content: Megathreads & Guides

For data-dense, sourced, organized-for-reference content. Not conversion-focused.

### Format A: Tier/Reference Guide

```
[QUICK REFERENCE TABLE — entire answer in one scan, up top]

[TIER BREAKDOWN — one section per tier, table + one-sentence recommendation]

[ARCHITECTURE/THEORY — why things work this way]

[OPTIMIZATION TECHNIQUES — numbered steps, from highest impact]

[COMMUNITY PICKS — direct quotes/links from communities]

[BUYING ADVICE — if applicable, hardware recs with prices]

[SOURCES — bullet list of URLs + dates]
```

Key: The Quick Reference table IS the post. Everything below is supporting evidence.

### Format B: Definitive Model-Variant Guide

Single model family, exhaustive variant catalog. Two posts for a model (one per architecture) outperform a single mega-dump.

```
LAST UPDATED: [date]

ONE PARAGRAPH: what this model is, what hardware it fits
(FP16 VRAM, Q4 file size, Q3 file size with context)

---

THE BASE MODEL
- Bullet list: param count, architecture, context, multimodal, license
- Official benchmark scores (SWE-bench, AIME, GPQA, etc.)
- KEY DIFFERENCE from sibling models

VARIANT CATEGORIES — what changed from base
1. UNCENSORING (lossless safety removal)
2. HERETIC + FINE-TUNE (uncensor + capability boost)
3. ABLITERATION (surgical refusal removal)
4. REASONING DISTILLATION (from other models)
5. MTP / SPECULATIVE DECODING (speed layer)

THE VARIANTS (one subsection per variant)
#### VARIANT NAME (downloads, likes) — NICKNAME
- What: one sentence
- Quality: compared to base, with numbers
- Best for: one sentence
- Creator context
- VRAM: IQ2_M → IQ3_M → IQ4_XS → Q6_K with estimates
- Download links

QUICK PICK TABLE
| Your situation | Download this | Why |

SOURCES — bullet list of HuggingFace URLs + counts, community threads
```

**Critical rules for definitive guides:**

- **ONE model per post.** Don't cover Qwen, Gemma, DeepSeek, Llama in one post.
- **Hard data per variant:** HF download counts, like counts, benchmark scores, VRAM estimates. No "might be good."
- **User-facing voice:** "Download X if you want Y" beats "X is an option some users prefer."
- **Caveats belong at the end** or in "Watch For" section, not sprinkled through every recommendation.
- **Categories before catalog:** readers pick category then find variant. Don't dump alphabetically.
- **Comparisons live INSIDE variant entries**, not in a separate "real user reviews" section. If you have community pull-quotes about a specific variant, integrate them into that variant's entry under Quality/Best for/Creator context.

**Critical error: comparisons in wrong location**

If a user says "this guide isn't informative" or "lacks comparisons," the fix is ALMOST ALWAYS structural: move the reasoning INTO the catalog entries. Don't create a separate "REAL USER REVIEWS" section at the end — that separates reasoning from the variants it describes.

**Correct structure:**

```
#### DavidAU Heretic Uncensored NEO-CODE
- 131.4K downloads, 402 likes
- https://huggingface.co/...
- What: Two-stage process, heretic uncensor + coding fine-tune
- Quality vs base (HF card verified):
 - KL divergence: 0.0469 (vs 99/100 refusals on base)
 - Quant quality table (IQ2_M → Q8_0 with metrics)
 - "In house benchmarks" beat base on 7/7 metrics
- Best for: Coding, verified benchmark winner at every quant tier
- VRAM: Q4_K_M ~15.7 GB
- Settings: thinking temp=1.0, coding temp=0.6, instruct temp=0.7
```

Comparisons, refusal rates, benchmarks, KL divergence — all inline. Reader looking at "DavidAU NEO-CODE" sees immediately why it beats HauhauCS. They don't scroll 200 lines to line 290.

**Separate sections are only appropriate for:**
- Trade-offs between variants (27B vs 35B, dense vs MoE)
- Cross-cutting insights (MTP vs DFlash)
- EDITOR'S RIG: "I run X because Y"

**Do NOT create a separate "REAL USER REVIEWS" section that lists per-variant pull-quotes disconnected from variant entries.**

### Pitfall: HF model cards often list BASE benchmarks, not the variant's

When verifying variant benchmarks via HuggingFace model cards, many authors publish "Base model performance" tables with impressive numbers (SWE-bench 77.2, AIME 94.1) but those numbers belong to the BASE model — the fine-tuned variant has NO published delta.

Common traps:
- **rico03/Qwen3.6-27B-Claude-Opus-Reasoning-Distilled-GGUF**: card shows "77.2 SWE-bench, 94.1 AIME 2026" — these are base Qwen3.6-27B numbers. The distilled variant has no published benchmark delta.
- **unsloth/Qwen3.6-35B-A3B-MTP-GGUF**: card shows "SWE-bench 73.4, AIME 92.7" — again base model numbers.
- **lordx64/Qwen3.6-35B-A3B-Claude-4.7-Opus-Reasoning-Distilled**: card shows "GSM8K 84.3%, MMLU-Pro 74.9%" — these ARE the variant's own eval numbers (correctly scoped).

**Rule:** When a card shows benchmarks, check the table heading. If it says "Base model performance," "Qwen3.6-27B baseline," or "reference scores for comparison" — those are BASE numbers. Write them as "card lists BASE benchmarks only, no variant delta published." If the table is labeled with the variant's name and shows actual eval results, those are the variant's numbers.

For KL divergence (uncensored variants): lower = better preservation. Real Qwen3.6 numbers:
- llmfan46 Heretic v2 = 0.0021 (near-identical, best-in-class)
- DavidAU Heretic = 0.0469 (good but 22× worse than llmfan46)
- others often don't publish KL

### Pitfall: read_file line-number delimiters in patch

`read_file` output shows each line as `N| content` (e.g. `9| Qwen3.6 gives you...`). Those `N| ` prefixes are display artifacts — they are NOT in the file. If you copy a read_file excerpt into a `patch` `old_string` including the `N| `, the match fails. Always strip the `N| ` prefix; match the raw line content only.

### Research Workflow

1. **Parallel web searches** — 3-5 searches simultaneously targeting different angles. Overlap is fine; gaps are worse.
2. **Extract from best sources** — prefer `web_extract` for plain-text endpoints. For JS-heavy pages (InsiderLLM, Medium, **Reddit**, most modern blogs), skip `web_extract` entirely and go straight to `browser_navigate` + `browser_console` with JavaScript extraction. `web_extract` will timeout on these.
3. **Browser fallback for Reddit** — navigate to `old.reddit.com`, then extract via browser_console with JavaScript targeting `.expando .md` for post body. `web_extract` does not work on Reddit (returns "Website Not Supported").
4. **Compile** — consolidate findings into structure above. Every claim should trace to a source or be marked as estimate/community consensus.

### Pitfall: Parallel research dispatch with failure guardrails

When megathread research needs multiple distinct sources, dispatch parallel agents targeting different sources. One agent failing on Reddit shouldn't block HuggingFace card pulls.

**Critical: Don't retry failing tools in infinite loops.** If an agent hits 403s or timeouts, it will sometimes retry 20+ times before hitting an internal guardrail halt. Give each agent explicit instructions: "If a tool fails on one URL/author/variant, skip it and move to the next — do not retry indefinitely."

**File-based output preferred.** Agents writing results to files persist their work even if the session ends mid-research. An agent printing 200 lines of intermediate output loses that work if anything interrupts. Prefer file output for any research that takes more than a few tool calls.

**When one agent fails broadly, launch a dedicated retry with narrower scope + tighter instructions:**
- Explicit tool to use (e.g., `curl` against HF HTTP API rather than `web_extract`)
- Explicit skip-on-failure rules
- File-based output path named distinctly from failed attempt

### OpenRouter Free-Tier Verification

The free tier on OpenRouter contracts monthly. Models the prior month's post listed as free routinely move to per-token pricing. A refresh that copies the prior post's "free" assumptions ships factually wrong claims.

**Rule:** Never trust the OpenRouter collection page or the previous post's model list. Verify against the **live API** before writing any "free" claim.

Verify current model availability from the provider's documented, authenticated interface before making a free-tier claim; do not copy private credential or shell-loading recipes into a public skill.

**Pitfall: critic hallucination on availability.** Both cross-model audit passes can invent model-availability claims — e.g., "Qwen3 Coder 480B is now free", "Elephant Alpha is free", or specific "going away July X" banner dates. These are frequently FALSE against the live API. Re-verify EVERY availability claim a critic makes against the API before applying the fix.

### Money-maker / Revenue-claim Megathreads

When drafting a megathread about making money, side hustles, savings, lead generation, trading, or business impact:

- Treat all Reddit dollar figures as **self-reported** unless external proof exists
- Add a source-quality note near the top and a disclaimer near the bottom: not financial, legal, tax, compliance, or investment advice
- Separate **actual revenue/savings claims** from forecasts, avoided cost, reclaimed capacity, and course-funnel pricing estimates
- Keep productizable GitHub projects in an appendix; do not present ecosystem assets as proof people made money
- Replace hard pricing/CTA language with scope-dependent pilot language unless the user explicitly wants a sales page
- Include a "what not to oversell" section for trading bots, course-funnel rates, and fully autonomous fulfillment
- Before publishing, run two different Nous Portal models as critics for credibility, moderation optics, legal/financial risk, and exact wording changes

### Pitfall: web_extract timeout cascade

`web_extract` reliably times out (60s+) on JavaScript-heavy pages. When the first call fails, the rest in the same batch will too. Don't retry with `web_extract`. Browser tools are the correct fallback: slower per-page but actually complete.

This is especially true for: **reddit.com**, insiderllm.com, medium.com, apxml.com, willitrunai.com, and most Docusaurus-based doc sites.

### Pitfall: Research notes vs. Published post

Compiled research documents (586-line markdown files with internal guidance, caveats-everywhere tone, "For public wording:" framing) are NOT ready to post. They are raw material. Transformation from research notes → definitive guide requires:

1. Strip all meta-language ("public wording", "megathread should", "recommend for users")
2. Pick ONE model (or scope tightly)
3. Get hard numbers: downloads, likes, VRAM, benchmarks
4. Reorganize into categories → catalog → quick-pick table
5. Rewrite every hedge into a direct recommendation

## Cross-Model Audit: Independent Critic via API

Before publishing any factual Reddit content (megathreads, answer comments, guides, workshop posts, comparison tables), run it through a DIFFERENT model for review. This catches errors that the drafting model misses.

**When to use:** Any public-facing content that makes factual claims.

**Preferred workflow: Nous Portal via `hermes chat`**

For Claude Fable 5 and other Anthropic models, use Nous Portal OAuth + CLI:

```bash
hermes chat \
 --provider nous \
 --model "anthropic/claude-fable-5" \
 --quiet \
 --no-restore-cwd \
 --source desktop \
 -q "$(cat ~/Desktop/critique-prompt.txt)" \
 > ~/Desktop/critique-output.txt 2>&1
```

This avoids API keys entirely — OAuth is handled by `hermes auth status nous`.

See `references/nous-portal-critic-workflow.md` for the full workflow.

**When to use another configured critic provider instead:** If you need a model unavailable through the configured Hermes Portal route, use the provider documented by the current Hermes installation. Do not embed provider credentials or credential-reading recipes in a public skill.

Use the exact model identifier reported by the currently configured Hermes provider. Verify availability through that provider’s documented interface before starting the critic pass. Keep provider authentication outside this public skill.

**Recommended sequence for model-variant megathreads:**

1. Draft the guide → save as `combined-refresh-v4.md`
2. Run Fable critique → `hermes chat --model anthropic/claude-fable-5 > critique.md`
3. Apply critique fixes → save as `combined-refresh-v4.5.md`
4. Push to the user's own GitHub mirror repo (if they maintain one) → clone it, copy the file in, commit, push
5. Verify the GitHub link works → `curl -sI <the pushed file URL>`
6. Publish on Reddit with working GitHub link

**Why push before Reddit:** The permanent GitHub mirror link must work on day one. Pushing after Reddit publication creates a broken link that erodes trust. The guide's credibility depends on the mirror being live when readers click it.

See `references/cross-model-audit-prompt.md` for the canonical audit prompt structure.

## Examples of Good Hooks

- "Welp, I think I've gone deeper than 99.9% of people into Hermes..."
- "The tool everyone's using wrong (and what to use instead)"
- "I stopped writing code and started writing prompts"
- "Your skill file is lying to you"

---

## Publication Pre-Flight

Three checks that catch real bugs before you post.

### Reddit URL format — always use `old.reddit.com` in megathreads

**Rule:** Every Reddit link you publish in a guide, megathread, or "See also" block must use `old.reddit.com/r/<sub>/comments/<id>/`. The trailing slug is optional — omitting it is fine and matches how readers find posts from a URL they paste.

**Why:** `www.reddit.com/r/<sub>/comments/<id>/` (bare, no slug) reliably bot-detects curl and headless scrapers — returning 403 or silently redirecting to Reddit home. A link that works in a logged-in browser fails every independent verification a reader runs, and the "broken link" report comes back as a bug.

| Form | Use for |
|---|---|
| `https://old.reddit.com/r/<sub>/comments/<id>/` | **Default for all Reddit URLs in guides.** Slug may be omitted. |
| `https://www.reddit.com/r/<sub>/comments/<id>/<full-title-slug>/` | Only when the URL already has the full slug from Reddit's share button. Don't hand-type slugs — must match Reddit's exact kebab-case. |
| ❌ `https://www.reddit.com/r/<sub>/comments/<id>/` (bare, no slug) | **Never.** Bot-detects; fails verification. |

**Single-switch recovery:** If a link audit reports "403" on a Reddit URL, rewrite it as `old.reddit.com/r/<sub>/comments/<id>/`. This pattern has flipped flagged Reddit links from broken to working in one batch edit.

### Reddit post body limit — 40,000 characters

Reddit's self-post body hard limit is **40,000 characters**. A 50KB draft passes local checks silently and hits the limit only on submit.

**Pre-check:**

```bash
wc -c path/to/draft.md
```

If over 40K, triage in preference order:

1. **Post as a threaded comment series** — main post is an intro + link to the GitHub mirror; paste each major section as a comment. Full content stays accessible, no truncation risk.
2. **Trim to 40K** — cut large tables (NVFP4 family, GPU/VRAM matrix) or move the detailed variant catalog to GitHub-only.
3. **Split into two posts** — e.g. "27B guide" + "35B guide" as separate posts with cross-links.

Do not discover the limit *after* hitting submit — Reddit's rejection is vague ("body too long").

### HuggingFace 401 is a wrong-name signal, not an auth failure

When `curl -sL https://huggingface.co/{owner}/{repo}` returns **HTTP 401**, do not assume the repo is gated or that credentials are missing. On HF model-card URLs, 401 commonly means the repo slug was guessed wrong — the error is identical either way, so it's a name-check, not a secret-check.

**Session-confirmed traps (Qwen3.6, July 2026):**

- Guessed `huihui-ai/Qwen3.6-35B-A3B-abliterated` → 401. **Canonical:** `huihui-ai/Huihui-Qwen3.6-35B-A3B-abliterated` (the author prefixes every 35B-A3B variant name with `Huihui-`)
- Guessed `DavidAU/Qwen3.6-27B-NEO-CODE-GGUF` → 401. **Canonical:** `DavidAU/Qwen3.6-27B-NEO-CODE-Di-IMatrix-MAX-GGUF` (the `-Di-IMatrix-MAX` suffix is load-bearing)

**Recovery — search the HF API, don't retry the URL:**

```bash
curl -s "https://huggingface.co/api/models?author=<owner>&search=<fragment>&limit=10" \
 | python3 -c "import json,sys; data=json.load(sys.stdin); [print(m['id'], m.get('downloads',0)) for m in data[:10]]"
```

Then `curl -sI` the canonical URL to confirm 200 before embedding it in a megathread. Run this on every HF URL in a link audit, even ones written by hand. HF repo-id names are easy to misremember; prefix/suffix/`-GGUF` suffixes all matter.
## Public support files

- `references/beginner-setup-guide-format.md`
- `references/community-aggregated-megathread-format.md`
- `references/compliance-to-readable-patterns.md`
- `references/cross-model-audit-prompt.md`
- `references/definitive-guide-format.md`
- `references/definitive-guide-reviews-section.md`
- `references/hermes-instruction-compliance-memory.md`
- `references/huggingface-card-benchmark-verification.md`
- `references/mac-mlx-research-data.md`
- `references/nous-portal-critic-workflow.md`
- `references/publication-artifact-critic-sequencing.md`
- `references/reddit-megathread-polish-workflow.md`
