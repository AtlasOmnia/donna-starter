# OpenRouter Free-Tier Verification (mandatory for model/API megathreads)

The free tier on OpenRouter contracts monthly. Models a prior month's post listed as free routinely move to per-token pricing. Between June and July 2026, all of these went PAID (no `:free` variant on the live API): Owl Alpha, DeepSeek V4 Flash, DeepSeek V4 Pro, gpt-oss-120b, Llama 3.3 70B, Llama 3.2 3B, Hermes 3 405B, and the LFM2.5 family. The June 2026 megathread listed every one of those as free — so a refresh that copies the prior post's assumptions ships factually wrong "free" claims.

## Rule
Never trust the OpenRouter collection page or the previous post's model list. Verify against the **live API** before writing any "free" claim.

## Recipe
```bash
curl -s "https://openrouter.ai/api/v1/models" | python3 -c "
import sys, json
data = json.load(sys.stdin)
models = data.get('data', data if isinstance(data, list) else [])
free = [m for m in models
 if m.get('pricing',{}).get('prompt')=='0'
 and m.get('pricing',{}).get('completion')=='0']
print('FREE COUNT:', len(free))
for m in free:
 print(m.get('id'), '| ctx', m.get('context_length'),
 '| in', m.get('architecture',{}).get('input_modalities'))
"
```
A model is free ONLY if BOTH `pricing.prompt` and `pricing.completion` are exactly the string `'0'`. The base model ID (e.g., `deepseek/deepseek-v4-flash`) is paid; the `:free` suffix variant (`...:free`) is the free one — check the specific ID, not the family name.

## When a research subagent times out
OpenRouter free-tier verification via a web-research subagent can hit the 600s timeout (happened July 2026 — the agent timed out, the gap was covered by a direct API pull). The direct curl/python pull above is faster and authoritative. Prefer it over re-dispatching.

## Pitfall: critic hallucination on availability
Both cross-model audit passes can invent model-availability claims — e.g., "Qwen3 Coder 480B is now free", "Elephant Alpha is free", or specific "going away July X" banner dates. These are frequently FALSE against the live API (the banner dates are UI-only and unverifiable from JSON; the "now free" claims contradict the `:free` check). Re-verify EVERY availability claim a critic makes against this API pull before applying the fix. Apply only substantiated fixes.
