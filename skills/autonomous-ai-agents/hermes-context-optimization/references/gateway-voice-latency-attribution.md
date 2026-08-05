# Gateway and voice latency attribution

Use this to determine whether perceived voice latency comes from STT endpointing, Hermes/model processing, tools, transport, or TTS playback.

## Measurement discipline

1. **Do not ask the measured agent to inspect its own logs during the measured turn.** Those tool calls create extra model round trips and contaminate the result.
2. Send one short, tool-free probe such as `Reply with exactly: LATENCY_OK`.
3. Inspect logs and session state from a separate controller/session after the probe completes.
4. Keep component boundaries distinct:
 - speech end → final transcript: STT/endpointing
 - final transcript accepted → first/complete model response: Hermes + provider
 - each tool call: actual tool duration plus the additional model calls before/after it
 - completed model response → audio playback start: TTS synthesis/buffering
 - client ↔ gateway health request: transport/tunnel baseline
5. If the current build does not timestamp a boundary, label it unmeasured rather than estimating it.

## Hermes log calculation

For each turn, capture:
- `agent.turn_context` timestamp
- every `API call #N ... latency=Xs` line
- each `tool ... completed (Xs)` line
- `Turn ended` timestamp
- input tokens and cache ratio per API call

Compute:

```text
total turn = Turn ended - conversation turn
model time = sum(API call latencies)
tool time = sum(tool durations)
overhead = total turn - model time - tool time
```

Report model/tool/overhead percentages and API-call count. Use a calculation tool; do not do arithmetic mentally.

## Interpretation

- Tool-heavy latency is often dominated by the model calls surrounding tools, not by the tool execution itself.
- Compare clean single-call turns at several context sizes. Input-token growth correlated with longer model calls is direct evidence of context pressure even when cache hits are high.
- Tool Router reduces transmitted schemas and unnecessary tool selection; it does not compact accumulated message history. Pair it with an explicit context/compression policy when history is the bottleneck.
- A dedicated voice profile can isolate session history, but it also isolates ongoing profile memory. Treat that as an architecture tradeoff, not a free optimization.
- A healthy gateway PID does not establish low transport latency. Measure the actual client-side tunnel/health round trip.
- If the voice client waits for the complete LLM response and then buffers the complete TTS artifact before playback, perceived silence includes both delays. Streaming text into sentence-level TTS is the architectural remedy; first prove the existing boundary timings.

## Acceptance shape

Return a compact table with total, model, tool, and overhead times; state the dominant component; show context-token growth; identify any unmeasured STT/TTS boundary; and name the smallest reversible optimization to test next.
