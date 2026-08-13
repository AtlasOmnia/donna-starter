---
name: local-model-selection
description: local-model-selection — Choose and recommend local LLM models for Hermes Agent — VRAM-tier recommendations, uncensored/abliterated variants, quant selection, model family naming conventions, dual-GPU setups, and auxiliary model selection.
version: 1.2.3
created_by: agent
tags:
- local-llm
- model-selection
- gguf
- vram
- uncensored
- abliterated
- lm-studio
- ollama
related_skills:
- llama-cpp
---
# Local Model Selection for Hermes

Use this skill when the user asks which local model to run, which quant to pick, which uncensored variant to use, how to pair models across GPUs, or what auxiliary model to use alongside their main model.

## When to use

Trigger on requests like:
- "what's the best Qwen model for my hardware"
- "which quant should I use for 32GB VRAM"
- "what uncensored model for 16GB"
- "what should I run as a secondary/auxiliary model"
- "compare these three models for agent use"
- "is this model still the best or has something newer dropped"
- "where are my LM Studio models"
- "move/delete these LM Studio models to free space"
- "are there any Ollama models on this Mac"
- "uninstall Ollama"

For storage operations, distinguish the machine being cleaned from any remote model host. For LM Studio, inventory exact model directories, check `lms ps` before deletion, delete only explicitly named model repositories, and verify both path removal and real free-space change; see `references/lm-studio-model-storage-operations.md`. For Ollama on macOS, cross-check `ollama list`, allocated model blobs/manifests, and large files before claiming models exist, then use the process/app/CLI/package/data verification sequence in `references/macos-ollama-storage-and-uninstall.md` for a complete uninstall.

## Core rule: verify model existence before recommending

**Never fabricate model names.** Model families have specific size tiers — not every number exists in every family. Before recommending, verify the model exists on HuggingFace or Ollama.

When a user asks for recommendations:

- Use **exact model identifiers**, e.g. "Qwen3.6-27B" not just "a Qwen 3 model."
- Never say "we can run about X parameters" without naming at least one concrete, released, GGUF-available candidate that actually fits.
- If you're unsure of the latest family/size, check via web_search or HuggingFace before answering — the user will spot vague or outdated claims immediately.

**If you mix up versions (e.g., saying "Qwen 3.5" when Qwen 3.6 is current), correct yourself directly instead of hedging.**

## Model family naming conventions

### Qwen family
| Family | Sizes | Key dates |
|--------|-------|-----------|
| Qwen3 | 0.6B, 1.7B, 4B, 8B, **14B**, 32B | Dec 2025 |
| Qwen3.5 | **0.8B, 2B, 4B, 9B**, 27B, 35B-A3B, 122B-A10B | Feb–Jul 2026 |
| Qwen3.6 | 27B, 35B-A3B, 40B (Claude distill) | Apr 2026 |
| Qwen-AgentWorld | **35B-A3B**, 397B-A17B | Jun 2026 — world-model CPT/SFT/RL atop Qwen3.5 MoE, 256K ctx |

**Common pitfall:** No Qwen3.5 14B exists. Qwen3 has 14B; Qwen3.5 has 9B. Do not combine family names with wrong sizes.

**AgentWorld positioning:** Qwen-AgentWorld-35B-A3B is best treated as a world-model / agent-worker candidate, not a drop-in replacement for Qwen3.6-27B dense as the main Hermes brain. Early community reports are promising for long, non-coding agent tasks and local tool-heavy workflows, but mixed for coding. Before judging quality, verify the chat template/tool-call formatting; a patched Qwen `chat_template.jinja` may be necessary for reliable role/tool behavior.

### Gemma 4 family (Apr 2026)
| Size | Type | Notes |
|------|------|-------|
| 12B | Dense | Vision + tool calling |
| 26B-A4B | MoE (~4B active) | Vision + tool calling, good 16GB pick |
| 31B | Dense | Vision + tool calling |

### Other relevant families
- **GPT-OSS 20B** — OpenAI MoE (20B total, 4-6 active), 128K ctx
- **Mistral Small 24B** — Dense, Apache 2.0, naturally less restricted base training
- **Dolphin 3.0** — Dataset-filtered uncensored variants (Mistral 24B, Llama 8B)

## Uncensored/abliterated landscape

Three main techniques:

| Method | How | Trade-off |
|--------|-----|-----------|
| **Heretic** | LoRA-based refusal vector extraction | Lowest KL divergence, best capability preservation |
| **HauhauCS** | Aggressive/Balanced variants | Balanced variant tuned for agentic stability. Aggressive strips preamble. |
| **Huihui** | Crude abliteration (proof-of-concept) | Can cause catastrophic degradation at larger scales (KL >3 on 4B+) |

### Key findings from community benchmarks (Nathan Sapwell, Apr 2026)
- Abliteration is NOT lossless at any scale. All techniques cause measurable benchmark drops.
- Base Qwen3.6-27B refuses 99.5% of harmful prompts. Heretic and HauhauCS both reduce to near-zero while preserving most benchmarks.
- Huihui degrades catastrophically on models >4B — avoid for serious agent work.
- **HauhauCS Balanced** is specifically recommended for agentic coding — keeps self-reasoning preamble which stabilizes long tool-call chains.

### Where to find uncensored GGUFs
- **DavidAU** (HuggingFace) — Heretic + NEO-CODE-Di-IMatrix quants for many models
- **mradermacher** (HuggingFace) — static quants of Heretic variants (Gemma 4 especially)
- **bartowski** (HuggingFace) — standard quants of most models including abliterated
- **huihui-ai** (HuggingFace + Ollama) — crude abliterated variants
- **HauhauCS** (HuggingFace) — Aggressive and Balanced uncensored variants

## VRAM tier recommendations (as of June 2026)

### 16GB VRAM tier (RTX 5070 Ti-class cards)

| Rank | Model | Repo | Quant | VRAM | Notes |
|------|-------|------|-------|------|-------|
| 1 | Gemma 4 26B-A4B Heretic | `mradermacher/gemma-4-26B-A4B-it-heretic-GGUF` | Q4_K_M | ~14GB | MoE, vision, tool calling. InsiderLLM top pick. |
| 2 | Mistral Small 24B Abliterated | various on HF | Q4_K_M | ~14GB | Dense, BSWEN #1 pick, limited ctx room |
| 3 | GPT-OSS 20B Heretic | `DavidAU/OpenAi-GPT-oss-20b-HERETIC-uncensored-NEO-Imatrix-gguf` | IQ4_NL | ~12GB | Highest benchmark scores, MoE can be quirky |
| 4 | Qwen3 14B Abliterated | `huihui-ai/Qwen3-14B-abliterated` | Q4_K_M | ~10.7GB | Same Qwen DNA as main 27B, lots of headroom |
| 5 | Qwen3.5 9B Uncensored | `HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive` | Q4_K_M | ~6GB | Lightning fast, weak for complex aux tasks |

### 24GB VRAM (RTX 3090/4090)
- **Qwen3.6-27B abliterated (MTP-GGUF)** at Q6_K (~22.4GB) — headline pick
- **Gemma 4 31B Heretic** at Q4_K_M — dense with vision

### 32GB VRAM tier (RTX 5090-class cards)
- **Primary agent at ordinary context:** Qwen3.6-27B at Q6_K, or Q8_0 when the loaded context leaves enough KV/compute headroom. Heretic/HauhauCS variants are test-first options only for roles that actually require refusal removal; stock is preferred for faithful summarization.
- **Dedicated 231K–262K compressor on one 5090:** use the stock-based `LibertAIDAI/Qwen3.6-27B-NVFP4-GGUF` file `Qwen3.6-27B-NVFP4-Q8_0.gguf` with Q8 K/V cache, text-only, non-thinking, and parallelism 1. Its NVFP4 FFN + Q8 attention/embedding layout leaves room for the long KV cache while preserving more retrieval fidelity than ordinary Q4_K_M.
- Do not recommend a quant without its loaded context: a model that fits at 32K may OOM at 262K.
- Full single-GPU compression memory math, fallback, live spill diagnosis, and verification: `references/single-gpu-long-context-compression.md`.
- **Loaded-but-spilling rule:** inspect the endpoint's live `loaded_instances` configuration and the OS's active CUDA inventory before changing quants or context. A remembered or installed second GPU is not usable capacity; `nvidia-smi` must enumerate it. On Windows, a `CM_PROB_PHANTOM` display adapter is only a stale registry device, not an active accelerator.
- At 231K–262K context on one 5090, remediate system-RAM spill in this order: set parallel predictions to `1`; reduce KV precision from Q8 to Q4 if needed; reduce eval batch/workspace; lower context only last, and never below the main model's effective compression threshold without explicitly accepting earlier compaction.
- General Qwen3.6 configuration details remain in Apple Notes #272.

### 8-12GB VRAM
- **Qwen3 8B abliterated** at Q4_K_M (~5GB) — best budget pick
- **Qwen3.5 9B** at Q4_K_M (~6GB) — stronger than Qwen3 8B
- **Dolphin 3.0 Llama 3.1 8B** — reliable creative writing pick

## Dense vs MoE: which architecture for Hermes agent work

**Rule:** For a primary Hermes brain, dense models consistently outperform MoE in the same family on agentic benchmarks. The MoE speed advantage comes from activating fewer parameters per token — that's throughput, not intelligence.

| Benchmark | Qwen3.6-27B (dense) | Qwen3.6-35B-A3B (MoE) | Delta |
|-----------|---------------------|----------------------|-------|
| SWE-bench Verified | 77.2 | 73.4 | +3.8 |
| Terminal-Bench 2.0 | 59.3 | 51.5 | +7.8 |
| SkillsBench (coding agent) | 48.2 | 28.7 | **+19.5** |
| MMLU-Pro | 86.2 | 85.2 | +1.0 |
| GPQA Diamond | 87.8 | 86.0 | +1.8 |
| LiveCodeBench v6 | 83.9 | 80.4 | +3.5 |
| BenchLM aggregate | **71** | 62 | **+9** |

The MoE model (35B total, ~3B active/token) is 3-4x faster in token generation but loses quality across the board. The dense model (27B all active) processes more parameters per token — slower but smarter. For Hermes agent work where tool calling reliability, multi-step reasoning, and coding matter: **dense wins**.

MoE excels at throughput-heavy tasks: RAG pipelines, serving many concurrent requests, or when speed is the primary constraint and quality is acceptable at a lower tier. Dense is the right pick for your primary agent brain on hardware that can run it comfortably.

## Quant selection guide

| Quant | BF16 % | Size vs BF16 | Best for |
|-------|--------|-------------|----------|
| Q4_K_M | ~94-95% | ~25% | Budget, max context headroom |
| Q5_K_M | ~96% | ~30% | Good balance |
| Q6_K | ~97.4% | ~35% | Minimum for serious agent work |
| Q8_0 | ~98.5% | ~50% | Best quality, tight on VRAM |

**Community rule (r/LocalLLaMA, May 2026):** "Q6 really is the minimum. Q4_K_M amplifies a bias invisible at Q6+. Q4 looks fine on single-shot benchmarks but starts losing coherence on sequential tool calling."

**For Hermes agent workloads with heavy multi-tool use (long context, frequent tool calls, config edits, JSON schemas):**
- Treat **Q6_K as preferred** for the qwen3.6-27b-heretic family and similar 27B-class abliterated models — not just a single variant like neo-code-di-imatrix-max.
- **Q5_K_M is the practical floor** for agentic use in this class; going below it increases silent hallucinations, schema drift, and instruction loss across long sessions.
- Code-heavy / heavily finetuned variants (e.g., neo-code-di-imatrix-max) are more sensitive to quant degradation — Q6_K is strongly recommended there.

**Exception:** MoE models (GPT-OSS 20B, Gemma 26B-A4B) tolerate lower quants better. IQ4_NL on GPT-OSS 20B is described as "wild, off-the-cuff" but still functional.

### Narrow Q4 exception: cloud-orchestrated local delegates

Q4_K_M is still not the default recommendation for a standalone primary Hermes brain. It can be rational for a **bounded local delegated worker** when a stronger cloud flagship owns decomposition, architecture, integration, and final verification.

Require all of the following:

- The Q4 worker receives scoped implementation/test tasks rather than final authority.
- Saved VRAM produces a measured benefit such as a second parallel slot or removal of system-RAM spill.
- `delegation.max_concurrent_children` matches the runtime's live `parallel` count.
- Thinking stays enabled for coding/tool loops.
- The cloud main verifies actual diffs and test output, not only the delegate summary.
- A reliable cloud delegation fallback exists.
- N simultaneous tool-call smokes succeed for N configured slots.

If concurrency is not materially valuable, keep Q6/Q8. For the decision matrix, mmproj guidance, and a verified Qwen-Q4 + Gemma-Q6 example, read `references/cloud-orchestrated-q4-delegates.md`. Routing mechanics belong in the model-switching guidance.

## KV cache quantization

When the user asks about KV cache precision (Q8 vs Q4), or about splitting K-cache vs V-cache:

- Most backends (llama.cpp, LM Studio) use a single global KV quant; they do not expose independent K vs V settings in stable form today.
- Keys tolerate aggressive quant better than values; hurting V tends to degrade quality faster.
- Q8_0 KV is the default recommendation for agent work: closest thing to "free lunch."
- Q4_0 KV is acceptable when:
 - You are close to VRAM limits with high-weight quants (e.g., Q8_0 weights), or
 - You need very long context and would otherwise spill into system RAM.

Hard rule: avoid CPU/system-RAM spillover at all costs for agent workloads. A second GPU over PCIe is preferable to offloading layers/KV cache into main RAM; token speed drops hard and latency spikes once you hit CPU memory.

If Q8_0 weights + Q8_0 KV would cause LM Studio to offload:
- Prefer either:
 - Using both GPUs in the same LM Studio instance to keep everything on VRAM, or
 - Dropping KV cache to Q4_0 so the model fits fully on the primary GPU.

Asymmetric K=Q8 / V=Q4 is mostly research-level and not reliably exposed; don't recommend it as a practical solution unless there's clear backend support.

## Dual-GPU usage guidance (single model across GPUs)

When the user has two GPUs and a single large model that doesn't fit comfortably on one:

- Using both GPUs in the same LM Studio instance is appropriate when:
 - The model (including context) would otherwise spill into system RAM, or
 - They want to maximize context length at higher quants.
- For models that comfortably fit on the primary GPU at the **intended loaded context** (for example, Qwen3.6-27B Q6/Q8 at ordinary 16K–64K contexts on a 5090):
 - Prefer running them on the primary GPU only; avoid PCIe overhead and keep latency low.
- Do not generalize that fit claim to 231K–262K compression loads. At very long context, KV cache changes the answer; run the architecture-specific memory calculation and inspect real runtime allocation.

Important: LM Studio auto-balances across GPUs — it does NOT let you pin one model to one GPU.
- The "GPU priority" UI (drag to reorder) only affects allocation order, not hard isolation.
- You cannot guarantee that model A runs solely on GPU0 while model B runs solely on GPU1 in a single LM Studio instance.
- If strict per-GPU separation is required, use different runtimes or environment variables (e.g., llama-server with CUDA_VISIBLE_DEVICES).

If they also want a secondary model:
- Best practice is to dedicate one GPU/endpoint per role:
 - Primary Hermes model → dedicated endpoint (e.g., LM Studio or Unsloth on GPU0).
 - Secondary/auxiliary model → separate instance on GPU1, or same LM Studio only when needed and not both heavy models hot at once.

## Thinking mode for agent workloads

When the user asks whether to enable/disable "thinking" or internal reasoning:

- Default stance: thinking must stay enabled for Hermes agent use.
- It is used to plan multi-step tasks, manage tool calls, and maintain consistency across long loops.
- Disabling it noticeably:
 - Increases hallucinations in complex chains,
 - Weakens instruction adherence,
 - Makes tool-calling more brittle.
- Only consider disabling for simple, single-shot tasks where you want faster/shorter answers—and even then the gain is small compared to risk.

### Qwen3.6-27B local coding-agent preset

For `qwen3.6-27b-nvfp4-mtp` acting as a Hermes coding/tool agent—not as the top-level cloud orchestrator—start with:

- Thinking: **enabled**
- Temperature: **0.6**
- Top P: **0.90–0.95**
- Top K: **20**

Do not default to temperature 0 for autonomous agent loops; it can make recovery and tool selection overly rigid. If edits wander or tool behavior becomes unstable, lower temperature to 0.3–0.4 before disabling thinking. Thinking-off is reserved for disposable one-shot rewriting, classification, or summaries—not coding, file mutation, terminal work, or verification loops.

## LM Studio prompt ownership when serving Hermes

When LM Studio is acting as Hermes's OpenAI-compatible backend:

- Leave LM Studio's **system prompt blank**. Hermes builds and sends its own dynamic system message containing profile identity, tools, skills, memory, project instructions, environment context, and completion rules.
- Do not add a generic "coding assistant" system prompt in an LM Studio preset. It can conflict with Hermes tool use—for example, encouraging direct code output when Hermes needs file or terminal calls.
- Keep the model's native **chat/prompt template** enabled. The chat template serializes roles and tool calls; it is not the same thing as a system prompt. Do not blank or replace it unless a verified model-specific Jinja fix is required.
- LM Studio sampling defaults may remain configured, but request-level parameters sent by Hermes generally take precedence.

Rule of thumb: LM Studio serves the model cleanly; Hermes owns agent behavior.

### Do not blame the checkpoint for tool-grammar initialization failures

If plain chat, a small structured response, and a one-tool request succeed but a full Hermes session fails before generation with `Failed to initialize samplers: failed to parse grammar`, treat the model/quant/MTP path as provisionally healthy. Inspect LM Studio's exact preceding grammar error and the advertised Hermes schemas. llama.cpp can reject one oversized nested constraint—such as a generated `char{1,5000}` rule from a tool string `maxLength: 5000`—before the model runs. Compare slim-tool and full-tool Hermes-path smokes, then fix/defer the offending schema or use the upstream tiered-disclosure mitigation; changing quants is not a grounded response to this signature.

## Verify Hermes routing layers before judging a local setup

A Hermes profile's displayed model is only its **main** model. It does not reveal the profile's delegated-agent or auxiliary routes. Before answering whether two roles are “the same” or whether a dual-model setup works, inspect and state all three layers:

1. `model.*` — profile main/orchestrator.
2. `delegation.*` — spawned agent worker.
3. `auxiliary.*` and task-specific overrides — compression, vision, approval, titles, and related support calls.

Then query LM Studio's `/v1/models` for advertised IDs and `/api/v1/models` for live context, parallel slots, capabilities, and load settings. Require a Hermes-path smoke in addition to a raw endpoint smoke. Named custom-provider vision aliases, uncapped image requests, single-slot recovery, context-metadata matching, and one-shot background-delegation verification are covered in `references/hermes-local-routing-verification.md`.

## Dual-GPU dual-model setups

When the user has two GPUs and wants separate worker + auxiliary models, current LM Studio builds support two viable architectures.

### One LM Studio server with multiple loaded models

Recent LM Studio builds can keep multiple models loaded behind the same OpenAI-compatible endpoint. Each loaded instance can have its own context length and parallel count.

Verification is mandatory:

- `/v1/models` confirms the advertised model IDs.
- `/api/v1/models` confirms `loaded_instances`, live context, parallel slots, Flash Attention, GPU KV offload, and effective capabilities such as whether mmproj is loaded.
- Inspect GPU telemetry separately; multiple loaded models do not prove strict per-GPU isolation.

This is the simplest architecture when both models fit and hard GPU pinning is unnecessary.

### Engine Protocol CPU thread pools

Current LM Studio builds place llama.cpp CPU thread control under `Load → Advanced Load Params → CPU Thread Pool Size`. This is a load-time setting; verify the running server uses the intended `--threads N` after reloading.

For multiple simultaneously active, GPU-offloaded model servers, divide physical CPU cores across the busy servers instead of giving every process the full machine. A 24-core/24-thread CPU with two active servers should start at **12 threads each**. Fully GPU-offloaded models rarely benefit from all CPU cores; CPU-offloaded models may. Hybrid P/E-core systems should benchmark smaller pools because synchronization on slower E-cores and cross-process contention can reduce performance.

Do not interpret `--tensor-split` values as literal percentages or subtract their sum from 1 to claim CPU spill. llama.cpp treats them as normalized proportions. Prove CPU layer offload using load logs, `--n-gpu-layers`, GPU telemetry, CPU utilization during a request, and throughput—not process RAM usage alone.

Detailed sizing, verification commands, fallbacks, and the tensor-split pitfall are in `references/lm-studio-engine-protocol-threading.md`.

### LM Studio + llama.cpp server for strict isolation

```text
GPU 0: LM Studio → worker model on port <port-a>
GPU 1: llama-server → auxiliary model on port <port-b>
 Windows: set CUDA_VISIBLE_DEVICES=1
 Linux: CUDA_VISIBLE_DEVICES=1 llama-server -m model.gguf --port <port> -ngl 99
```

Use separate runtimes when a model must be pinned to one GPU, independent endpoint availability matters, or one runtime's allocator causes cross-GPU contention.

### What still does not work reliably

- Two LM Studio GUI instances — single-instance application behavior remains the default.
- Treating LM Studio GPU priority/order as a hard per-model GPU pin without telemetry proof.
- Assuming `/v1/models` alone proves context, parallelism, KV placement, or vision-projector state.
- Multi-GPU controls for one loaded instance are not a substitute for strict process-level isolation.

See `references/cloud-orchestrated-q4-delegates.md` for a verified same-endpoint Qwen worker + Gemma auxiliary example.

## Orchestrator selection for external tool executors

When a model orchestrates a separate cloud-powered application agent—such as a cloud model operating the Hermes for Excel bridge—choose the orchestrator for **controller duties**, not for the executor's domain alone.

1. Split the roles explicitly:
 - orchestrator: scenario selection, campaign state, failure classification, repair decisions, and closeout;
 - application executor: performs workbook/browser/host actions;
 - deterministic evaluator: reads actual state and decides PASS/FAIL from frozen assertions;
 - repair worker: edits code and runs gates when a reproducible defect appears.
2. Never let either model grade its own work. Workbook values/formulas/formats, tool transcripts, test commands, and exit codes are the acceptance surface.
3. If one local model must both orchestrate and repair TypeScript/Python, prefer the strongest dense tool/coding model that fits at the intended context. On a 32GB Blackwell card, stock Qwen3.6-27B Q6_K is the reliability-first one-model choice; use thinking, one parallel slot, Flash Attention, GPU KV offload, and enough KV headroom to avoid spill.
4. If cloud orchestration is allowed, compare against the available Codex coding-agent route before downloading another local checkpoint. A strong cloud coding model can be the better controller/repair agent, while a local model remains the unlimited-runtime fallback. Put repetition in an external bounded controller rather than one endless conversation, and define quota/failure fallback before launch.
5. Treat `Qwen-AgentWorld-35B-A3B` as a specialized benchmark challenger, not an automatic replacement for a dense coding agent. It is trained as a language world model across MCP, terminal, SWE, web, OS, and related domains and is fast at roughly 3B active parameters, but normal Hermes tool behavior, chat-template compatibility, coding repairs, and required long-context memory must pass the exact workload first. On a 32GB card, Q6 leaves little context headroom; Q5-class quants are more practical but increase the need for live evaluation.
6. Prefer current stock/upstream-derived GGUFs with verified developer-role and nested tool-call templates over flashy community distills when reliability is the objective. Verify exact repository, filename, template, loaded context, and a Hermes-path tool-call smoke before judging the model.

For overnight autoresearch, model quality and campaign architecture are separate decisions: even the best model needs a persistent controller, frozen evaluator, bounded iteration contract, durable logs, and clean keep/revert semantics.

## Auxiliary model selection for Hermes

Hermes has 11 auxiliary task slots. The two that matter most for model choice:

| Task | Priority | Needs |
|------|----------|-------|
| compression | HIGH — touches agent state | Reliable, handles long inputs |
| approval | HIGH — can allow/block commands | Reliable reasoning |
| vision | HIGH if main lacks mmproj | Vision support |
| web_extract | MEDIUM | Cheap, fast |
| title_generation | LOW | Disposable |

**For 16GB auxiliary alongside a 27B main:**
- **Primary pick:** Gemma 4 26B-A4B Heretic Q4_K_M (~14GB) — different family avoids correlated failures, has vision + tool calling
- **Smaller verifier/compression pick:** Gemma 4 12B IT Q6_K — good when 26B-A4B is too large but the auxiliary still needs enough judgment for compression, approval sanity checks, schema checks, and simple “did we actually complete the task?” loops. Treat it as first-pass QA, not a final auditor for code, bookkeeping, safety, medical, legal, or other subtle/high-stakes review.
- **Budget pick:** Qwen3 14B Abliterated Q4_K_M (~10.7GB) — same Qwen DNA, no template surprises, more context headroom
- **Lightweight long-context compression floor:** stock `Qwen3.5-4B` Q6_K (native 262K) — substantially lighter than Gemma 4 E4B in total resident weights and suitable for coding-session compression when loaded at the required context and verified with a near-boundary structured-summary smoke. Use non-thinking/text-only and parallel=1. Treat `Qwen3.5-2B` as a technical minimum only, not a dependable coding-state compressor.
- **Tiny/light fallback:** Gemma 4 E4B Q5/Q6-class quants — suitable for cheap compression and obvious-error detection, but its native 128K window may be too short for large cloud-parent triggers, and it is too small for deep independent verification.
- **Do not generalize by parameter count alone:** current Qwen3.5 small models (0.8B/2B/4B/9B) differ materially from older small-model guidance. For compression, require enough live context plus a boundary smoke; 4B is the practical floor for coding state, while 2B and below are for disposable summaries/classification.

**Cross-family is preferred.** Running the same model family on both GPUs means a failure mode affecting one probably affects both. Different architectures (dense + MoE) or different families (Qwen + Gemma) is safer.

### Small auxiliary verifier/compressor guidance

When the user wants a small model that can both compress context and run a loop to check whether a task/result is correct:

1. **If Gemma 4 12B IT Q6_K fits, recommend it over E4B/9B.** It is the practical sweet spot for compression plus meaningful sanity checks.
2. **Use one parallel request for verifier/compressor duty.** Parallel=2 duplicates active KV/context pressure and trades away reliability for throughput. Only raise parallelism for low-stakes batch summaries that stay fully in VRAM.
3. **Configure high effective context, but leave headroom.** For a 128K context auxiliary model, 80% is 102,400 tokens; use that as a conservative operating target when the runtime needs a manual value.
4. **Verifier scope matters:**
 - Good: compression, summarizing tool output into state, schema/JSON checks, “did the answer cover all requested parts?”, obvious contradictions, command approval sanity checks.
 - Not enough alone: final bookkeeping decisions, safety/compliance conclusions, deep code/security review, subtle multi-step reasoning audits.
5. **Hermes does not have a single universal “verify every final answer with aux” switch.** Wire the model into built-in auxiliary tasks instead: `auxiliary.compression`, `compression.summary_*`, `auxiliary.approval` with `approvals.mode: smart`, and optionally `auxiliary.monitor` / `auxiliary.triage_specifier`. For task-result verification, include an explicit verification instruction in the task prompt or spawn a verifier/delegation pass deliberately.
6. **Use the model ID exposed by the live local endpoint, not the GGUF filename guess.** Query `/v1/models` when permitted; otherwise tell the user to copy the loaded model name from LM Studio/llama.cpp.
7. **Use whole-trigger matching as the safe default, then evaluate the shared-model exception explicitly.** Hermes' built-in compressor sends the whole compressible middle in one request; it does not map-reduce through repeated chunks. Normally the auxiliary context should meet the main trigger. When reusing one stronger local checkpoint for parallel workers and compression, calculate `trigger × (1 - target_ratio)` plus prior-summary/instruction headroom and prove the near-boundary request live before accepting a smaller worker slot. See `references/shared-local-worker-compressor.md`.
8. **Interpret `compression.target_ratio` correctly.** It is the fraction of the compression threshold retained as the recent raw tail, not a source-to-summary output ratio. Lowering it summarizes more history and leaves more room; it does not make a short-context auxiliary process multiple chunks.
9. **Size a shared compressor for its largest client, not the smallest worker.** If the same Gemma/compressor can summarize both a cloud parent and local delegated Qwen sessions, calculate every client's effective trigger and provision against the largest one. A compressor sized only to the Qwen worker may be safe for Qwen yet truncate or force early compaction for the larger cloud parent. Keep the larger context unless the routes are truly isolated or the cloud trigger is deliberately lowered and verified.

For mechanics, worked arithmetic, model-selection consequences, and verification, read `references/hermes-compression-window-matching.md`.

## NVFP4 inference parameter tuning

NVFP4 quants (e.g., the community RSF series — tens of thousands of downloads/month, actively updated) trade some quality for significant speed gains (~1.7x prefill over Q4_K_M). When the author publishes same-top-token probability metrics, use them to set Top K:

- **Same-top-p ~80-92%** (meaning 8-20% of tokens shift rank from BF16): keep **Top K at 15-25** for agent work. A narrower window reduces the chance quant noise pulls in low-quality tail tokens.
- **Same-top-p >93%**: Top K 25-40 is safe; the quant closely tracks BF16 rankings.
- Pair with **Top P ~0.85-0.9** and **temp 0.3-0.6** for structured agent use. Bump to creative ranges (K=40, temp 0.7+) only when variety is desired.

If output feels too narrow or refuses valid options, raise K by 5-10. If it wanders into artifacts or repetition, lower it back down.

### NVFP4 backend and MTP requirements

Separate three claims that were previously conflated:

1. **Native NVFP4 execution:** Current llama.cpp CUDA builds can execute NVFP4 tensors directly on Blackwell GPUs. LM Studio support depends on its selected runtime pack, so inspect the installed runtime rather than assuming the app version is enough. Look for `GGML_TYPE_NVFP4` handling / CUDA NVFP4 kernels or prove it by loading a known NVFP4 GGUF.
2. **MTP speculative decoding:** MTP is optional acceleration for token generation, not a requirement for NVFP4 quality or memory savings. Recent llama.cpp builds can support native Qwen3.6 MTP, but LM Studio may lag or expose it differently. Verify the actual runtime and model tensors before promising a speedup.
3. **Compression workload:** Long prompt prefill and summary fidelity matter more than speculative generation speed. Establish a stable non-MTP baseline first; add MTP only if the runtime supports it cleanly and measured end-to-end compression latency improves. Verify LM Studio's native `/api/v1/models` response, not the filename alone: require the intended loaded instance plus `speculative_draft_mtp: true`, the actual draft-token limit, live context, parallel count, and Flash Attention state. Then run a compression-shaped prompt near the expected middle size and record returned model, prompt tokens, finish reason, content, and elapsed time. Do not attribute a faster result to MTP when the checkpoint, context, parallelism, or other load settings also changed.

The official `nvidia/Qwen3.6-27B-NVFP4` checkpoint targets vLLM/ModelOpt and is the authoritative NVIDIA calibration source. For LM Studio/llama.cpp, use a GGUF conversion that explicitly preserves NVFP4 tensors and documents the precision of non-FFN tensors. On a single 5090 at 262K context, the `LibertAIDAI/Qwen3.6-27B-NVFP4-GGUF` Q8_0 hybrid is the preferred compression variant; see `references/single-gpu-long-context-compression.md`.

## Shared local worker + compressor

When the user wants one strong local checkpoint to serve parallel delegated agents and compression, do not introduce a second smaller auxiliary model by reflex. First calculate the actual compressible middle (`trigger × (1 - target_ratio)`), include prior-summary/instruction headroom, and run a near-boundary compression-resolver smoke. Short worker sessions can share one LM Studio continuous-batching instance while the same weights handle compression, provided the tested compression payload fits the live slot.

Keep three context concepts separate:

- LM Studio's live loaded context and parallel count;
- Hermes's delegated-worker context metadata;
- the compression compatibility context used by Hermes's conservative feasibility guard.

Current Hermes can auto-lower too aggressively when the live compressor context is below the whole main trigger even though the actual middle fits. Use the narrow, documented workaround only with arithmetic and live proof. Full procedure, verified example, and pitfalls: `references/shared-local-worker-compressor.md`.

## Local document OCR / PDF parsing models

When the user asks about local models for PDF/image OCR, PDF-to-Markdown, or PDF-to-JSON extraction, check `references/local-document-ocr-models.md` before answering. Key current candidates:

- `datalab-to/chandra-ocr-2` — Chandra OCR 2; local/open OCR model that outputs Markdown, HTML, and JSON with layout information. This is the likely answer when the clue is "local model that strips PDFs down to JSON."
- `ChatDOC/OCRFlux-3B` — local PDF/image to clean Markdown, with JSONL pipeline output and strong cross-page table/paragraph merging.
- `baidu/Unlimited-OCR` — one-shot long-horizon document parsing; more Markdown/structured parsing than direct custom JSON.
- `zai-org/GLM-OCR` — local/open OCR model; JSON output may come through wrappers/deployment examples.

For recall-style questions, give the most likely model first with one short reason and links; do not start with a broad OCR model survey unless the user asks for comparison.

## Research methodology

When researching models for the user:

1. **Start with authoritative sources** — Hermes docs, upstream model repos/cards, runtime release notes, then community sources (r/LocalLLaMA, r/LocalLLM, r/hermesagent, HuggingFace).
2. **Verify existence before recommending** — check HuggingFace for actual model repos and exact filenames.
3. **Check model family sizes** — not every number exists (no Qwen3.5 14B, no Qwen3 9B).
4. **Prefer sustained agent evidence** (Terminal-Bench, SWE-bench, real Hermes/tool loops, runtime issue reports) over single-shot benchmarks (MMLU).
5. **Note the quant table** — Q4 vs Q6 gap matters for agent loops; for public guidance, recommend Q6 where RAM allows for dense agent models.
6. **Surface recency bias** — models and runtimes move fast; for megathreads, check the last 30–45 days and record the compile date.
7. **Run a defensibility pass** before public posts: check current MLX-LM, llama.cpp, Ollama, Unsloth, and Hugging Face issues/releases for tool-calling, MTP, cache, Jinja/template, and Apple Metal caveats.
8. **Use subagent verification for public research drafts** — ask a separate agent to audit overclaims, missing caveats, and claims that need softer wording.
9. **Keep uncensored/abliterated wording neutral** — stock/instruct first; Heretic/HauhauCS/Huihui-style builds are advanced test-first options. Avoid pejorative labels unless backed by direct evidence.
10. **Apple Notes #272** has the full Qwen3.6-27B config guide — reference it for 27B-tier recommendations.
11. **Check runtime evidence**, not just model quality. For MLX, inspect `ml-explore/mlx-lm` issues/releases for OpenAI server behavior, tool-call parsing, Qwen/Gemma support, and MTP truncation. For GGUF, inspect `ggml-org/llama.cpp` issues/discussions for Apple Metal, MTP, KV cache, and Jinja/template behavior.
12. **Add a known caveats as of <date> section** for public megathreads. Include negative evidence such as MLX tool-call gaps, MTP regressions on Metal, template pitfalls, and uncensored variants needing re-test for function calling.
13. **Treat synthesis blogs as lead generators**, not final authority. Back headline claims with official docs, model metadata, implementation threads, or reproducible benchmark posts.
14. **Keep recommendations framed around Hermes agent reliability**: schema discipline, long tool-loop stability, context/KV management, and OpenAI-compatible endpoint behavior matter as much as tokens/sec.

## Mac + Hermes Agent megathread pitfalls

- MLX is usually the Mac token-generation speed path, but llama.cpp can have faster time-to-first-token and stronger control for short tool loops.
- MTP/TurboQuant are test-first on Apple Silicon; do not promise speedups without local/runtime-specific benchmarks.
- Ollama is easiest for users, but version-specific MLX/cache/tool-loop regressions can affect Hermes workflows; verify with llama.cpp or MLX-LM before blaming the model.
- For Mac recommendations, RAM decides what fits and memory bandwidth decides how fast it feels. Do not rank solely by chip generation.

## New/untested model VRAM estimation workflow

Use this for brand-new models (just-released, no GGUF, no community quants yet) where the user asks "can I run this with my hardware?"

**Step 1: Find the raw FP16 size.**
- Most HuggingFace model repos expose `model.safetensors.index.json` at the root.
- Fetch it via curl: `curl -sL "https://huggingface.co/<org>/<model>/resolve/main/model.safetensors.index.json" | python3 -c "import json, sys; d=json.load(sys.stdin); print(d.get('metadata',{}).get('total_size', 'not found'))"`
- That `total_size` is in bytes. Divide by 1e9 for GB.

**Step 2: Estimate at target quants.**
| Quant | Multiplier (vs FP16 size) |
|-------|--------------------------|
| Q8_0 | ×0.50 |
| Q6_K | ×0.36 |
| Q5_K_M | ×0.31 |
| Q4_K_M | ×0.28 |
| Q3_K_M | ×0.22 |
| IQ4_NL | ×0.26 |

For MoE models (35B total / 3B active, 397B total / 17B active, etc.), the total param count determines memory, not the active count — all experts are resident.

**Step 3: Add KV cache overhead.**

Find architecture params from the model's `config.json`:
- `num_hidden_layers` (or `num_layers`)
- `num_key_value_heads` (or `num_kv_heads`) — defaults to `num_attention_heads` if absent (MHA)
- `head_dim` — usually `hidden_size / num_attention_heads`
- `max_position_embeddings` or target context

KV cache per token (FP16): `layers × kv_heads × head_dim × 2 bytes × 2 (K+V)`.
At 256K tokens: multiply by 262144. At Q8 KV: ×0.5. At Q4 KV: ×0.25.

If exact arch params are hard to find, use a conservative estimate:
- 35B-class MoE (~28-32 layers, 8 KV heads, 128 dim): ~5-9 GB for full 256K at Q4-Q8 KV. Manageable on 48GB.
- 70B-class dense (80 layers, 8 KV heads, 128 dim): ~33 GB at FP16 KV for full context — dominates your budget fast.

**Step 4: Check backend support and GGUF availability.**
- Web search: `"<model-name> GGUF"` — check HuggingFace for unsloth, bartowski, mradermacher quants.
- Brand-new models (≤48h old) rarely have GGUF yet. Unsloth usually releases within 2-7 days for popular Qwen releases.
- If no GGUF exists, the user must:
 - Wait for community quants, or
 - Convert themselves (requires ~2× FP16 RAM for conversion — 70B model needs ~140GB system RAM), or
 - Run FP16 via vLLM across multiple GPUs (needs matching GPU VRAM).

**Step 5: Check multi-GPU feasibility (dual heterogeneous GPUs like 32GB+16GB).**
- llama.cpp / LM Studio can split across mismatched GPUs; the slower GPU becomes the bottleneck for layer throughput.
- FP16 (70GB): needs a second machine — won't fit even across 32+16.
- Q8 (~35GB): fits 32+16 combined, but the 5070 Ti's lower bandwidth slows inference.
- Q4_K_M (~20GB): fits with generous KV cache headroom on both GPUs.

## REAP-pruned MoE variants

REAP (Router-weighted Expert Activation Pruning) removes low-impact experts from SMoE models. The technique can produce models that beat full-size stock (Gemma 4 21B REAP scored #1 of 23 on a community benchmark), but Qwen3.6-specific REAP implementations have mixed reviews — one serious evaluation called the results "largely negative."

Key trade-off: REAP reduces total params (35B→19-27B) but active params stay ~3B. For general Hermes agent work, stock 27B dense (27B active/token) remains the safer pick. For VRAM-constrained coding, REAP may be worth exploring. Full model list, benchmark data, and uncensored availability in `references/reap-pruned-models.md`.

## Prefill / prompt processing optimization

When the user asks how to speed up prompt processing (time-to-first-token, prefill throughput) on local hardware:

**The two knobs that matter most:**

1. **`--batch-size` (`-b`)** — Logical batch for prefill. Controls how many tokens are processed in one forward pass during the prefill phase. Higher = faster prompt processing but more VRAM required.
 - `2048` is high throughput (~maximum for most models)
 - `1024` is a balanced default
 - `512` is conservative; use for vision or tight VRAM
 - LM Studio exposes this as `evalBatchSize` in Advanced settings

2. **`--ubatch-size` (`-ub`)** — Physical micro-batch within the logical batch. Must be ≤ `--batch-size`. This is where the biggest recent gains have been found.
 - Default is `512` — this is a safe default, not optimal
 - Increasing to `4096–8192` can give **3–5x faster prefill** with only ~7% token generation penalty (see reference below)
 - Larger ubatch needs more GPU compute workspace VRAM; on MoE models you may need to shift a couple layers to CPU (`--n-cpu-moe`) to free room
 - Vision/multimodal: image tokens can tokenize to several hundred tokens — `--ubatch-size` must be ≥ the largest image token count or llama.cpp asserts. Use 512+ as baseline.

**LM Studio limitations:** LM Studio exposes `evalBatchSize` in the Advanced settings sidebar but does NOT expose `--ubatch-size` in its UI. For maximum prefill control, run `llama-server` directly with explicit `-b` and `-ub` flags instead of going through LM Studio for that model.

**Other optimization levers:**
- **Flash Attention** (`flashAttention: true`): Reduces memory bandwidth pressure during prefill on long contexts (4k+ tokens). Enable in LM Studio Advanced settings or via llama.cpp flag. Significant on RTX 50-series architectures.
- **KV cache quantization**: Quantizing KV to Q4/Q8 frees VRAM that can be used for larger batch sizes. Trade-off: minor accuracy loss on very long contexts.
- **`--threads-batch`**: CPU threads for the prefill phase. PP is a burst workload — set to full thread count. Default usually works fine on consumer hardware; cuBLAS optimizations are tuned for datacenter batch sizes, so raising this doesn't always help on consumer GPUs.

**Upcoming features (as of July 2026):**
- **Chunked prefill**: Breaking long prompts into chunks during prefill improves GPU utilization and reduces latency variance. Available in TensorRT-LLM v3.2; trickling down to llama.cpp but not yet exposed in LM Studio.
- **MTP speculative decoding**: Recent llama.cpp builds support native Qwen3.6 MTP when launched with explicit speculative-decoding flags. vLLM remains the preferred high-throughput path for Unsloth's Safetensors NVFP4 checkpoint. LM Studio may bundle an MTP-capable runtime without exposing the controls, so verify the selected runtime and measured end-to-end behavior. MTP accelerates decode, not prompt prefill.

See `references/prefill-optimization-notes.md` for benchmark data and tuning recipes.

## Support files

- `references/macos-ollama-storage-and-uninstall.md` — verify whether Ollama models actually occupy Mac storage and perform a complete process/app/CLI/package/data uninstall with an explicit administrator boundary.
- `references/lm-studio-model-storage-operations.md` — locate, relocate, or safely delete Mac-local LM Studio models; verify loaded state, deletion scope, and recovered space.
- `references/local-compression-economics.md` — measure profile-specific compression usage and compare local API savings against the effective auxiliary route, flagship fallback exposure, and electricity.
- `references/cloud-orchestrated-q4-delegates.md` — narrow Q4 exception for supervised local delegates, concurrency gates, mmproj guidance, and a verified same-endpoint Qwen/Gemma topology
- `references/qwen-family-size-map.md` — exact Qwen family sizes, model repos, and naming pitfalls
- `references/16gb-vram-recommendations.md` — detailed 16GB tier picks with GGUF filenames and sizes
- `references/mac-model-research.md` — source strategy, caveats, high-RAM Mac tiers, and search queries for Mac local-LLM/Hermes megathread research
- `references/jinja-template-patches.md` — Jinja chat template patch ecosystem: active bugs, upstream status, and what to recommend for Hermes tool-calling reliability (Qwen3.5, Qwen3.6, Gemma 4)
- `references/reap-pruned-models.md` — REAP-pruned MoE model landscape: published variants, benchmark quality, VRAM estimation, uncensored availability, and when REAP makes sense for Hermes
- `references/qwen-agentworld-field-notes.md` — Qwen-AgentWorld community signal, Hermes positioning, chat-template warning, and runtime caveats
- `references/dense-vs-moe-qwen36-comparison.md` — full benchmark comparison between Qwen3.6-27B dense and 35B-A3B MoE: agentic scores, speed tradeoffs, architecture differences, NVFP4 backend requirements
- `references/local-document-ocr-models.md` — local OCR/document parsing candidates for PDF-to-Markdown/HTML/JSON recall questions, including Chandra OCR 2, OCRFlux-3B, Unlimited-OCR, and GLM-OCR
- `references/hermes-compression-window-matching.md` — built-in Hermes compression mechanics, context-threshold matching, `target_ratio` semantics, worked long-context arithmetic, and verification checks
- `references/shared-local-worker-compressor.md` — one-checkpoint architecture for parallel local workers plus compression, including trigger/middle math, conservative-guard workaround, dotted model-ID pitfall, and live verification
- `references/single-gpu-long-context-compression.md` — exact Qwen3.6-27B NVFP4-Q8 compressor choice for one 32GB GPU, 262K Q8-KV memory math, stable load preset, fallback, concurrency, and dual-5090 buying gates
- `references/prefill-optimization-notes.md` — benchmark data, ubatch tuning recipes, LM Studio config mapping, and upcoming prefill features (chunked prefill, MTP speculative decoding)
## Public support files

- `references/16gb-vram-recommendations.md`
- `references/cloud-orchestrated-q4-delegates.md`
- `references/dense-vs-moe-qwen36-comparison.md`
- `references/hermes-compression-window-matching.md`
- `references/hermes-local-routing-verification.md`
- `references/jinja-template-patches.md`
- `references/lm-studio-engine-protocol-threading.md`
- `references/lm-studio-model-storage-operations.md`
- `references/local-compression-economics.md`
- `references/local-document-ocr-models.md`
- `references/mac-megathread-research.md`
- `references/mac-model-research.md`
- `references/macos-ollama-storage-and-uninstall.md`
- `references/prefill-optimization-notes.md`
- `references/qwen-agentworld-field-notes.md`
- `references/qwen-family-size-map.md`
- `references/reap-pruned-models.md`
- `references/shared-local-worker-compressor.md`
- `references/single-gpu-long-context-compression.md`
