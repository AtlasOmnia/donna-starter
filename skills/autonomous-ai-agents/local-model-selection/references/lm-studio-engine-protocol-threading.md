# LM Studio Engine Protocol: CPU Thread Pools and Multi-GPU Verification

Use this when LM Studio moves llama.cpp thread controls into per-model load settings or when multiple loaded model servers compete for one CPU.

## Where the setting lives

In current LM Studio builds with Engine Protocol enabled:

`Load → Advanced Load Params → CPU Thread Pool Size`

This is a **load-time** parameter. Changing it does not alter an already-running server until the model is reloaded. Verify the effective value in the llama-server command line as `--threads N`.

## Sizing rule

1. Inventory physical cores, logical processors, hybrid P/E topology, simultaneously busy model-server processes, each model's parallel slot count, and whether any layers actually run on CPU.
2. For several simultaneously loaded and actively used GPU-offloaded models, start with:

 `physical cores ÷ concurrently busy model servers`

 Round conservatively and leave capacity for Windows and tokenization. Example: a 24-core/24-thread CPU with two active LM Studio servers starts at **12 threads each**, not 24 each.
3. For a fully GPU-offloaded model, more CPU threads usually provide little decode benefit. Use 8–12 as a practical starting range on a hybrid desktop CPU, then benchmark.
4. For real CPU layer offload, CPU-only inference, or one model running alone, using most or all physical cores can help. Benchmark rather than assuming the maximum wins.
5. Parallel prediction slots share a server process and its CPU pool. Do not multiply thread count blindly by parallel slots.
6. Keep Evaluation Batch Size separate from CPU Thread Pool Size. A high eval batch (for example 2048) is primarily a prefill/workspace choice; it does not justify oversubscribing CPU threads.

## Hybrid CPU caution

On CPUs with fast P-cores and slower E-cores, a smaller pool can outperform an all-core pool because barriers wait for the slowest workers and two model servers can thrash across core classes. If latency matters, compare 8, 12, and all-physical-core settings with the same prompt and loaded context.

## `--tensor-split` pitfall

`--tensor-split` values are **weights/proportions that llama.cpp normalizes**. They are not literal percentages and do not need to sum to 1.

Example:

`--tensor-split 0.1876,0.4382`

This does **not** prove that 37.42% of the model remains on CPU. Treating `1 - sum(values)` as CPU spill is wrong.

To prove CPU offload or system-RAM spill, combine:

- `--n-gpu-layers` and model-load logs showing actual layer placement;
- GPU VRAM usage before/after loading;
- model size, KV-cache precision/context, and workspace requirements;
- token throughput and CPU utilization during a real request;
- process working set only as supporting evidence, because mmap/file cache can make RAM usage look like CPU inference.

## Live verification

- `GET /v1/models` — advertised loaded model IDs.
- `GET /api/v1/models` — loaded instances, context, parallel count, eval batch, Flash Attention, and GPU KV offload.
- Inspect the running llama-server command line for `--threads`, `--tensor-split`, `--n-gpu-layers`, `--ctx-size`, `--parallel`, and cache flags.
- Inspect GPU telemetry separately. A loaded model list does not prove GPU placement or lack of spill.

## Recommended reporting

State the per-model thread value, why it matches the concurrency topology, whether reload is required, and a fallback:

- dual GPU-offloaded servers on 24 physical cores: start **12 + 12**;
- contention or latency spikes: try **8 + 12** or **8 + 8**;
- one CPU-heavy/spilling server alone: test up to all physical cores.

Never claim a tensor-split remainder is CPU execution without placement evidence.