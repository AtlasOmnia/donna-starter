# Hermes Compression Window Matching

Use this note when choosing a local model for `auxiliary.compression`, especially when the main model has a much larger context window.

## Built-in compressor behavior

Hermes' built-in compressor is single-pass, not map-reduce:

1. Preserve the configured head messages.
2. Preserve a recent raw tail selected by token budget.
3. Serialize the entire compressible middle section.
4. Send that middle to the compression model in one LLM request.
5. On later compactions, update the previous structured summary with the new middle turns.

Hermes does **not** automatically divide an oversized middle into repeated 64K chunks. Chunked or hierarchical compression requires a separate custom pipeline.

## Context requirement

**Safe default:** the compression model's effective runtime context should meet or exceed the main session's compression threshold. This conservative rule avoids edge cases from large prior summaries, tool-heavy turns, or future changes to tail selection.

**Advanced shared-model exception:** Hermes sends the compressible middle, not the preserved raw tail. A first-order estimate is:

`new_middle ≈ trigger × (1 - target_ratio)`

Add the previous structured summary, instructions, serialization overhead, and safety headroom. A smaller live compressor can therefore work when this complete request—not merely the threshold—fits its runtime context and a near-boundary live smoke succeeds.

Example safe-default sizing:

- Main effective context: 272,000
- `compression.threshold: 0.85`
- Compression trigger: 231,200 tokens
- Conservative compressor context: at least approximately 231,200 tokens

A native 262,144-context model is sufficient even though it does not exactly match 272,000.

Current Hermes performs its feasibility comparison lazily on the first compression attempt and compares the auxiliary context against the whole trigger. If the auxiliary model is at least 64K but smaller than that trigger, Hermes may auto-lower the live threshold. This can waste the main model's context and, because the tail budget was derived earlier, may create immediate retrigger pressure. Treat auto-lowering as a compatibility fallback, not proof that the resulting policy is optimal.

Always query and record the model's actual loaded context. A model loaded at 64K is a 64K runtime even if its architecture supports 262K. If using the advanced shared-model exception, keep delegated-worker metadata truthful and document any separate compression compatibility override with the arithmetic and successful boundary smoke that justify it. See `shared-local-worker-compressor.md`.

## Exact trigger alignment: output reservation and Codex auto-raise

Hermes may reserve `model.max_tokens` before calculating the compression trigger. For an explicit main context pin, the practical trigger is:

`trigger = (model.context_length - model.max_tokens) × compression.threshold`

Therefore, when deliberately matching a smaller local compressor, solve for the main pin with:

`model.context_length = (desired_trigger / compression.threshold) + model.max_tokens`

Worked example: desired Gemma trigger `132096`, threshold `0.75`, and `model.max_tokens: 8192` gives `184320`; verbose startup must show `context_length=184320 threshold=132096`.

Codex-family runtimes can also override a deliberately lowered threshold when `compression.codex_gpt55_autoraise: true`. If exact compressor alignment is intentional, set that flag to `false`; otherwise an explicit `0.75` can silently become `0.85`. Verify the effective values with a fresh verbose Hermes process—YAML readback alone is insufficient.

For custom providers, persist exact per-model context metadata under `providers.<provider>.models.<model>.context_length` so delegated workers use the live limit. Normally `auxiliary.compression.context_length` should also equal the actual loaded compressor window. The only exception is the documented shared-worker/compressor compatibility override: use it solely when the calculated complete compression request fits the smaller live slot, a near-boundary smoke passes, and the override is necessary to prevent Hermes's whole-trigger feasibility guard from auto-lowering incorrectly.

## `target_ratio` semantics

`compression.target_ratio` is not a source-to-summary output ratio. It controls the recent uncompressed tail budget as a fraction of the compression threshold.

Worked example:

- Threshold: 231,200
- `target_ratio: 0.70`
- Recent raw tail budget: 161,840 tokens
- Approximate older region eligible for summarization: 69,360 tokens, before head/system/tool-overhead effects

Lowering `target_ratio`:

- preserves less recent history verbatim;
- sends more old history through lossy summarization;
- leaves more room before the next compression event;
- does **not** make a small-context compressor cycle through chunks.

Raising it preserves more raw tail and reduces the middle per event, but causes more frequent compaction. For long-context agent sessions, `0.65-0.75` is a reasonable starting range; `0.70` is balanced.

Hermes separately guides summary output size based on the compressed content and caps the normal target near 10K tokens. Do not confuse that output budget with `target_ratio`.

## Model-selection implications

Compression is state preservation, so prefer:

- stock/instruct checkpoints over coding, roleplay, or uncensored fine-tunes unless refusal behavior is a demonstrated blocker;
- Q6-class or better weight precision when VRAM permits;
- Q8 KV cache as the practical long-context default;
- non-thinking/instruct mode for straightforward structured summarization;
- text-only loading when vision is unnecessary, to recover memory for KV cache;
- one parallel request, because compression is on the session-critical path.

For a machine with 48 GB combined NVIDIA VRAM and a roughly 231K compression threshold, stock Qwen3.6-27B at its native 262,144 context is a strong fit. Start with Q6_K; use Q8_0 plus Q8 KV when maximum fidelity is worth extra load. A 64K loading of the same model is not an equivalent setup.

## Verification checklist

Before routing Hermes compression to a local endpoint:

1. Query the endpoint's live model identifier.
2. Confirm the runtime is actually loaded at the intended context length.
3. Compare effective auxiliary context against `main_context × compression.threshold`.
4. Confirm `target_ratio` is being interpreted as tail preservation, not summary compression ratio.
5. Run a real compression event and inspect logs/readback for the selected provider/model and successful structured summary.
6. Confirm the session returns below the compression threshold without immediately retriggering.
