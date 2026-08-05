# Compliance-to-Readable Transformation Patterns

Concrete before/after examples from rewriting a bland workplace-enterprise compliance megathread into a Reddit-native post. These are the micro-moves that make the difference, not just structural rearrangements.

## Title transformation

**Before:** `Hermes at Work: Enterprise, IT Approval, Shadow AI, and Compliant Alternatives`
**After:** `Hermes at Work: How Not to Get Fired for Using an AI Agent`

Pattern: replace keyword soup with a single sharp consequence. The reader already knows the topic — the title's job is to make them stop scrolling.

## TL;DR: bullets → decision table

**Before:** A wall of 12 hyphenated bullet points starting with "If IT/security says no, do not bypass them."

**After:** A 5-row table:

| Your situation | Your move |
|---|---|
| IT already said no | Do not bypass them. Use approved tools or ask for a scoped pilot. |
| You want to try it with public data | Safest starting point. Still keep it off company systems. |

Pattern: the reader is in a *situation* and needs a *move*. Name both. This turns passive advice into active guidance.

Close the TL;DR with a one-line bottom line: "If your setup would sound bad in one sentence to security, stop."

## Fast-path section before deep explanations

Add a "Two-Minute Decision Tree" section immediately after the TL;DR. Structure as numbered questions with clear branches:

1. Has IT approved this? → Yes/No/Explicit no → action
2. What data will Hermes see? → Public/Internal/Regulated → risk level
3. What can Hermes do? → Draft-only/Read-only/Terminal+accounts → required gates
4. Where does processing happen? → Local/Direct/Router/Portal → check needed

This lets people who know their answer at step 1 stop reading. The deep dive sections serve the people who need to build a case.

## Section header voice

**Before:** "B. Why IT/security may object" / "D. 'IT said no' — what to do instead"
**After:** "Why IT Says No — And Why They Are (Often) Right" / "IT Said No. Now What."

Pattern: question → answer framing, conversational but not cute. Drop the letter prefixes — this is not an ISO document.

## Risk matrix: add consequence columns

Don't just list use cases. Add columns that tell a story:

| Use case | Hermes-safe pattern | The catch | Human gate needed? |
|---|---|---|---|

The "catch" column does the heavy lifting — it acknowledges the tradeoff without hedging the recommendation. The "human gate needed?" column puts responsibility where it belongs.

## Merge overlapping sections

When two sections both cover "here are architecture patterns and what they solve," merge them into one compact table. The original had "G. Lower-risk architecture patterns" AND the DeepSeek version added "Enterprise-safe architecture patterns." One table with columns `Pattern | What it solves | What it does NOT solve` does both jobs in half the space.

## Wit tied to tradeoffs, not decoration

- "Do not turn this into a spy movie. You are trying to use an automation tool, not evade a hostile regime."
- "Boring is good. Boring keeps you employed."
- "This is not pedantic — it is the difference between a pilot pitch and an HR meeting."

Every joke makes a real point about risk, compliance, or boundaries. Random humor without a tradeoff underneath is dead weight.

## Opening hook formula

Lead with what the reader wants, then immediately confront them with the tension:

> You want to run Hermes at work. It can read your files, automate your browser, reply to emails, schedule jobs, and remember context across sessions. It is, in other words, exactly the kind of tool your IT department wants to say no to.

Structure: desire → capability → tension. Three sentences max before the reader understands the stakes.

## FAQ signoff

End the FAQ section with the hardest question ("What if my company says 'AI-first' but blocks Hermes?") — not the softest. The last FAQ answer is what lingers.
