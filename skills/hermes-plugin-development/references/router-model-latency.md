# Router Model Latency Benchmarks

Live data from OpenRouter provider pages, June 2026. These models are candidates for pre-turn router/prediction calls where latency is critical (runs on every user turn).

## Top candidates (sorted by estimated total latency)

Estimates assume ~200 input tokens and ~50 output tokens (typical router prompt).

| Model | Slug | Best Provider | p50 Latency | Throughput | Est. Total | Cost/1M (I/O) |
|---|---|---|---|---|---|---|
| Llama 3.1 8B Instruct | `meta-llama/llama-3.1-8b-instruct` | Groq | 0.19s | 149 tok/s | ~0.5s | $0.04/$0.07 |
| Gemini 2.5 Flash Lite | `google/gemini-2.5-flash-lite` | Google AI Studio | 0.38s | 101 tok/s | ~0.9s | $0.10/$0.40 |
| Qwen3.5 Flash | `qwen/qwen3.5-flash-02-23` | Alibaba Cloud | 0.55s | 91 tok/s | ~1.1s | $0.07/$0.26 |

## Provider detail — Llama 3.1 8B Instruct (top pick)

| Provider | Latency | Throughput | Input $/M | Output $/M | Token Share |
|---|---|---|---|---|---|
| Groq | 0.19s | 149 tok/s | $0.039 | $0.071 | 46.3% |
| DeepInfra | 0.26s | 23 tok/s | $0.020 | $0.027 | 16.3% |
| DeepInfra (2) | 0.34s | 19 tok/s | $0.020 | $0.047 | 23.2% |
| Weights & Biases | 0.21s | 99 tok/s | $0.219 | $0.220 | 1.1% |

OpenRouter auto-routes; Groq gets ~46% of traffic. DeepInfra fallback at 0.26s latency is still acceptable (~2.4s total for 50 output tokens).

## Why not Codex for router calls

The Codex endpoint (`chatgpt.com/backend-api/codex`) uses the Responses API format. A standard OpenAI SDK client calling `chat.completions.create()` hits Cloudflare WAF and receives HTML challenge pages — not JSON. Hermes routes through `agent/transports/codex.py` (`ResponsesApiTransport`) which handles this correctly, but plugin-level direct calls to Codex will fail unless they implement Responses API format.

## OpenRouter integration pattern

```python
from openai import OpenAI

client = OpenAI(
 api_key=os.environ["OPENROUTER_API_KEY"],
 base_url="https://openrouter.ai/api/v1",
 timeout=8,
 max_retries=0,
)
response = client.chat.completions.create(
 model="meta-llama/llama-3.1-8b-instruct",
 messages=[{"role": "system", "content": "Classify this..."}],
 temperature=0.0,
 max_tokens=200,
)
```

Always wrap in `ThreadPoolExecutor` with a hard timeout (see parent skill).
