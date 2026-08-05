# Qwen3.6 Dense vs MoE: 27B vs 35B-A3B Comparison

## Benchmark Summary (as of July 2026)

**Source:** BenchLM.ai, ZoliBen benchmarks, official Qwen results

| Benchmark | Qwen3.6-27B (dense) | Qwen3.6-35B-A3B (MoE) | Winner |
|-----------|---------------------|----------------------|--------|
| SWE-bench Verified | 77.2 | 73.4 | +3.8 dense |
| SWE-bench Pro | 53.5 | 49.5 | +4.0 dense |
| Terminal-Bench 2.0 | 59.3 | 51.5 | +7.8 dense |
| SkillsBench (coding agent) | 48.2 | 28.7 | **+19.5 dense** |
| MMLU-Pro | 86.2 | 85.2 | +1.0 dense |
| GPQA Diamond | 87.8 | 86.0 | +1.8 dense |
| AIME 2026 | 94.1 | 92.7 | +1.4 dense |
| LiveCodeBench v6 | 83.9 | 80.4 | +3.5 dense |
| HLE | 24.0 | 21.4 | +2.6 dense |
| QwenWebBench | 1487 | 1397 | +90 dense |
| BenchLM aggregate | **71** | 62 | **+9 dense** |

**Agentic category:** 59.3 vs 51.5 (+7.8) — biggest separator is Terminal-Bench 2.0 and GDPval-AA.
**Coding category:** 70.6 vs 66.9 (+3.7).
**Knowledge category:** 62.2 vs 60.5 (+1.7).
**Multimodal category:** 76.6 vs 76.1 (+0.5) — nearly identical.

## Architecture Differences

### Qwen3.6-35B-A3B (MoE)
- 35B total parameters, ~3B active per token
- 40 layers: 10 × (3× Gated DeltaNet → MoE) + 1 × (Gated Attention → MoE) per block
- Only 10 full attention layers (GQA, 16Q/2KV, 256-dim)
- 30 Gated DeltaNet layers (recurrent, no KV cache)
- MoE routing: 8+1 shared expert out of 256 experts
- Native context: 262K tokens

### Qwen3.6-27B (Dense)
- 27B total parameters, **27B active** per token (every parameter fires)
- 64 layers: 16 × (3× Gated DeltaNet → FFN) + 1 × (Gated Attention → FFN) per block
- Only 16 full attention layers (GQA, 24Q/4KV, 256-dim)
- 48 Gated DeltaNet layers (recurrent, no KV cache)
- Dense FFN — no MoE, everything computed every token
- Native context: 262K tokens

## Performance Characteristics

### Speed (RTX 4090 benchmark via llama.cpp)
| Metric | 35B-A3B | 27B Dense | Ratio |
|--------|---------|-----------|-------|
| Decode peak | **161.8 tok/s** | 40.3 tok/s | **4.0× faster** |
| Decode at 4K ctx | 152.6 | 38.7 | 3.9× |
| Decode at 16K ctx | 122.2 | 32.4 | 3.8× |
| Decode at 64K ctx | 65.4 | 18.6 | 3.5× |
| Prefill peak | **5912 tok/s** | 2620 tok/s | **2.3× faster** |

### VRAM & Context (llama.cpp, turbo3 KV cache)
| Metric | 35B-A3B IQ4_XS | 35B-A3B Q4_K_S | 27B UD-Q5_K_XL |
|--------|---------------|----------------|-----------------|
| Model size | 17.7 GB | 20.9 GB | 18.65 GB |
| VRAM idle | ~20.4 GB | ~22.7 GB | ~22.9 GB |
| Max context | **262K** | 188K | 156K |

### Quality Metrics (RSF NVFP4 v4 vs base)
- PPL gap to base: 0.129 vs 0.227 (earlier version) — **43% smaller**
- Mean KLD: 0.045 vs 0.059 — **24% lower**
- Same-top probability: 91.9% (vs 90.5% earlier)

## When to Choose Which

### Pick Qwen3.6-27B Dense when:
- It's your primary Hermes agent brain
- Quality > speed for tool calling, coding, multi-step reasoning
- You have hardware that can run it comfortably (16GB+ VRAM for Q4_K_M)
- Agentic task performance matters more than raw tok/s

### Pick Qwen3.6-35B-A3B MoE when:
- Throughput is the primary constraint (RAG pipelines, many concurrent requests)
- You need 200K+ context headroom at lower quants
- Speed matters and quality degradation is acceptable
- Serving as an auxiliary model for non-critical tasks

## NVFP4 Quantization Notes

### A community Qwen3.6-27B NVFP4-MTP GGUF (RSF v4, June 2026)
- RSF scale fitting technique on Q_K tensors
- MTP draft head also quantized to NVFP4 (~130 tok/s TG on a single high-end GPU with vLLM+MTP)
- kaitchup's benchmark: NVFP4 models keep linear attention in 16-bit perform better than full-NVFP4 (which quantizes linear attention layers and underperforms significantly)

### Backend requirement: MTP only works through vLLM
- Speculative decoding via `--speculative-config '{"method":"qwen3_5_mtp","num_speculative_tokens":3}'` in vLLM
- On dual Blackwell GPUs: ~161 tok/s generation, MAL 3.64, draft acceptance 87.9%
- Single high-end GPU with vLLM+MTP: ~130 tok/s (author reported)
- **Running as plain GGUF in LM Studio or llama.cpp:** MTP head is unused — you get quantization quality but NOT the speculative decoding speedup

### kaitchup benchmark findings (May 2026, paid article):
- Full NVFP4 (linear attention also quantized) consistently underperforms on most benchmarks — clear loser
- NVFP4 with linear attention kept at 16-bit is better but still trails INT4 and FP8 variants
- Intel's AutoRound INT4 variant was especially strong even with some linear-attention modules quantized

## Key Sources
- BenchLM.ai comparison page (provisional ranking lane)
- ZoliBen Csupra(Kabra) — full benchmark results with RTX 4090 data, April 2026
- The community RSF HuggingFace repo — RSF NVFP4 quantization metrics, June 2026
- kaitchup.substack.com — Qwen3.6 27B quantization comparison (FP8 vs INT4 vs NVFP4), May 2026
