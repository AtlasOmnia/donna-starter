# Mac Hermes Agent Model Research Notes

Use this reference when researching or drafting public recommendations for local LLMs on Apple Silicon running Hermes Agent.

For Jinja/template troubleshooting that affects Hermes tool-calling on Mac, see `references/jinja-template-patches.md`.

## Source coverage target

A defensible Mac/Hermes model recommendation should include more than model cards or synthesis blogs. Aim for this mix:

1. Hermes/runtime integration
 - Hermes Agent local Mac docs.
 - Unsloth/Hermes or other OpenAI-compatible local endpoint guides.
 - Verify `/v1/models` and a real `/v1/chat/completions` smoke test before saying a backend works with Hermes.

2. Official model/vendor sources
 - Qwen official repo/model cards for Qwen3.5/Qwen3.6 sizes, context, license, and local runtime support.
 - Google/Gemma official docs/blogs for Gemma 4 agentic and multimodal claims.
 - Hugging Face model cards plus HF API metadata for lastModified/downloads when recency matters.

3. Runtime implementation evidence
 - `ml-explore/mlx-lm` issues/releases for Apple Silicon, server behavior, tool calling, Qwen/Gemma bugs, MTP truncation, and parallel tool-call fixes.
 - `ggml-org/llama.cpp` issues/discussions for Metal support, Qwen/Gemma architecture support, MTP performance, KV-cache behavior, and template parsing.
 - TurboQuant or other forks only as advanced/experimental unless merged or widely packaged.

4. Community/benchmark evidence
 - Current Reddit/Discord/community threads for real Hermes agent driver reports.
 - Independent benchmark posts with exact hardware, backend, model, quant, context, and tokens/sec.
 - Treat synthesis blogs as secondary sources; use them to find leads, not as sole support.

## Pitfalls for public recommendations

- Do not oversell MLX as universally better. MLX can be faster, but Hermes needs stable OpenAI-compatible serving, tool calls, templates, and multi-turn behavior.
- Check current MLX-LM issues when recommending Qwen3.5/Qwen3.6 for agentic tool use; server tool-call parsing and MTP truncation can be version-specific.
- Check llama.cpp/Metal issues before claiming MTP speedups on Apple Silicon; MTP may be slower than baseline on some Qwen3.6 paths.
- For Mac guidance, separate token-generation speed from agent reliability. Hermes cares about schema discipline, context survival, and tool-loop stability.
- Recommend stock/instruct models first for public guides. Abliterated/uncensored builds such as Heretic or HauhauCS are advanced options that must be re-tested for function/tool calling.
- For Jinja/template advice, mention fixed Qwen3.6 templates only as a troubleshooting path unless current runtime evidence shows stock templates still fail.

## Suggested fresh-search queries

- `site:github.com/ml-explore/mlx-lm Qwen3.6 tool_calls mlx_lm.server`
- `site:github.com/ml-explore/mlx-lm Qwen3.6 MTP truncation`
- `site:github.com/ggml-org/llama.cpp Qwen3.6 Apple Metal MTP`
- `site:github.com/ggml-org/llama.cpp Gemma 4 Metal llama.cpp`
- `site:reddit.com/r/LocalLLaMA Hermes Qwen3.6 local agents June 2026`
- `site:reddit.com/r/hermesagent Mac Qwen3.6 Hermes local model`

## Recommendation framing

For megathreads, add a "Known caveats as of <date>" section. That section should include both positive picks and negative evidence:

- MLX is often fastest on Apple Silicon, but verify server/tool-call behavior.
- llama.cpp/GGUF is the safer control path for KV cache, Jinja, and compatibility.
- Ollama is easiest, not automatically best for Hermes tool use.
- Bigger models at Q2/Q3 are usually worse Hermes drivers than smaller models at Q4/Q6.
- More RAM should usually buy better quants and context headroom, not just the largest model name.

## High-RAM Mac tiers (96GB / 128GB / 192GB+)

Bandwidth ceilings per chip:
| Chip | Bandwidth | RAM ceiling |
|------|-----------|-------------|
| M4 (base) | 120 GB/s | 24 GB |
| M4 Pro (Mac Mini) | 273 GB/s | 48 GB |
| M4 Max (Mac Studio) | 546 GB/s | 128 GB |
| M4 Ultra (Mac Studio) | ~800 GB/s | 192 GB |
| M3 Ultra (prev gen Mac Studio) | ~800 GB/s | 192 GB |

**Bandwidth tiers and what they feel like:**
- **120 GB/s (M4 base):** ~15-25 tok/s on generation. Fine for 9B; larger models drag.
- **273 GB/s (M4 Pro):** ~25-45 tok/s on MoE 35B-A3B at 4-bit. Daily-driver minimum for serious Hermes work.
- **546 GB/s (M4 Max):** ~50-90 tok/s on the same model. The sweet spot.
- **800 GB/s (M4/M3 Ultra):** mostly capacity advantage (192GB) matters more than bandwidth.

**At 96GB (M4 Max):**
- Qwen3.6-27B Q8 (~32 GB file) with ~128K context fits comfortably.
- Qwen3.6-35B-A3B Q8 with full 262K native context.

**At 128GB (M4 Max maxed):**
- Llama 4 Scout (109B total, ~17B active MoE) at Q4: ~30 tok/s on M3 Ultra class.
- DeepSeek V4 Flash at Q3/Q4.
- Speculative decoding with separate drafter (~1-2 GB overhead, ~1.5-2x speedup).

**At 192GB+ (M4 Ultra / M3 Ultra):**
- Llama 3.3 70B at Q4 (~40 GB) or Q5 (~50 GB) with full 128K context.
- Multiple models simultaneously for cross-model comparison.

**What fails at high RAM:**
- Running a dense 70B at Q2/Q3 just because it fits — quality loss outweighs capacity.
- "Bigger = better" heuristic. Qwen3.6-35B-A3B at 8-bit is the right Hermes default even with 192GB.
