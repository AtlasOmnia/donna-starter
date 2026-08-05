# Local Compression Economics

Use this when deciding whether moving Hermes context compression from a cloud auxiliary model to a local model is financially worthwhile.

## Compare against the effective route

Do not compare local compression only against the main model. First inspect the profile's effective compression route:

1. `auxiliary.compression.*` — usually authoritative.
2. `compression.summary_*` / `compression.*` — fallback or compatibility settings.
3. Main-model fallback behavior if the auxiliary compressor fails.

A profile using an inexpensive auxiliary API can have very different savings from one compressing with its flagship main model.

## Measure actual usage

Hermes records task-level usage in the profile-specific state database. Named profiles normally use:

```text
~/.hermes/profiles/<profile>/state.db
```

The default profile normally uses:

```text
~/.hermes/state.db
```

Query `session_model_usage` for `task='compression'` and aggregate:

- `api_call_count`
- `input_tokens`
- `output_tokens`
- `estimated_cost_usd` / `actual_cost_usd`
- `first_seen` / `last_seen`

Join `sessions` only when profile/session metadata is needed. Do not accidentally query the default profile database for a named profile and conclude there is no usage.

## Calculation

For a measured interval:

```text
cloud_cost = input_tokens / 1M × input_rate
 + output_tokens / 1M × output_rate

30_day_projection = observed_cost × 30 / observed_days
```

Report at least:

- observed interval and number of compression calls;
- measured cloud cost;
- cost per compression;
- projected monthly savings before electricity;
- a separate hypothetical flagship-main-model cost only if useful.

Verify current pricing from the provider's official pricing page or Hermes' current pricing registry. Never reuse remembered prices without checking.

## Local operating cost

Local inference has zero API cost, not zero total cost. If runtime duration and GPU power are known:

```text
electricity_cost = average_kW × runtime_hours × electricity_rate_per_kWh
```

If those measurements are unavailable, label savings as **before electricity** rather than inventing a net figure.

## Decision rule

When the current cloud compressor is already extremely cheap, local compression may save only a few dollars per month. In that case, frame the main benefits accurately:

- code and session-state privacy;
- independence from API availability and rate limits;
- protection against expensive fallback to the flagship main model;
- predictable local operation.

Do not sell a local compressor as a major cost optimization when the measured data says otherwise.

## Model-sizing lesson

For coding-session compression, distinguish the smallest model that technically accepts the context from the smallest model dependable enough to preserve file paths, implementation decisions, errors, test evidence, and unfinished work. Recommend the dependable floor first; identify smaller models only as technical/disposable-summary options.