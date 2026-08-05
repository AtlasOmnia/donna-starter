# Prompt Composition Baseline (post-audit)

High-level shape of the initial prompt before heavy optimization:

- AGENTS.md: ~8.5KB / ~190 lines (too long; compressed to ~5.5KB).
- Skills list: 67 skills → now ~55 after dedup (multi-profile, planning, computer-use merged).
- Memory/user profile: both were near-capacity with redundant entries; targeted compression planned but blocked by tool-call guardrail loop (see pitfall below).

Key drivers of prompt size:
- Tool schemas (~11–13k tokens) dominate.
- Skill index contributes ~2–5k depending on count and description length.
- AGENTS.md, memory, user profile add ~2–4k combined; highly compressible.

Actionable rules (from live audit):
- AGENTS.md: keep only decision-critical policy; move detailed workflows into:
 - ~/.hermes/docs/hermes-update-guide.md
 - ~/.hermes/docs/config-locations.md
- Skills: merge overlapping class-level skills aggressively.
- Memory/user profile: compress duplicates; store procedure-heavy detail in skills, not memory.

Pitfall (memory tool):
- The memory tool requires an explicit action field; calling it without one triggers a hard loop and can block further optimization steps. Use terminal or direct file inspection to read current entries when the memory tool is behaving unreliably or triggering guardrails.
