# Mac Hermes Agent local model megathread research notes

Use this reference when researching or drafting public guidance for running Hermes Agent on Apple Silicon with local LLMs.

## Public recommendation posture

- Stock/instruct models first. Uncensored/abliterated variants are optional advanced picks, not public defaults.
- For Hermes, tool-call reliability and long-loop coherence matter more than single-shot benchmark scores.
- Phrase uncensored variants neutrally: Heretic, HauhauCS, Huihui-style/simple abliterated builds are all test-first options. Avoid inflammatory wording like "crude" unless backed by direct evidence.
- For dense agent models, Q6 is the preferred serious-agent quant where RAM allows; Q4 is acceptable for entry tiers/MoE but can drift in long tool loops.

## Mac-specific model guidance as of June 2026

- 16GB unified memory: Qwen3.5-9B Q4/Q6 is the practical Hermes floor. Do not force 14B/27B at very low quant; preserve RAM for context and tools.
- 24GB: Qwen3.6-27B Q4 is possible but tight; Qwen3.6-35B-A3B 4-bit MLX may feel faster if the runtime supports the workflow cleanly.
- 32-48GB: Qwen3.6-35B-A3B 4-bit MLX/OptiQ is the current Mac sweet spot because only ~3B params activate per token.
- 64GB+: choose between Qwen3.6-35B-A3B higher-quality quants, Qwen3.6-27B Q6/Q8 for dense stability, or Gemma 4 26B-A4B/31B for cross-family/multimodal needs.
- RAM determines what fits; memory bandwidth determines how fast it feels. Do not rank Macs by chip generation alone — Max/Ultra bandwidth can beat newer lower-tier chips for LLM inference.

## Backend caveats to include in public-facing work

- MLX is the Mac speed path, especially for token generation, but llama.cpp can have faster time-to-first-token and more predictable short tool loops.
- llama.cpp/GGUF remains the control path: KV cache quantization, Jinja templates, mmproj/vision files, and easier diagnosis.
- Ollama is easiest, not necessarily most stable for Hermes tool loops. Verify the same model in llama.cpp or MLX-LM before blaming the model.
- TurboQuant is promising for long context but is an advanced path; benchmark locally and avoid promising speedups.
- MTP is test-first on Apple Metal. Some reports show self-MTP slower than baseline despite high acceptance.

## Runtime issue trackers worth checking

Before publishing or updating a megathread, check current status of:

- `ml-explore/mlx-lm` releases and Qwen tool parser issues.
- MLX-LM Qwen3.6 MTP truncation/prefix-cache issues.
- llama.cpp Apple Metal + Qwen3.6 MTP issues.
- Ollama MLX release notes and current Apple Silicon regressions around queue delay, cache growth, and tool loops.
- Hugging Face model cards/API for last-modified dates, download counts, exact quant names, and chat-template notes.

## Research workflow pattern

1. Start from official docs/model repos: Hermes Mac local LLM docs, Qwen, Gemma/Google, Unsloth.
2. Verify model existence and exact family/size names on Hugging Face.
3. Pull live HF API metadata for lastModified/downloads/likes when using model popularity/recency claims.
4. Add runtime caveats from GitHub issues/releases, not just model cards.
5. Use a subagent to audit the draft for overclaims, missing caveats, and public-community defensibility.
6. Soften superlatives unless directly backed by comparative evidence.
7. Keep the final public guidance practical: recommended RAM tier, backend, quant, caveats, verification commands.