# REAP-Pruned MoE Models

REAP (Router-weighted Expert Activation Pruning) removes low-impact experts from SMoE models while preserving quality. Paper: <https://arxiv.org/abs/2510.13999> (Cerebras, ICLR 2026). Key claim: near-lossless at 50% compression on code generation and tool-calling.

## How it works

- Scores each routed expert by `softmax(router_logits) × ||expert_output||₂` averaged across calibration sequences
- Removes the lowest-scoring experts per layer
- Shared experts are never pruned
- Router automatically rebalances across remaining experts
- Active parameters per token unchanged (still ~3B for Qwen 35B-A3B family)

## Quality evidence (mixed)

### Positive: 05bmckay benchmark (MacBook M4 Pro, 24GB, April 2026)
- **gemma-4-21b-REAP**: Quality 4.49/5 — ranked #1 of 23 models, beating stock qwen3-coder-30b (4.40)
- **qwen-3.5-28b-REAP** (IQ3_XXS): Quality 4.09/5, "best <35B composite"
- Shows REAP CAN beat full-size stock models when calibration is well-tuned

### Negative: Kaitchup review (June 17, 2026, paywalled)
- Tested Qwopus and REAP variants vs stock Qwen3.6
- Called results "largely negative for all these models"
- The 0xSero/Qwen3.6-28B reviewed negatively
- Suggests Qwen3.6-specific REAP implementations may lose quality relative to stock

## Published Qwen REAP models

| Model | Base | Ratio | Total params | Active | Status |
|-------|------|-------|-------------|--------|--------|
| bshener/Qwen3.6-VL-REAP-26B-A3B | Qwen3.6-35B-A3B | 25% (256→192) | ~27B | ~3B | BF16 only, VL preserved |
| 0xSero/Qwen3.6-28B | Qwen3.6-35B-A3B | ~20% | ~28B | ~3B | Kaitchup: negative review |
| RangerX/Qwen3.6-35B-REAP-Pruned-ratio-0.5 | Qwen3.6-35B-A3B | 50% (256→128) | ~19B | ~3B | GGUF available (lennyhans) |
| sandeshrajx/Qwen3.5-24B-A3B-REAP-0.32 | Qwen3.5-35B-A3B | 32% | ~24B | ~3B | GGUF available, custom quantization |
| qwen-3.5-28b-REAP | Qwen3.5-35B-A3B | ~20% | ~28B | ~3B | Benchmarked at 4.09 quality |

## bshener 26B-A3B details (most relevant for agent work)

- 25% prune, calibration: 50% agentic coding/tool-use (SWE-bench trajectories, xlam function-calling), 50% reasoning
- VL encoder preserved (not needed for text-only Hermes)
- BF16: ~50GB disk (vs 67GB original)
- No GGUF published yet
- No abliterated/uncensored variant exists
- dtype MUST be bfloat16 — GDN linear attention overflows float16

## VRAM estimation for REAP-pruned models

Same formula as parent MoE but with reduced total params. At Qwen 35B→27B (25% prune):
- Q4_K_M: ~27 × 0.28 = ~7.6GB
- Q6_K: ~27 × 0.36 = ~9.7GB
- Q8_0: ~27 × 0.50 = ~13.5GB

KV cache behavior should mirror parent architecture (Qwen handles KV quantization well regardless of expert count).

## Uncensored availability

No abliterated/Heretic/HauhauCS REAP-pruned Qwen models exist publicly. To get one:
1. REAP-prune an existing uncensored base (e.g., llmfan46/Qwen3.6-35B-A3B-uncensored-heretic), OR
2. Apply Heretic to an already-pruned REAP checkpoint

Neither path has been published. This is a blocker for users who require uncensored models.

## Recommendation for Hermes agent use

- **Coding-heavy workflows**: REAP-pruned models may be worth exploring (Gemma 4 21B REAP evidence is strong)
- **General agent/orchestration work**: Stock 27B dense at Q6_K/Q8_0 is safer — proven, no MoE router surprises, 27B active per token, abliterated variants available
- **When REAP makes sense**: If VRAM is tight (16GB GPU) and you need MoE knowledge distribution at smaller size — the sandeshrajbhandari 24B IQ4_K_M fits 16GB. On 32GB 5090, this constraint doesn't apply.
