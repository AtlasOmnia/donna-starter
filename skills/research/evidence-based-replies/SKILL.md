---
name: evidence-based-replies
description: evidence-based-replies — Compare a person's claim to a cited paper or source, isolate what the evidence actually supports, and draft concise replies that correct overreach without sounding evasive.
version: 1.0.0
created_by: agent
---
# Evidence-Based Replies

Use this skill when the user wants to:
- compare someone's claim to a research paper, benchmark, article, or repo README
- draft a reply that corrects a misunderstanding of the evidence
- separate "the source supports X" from "the source does not support Y"
- turn a source-comparison into a Reddit/X/forum-ready response

## Core principle
Do **not** stop at summarizing the source. The deliverable is usually the **distinction**:
1. what the source actually establishes
2. what stronger conclusion the other person is trying to import into it
3. why that leap does not follow

If the user is asking for a reply, the misunderstanding of the evidence must be addressed explicitly, not left implicit.

## Default workflow
1. Read the conversation/claim carefully.
2. Extract the **specific proposition** the other person is asserting from the source.
3. Read the cited source.
4. Split findings into:
 - **Supported by the source**
 - **Not established by the source**
 - **Reasonable but unproven extrapolations**
5. Compare the source type:
 - empirical paper
 - benchmark paper
 - opinion/design README
 - repo guidance / author doctrine
6. Draft the response around the distinction, not around vague disagreement.

## Required output shape
When explaining the comparison, prefer this structure:
- "The paper/source does show ..."
- "What it does not show is ..."
- "That is the step I disagree with."
- "So my criticism is not X; it is Y."

This pattern prevents straw-manning and keeps the correction precise.

## Writing guidance for this user
the user prefers concise, practical responses. For forum replies:
- lead with the misunderstanding, not with throat-clearing
- avoid generic "both sides have a point" filler
- make the inferential gap explicit
- distinguish directionally true claims from overclaims
- prefer operational language over academic hedging

If he says a draft "needs to address the misunderstanding of the research," revise around the evidentiary gap immediately.

## Pitfalls
- **Do not equate "source says style matters" with "source proves this specific implementation is better."**
- Do not let a repo README or manifesto carry the evidentiary weight of a paper.
- For software/config claims, prefer current upstream docs and source code over stale third-party guides; explicitly label stale or unverified config paths instead of treating all cited paths as current.
- When fact-checking a complaint, distinguish: true current behavior, stale terminology, fair UX criticism, and rhetorical overclaim. Do not collapse those into a simple true/false verdict.
- Do not answer only at the concept level if the user needs a postable reply.
- Do not bury the key distinction in paragraph four.
- Do not over-hedge once the inferential error is clear.

## Heuristic: evidence ladder
From strongest to weakest:
1. direct empirical finding in the cited paper
2. constrained implication from that finding
3. plausible implementation guess
4. repo philosophy / author preference

Label which rung the person's claim sits on.

## Forum-ready reply recipe
For Reddit/X/forum use:
1. Sentence 1: identify the misunderstanding.
2. Sentence 2: state what the paper actually supports.
3. Sentence 3: state what it does not support.
4. Sentence 4+: tie back to the concrete artifact under debate.

- `references/research-overclaim-patterns.md` — session-derived example of correcting a paper-based overclaim in a SOUL.md / persona-file debate.
## Public support files

- `references/research-overclaim-patterns.md`
