---
name: hermes-nightly-self-check-decisions
description: hermes-nightly-self-check-decisions — Record decisions from nightly self-check findings so behavior is consistent.
category: automation-governance
version: 1
triggers:
- hermes nightly self-check
- nightly self-check
- self-check decision
---
# Hermes Nightly Self-Check — Decisions Log

Purpose: Record decisions made from hermes-nightly-self-check findings so behavior is consistent across sessions.

## How to record

Each entry captures one finding and the decision it produced. Use this format:

```markdown
### YYYY-MM-DD — Short issue title (Issue #N)
- Issue: What the self-check flagged — the symptom, where it came from, and why it happened.
- Decision: The rule or fix chosen, stated so a future session can apply it without re-litigating.
```

Rules:
- One entry per finding; append chronologically under Decision history.
- Write the decision as an executable rule (what to do), not a description of what was done.
- If the finding is resolved by a change to config, skills, or process, note where that change lives so the next check can verify it.
- Do not record credentials, tokens, or private paths in the log — reference locations by role (for example "the primary model endpoint" or "the profile config") instead.
- If the same class of finding recurs, the decision should tighten the check or the rule, not just repeat the note.

## Decision history

### Starter template (Example #1)
- Issue: Nightly check flagged a mismatch between two config locations for the same setting.
- Decision: Keep one location canonical; document the relationship so future checks do not flag it as a conflict.

### Setup flow (Example #2)
- Issue: A tool call failed because an argument was passed as null.
- Decision: Always specify an explicit value; never pass null or omit the argument. Default to the safest explicit value when unsure.
