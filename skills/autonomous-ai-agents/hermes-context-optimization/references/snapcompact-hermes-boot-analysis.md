# Snapcompact for Hermes startup payloads

Session-derived notes from a discussion about using Snapcompact-style visual compression for Hermes initial context.

## Core distinction

Hermes initial payload is not one uniform blob. Split it before recommending compression:

1. **Authoritative instructions** — system/developer rules, safety boundaries, tool-use requirements, prompt-injection handling. Keep as real text.
2. **Tool schemas** — provider-facing structured JSON schema definitions. Cannot be replaced by images because the provider must register callable functions.
3. **Reference context** — memory, user profile, skill index, environment notes, prior summaries. Can be lazy-loaded, retrieved, summarized, or represented visually.

## Why the whole boot payload should not be an image

- Image text does not have the same authority as system-channel text.
- OCR/vision interpretation is probabilistic.
- Tool calling needs actual JSON/function schemas; a screenshot of schemas does not expose tools.

## Where visual context can help

Good candidates:

- full user profile beyond the compact core
- large memory/reference notes
- skill directory/index
- environment/project notes
- prior session summaries or compressed conversation archives

Poor candidates:

- system/developer instructions
- permission and safety boundaries
- prompt-injection rules
- tool schemas
- secrets or credentials

## Savings ratio from the discussed article

Observed ratio used for quick estimates:

```text
10,000 text tokens -> 3,279 image tokens
reduction ≈ 67.2%
```

Formula:

```text
image_tokens = text_tokens * 0.3279
saved_tokens = text_tokens * 0.6721
```

Examples:

| Text tokens | Image-equivalent | Saved |
|---:|---:|---:|
| 14,000 | ~4,591 | ~9,409 |
| 15,000 | ~4,918 | ~10,082 |
| 22,000 | ~7,214 | ~14,786 |

For Hermes boot optimization, apply this only to the imageable/reference subset. If only 8k of a 20k startup payload is reference material, the savings estimate is ~5.4k tokens, not ~13.4k.

## Recommended Hermes design

Use a hybrid boot model:

```text
Tiny authoritative bootloader
+ typed user prompt
+ minimal initial tool schemas
+ small core user profile
+ lazy skill/memory retrieval
+ optional snapcompact visual appendix for cold reference context
```

Possible config concept, not current verified syntax:

```yaml
startup:
 minimal_first_turn: true
 gate_tool_schemas: true
 visual_reference_appendix: optional

compression:
 strategy: hybrid_summary_plus_visual_archive
```

## Response style lesson

When the user asks a direct numeric question such as “what is the savings?”, answer with the estimate immediately and keep caveats short. Use tables only when they make the answer shorter.
