# 16GB VRAM Model Recommendations (June 2026)

Tested on: a 16GB GDDR7 GPU (~58 tok/s at Q4_K_M).

## Top picks with exact GGUF filenames

### 1. Gemma 4 26B-A4B Heretic — Best overall
- HF: `mradermacher/gemma-4-26B-A4B-it-heretic-GGUF`
- Architecture: MoE (26B total, ~4B active/token)
- Q4_K_M: ~14GB, fits 16GB with ~2GB headroom for context
- Has vision + tool calling built-in
- Different family from Qwen — reduces correlated failures
- Source: InsiderLLM top 16GB pick, Feb 2026

### 2. Mistral Small 24B Abliterated — Best dense
- Various abliterated GGUFs on HF (search "mistral-small abliterated")
- Dense 24B, 128K context, Apache 2.0
- Q4_K_M: ~14GB. Tight — Q3_K_M (~12GB) gives more context room.
- Naturally less restricted base training means less damage from abliteration
- Source: BSWEN #1 pick for 16GB uncensored, Mar 2026
- Dolphin 3.0 variant: `dphn/Dolphin3.0-Mistral-24B` (dataset-filtered, not abliterated)

### 3. GPT-OSS 20B Heretic — Highest intelligence
- HF: `DavidAU/OpenAi-GPT-oss-20b-HERETIC-uncensored-NEO-Imatrix-gguf`
- Architecture: MoE (20B total, 4-6 active experts), 128K context
- IQ4_NL: ~12GB. Q5_1: ~16GB (tight).
- Best benchmark scores in 16GB tier
- Can be "rough around edges" due to abliteration — needs temp 0.4-0.8, rep_pen 1.1
- DavidAU notes: IQ4_NL "wild, off-the-cuff"; Q5_1 "more stable"
- Ollama: `second_constantine/gpt-oss-u:20b`

### 4. Qwen3 14B Abliterated — Qwen family consistency
- HF: `huihui-ai/Qwen3-14B-abliterated` (GGUF via bartowski)
- Ollama: `huihui_ai/qwen3-abliterated:14b` or `richardyoung/qwen3-14b-abliterated`
- Dense 14B. Q4_K_M: ~10.7GB. Massive headroom (~5GB for context).
- Same Qwen DNA as main 27B — no template/behavior surprises
- NOTE: This is Qwen3 (Dec 2025), not Qwen3.5/3.6. One generation behind.
- **Caution:** Huihui method causes catastrophic degradation at larger scales. The 14B may be affected — prefer the richardyoung Heretic-based version on Ollama.

### 5. Qwen3.5 9B Uncensored — Lightweight/fast
- HF: `HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive`
- Dense 9B. Q4_K_M: ~6GB. 0/465 refusals.
- Good for: title_generation, skills_hub, session_search (disposable tasks)
- Too weak for: compression, approval (these need reasoning)

## For auxiliary use alongside Qwen3.6-27B main (5090)

Best pick: **Gemma 4 26B-A4B Heretic**
- Different family = correlated failure protection
- Vision support = handles vision auxiliary slot
- MoE = fast enough for auxiliary calls
- Fits 16GB comfortably at Q4_K_M

Budget pick: **Qwen3 14B Abliterated** (richardyoung Heretic variant)
- Same Qwen DNA = zero template surprises
- Lighter = more context headroom
- Weaker than 26B MoE but simpler/safer

## Community quotes

> "For most 16GB rigs the choice is between Gemma 4 26B-A4B Heretic (MoE, faster, vision-capable) and Dolphin 3.0 Mistral 24B (dense, the established uncensored all-rounder)." — InsiderLLM, Feb 2026

> "The main agent is already on Qwen3.6-27B, the critic subagent on 12GB vram with Gemma-4-12B-it gives me a different model family." — r/LocalLLaMA, Jun 2026

> "Mistral-based models offer the best balance of uncensorship and quality for 16GB VRAM." — community test on a 16GB card
