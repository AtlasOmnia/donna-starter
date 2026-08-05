# Reddit Megathread Polish Workflow

Use when a researched megathread is factually complete but reads bland, over-compliant, or like internal research notes.

## Trigger signals

- User says the draft is "bland," "too clinical," "too much like notes," or asks a second model to arrange it.
- Draft contains a research brief, evidence tables, critic checklist, and post draft all in one file.
- The post has good sources but weak Reddit-native framing.

## Workflow

1. Preserve the original research file.
2. Ask a reviewer model for structure and voice, not new facts:
 - diagnose why the post is bland
 - propose a stronger opening/hook
 - reorganize the section flow
 - rewrite the TL;DR table headings
 - identify what should move to a companion research brief
 - forbid invented claims and require official/community labels to stay intact
3. Split outputs into two files:
 - `<topic>_post_ready.md` — one clean publishable Reddit post
 - `<topic>_research_brief.md` — source list, evidence tables, duplicate check, critic notes, and verification caveats
4. In the post-ready version:
 - lead with the decision/problem, not the source list
 - use a direct hook within the first 3 lines
 - keep the TL;DR table near the top
 - use columns like `Your move / The case / The catch`
 - move status matrices and source apparatus near the bottom
 - keep inline source links for factual claims
 - explicitly label community apps/prototypes as community/unverified where appropriate
5. Re-add FAQ if trimming removed useful search-intent questions.
6. Verify links after rewriting, especially Reddit links via authenticated old-Reddit JSON when normal www links 403.
7. If a generic megathread verifier fails because the format is intentionally different, treat it as a style-specific check failure, not automatically a content failure; manually verify the requested requirements instead.

## Reviewer prompt pattern

```text
You are reviewing a public r/hermesagent megathread draft. Make it less bland and arrange the existing researched data into a stronger Reddit-native megathread. Do not invent facts. Preserve source links and official/community labels. Output: (1) structural diagnosis, (2) stronger arrangement/outline, (3) concrete rewrites for opening, TL;DR, decision table, and headers, (4) specific edits to apply. Keep factual audit secondary; focus on arrangement and voice while respecting evidence.
```

## Practical post structure

1. Hook / framing
2. TL;DR decision table
3. Interface or decision map
4. Highest-interest frontier section (voice, models, money, setup pain, etc.)
5. Architecture / safety / tradeoff section
6. Community field notes
7. Setup recipes
8. FAQ
9. Status matrix / source appendix
10. Bottom-line recommendation

## Tone moves that worked

- "There is no official X. That has not stopped anyone."
- "The useful question is not which app wins; it is which workflow fits without wrecking privacy, reliability, or sanity."
- Use memorable headers: `The Boring Workhorse That Ships`, `Phone Access Means Phone Risk`, `Where Does the Agent Live?`
- Keep the wit tied to real tradeoffs, not random jokes.
