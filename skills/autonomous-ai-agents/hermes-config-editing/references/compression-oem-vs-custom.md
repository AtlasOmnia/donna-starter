# Hermes Compression: OEM vs Custom Config Notes

Session-derived notes for debugging whether prompt-processing/compression behavior is caused by custom config or a code patch.

## OEM top-level compression defaults
Observed in `~/.hermes/hermes-agent/hermes_cli/config.py`:

```yaml
compression:
 enabled: true
 threshold: 0.50
 target_ratio: 0.20
 protect_last_n: 20
 hygiene_hard_message_limit: 400
 protect_first_n: 3
 abort_on_summary_failure: false
```

Interpretation from code/status:
- `threshold` triggers compression at that fraction of model context.
- `target_ratio` is a fraction of the threshold token budget preserved as recent tail. Example: 131072 context × 0.50 threshold × 0.20 target ≈ 13107 tail tokens.
- `protect_first_n` preserves non-system head messages in addition to the always-protected system prompt.

## Auxiliary compression model
The status output's compression `Model` and `Provider` come from:

```yaml
auxiliary:
 compression:
 provider: ...
 model: ...
```

Do not confuse this with old top-level `compression.summary_model` / `summary_provider` fields.

To make aux compression follow the active/main model-provider route, clear the explicit override instead of duplicating model fields:

```yaml
auxiliary:
 compression:
 provider: auto
 model: ""
 base_url: ""
 api_key: null
 timeout: 180
 extra_body: {}
```

`provider: auto` with an empty `model` lets Hermes resolve through the current runtime/provider chain. Keep the existing `timeout` unless the user asks for OEM defaults.

## Legacy/dangling keys
`threshold_ratio` was found in config but no Python references were found in the checkout. Treat it as custom/dangling unless a local patch outside the searched tree reads it.

Top-level compression keys like `summary_model`, `summary_provider`, `summary_base_url`, and `summary_api_key` appear legacy/migrated relative to current `auxiliary.compression`; verify in source before removing.

## Workflow lesson
When the user is isolating OEM behavior vs custom patches, do not proactively remove unknown keys. First report:
1. current config block,
2. upstream OEM block,
3. keys that appear unread by source,
4. proposed cleanup diff.

Only write after approval when the change removes or migrates keys.
