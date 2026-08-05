# Shared Local Worker + Compressor Architecture

Use this note when one local checkpoint should serve both parallel delegated agents and Hermes context compression, especially when eliminating a separate smaller auxiliary model.

## Core decision

Before loading a second auxiliary checkpoint, test whether the primary local worker can cover compression too. A single loaded checkpoint can be preferable because it avoids a second set of model weights and reduces operational complexity. LM Studio continuous batching exposes one loaded instance with one `context_length` and a `parallel` prediction count; short worker sessions can share that instance while one slot services compression.

Do not assume the compressor receives the main session's entire compression threshold. With the built-in Hermes compressor, the approximate new middle sent for summarization is:

`compressible_middle ≈ trigger × (1 - target_ratio)`

Add headroom for the previous structured summary, compression instructions, serialization overhead, and tool-heavy turns. Verify with a real compression-shaped request near the expected size.

## Verified July 2026 example

Configuration:

- Main brain: `openai-codex / gpt-5.6-sol`
- Main context pin: `184320`
- Main output reservation: `8192`
- Compression threshold: `0.75`
- Compression target ratio: `0.70`
- Local worker/compressor: `qwen3.6-27b-nvfp4-mtp`
- Live local context: `64000`
- LM Studio parallel predictions: `3`
- Flash Attention: on
- Native MTP: on, draft max 2 tokens

Arithmetic:

- Trigger: `(184320 - 8192) × 0.75 = 132096`
- Recent raw tail: `132096 × 0.70 ≈ 92467`
- New middle to summarize: `132096 - 92467 ≈ 39629`

A real Hermes compression-resolver request with 40,023 prompt tokens completed on the live 64K MTP instance in 13.49 seconds. This demonstrated that the local model could service the expected compression payload even though its live context was smaller than the main session trigger.

## Hermes feasibility-guard mismatch

Current Hermes conservatively compares `auxiliary.compression.context_length` against the whole main compression trigger. If the true local value is 64K while the main trigger is 132K, the guard may auto-lower the session threshold even though the actual middle sent to the compressor is only about 40K. Because `tail_token_budget` was derived from the original trigger, late auto-lowering can create immediate retrigger/thrashing behavior.

The verified compatibility arrangement was:

- Provider per-model context metadata for delegated workers: `64000`
- `auxiliary.compression.context_length`: `132096` compatibility override
- Comment in config documenting the real 64K slot, expected ~39.6K middle, and successful 40K live smoke

This override is deliberately narrow and test-backed. Do not generalize it without calculating the middle payload and running a near-boundary request. If the target ratio, main context, output reservation, tool footprint, or summary size changes, re-run the arithmetic and smoke.

## Exact dotted model-key pitfall

Model IDs such as `qwen3.6-27b-nvfp4-mtp` contain dots. Do not create `providers.<provider>.models.<model-id>.context_length` with a dotted `hermes config set` path: it splits `qwen3.6...` into nested YAML keys. Insert the exact model ID as one literal YAML dictionary key, then verify with `get_compatible_custom_providers()` and `get_custom_provider_context_length()` against the exact base URL.

## Profile boundary for parent/worker compressor splits

A shared checkpoint only works inside one profile when the parent and native delegated children are allowed to share the same compressor. Hermes native delegation overrides the child's primary provider/model but not its profile-scoped `auxiliary.compression` route.

If the cloud parent must compress with Luna while the local Qwen worker must compress with Qwen:

- Keep the cloud orchestrator profile on Luna compression.
- Create a separate Qwen worker profile with Qwen main and Qwen compression.
- Route work through the worker profile alias/process or Kanban assignment rather than native parent `delegate_task`.
- Remove inherited cloud `model.context_length` pins from the Qwen profile and resolve the exact context from the custom provider's literal per-model metadata.
- Budget LM Studio parallel slots for both worker turns and compression; fully occupying every slot with workers can queue the compressor.

The complete cloning, routing, identity, and verification recipe lives in the model-switching guidanceitching/references/profile-scoped-parent-worker-compression.md`.

## Verification checklist

1. Query LM Studio's native `/api/v1/models`; record the loaded instance ID, live context, parallel count, Flash Attention, and MTP state.
2. Confirm only the intended checkpoint is resident; unload redundant auxiliary models.
3. Verify Hermes delegation resolves to the exact local model and worker context.
4. Verify the `compression` auxiliary resolver returns the same local model.
5. Calculate trigger, tail, and expected middle using the live config.
6. Run a compression-shaped prompt near the expected middle size and require a stopped, non-empty response from the exact returned model.
7. Run a fresh verbose main-profile smoke and confirm the intended main context and compression trigger.
8. Re-query LM Studio after testing because the user may adjust parallel/context settings in the UI mid-session.
