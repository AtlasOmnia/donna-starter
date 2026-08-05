# OpenRouter Independent Critic Workflow

Canonical workflow for sending a draft to an independent model (Anthropic Claude 3.5 Sonnet via OpenRouter) for pre-publication review. Used when the user says "have Fable critique this" or "have Sonnet review before posting."

## Model IDs (authoritative — copy exactly)

OpenRouter returns 404 if the model identifier is wrong. Current stable IDs as of July 2026:

| Critic | OpenRouter ID | Notes |
|---|---|---|
| Claude Fable (3.5 Sonnet) | `anthropic/claude-3.5-sonnet` | NOT `anthropic/claude-fable` — that 404s |
| Claude Sonnet 4 | `anthropic/claude-sonnet-4` | Newer, more expensive |
| Claude Opus 4 | `anthropic/claude-opus-4` | Flagship, highest cost |

If OpenRouter's model list changes, verify with `curl -s https://openrouter.ai/api/v1/models | grep '"id"'`.

## API Key Locations (search order)

1. `~/.hermes/.env` → `OPENROUTER_API_KEY=sk-or-...`
2. Environment variable from Hermes session launch
3. Prompt user to set it — never fabricate a key

Load via:
```python
from pathlib import Path
env = Path.home() / '.hermes' / '.env'
for line in env.read_text().splitlines():
    if line.startswith('OPENROUTER_API_KEY='):
        api_key = line.split('=', 1)[1].strip()
        break
```

Do NOT source the .env file (`source ~/.hermes/.env`) in subprocess — the export doesn't propagate to child Python. Load the file directly in Python.

## Canonical Prompt Shape

```
You are an independent critic (Claude 3.5 Sonnet via OpenRouter) reviewing
a [POST TYPE] draft about [TOPIC] for [AUDIENCE].

Your task:
1. Read the entire post carefully
2. Identify factual errors, outdated claims, inconsistencies, or misleading statements
3. Check if claims about benchmarks are accurate or contradict each other
4. Verify that the [specific table/section claimed to be hard] is honest and complete
5. Look for missing comparisons or important context that would help readers choose
6. Check if the tone is appropriate for [AUDIENCE] (technical but accessible to beginners)
7. Identify statements that could mislead beginners or advanced users
8. Note formatting issues or structural problems

Output format:
- List each issue with section/heading and quote from the file
- Explain why it's a problem
- Suggest a specific fix
- Rate overall quality 1-10
- Final verdict: READY FOR REDDIT / NEEDS REVISION / NEEDS MAJOR WORK

Be thorough but fair. No praise — just honest technical feedback.

--- BEGIN POST ---
[draft content]
--- END POST ---
```

**Post-type-specific prompts:**
- Megathreads / variant guides: emphasize benchmarks, catch columns, NVFP4 caveats
- Workshop posts: emphasize whether hook lands, whether the copy-paste prompt works
- Website copy: emphasize SEO, tone, whether claims match the business's service-area positioning
- Community FYI posts: emphasize whether the system's "what it CAN'T do" is clear

## HTTP Call (Python reference)

```python
import requests, time, json
from pathlib import Path
from datetime import datetime

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:3000",  # required for OpenRouter
    "X-Title": "Critique Request",
}
payload = {
    "model": "anthropic/claude-3.5-sonnet",
    "messages": [{"role": "user", "content": full_prompt}],
    "temperature": 0.7,
    "max_tokens": 4000,
}

start = time.time()
response = requests.post(url, headers=headers, json=payload, timeout=180)
elapsed = time.time() - start
result = response.json()
```

Handle 404 as "model ID not found" — check the ID list above.

## Mandatory Preservation Block

ALWAYS save the critique to disk with this metadata header. The user reads these as audit artifacts, not throwaway notes:

```markdown
# Independent Critique: [POST TITLE / FILENAME]

**Model:** Anthropic Claude 3.5 Sonnet (Fable) via OpenRouter
**Model ID:** anthropic/claude-3.5-sonnet
**File Reviewed:** <absolute path>
**File Size:** N bytes, N lines
**Timestamp:** <ISO 8601>
**Response Time:** N.NN seconds

## Usage
- Prompt tokens: N
- Completion tokens: N
- Total tokens: N
- Estimated cost: $N.NNNN

## Critique Contents
[body of critique verbatim]

## Notes
- Pure critic read, no drafting context provided
- Raw request: model=anthropic/claude-3.5-sonnet, temp=0.7, max_tokens=4000
- Response ID: <from JSON result>
```

Save to `<original-filename-without-ext>_critique_fable.md` on Desktop (e.g., `megathread_critique.md`).

## Post-Critique Verification (mandatory)

1. Read the critique. Separate grounded findings from hallucinated ones.
2. For each issue the critic raised:
   - If the critic cites a specific line/quote → verify it still exists in the draft
   - If the critic claims something is factually wrong → verify against the primary source (HF card, Reddit thread, API)
   - If the critic invents a detail (model doesn't exist, benchmark number never claimed) → IGNORE
3. Apply only grounded fixes. Document:
   - Fixes applied: [list]
   - Fixes skipped with reason: [list]

The user has explicitly said: "critic findings should be independently verified against primary sources before implementation." Don't auto-apply critic output.

## Common Critic Hallucination Patterns

Watch for these specifically and always verify:

- **Benchmark regression claims**: "X variant scores 67% SWE-bench" — verify the number is actually in the card, and that the comparison base is correct
- **KL divergence numbers**: critic may invent a KL value. Verify against the model card (llmfan46 Heretic v2 = 0.0021, DavidAU Heretic = 0.0469, huihui-ai doesn't publish KL)
- **Model IDs that don't exist**: critic may mention a model that was never released
- **Download counts**: critic may quote stale HF numbers — re-pull the HF API for current stats
- **Availability claims**: if the critic says "model X isn't free anymore" or "model X was added," verify against the live OpenRouter API

## Cost Budget

Claude 3.5 Sonnet via OpenRouter: ~$3/M input, ~$15/M output (July 2026 rates). For a 38KB megathread draft + 2K response = ~$0.13 per critique. Cheap, but don't run 10 critiques per draft — one good critic pass is the threshold.
