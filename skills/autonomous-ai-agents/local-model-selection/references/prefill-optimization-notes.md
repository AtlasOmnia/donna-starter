# Prefill / Prompt Processing Optimization Notes

Source: Research session July 2026. Covers llama.cpp batch/ubatch tuning, LM Studio config mapping, and upcoming features.

## ubatch benchmark data (May 2026)

r/LocalLLaMA thread by coder543 — RTX 3090 24GB running gpt-oss-120b-F16.gguf via llama.cpp:

| ubatch | n-cpu-moe | prefill tok/s | generation tok/s |
|--------|-----------|---------------|------------------|
| 256 | 25 | 240.03 | 33.14 |
| 512 (default) | 26 | 380.27 | 32.29 |
| 2048 | 25 | 1112.54 | 32.96 |
| 4096 | 26 | 1682.47 | 32.38 |
| 8192 | 28 | 2090.68 | 30.05 |

Key finding: Going from default `-ub 512` to `-ub 8192` gave ~5.5x faster prefill with only a ~7% generation penalty. The tradeoff is shifting more MoE layers to CPU (`--n-cpu-moe`) to free VRAM for the larger batch workspace.

**Takeaway:** For prompt-heavy workloads (long context, agent tool loops), raising ubatch is the single biggest prefill lever. Test in steps: 512 → 1024 → 2048 → 4096 → 8192, watching for CUDA OOM during prefill.

## llama.cpp flag mapping

| Flag | Short | What it does | Default |
|------|-------|-------------|---------|
| `--batch-size` | `-b` | Logical batch for prefill — tokens processed per forward pass | 2048 |
| `--ubatch-size` | `-ub` | Physical micro-batch within logical batch. Must be ≤ -b | 512 |
| `--threads-batch` | `-tb` | CPU threads during prefill phase (burst workload) | auto |
| `--flash-attn` | — | Flash attention for reduced memory bandwidth pressure | false |

## LM Studio config mapping

LM Studio exposes these in the Advanced settings sidebar:

- **evalBatchSize** → maps to llama.cpp `--batch-size` / `-b`. Set to 1024 or 2048 for faster prefill.
- **flashAttention** → boolean toggle. Enable for long contexts (4k+ tokens).
- **llamaKCacheQuantizationType / llamaVCacheQuantizationType** → KV cache quantization. Q4/Q8 options free VRAM for larger batches.

NOT exposed in LM Studio UI:
- `--ubatch-size` — requires running llama-server directly with explicit `-ub` flag
- `--threads-batch` — not configurable via GUI

For maximum prefill control, run `llama-server` directly instead of through LM Studio when ubatch tuning is needed.

## Vision/multimodal gotcha

Image tokens can tokenize to several hundred tokens. If `--ubatch-size` < image token count, llama.cpp throws an assertion during vision inference. Use `--ubatch-size 512` or higher as a stable baseline for multimodal models. On tight VRAM (e.g., 12GB), `--batch-size 256 --ubatch-size 512` is a known-stable vision config.

## Upcoming features (as of July 2026)

### Chunked prefill
- Breaking long prompts into chunks during prefill improves GPU utilization and reduces latency variance
- Available in TensorRT-LLM v3.2 stable release with dynamic chunk sizing based on system load
- Trickling down to llama.cpp; not yet exposed in LM Studio
- Expected benefit: ~50% throughput gain on aggregated systems per empirical evidence from TNG 2025

### MTP speculative decoding
- llama.cpp beta support landed May 2026 (commit for Gemma-4 MTP showed significant improvement)
- Benefits models with MTP draft heads: Qwen 3.6 MTP, Gemma 4 MTP variants
- Full throughput benefit requires vLLM; partial support in llama.cpp
- LM Studio integration pending

### Cross-Family Speculative Prefill (ICLR 2026 paper)
- Small draft models estimate token importance and compress prompts for larger target models
- Can reduce TTFT by up to 39% while maintaining high task accuracy
- Research-stage; not yet in consumer runtimes

## Tuning recipe (local GPU + LM Studio)

1. In LM Studio Advanced settings, set `evalBatchSize` to 2048
2. Enable `flashAttention: true`
3. If prefill still feels slow on long prompts, run llama-server directly with `-ub 4096` or higher
4. Monitor VRAM — if CUDA OOM during prefill, reduce ubatch or shift layers to CPU

Sources:
- r/LocalLLaMA thread: https://www.reddit.com/r/LocalLLaMA/comments/1tany5t/drastically_improve_prompt_processing_speed_for/
- carteakey.dev complete guide (June 2026): https://carteakey.dev/blog/local-inference/local-llm-optimization/
- dasroot.net prefill bottleneck analysis (May 2026): https://dasroot.net/posts/2026/05/prefill-bottleneck-token-generation-latency-prompt-processing/
