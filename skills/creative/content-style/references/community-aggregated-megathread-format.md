# Community-Aggregated Megathread Format

## When to use

Use when building a megathread that synthesizes community questions + external research into one post. Different from:

- **Tier/Reference Guide** (Format A): single-dimension comparison (e.g., hardware tiers only)
- **Definitive Model-Variant Guide** (Format B): one model, exhaustive variant catalog

This format is for posts like "Everything the community knows about running Hermes on Mac" — multiple dimensions (models, backends, pitfalls, setups, configs) aggregated from 15+ threads and external sources.

## Structure

```
LAST UPDATED: [date]

[ONE PARAGRAPH scope statement — what this covers, how many threads sourced]

---

## TL;DR — Quick Reference Table
[The entire answer in one table. Hardware tier × model × backend × why. Readers get 80% from this.]

---

## [Dimension 1 Deep-Dive — e.g., Backends]
[Comparison. Setup commands. Known bugs with exact issue numbers. Community quotes.]

---

## [Dimension 2 Deep-Dive — e.g., Models]
[Per-model: specs, best quants, sampling configs, community experience, download links]

---

## Critical Pitfalls
[Numbered. Each: headline → hard data/reproduction → fix. Source GitHub issues and community quotes.]

1. [Pitfall Name] — [One-line description]
[HARD DATA from issue tracker or benchmarks]
[FIX — concrete commands]

---

## What the Community Is Actually Running
[Table: User | Hardware | Model | Speed | Notes]
[Every entry from a real Reddit comment. Date the post.]

---

## Setup Commands
[Copy-paste terminal block for Hermes config]

---

## FAQ — Real Questions from r/[subreddit]
[12+ entries. Every one traceable. Community quotes where valuable.]

---

## Decision Matrix
[Table: You Want... | Use This | Avoid]

---

## [Optional: Sampling/Config Quick Reference]
[Table with model-specific sampling recipes]

---

## Sources
[Grouped: Reddit threads, GitHub issues, articles. URLs + dates.]

---

## Contribute
[One-line invitation to add to the megathread]
*Last refreshed: [date].*
```

## Section ordering

1. **TL;DR table first** — no intro paragraphs before it. The table IS the post.
2. **Deep-dives second** — one per dimension (backends, then models, usually). Each includes: description → setup → known bugs → community quotes.
3. **Pitfalls third** — after readers know what to use, tell them what will break.
4. **Community setups fourth** — real data validates the recommendations above.
5. **FAQ fifth** — answers the long tail of questions.
6. **Sources + Knowledge Table last** — after all prose sections. Sources first (100% of threads cited), then Knowledge Table (quick-reference appendix). The Knowledge Table is reference material, not narrative — putting it before Sources breaks the reading flow and buries attribution.

## Key principles

- **Every claim traces to a source.** If it's from a GitHub issue, cite the number. If it's community sentiment, quote the user. If it's your estimate, mark it.
- **Hard data beats vibes.** "Baseline 25.3 tok/s → MTP 1.93 tok/s" beats "MTP is slower."
- **Pitfalls get their own numbered section.** Don't bury warnings in recommendations — surface them prominently.
- **FAQ entries must be real questions.** Every entry maps to an actual subreddit thread.
- **Sources grouped by type.** Reddit threads, GitHub issues, articles — separate lists. Makes verification easy.
- **Target 300-400 lines, 18-22KB.** Dense but scannable.
- **The TL;DR table should answer "what should I download?" in 5 seconds.**

## Anti-patterns

- Burying the quick-reference table after 3 paragraphs of intro
- Hedging every recommendation ("might work," "some users prefer") — pick a winner
- FAQ entries that are invented, not sourced from real threads
- Sources listed as one undifferentiated blob
- No decision matrix — readers have to read the whole post to make a choice
- Skipping negative community experiences — include the "M4 Max 36GB still has tool amnesia" alongside the success stories
- Placing the Knowledge Table before Sources — it's reference material, not narrative

## SEO Principles (mandatory for Reddit megathreads)

1. **Title as searchable question/guide.** "How to Set Up Hermes Agent from Scratch (2026 Beginner Guide)" beats "Hermes Setup Megathread." Reddit ranks in Google Discover; question-format titles capture search intent.
2. **GitHub mirror for permanent indexing.** Every megathread gets a markdown copy in the `hermesagent-megathreads` repo (or equivalent). Reddit posts fade; GitHub files are permanently indexed by Google. Mirrors sustain ~2x visits after the spike fades. Link the mirror at the top of the post.
3. **Internal cross-linking.** Link between related megathreads to boost dwell time. Add an "Also see" row at the top and a "Related Megathreads" table near the bottom. Every internal link should have a one-line "Best if you want to..." description.
4. **Opening paragraph SEO.** Include the brand name ("Hermes Agent by Nous Research"), the version ("updated for v0.18.0"), and a time-to-value claim ("under 20 minutes") in the first paragraph. Google weights early-page content higher.

## Pre-Publication Review (mandatory for megathreads)

Before publishing, run the draft through at least TWO different model families as critics. This catches different classes of issues:

1. **First pass (technical):** Use a detail-oriented model (e.g., deepseek-v4-flash) to audit for factual errors, missing content, overstatements, and version currency.
2. **Second pass (tone/structure):** Use a different model family (e.g., claude-sonnet-4) to audit for tone, readability, structure, and beginner-friendliness.

Apply grounded fixes from both reviews. Ignore hallucinated details. Different models will flag different things — if both independently flag the same issue, it's real.

**Anti-pattern:** Publishing after only one model review. The first reviewer will always miss something the second catches (and vice versa).
