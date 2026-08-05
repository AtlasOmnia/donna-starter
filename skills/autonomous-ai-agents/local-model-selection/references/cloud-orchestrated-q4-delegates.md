# Cloud-Orchestrated Q4 Delegates

## Scope

Q4_K_M remains a poor default for a standalone primary Hermes brain when Q5/Q6/Q8 fits. It can nevertheless be the correct local delegated-worker quant when a stronger cloud model owns architecture and final verification, and the local optimization goal is concurrent implementation throughput.

## When the exception is justified

Use a Q4 dense worker only when all of these are true:

- The cloud main model decomposes work into bounded tasks.
- The Q4 worker is not the final authority for security, bookkeeping, safety, medical, legal, release, or architectural decisions.
- The cloud main reads actual diffs and test output rather than trusting the delegate's summary.
- The VRAM saved is converted into a measured benefit: more KV headroom, a second runtime slot, or elimination of system-RAM spill.
- Thinking remains enabled for real coding/tool loops.
- A cloud fallback exists for local worker failure.
- Concurrent tool-call smokes prove the intended number of slots actually responds.

If these conditions do not apply, prefer Q6 or Q8.

## Q8 versus Q4 decision

Prefer Q8 when:

- one high-quality delegate is enough;
- sessions are long or instruction-dense;
- JSON/schema fidelity is more important than throughput;
- the worker may perform broad debugging with weak supervision.

Consider Q4 when:

- two or more bounded delegates materially shorten the mission;
- the cloud orchestrator will reconcile and verify every result;
- reducing loaded context alone does not create enough parallel KV headroom;
- the exact Q4 checkpoint passes sustained tool-loop tests, not merely a one-shot benchmark.

Do not infer that a smaller weight file automatically creates N usable slots. KV cache, batch workspace, mmproj, and runtime overhead still matter.

## Shared compressor sizing

Do not size Gemma only against the local Qwen worker when the same auxiliary route also compresses the cloud parent.

For a parent with context `C`, output reserve `R`, threshold `T`, and target ratio `K`:

```text
usable = C - R
trigger = usable × T
middle ≈ trigger × (1 - K)
```

The middle estimate explains actual first-cycle work, but the conservative operational target is the largest active parent trigger plus instruction/prior-summary headroom.

Verified example:

- Qwen worker: 80,128 context; 8,192 reserve; 0.75 threshold → 53,952 trigger and about 16,186 middle tokens.
- Sol parent: 184,320 context; 8,192 reserve; 0.75 threshold → 132,096 trigger and about 39,629 middle tokens.
- Shared Gemma compressor: 133,120 context, parallel 1—1,024 tokens above the larger Sol trigger.

Therefore:

- Qwen-only compressor: 80,128 is a safe whole-window match.
- Shared Qwen + Sol compressor: keep 133,120; lowering to the worker window would undersize the parent route or force earlier compression.
- Keep backend live context and Hermes context metadata truthful; do not overstate capacity to silence a conservative guard.

## Vision/MMProj

A text-only delegated worker does not need its vision projector loaded when Hermes has a separate explicit `auxiliary.vision` route. Unloading mmproj can recover additional VRAM, but verify the native runtime reports effective vision disabled. Do not change the dedicated Hermes vision route merely because the worker is text-only.

A separate Gemma auxiliary may retain mmproj and serve vision if explicitly routed. Prove this with a deterministic image request through the exact served model—not a text completion. In the verified topology, Gemma 4 12B Q6_K correctly identified a generated pure-red PNG as `RED`, while Qwen's native capability reported vision disabled.

## Modern LM Studio multi-model behavior

Recent LM Studio builds can keep more than one model loaded and advertise them through the same `/v1/models` endpoint. Each loaded instance can have its own context and parallel count. Use `/api/v1/models` to inspect those values; `/v1/models` alone only proves the IDs are advertised.

This does not prove strict per-GPU pinning. Verify GPU allocation separately when isolation matters.

## Verified example (July 2026)

A dual-GPU setup successfully ran:

- Qwen3.6 27B NVFP4 Q4_K_M: 80,128 context, parallel 2, no mmproj
- Gemma 4 12B IT Q6_K: 133,120 context, parallel 1
- Cloud Sol orchestrator and Codex Luna delegation fallback

Two simultaneous Qwen tool-call requests and one Gemma tool-call request all returned valid function calls from the exact requested model IDs. This validates the architecture, not every future checkpoint or runtime version; re-test after model/runtime changes.
