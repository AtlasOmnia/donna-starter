# Nous Portal Independent Critic Workflow

Alternative critic path using Nous Portal OAuth + `hermes chat` CLI. Preferred when the user says "have Fable critique this" because `anthropic/claude-fable-5` is available on Nous Portal (not on OpenRouter, which returns 404 for that model ID).

## When to Use

- User explicitly asks for Fable (Claude Fable 5)
- The requested model is unavailable through the configured Hermes Portal route
- OAuth is already configured (`hermes auth status nous` shows "logged in")

## Command

```bash
hermes chat \
 --provider nous \
 --model "anthropic/claude-fable-5" \
 --quiet \
 --no-restore-cwd \
 --source desktop \
 -q "$(cat <<'PROMPT'
You are an independent critic (Fable, Claude Fable 5 via Nous Portal) reviewing a [POST TYPE] draft about [TOPIC] for [AUDIENCE].

Read the file at ~/Desktop/[FILENAME].md and produce a structured critique.

Focus on:
1. Factual accuracy: Are benchmark claims (SWE-bench, AIME, etc.) accurate and internally consistent? Are there contradictions between sections (e.g., different download counts for the same model in different places)?
2. Clarity and readability: Is it accessible to beginners while still useful for advanced users? Are headings and tables navigable?
3. Completeness: Are there missing model variants, important caveats, or comparisons that would help readers choose between options?
4. Tone: Is it appropriate for [AUDIENCE]? Technical but accessible.
5. [SPECIFIC CHECK] honest? Does the [specific table/section] honestly describe tradeoffs?
6. [SPECIFIC CAVEAT] clear to [specific user group]?
7. Download counts: Verify consistency — same model cited with different numbers?
8. Overall quality 1-10 with final verdict (READY / NEEDS REVISION / NEEDS MAJOR WORK).

Be specific — cite line numbers or section headings. Be direct and constructive, not praising. Honest technical feedback.
PROMPT
)" \
 > ~/Desktop/[OUTPUT_FILE]_critique_fable.md 2>&1
```

## Key Flags

| Flag | Purpose |
|---|---|
| `--provider nous` | Use Nous Portal OAuth (no API key needed if `hermes auth status nous` shows logged in) |
| `--model "anthropic/claude-fable-5"` | Claude Fable 5 — the model the user asked for |
| `--quiet` | Suppress banner/spinner for programmatic output |
| `--no-restore-cwd` | Prevent directory changes from breaking the prompt |
| `--source desktop` | Set source for audit trail |
| `-q "$(cat <<'PROMPT' ... PROMPT )"` | Single query with heredoc prompt (avoids shell escaping issues) |

## Authentication

Requires an already authenticated Hermes Portal session. Do not read, print, or embed credential files or API keys in a public skill. If authentication is missing, stop and use the user's normal Hermes authentication flow.

## Example: Qwen 3.6 Megathread Critique

```bash
hermes chat \
 --provider nous \
 --model "anthropic/claude-fable-5" \
 --quiet \
 --no-restore-cwd \
 --source desktop \
 -q "$(cat <<'PROMPT'
You are an independent critic (Fable, Claude Fable 5 via Nous Portal) reviewing a Reddit megathread draft about Qwen 3.6 model variants for r/hermesagent.

Read the file at ~/Desktop/qwen36-combined-refresh-v4.md and produce a structured critique.

Focus on:
1. Factual accuracy: Are benchmark claims (SWE-bench, AIME, etc.) accurate and internally consistent? Are there contradictions between sections (e.g., different download counts for the same model in different places)?
2. Clarity and readability: Is it accessible to beginners while still useful for advanced users? Are headings and tables navigable?
3. Completeness: Are there missing model variants, important caveats, or comparisons that would help readers choose between options?
4. Tone: Is it appropriate for r/hermesagent? Technical but accessible.
5. Catch table honest? Does the 'Catch' column in the Quick Pick Table honestly describe tradeoffs?
6. NVFP4 caveats clear to non-Blackwell users?
7. Download counts: Verify consistency — same model cited with different numbers?
8. Overall quality 1-10 with final verdict (READY / NEEDS REVISION / NEEDS MAJOR WORK).

Be specific — cite line numbers or section headings. Be direct and constructive, not praising. Honest technical feedback.
PROMPT
)" \
 > ~/Desktop/qwen36_megathread_critique_fable.md 2>&1
```

## Post-Critique Verification (mandatory)

Follow the same verification steps as the provider-neutral critic workflow:
- Separate grounded findings from hallucinated ones
- Verify benchmark claims against primary sources (HuggingFace model cards, Reddit threads, live APIs)
- Apply only grounded fixes, document skipped fixes with reasons

## Common Critic Hallucination Patterns

Provider-neutral critic checks:
- Benchmark regression claims (verify the number is in the card and the comparison base is correct)
- KL divergence numbers (verify against model card — llmfan46 Heretic v2 = 0.0021, DavidAU Heretic = 0.0469)
- Model IDs that don't exist
- Download counts (re-pull HF API for current stats)
- Availability claims (verify against live API)

## Cost

Nous Portal: included with subscription, no per-token cost for OAuth users.
