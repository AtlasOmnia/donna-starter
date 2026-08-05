# Hermes local routing verification

Use this when a Hermes profile combines a cloud main model with local delegated workers and local auxiliary/vision models. The profile name, the word “agent,” and LM Studio’s loaded-model list describe different layers; verify each layer independently.

## Routing layers

1. **Profile main model** — `model.provider` and `model.default`. This is what `hermes profile list` displays.
2. **Delegated agent model** — `delegation.provider` and `delegation.model`. This is the child worker spawned by `delegate_task`; it is not necessarily another profile.
3. **Auxiliary model** — `auxiliary.provider/model` plus task-specific entries such as `auxiliary.vision` and `auxiliary.compression`.
4. **Provider definitions** — named custom-provider blocks and any legacy aliases may point at different endpoints even when their names look equivalent.

When explaining whether “Dev” and “Agent” are different, state all three routes. Two profiles may share a main model while retaining isolated SOUL, tools, skills, memory, sessions, and vault ownership. Conversely, one profile may use three different models internally.

## Live LM Studio verification

Query both surfaces:

- `/v1/models` proves advertised OpenAI-compatible model IDs.
- `/api/v1/models` proves loaded instances, context length, parallel slots, Flash Attention, GPU KV offload, and effective capabilities.

Compare each loaded instance with Hermes metadata. A configured context larger than the live slot is unsafe near the boundary; a smaller configured value is conservative but may cause earlier compression or reduced capacity. Do not infer live context from the GGUF’s maximum.

For a two-model worker/auxiliary setup, verify:

- Worker model ID, live context, and `parallel` match `delegation.*` and `delegation.max_concurrent_children`.
- Auxiliary model ID and live context can accommodate its largest client’s compression payload.
- Vision capability is effective, not merely advertised: run an actual image request.

## Smoke sequence

Use bounded requests so a failed test cannot monopolize a local slot:

1. Worker exact-text response.
2. Worker structured tool call with required JSON arguments.
3. N simultaneous worker requests for N configured parallel slots.
4. Hermes profile-level worker invocation or a real child delegation.
5. Auxiliary text call through `call_llm(task='title_generation' or 'compression')`.
6. Auxiliary vision call through `call_llm(task='vision')` using a generated solid-color PNG.

A raw endpoint smoke proves model/mmproj health; a Hermes-path smoke proves routing and request shaping. Require both before calling the setup healthy.

## Named custom-provider vision pitfall

On builds where the vision resolver normalizes `custom:<name>` to `<name>`, ordinary auxiliary calls can use `providers.custom:<name>` while vision resolves through a separate legacy `providers.<name>` block. Config readback can therefore look correct while the actual vision client uses a stale URL.

Diagnosis:

- Resolve the vision client and inspect its effective `base_url`.
- Align the legacy alias and/or set an explicit `auxiliary.vision.base_url` to the intended endpoint.
- Retest through Hermes rather than stopping at raw curl.

## Uncapped local vision requests

Some Hermes auxiliary paths intentionally omit top-level `max_tokens` for ordinary OpenAI-compatible calls. Certain multimodal models may not stop promptly on image requests without an output cap. With `parallel: 1`, the timed-out request can occupy the sole slot and make later tests queue.

A configuration-level mitigation is:

```yaml
auxiliary:
 vision:
 base_url: http://<local-host>:<port>/v1
 extra_body:
 max_tokens: 1024
```

Choose a practical cap for real analysis, commonly 512–2048. Verify the mechanism first with a tiny cap and an exact-answer image fixture, then retest with the production cap. Before retrying after a timeout, send a short capped text request to prove the slot is free.

## One-shot delegation lifecycle

`delegate_task` is background work. A one-shot `hermes ... chat -q` parent may return before the child result re-enters the session even though the child completed successfully. For an end-to-end delegation smoke:

- Prefer a persistent interactive/gateway parent session, or
- Verify the child session/log independently by session ID, model, endpoint, and exact response.

Do not classify a fast one-shot parent exit as a model failure without checking the child runtime evidence.
