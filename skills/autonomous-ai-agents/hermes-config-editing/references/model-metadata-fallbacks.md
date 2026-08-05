# Model Metadata Context Length Fallbacks

Source: `agent/model_metadata.py` line ~230-296

When `context_length: auto`, Hermes resolves the actual value through this chain:

1. **Exact model match** — specific model ID in `MODEL_CONTEXT_LENGTHS` dict
2. **Family fallback** — partial name match against `FAMILY_CONTEXT_LENGTHS`
3. **Default** — 131072 if nothing matches

## Family fallbacks (`FAMILY_CONTEXT_LENGTHS`)

| Family | Context Length | Notes |
|--------|--------------|-------|
| qwen | 131072 | Catches any model with "qwen" in name |
| llama | 131072 | Includes Llama 3.x, Meta-Llama |
| gemma-3 | 131072 | Gemma 3 family |
| grok-3 | 131072 | Grok-3, grok-3-mini, grok-3-fast |
| grok-2 | 131072 | Grok-2, grok-2-1212 |
| grok | 131072 | Catch-all for grok-* |
| nemotron | 131072 | NVIDIA Nemotron |

## Specific model overrides (`MODEL_CONTEXT_LENGTHS`)

| Model | Context Length |
|-------|--------------|
| Qwen/Qwen3.5-397B-A17B | 131072 |
| Qwen/Qwen3.5-35B-A3B | 131072 |

## Custom-named models

Custom GGUF names in LM Studio (e.g. `huihui-qwen3.6-27b-abliterated-mtp`) do NOT match any specific entry — they fall through to the family fallback. Since LM Studio's `/v1/models` endpoint doesn't report `n_ctx`, Hermes has no way to discover the actual loaded context window.

**Solution:** Set `context_length` explicitly in config.yaml for any custom-named local model.
