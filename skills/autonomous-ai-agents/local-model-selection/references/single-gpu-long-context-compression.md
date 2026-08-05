# Single-RTX-5090 long-context compression

Use this note when selecting a dedicated local compression model for a much larger cloud main model, especially Hermes + Codex GPT-5.6 Sol.

## Hermes compression semantics

Hermes' built-in compressor is not a map-reduce chunker. It protects a head and recent tail, then sends the entire compressible middle to the auxiliary model in one request. A 64K auxiliary model does not automatically cycle through successive 64K chunks.

`compression.target_ratio` is also easy to misread: it is the fraction of the compression threshold preserved as recent raw tail, not a source-to-summary output ratio. Lowering it preserves less raw history and summarizes more; it does not add chunking.

Current Hermes source performs a startup feasibility check. If the auxiliary compression context is smaller than the main model's compression threshold, Hermes may lower the live session threshold to the auxiliary window. That keeps compression callable but sacrifices the main model's usable raw context. Treat the auxiliary's effective loaded context—not merely its model-card maximum—as the relevant value.

Example for GPT-5.6 Sol over Codex OAuth:

- Main effective context: 272,000
- `compression.threshold: 0.85` -> compaction near 231,200 tokens
- `compression.target_ratio: 0.70` -> about 161,840 tokens of recent raw tail
- A 64K compressor is therefore not an equivalent substitute. Use an auxiliary loaded at roughly 231K+ effective context; Qwen3.6-27B's native 262,144 window clears it.

## Best single-GPU variant for faithful compression

Recommended stock-model GGUF:

- Repo: `LibertAIDAI/Qwen3.6-27B-NVFP4-GGUF`
- File: `Qwen3.6-27B-NVFP4-Q8_0.gguf`
- Architecture choice: NVIDIA-calibrated NVFP4 for FFN tensors, Q8 for attention/embeddings/remaining tensors
- Role: dedicated structured compression, non-thinking, text-only

Why this variant:

- Stock Qwen avoids correlated behavior from coding finetunes, Heretic/abliteration, or role-play tuning.
- Q8 non-FFN tensors preserve attention and retrieval fidelity better than ordinary Q4_K_M while NVFP4 keeps the large FFN portion compact and fast on Blackwell.
- It leaves enough memory for a 262K Q8 KV cache on one 32GB 5090.

Memory estimate from the official architecture (16 full-attention layers, 4 KV heads, head dimension 256):

- Q8 KV at 262,144 tokens: exactly 8 GiB
- Variant weights: about 18.65 GiB
- Allow roughly 2 GiB runtime/compute overhead
- Working estimate: about 28.65 GiB total

Load preset:

- Context: `262144`
- K cache: `Q8_0`
- V cache: `Q8_0`
- GPU offload: maximum
- Flash Attention: on
- Parallel requests: `1`
- Thinking: off (`chat_template_kwargs.enable_thinking=false` when the runtime supports it)
- Vision/mmproj: do not load for compression
- LM Studio system prompt: blank; Hermes owns the compression prompt

Fallback if runtime overhead or fragmentation causes OOM:

- Same repo, file `Qwen3.6-27B-NVFP4-Q4_K_M.gguf`
- Approximate working total at 262K with Q8 KV and 2 GiB overhead: 24.72 GiB

Do not default to these for compression:

- Heretic/abliterated or NEO-CODE finetunes: useful for other roles, but modification adds no value to faithful state preservation.
- Standard Q6/Q8 GGUF at full 262K on one 32GB GPU: weights plus KV/overhead are too tight or do not fit.
- BF16-attention NVFP4 at full 262K: insufficient headroom.
- MTP-focused builds solely for compression: MTP can improve generation speed, but stability and prompt prefill dominate this occasional auxiliary call. Add it only after a stable baseline.

## Prefill tuning for compression

MTP accelerates generated summary tokens; it does not materially accelerate the long transcript prefill that usually dominates compression latency. Tune prefill before adding speculative decoding.

LM Studio starting point:

- `evalBatchSize: 2048`; use `1024` as the CUDA-OOM fallback
- Flash Attention on
- K cache `Q8_0` and V cache `Q8_0`
- KV cache on GPU
- Maximum GPU offload
- Parallel requests `1`
- Text-only; no mmproj

LM Studio exposes logical eval batch size but not llama.cpp's physical `ubatch`. For direct `llama-server`, test in measured steps:

1. `-b 2048 -ub 2048`
2. `-b 4096 -ub 4096`
3. `-b 8192 -ub 8192` only if peak VRAM leaves real workspace
4. Reduce `ubatch` first on CUDA OOM

The Q8 hybrid has only about 3.3 GiB theoretical headroom from a 32 GiB card before runtime-specific fragmentation and buffers. If that prevents `ubatch=4096`, compare the NVFP4-Q4_K_M fallback at the larger ubatch against Q8 at the smaller ubatch using the same long prompt. Judge both latency and compression fidelity; the faster quant is not automatically the better compressor.

Large-ubatch multi-fold gains reported on other llama.cpp models are tuning leads, not guaranteed Qwen3.6 results. Record prompt-processing tokens/sec, peak VRAM, exact-path retention, omitted constraints, and whether every structured summary section completes.

## Live loaded-but-spilling diagnosis

Do not infer usable VRAM from the remembered machine inventory. Verify three separate surfaces:

1. Query LM Studio's native `GET /api/v1/models` and inspect the loaded instance's exact model ID, `context_length`, `parallel`, batch sizes, Flash Attention, and GPU-KV setting.
2. Run `nvidia-smi` and require every expected CUDA GPU to be actively enumerated. Installed hardware or a prior configuration is not evidence that the runtime can use it.
3. On Windows, inspect display PnP state when a GPU is missing. `CM_PROB_PHANTOM` means a stale device instance remains in the registry but the hardware is not presently enumerated; it contributes no VRAM.

Observed July 2026 single-GPU case:

- Model: `qwen3.6-27b-nvfp4@q4_k_m`
- Context: `262144`
- Parallel predictions: `2`
- Eval batch / physical batch: `2048 / 512`
- Flash Attention and GPU KV: enabled
- Active CUDA inventory: one GPU only; a second GPU was not present on the test hostce
- GPU allocation: about 29.0 GiB of 31.8 GiB reported by `nvidia-smi`
- LM Studio reported about 6.4 GB spilling to system memory

The durable lesson is the remediation order, not the exact numbers:

1. Set parallel predictions to `1`. Long-context compression is session-critical and should queue rather than duplicate active KV/context pressure.
2. If spill remains, reduce KV precision from Q8 to Q4 while keeping the KV cache on GPU. This is preferable to CPU KV/offload for agent loops.
3. Reduce eval batch/workspace from 2048 to 1024, then 512 if needed; expect lower prefill throughput.
4. Lower context only last. Keep the auxiliary's effective loaded window at or above the main model's compression threshold; otherwise Hermes may compact earlier and waste the cloud brain's larger raw context.
5. Re-query the live load and GPU allocation after each change. A model that loads is not acceptable if it silently spills several gigabytes to system RAM.

## Concurrency and GPU-buying guidance

Multiple Hermes windows do not imply multiple simultaneous local inference slots. Keep windows/profiles open, but set the local compression server to one parallel request and let calls queue. Parallel slots duplicate active KV/context pressure and can turn a fitting 262K load into an OOM or unstable runtime.

Do not recommend a second GPU merely because several UI windows are open. A second matched 5090 is justified when measured queueing is a bottleneck, a model genuinely needs more than 32GB, or concurrent local agents are a hard requirement. For mixed-GPU instability, first validate the workload on the single primary GPU; matching cards do not repair driver resets, power delivery, PCIe topology, or thermal faults.

If evaluating dual 5090s, verify before purchase:

- High-quality 1600W-class ATX 3.1 PSU and independent native 12V-2x6 feeds
- Physical slot spacing, cable bend radius, intake clearance, and sustained cooling
- CPU-connected x8/x8 or otherwise acceptable PCIe topology
- Stable single-GPU driver/load behavior

## Verification checklist

1. Confirm the installed llama.cpp/LM Studio runtime recognizes `GGML_TYPE_NVFP4`; do not assume model discoverability equals kernel support.
2. Load exactly 262,144 context with Q8 K/V cache, parallelism 1, and no mmproj.
3. Confirm the model remains fully in VRAM with several GiB of safety headroom.
4. Send a representative long structured-summary request and verify the returned response contains only the final summary (thinking stripped/off).
5. Confirm Hermes resolves the auxiliary compression model's context to 262,144 and does not auto-lower the main session threshold.
6. For loss-sensitive sessions, set `compression.abort_on_summary_failure: true` unless the user deliberately accepts deterministic fallback context.
7. Route Hermes only after the benchmark passes; a model merely loading is not proof that 231K-262K compression is reliable.
