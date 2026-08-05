# Beginner Setup Guide Format

Variant of the community-aggregated megathread for step-by-step onboarding content. Use when the goal is "get from zero to working agent" rather than "synthesize 15+ threads into a dimensional deep-dive."

## When to use

- The post is a linear tutorial (install → configure → use)
- Audience is complete beginners (no assumed AI/terminal knowledge)
- The structure follows a chronological setup path

## Structure

```
[SEO-OPTIMIZED TITLE — question format, year-stamped, brand name]
[GitHub mirror link + internal cross-links row]

LAST UPDATED: [date]
Covers: [version] + community threads from [range]

---

[ONE PARAGRAPH — what, who for, time-to-value claim]
[Include "by Nous Research", version, "under 20 minutes"]

---

## TL;DR — The 5-Minute Quick Start
[One table: Decision | Community Pick | Why]
[Include: install method, first setup path, first model, where to ask for help, first command to type, troubleshooting command]

## Jargon Buster
[Optional but recommended: 6-8 row table of technical terms in plain English]
[Include: LLM, API key, VRAM, Provider, Gateway, Profile, Tool calling]

## Part 1: Installation
[Two paths: Desktop installer (recommended) + CLI-only]
[OS-specific notes table: platform | command | watch-for]
[Exact commands, not descriptions]

## Part 2: Model Selection
[Decision tree (ASCII art)]
[Community consensus table: Model | Type | Cost | Tool-Calling | Verdict]
[Critical warning about model size thresholds]

## Part 3: Essential Tools
[Day 1 tools to enable, with exact commands]
[Why each one matters (one sentence each)]
[The #1 beginner trap + fix]

## Part 4: Common Pitfalls
[5+ numbered pitfalls]
[Each: Symptom → Fix → Community thread link]
[Most common first]

## Part 5: Profiles
[What they are, when to create, community philosophy]
[Key commands block]

## Part 6: Interfaces
[Desktop vs CLI vs TUI comparison table]
[Desktop app features list]

## Part 7: Gateway / 24/7 Setup
[Commands to install and run the gateway]
[OS-specific persistence tips]

## Part 8: FAQ
[10-15 questions, every one traceable to a real thread]
[Link to related megathreads where applicable]

## Part 9: Sources & Threads
[Community threads, official sources, external guides — grouped]

## Part 10: Knowledge Table
[23+ row reference table: Category | Item | Description | Best For | Watch For]
[This is an appendix — comes AFTER sources]

## Related Megathreads
[Table: Megathread | Best If You Want To... with 4-6 entries]

## Closing
[One-line contribution invitation]
[GitHub mirror link repeated for indexing]
[Last refreshed date]
```

## Jargon Buster

For any beginner guide, include a short glossary early (after TL;DR). Define: LLM, API key, VRAM, Provider, Gateway, Profile, Tool calling. Keeps the rest of the guide readable without inline definitions.

## Pitfalls naming

When referencing a community-named pitfall (e.g., "fetus in fetu"), keep the community name but add a plain-English parenthetical: `The "Fetus in Fetu" Install (Nested/Double Installation)`. Preserves the inside joke while keeping it accessible.

## Verification

Same as community-aggregated format: run a verify-megathread helper if the user has one (user-local). The checker handles KT detection whether it's Part 9 or Part 10.
