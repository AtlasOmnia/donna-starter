# Qwen Model Family Size Map

Last verified: June 2026

## Naming pitfall
Do NOT cross family names with wrong sizes. The most common error is "Qwen3.5 14B" — there is no such model. Qwen3 has 14B; Qwen3.5 has 9B.

## Qwen3 (Dec 2025)
| Size | HF Repo | Notes |
|------|---------|-------|
| 0.6B | `Qwen/Qwen3-0.6B` | |
| 1.7B | `Qwen/Qwen3-1.7B` | |
| 4B | `Qwen/Qwen3-4B` | |
| 8B | `Qwen/Qwen3-8B` | huihui-ai has abliterated |
| 14B | `Qwen/Qwen3-14B` | huihui-ai, richardyoung have abliterated on Ollama |
| 32B | `Qwen/Qwen3-32B` | |
| 30B-A3B | `Qwen/Qwen3-30B-A3B` | MoE |

## Qwen3.5 (Feb 2026)
| Size | HF Repo | Notes |
|------|---------|-------|
| 4B | `Qwen/Qwen3.5-4B` | |
| 9B | `Qwen/Qwen3.5-9B` | HauhauCS, DavidAU have uncensored; DavidAU has Claude-4.6 distill |
| 27B | `Qwen/Qwen3.5-27B` | |
| 35B-A3B | `Qwen/Qwen3.5-35B-A3B` | MoE |
| 122B-A10B | `Qwen/Qwen3.5-122B-A10B` | MoE |

Key: NO 14B in Qwen3.5. NO 8B in Qwen3.5.

## Qwen3.6 (Apr 2026)
| Size | HF Repo | Notes |
|------|---------|-------|
| 27B | `Qwen/Qwen3.6-27B` | Dense, SWE-bench 77.2. DavidAU Heretic is top pick. |
| 35B-A3B | `Qwen/Qwen3.6-35B-A3B` | MoE. SWE-bench 73.4. Worse for long agent loops. |
| 40B | Community | Claude Opus Deckard distill. <1K downloads, unvalidated. |

## Other families
| Model | Size | Type |
|-------|------|------|
| Gemma 4 | 12B, 26B-A4B (MoE), 31B | Vision + tool calling |
| GPT-OSS | 20B, 120B | OpenAI MoE |
| Mistral Small | 24B | Dense, Apache 2.0 |
| GLM-4.7-Flash | ~30B class | MoE, strong CJK, Heretic variant available |
