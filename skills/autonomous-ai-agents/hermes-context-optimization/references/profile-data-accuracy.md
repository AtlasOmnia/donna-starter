# Profile Data Accuracy — Vague Labels Cause Downstream Hallucination

## The Problem

When user profile data uses vague, broad labels, downstream models fill in the gaps with speculation. This creates a cascade:

1. A model in any session (the assistant, another profile, or a model asked to analyze the user) reads the vague label.
2. The model extrapolates — it must, because "HK experience" could mean anything: finance, logistics, teaching, hospitality, import/export.
3. The extrapolation becomes an assertion in output. Another session may pick it up and compound it.
4. The user corrects it, but only in one session. The source data remains vague.

## Real Example

**Profile had:** "20 years HK experience"
**Model output:** "Bilingual? HK background suggests possible Cantonese/Mandarin" — and treated the experience as general business/regional context.
**Reality:** 20 years Hong Kong **housekeeping/hospitality** experience. Not bilingual Cantonese. Not general business.

**Fix:** "20 years Hong Kong housekeeping/hospitality experience"

## Rule

User profile labels must be specific enough that a model reading them cold cannot reasonably extrapolate into a wrong domain. If "HK experience" could mean 10 different careers, it's too vague. "HK housekeeping/hospitality experience" closes the gap.

## When to Act

- ANY time you see a vague label in profile data (memory, user profile, vault files), flag it and ask for specificity.
- When the user corrects a downstream model's speculation, trace back to the source label and fix it there — don't just correct the session output.
- Profile precision is a first-order defense against model hallucination. Memory compaction should never trade specificity for brevity.
