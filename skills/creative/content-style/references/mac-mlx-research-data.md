# Mac/MLX Research Data — Reference for r/hermesagent Content

Condensed research findings for Mac/MLX/Hermes content. Update when new data surfaces.

## Key GitHub Issues (June 2026)

| Issue | Title | Verdict | Key Number |
|-------|-------|---------|------------|
| llama.cpp #23752 | MTP degrades throughput on Metal | MTP is **net loss at every config** on Apple Metal | Baseline 25.3 tok/s → MTP 19.3 tok/s (-24%) |
| llama.cpp #23011 | Qwen3.6-35B-A3B self-MTP slower on Metal | 13.6x slower despite 95.6% acceptance | Baseline 26.23 tok/s → MTP 1.93 tok/s |
| mlx-lm #1293 | Qwen3.5/3.6 non-Coder tool parser mismatch | Tool calls fail silently — parser auto-detect wrong | — |
| mlx-lm #1292 | Qwen3.6 MTP variants multi-turn failures | 1-2 token completions on second requests | Use non-MTP MLX variants |
| mlx-lm #1162 | Prompt-cache failure on Qwen3-Next hybrid | Full recomputation every turn | — |
| Ollama #16698 | MLX KV cache memory leak (v0.30.8) | Memory grows 24GB→75GB, collapses under swap | M4 Max 64GB |
| Ollama #16170 | Inter-prompt delay regression on MLX (v0.24.0) | — | — |

## Backend Speed Claims

| Backend | Claim | Context | Verification |
|---------|-------|---------|-------------|
| Rapid-MLX | 2-4x faster than Ollama | Apple Silicon, 17 tool parsers | 3,000+ GitHub stars, June 2026 |
| Lightning MLX | 220 tok/s | Fork of Rapid-MLX, agentic-optimized | Newer, less tested |
| Ollama MLX (v0.19) | 2x decode, ~1.6x prefill vs Metal | M5 Max, Qwen3.5-35B-A3B NVFP4 | Ollama's own benchmark |
| MLX-LM vs llama.cpp | MLX 20-30% faster on generation | Gap widens on larger models | Hermes official Mac docs |
| llama.cpp TTFT | Faster TTFT than MLX | Qwen3.5-9B test case | Hermes official Mac docs |

## Model Performance Data (Mac-specific)

| Model | Backend | Hardware | tok/s | Notes |
|-------|---------|----------|-------|-------|
| Qwen3.6-35B-A3B 4-bit MLX | MLX-LM | M1 Max 64GB | 61.2 | Peak RAM 18.41GB |
| Qwen3.6-27B 4-bit dense | MLX-LM | M1 Max 64GB | 16.7 | Peak RAM 14.55GB |
| Qwen3.6-27B Q4_K_M | llama.cpp | ? | 25.57 | Simon Willison, Unsloth GGUF |
| Qwen3.5-9B Q4_K_M | llama.cpp | M1 Max | 25.3 | Non-thinking baseline |
| Qwen3.5-9B MTP Q4_K_M | llama.cpp+MTP | M1 Max | 19.3 | MTP slower! (n-max=6) |
| Qwen3.6-35B-A3B MTP Q4_K_M | llama.cpp+MTP | M1 Pro 32GB | 1.93 | Self-MTP 13.6x slower |
| Gemma 4 E2B | MLX | M5 Max | ~158 | LLMCheck June 2026 |
| Phi-4 Mini | MLX | M5 Max | ~135 | LLMCheck June 2026 |

## Bandwidth Tiers

| Chip Class | Bandwidth | Relative Speed |
|-----------|-----------|---------------|
| Base (M1-M5) | 68-150 GB/s | 1x |
| Pro | 150-307 GB/s | 2-2.5x |
| Max | 300-614 GB/s | 3-5x |
| Ultra | 400-800 GB/s | 4-7x |

## Model File Sizes (Approximate)

| Model | Quant | Size |
|-------|-------|------|
| Qwen3.5-9B | Q4_K_M GGUF | ~5.5GB |
| Qwen3.6-27B | Q4_K_M GGUF | ~16.8GB |
| Qwen3.6-35B-A3B | MLX 4-bit | ~20.4GB |
| Qwen3.6-35B-A3B | OptiQ 4-bit | ~20GB |
| Ornstein-Hermes-3.6-27B | MLX 6-bit | ~22.6GB |
| Gemma 4 12B | Q4 GGUF | ~7.5GB |
| Gemma 4 26B-A4B | Q4 GGUF | ~15.5GB |
| Gemma 4 31B | Q4 GGUF | ~18GB |

## HuggingFace Download Counts (as of June 20, 2026)

- mlx-community/Qwen3.6-35B-A3B-4bit: 93,356/month
- mlx-community/Qwen3.6-35B-A3B-OptiQ-4bit: 14,638 total (June 19)
- DavidAU/Qwen3.6-27B-Heretic-NEO-CODE: 523,948 total (June 11)

## M5 Neural Accelerator (Apple ML Research, June 2026)

- M5 adds Neural Accelerators to GPU
- Apple claims 4x TTFT gains for MLX models
- Tested on MacBook Pro M5 24GB vs M4 24GB
- Real-world: modest improvement for LLM inference, not game-changing

## Rapid-MLX Key Facts (June 2026)

- 2-4x faster than Ollama on Apple Silicon
- 0.08s cached TTFT
- 17 tool parsers, 100% tool calling
- Drop-in OpenAI replacement
- Works with Hermes, Claude Code, Cursor, Aider
- GitHub: raullenchai/Rapid-MLX, 3,000+ stars, v0.8.5
- Lightning MLX: fork by samuelfaj, optimized for agentic use

## Ollama Version Timeline (Relevant to Mac)

- v0.17.x: Qwen 3.6 readiness (architecture + GPU/CPU fix + tool parsing + thinking)
- v0.19: MLX backend, 2x decode speed on Apple Silicon
- v0.24.0: Inter-prompt delay regression on MLX
- v0.30.0: llama.cpp alongside MLX engine, flash attention auto-enable
- v0.30.8: KV cache memory leak on M4 Max

## Community Quotes to Watch For (from subreddit threads)

Common Mac user pain patterns:
1. "Qwen3.5-9B tool calling broken on Ollama/Mac" → likely backend, not model
2. "M1 Ultra 128GB still struggling" → backend stack, not hardware
3. "LM Studio broke my tool calls" → parser bug, try GGUF backend
4. "Why is MTP slower?" → known Metal regression, disable it
5. "Ollama eating all my RAM" → KV cache leak, try llama.cpp

## Sources

- llama.cpp issues: https://github.com/ggml-org/llama.cpp/issues/
- mlx-lm issues: https://github.com/ml-explore/mlx-examples/issues
- Ollama issues: https://github.com/ollama/ollama/issues
- InsiderLLM Mac guide: https://insiderllm.com/guides/best-local-llms-mac-2026/
- Hermes Mac LLM docs: https://hermes-agent.nousresearch.com/docs/guides/local-llm-on-mac
- Apple ML Research M5: https://machinelearning.apple.com/research/exploring-llms-mlx-m5
- LLMCheck benchmarks: https://llmcheck.net/benchmarks
- mac-llm-bench: https://github.com/enescingoz/mac-llm-bench
- Rapid-MLX: https://github.com/raullenchai/Rapid-MLX
- Lightning MLX: https://github.com/samuelfaj/lightning-mlx
