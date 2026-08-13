# Cross-Model Audit Prompt (Reusable)

Use this prompt with `delegate_task` to have a different model audit a megathread draft before publishing.

## Prompt Template

```
Audit the megathread at <FILE_PATH> for factual accuracy, completeness, and currency against Hermes Agent <VERSION> (<DATE>).

Return a structured review:
(a) ERRORS with specific line-level fixes — wrong commands, paths, version claims
(b) MISSING critical content a beginner/reader would need
(c) OVERSTATEMENTS or misleading recommendations to soften
(d) SEO effectiveness of title and opening paragraph
(e) Internal link quality and coverage
(f) Overall verdict: ready / minor-fixes / needs-rework
```

## Example Dispatch

```python
delegate_task(
 goal="Audit the megathread at <PATH> for factual accuracy, completeness, and currency against Hermes Agent v0.18.0 (July 2026). Flag any errors, missing critical content, overstatements, and SEO issues. Return a structured review with specific line-level fixes.",
 context="The file is a draft Reddit megathread. Read it fully, cross-check against what you know about the current version, and return ERRORS, MISSING sections, OVERSTATEMENTS, and overall verdict."
)
```

## Post-Audit Workflow

1. Read the full subagent output (it may be truncated in the inline summary — use the saved file path)
2. Apply grounded fixes; ignore hallucinated criticisms
3. Re-run the verify-megathread helper if the user has one (user-local)
4. Push updated GitHub mirror
5. Report changes applied vs. skipped to the user

## Dispatch Methods (Two Paths)

### Path A: delegate_task (uses configured delegation model)

Simplest path. The subagent inherits whatever model is configured in `delegation.model`/`delegation.provider` in config.yaml.

```python
delegate_task(
 goal="Audit the megathread at <PATH> for factual accuracy...",
 context="The file is a draft Reddit megathread..."
)
```

**Limitation:** You cannot override the model per-call. If the configured delegation model is the same family as your primary model, you won't get a truly independent review.

### Path B: hermes chat (explicit model override)

Use when you need a SPECIFIC model for review that differs from the configured delegation model. This runs as a background terminal process.

```bash
hermes chat -q "Read <FILE> and audit it. ..." \
 --model claude-sonnet-4 \
 --provider openrouter \
 2>&1
```

Run with `background=true` and `notify_on_complete=true` so you can keep working while the review runs.

**When to use which:**
- Path A first (delegate_task) — fast, uses existing config
- Path B for the second review — explicitly requests a different model family (e.g., Anthropic if first review was DeepSeek)

### Minimum Two-Review Protocol

1. **First pass (technical):** deepseek-v4-flash via delegate_task — factual errors, missing content, overstatements
2. **Second pass (tone/structure):** claude-sonnet-4 via `hermes chat` — readability, flow, beginner-friendliness
3. Apply grounded fixes from both; report to the user which were applied and which were skipped (with reasons)

**Anti-pattern:** Only running one review. The first reviewer always misses something the second catches. Two different model families with different strengths (DeepSeek = detail-oriented, Claude = tone/structure) is the proven combination from July 2026.

## Timeout / fallback + review authorization

- If the audit delegate times out or returns nothing, run the factual audit inline against the agent transcript instead, and note the fallback.
- Keep the two-review principle when a second model is reachable, but treat it as best-effort.
- Use only the provider and authentication route already configured for the current Hermes installation. Do not add credential-reading or provider-switching recipes to a public skill.
- When authorized, split the audit by cost: an expensive critic for tone/SEO/optics, a cheap model for mechanical link/reference checks.
- Credential policy: never read `.env` or connected-account files directly; rely on the configured provider routes.

## Reddit JSON extraction (for Community Verdicts sections)
When pulling real comment signal from r/LocalLLaMA / r/localllm / r/hermesagent to add ranking/verdict quotes to a guide:
- The direct `requests.get('<post-url>.json')` path from terminal now returns NO data (unauthenticated-style throttle or endpoint change as of July 2026). Do NOT retry that path.
- Use `browser_navigate` to `<post-url>.json` with the Safari session — it returns raw JSON as page text reliably. The full snapshot is saved to a cache file; read that file to extract the OP selftext + top comments (walk the `replies` tree, filter by score > 3, sort by score desc, take top 6).
- Reading `.env` directly in the default profile is blocked by credential policy. Do not retry another general-execution tool; route the authorized critic through the approved credential-aware profile or Nous Portal OAuth path.
- For the cheaper mechanical link/reference check, delegate a cheap leaf agent with the draft path + a link-list file; its job: confirm every HF URL resolves (200), counts match their own repo, the Quick-Pick/VRAM tables reference real listed variants, and "Notable Absences" doesn't contradict a listed variant. Report CLEAN or a specific mismatch list; do NOT edit the draft.
