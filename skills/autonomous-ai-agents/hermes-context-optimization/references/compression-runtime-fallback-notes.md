# Compression Runtime and Fallback Behavior


Key findings:

- File: agent/context_compressor.py
 - ContextCompressor is initialized with summary_model from config.
 - Compression call site (line ~1500):
 - `call_llm(task="compression", model=self.summary_model)`
 - If summary_model is set, it overrides; otherwise uses main_runtime provider/model.
 - Fallback method: `_fallback_to_main_for_compression(e, reason)`:
 - Sets `self.summary_model = ""` (empty → use main model).
 - Clears cooldown so next compression immediately retries with main model.
 - Triggers on: timeout, JSON decode error, model-not-found, 503/404, and other non-transient errors.
 - Once triggered, persists for the session until a new ContextCompressor is created (new session).

- File: agent/auxiliary_client.py
 - `call_llm(task="compression", ...)` resolves provider via `_resolve_task_provider_model`.
 - For task="compression":
 - Reads auxiliary.compression config if present.
 - But compression uses explicit model=summary_model, so its own summary_provider config is primary.

- Config (config.yaml):
 - Compression settings live under:
 - `compression.summary_provider`
 - `compression.summary_model`
 - `compression.summary_base_url`
 - If these are set to a local endpoint (e.g., LM Studio), compression uses that model unless fallback occurs.

- User impact:
 - For large sessions (~100k+ tokens), if the summary model is slow, Hermes may time out and silently fall back to the main model for all subsequent compressions in that session.
 - "Preflight compression" only means the session size has crossed the threshold; it does not confirm which model will actually be used.

- Debugging:
 - After seeing "Preflight compression", check gateway logs:
 - `grep -i "fallback.*main\|Summary model.*Falling back" ~/.hermes/logs/gateway.log`
 - If no fallback log but main model is still being used, suspect timeout or misconfigured summary_provider.
