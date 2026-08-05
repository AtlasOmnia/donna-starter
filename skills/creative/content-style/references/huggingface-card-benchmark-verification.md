# HuggingFace Model Card Benchmark Verification

When a megathread covers model variants, authors' published benchmark claims MUST be verified against the HF card before citing. Many HF cards list BASE model benchmarks in a "performance" table even though the card is for a fine-tuned variant — citing those numbers without attribution misleads readers.

## Two-Step Extraction Recipe

### Step 1: Stats via HF API (reliable, always use this)

```bash
curl -s "https://huggingface.co/api/models/{owner}/{repo}" | python3 -c "
import sys, json
j = json.load(sys.stdin)
print('downloads:', j.get('downloads', 0))
print('likes:', j.get('likes', 0))
print('siblings:', [s.get('rfilename','') for s in j.get('siblings', [])
 if s.get('rfilename','').lower().endswith('.gguf')][:6])
"
```

This is authoritative for download counts, likes, and file inventory. Run this for every repo in the guide.

### Step 2: Benchmark claims via web_extract on the web URL

```
web_extract on https://huggingface.co/{owner}/{repo}
```

Parse the model card README for quality claims: SWE-bench, AIME, refusal counts, KL divergence, per-quant quality tables, speed benchmarks.

**If web_extract fails on one URL, move to the next author** — do not retry indefinitely. Research subagents hitting timeouts will retry the same failing tool 20+ times before hitting an internal guardrail halt.

## Critical Pitfall: Base Model vs. Variant Benchmark Confusion

Many variant cards quote the BASE model's benchmarks in a "Base model performance" table but do NOT provide the variant's own benchmark deltas. Common trap cards:

- **rico03/Qwen3.6-27B-Claude-Opus-Reasoning-Distilled-GGUF**: Card lists "77.2 SWE-bench Verified, 94.1 AIME 2026" — but these are numbers for the BASE Qwen3.6-27B (sourced from official release), NOT for the rico03 Opus distilled variant. The fine-tune has no published benchmark delta.
- **unsloth/Qwen3.6-35B-A3B-MTP-GGUF**: Card lists "SWE-bench Verified 73.4, AIME 2026 92.7" — again base model numbers, not MTP variant numbers.
- **lordx64/Qwen3.6-35B-A3B-Claude-4.7-Opus-Reasoning-Distilled**: Card lists "GSM8K 84.3%, MMLU-Pro 74.9%" — these ARE the variant's own benchmarks (only lordx64 had real eval numbers).

**Rule:** When a card shows benchmarks, check whether the table heading says "Base model performance," "Qwen3.6-27B baseline," or "reference scores shown for comparison." If yes, those are BASE numbers — do not attribute them to the variant. Attribute as: "card lists BASE benchmarks (77.2 SWE-bench) but provides no metric for the distilled variant."

## KL Divergence Comparison Framework

For uncensored / abliterated variants, KL divergence from the base model is the best single capability-preservation metric:

| KL Range | Interpretation |
|---|---|
| 0.000–0.005 | **Near-identical to base** — surgical, best preservation |
| 0.005–0.01 | Very close — minimal drift |
| 0.01–0.05 | Noticeable but small drift |
| 0.05–0.15 | Moderate drift — may show measurable capability shifts |
| > 0.15 | Significant behavioral change |

Real numbers from July 2026 Qwen3.6 variants:
- **llmfan46 Heretic v2: KL 0.0021** — near-identical, best in class for preservation
- **DavidAU Heretic: KL 0.0469** — good, 22× worse than llmfan46 but still under 0.05
- **Other abliteration variants**: often KL not published — only refusal counts given

When comparing two uncensored variants, prefer the one with lower KL if the refusal counts are similar. When a variant has significantly higher KL, that's usually because the author added a capability fine-tune on top (coding, reasoning traces, etc.), not because abliteration itself drifted more.

## Specialization-Regression Pattern

Some variants SPECIALIZE — they improve on a subset of tasks but regress on general benchmarks. Flag these as REGRESSIONS on the headline metric with the delta, even if the specialization is useful.

**Real example from July 2026:**
- **Jackrong Qwopus 27B Coder-MTP**: SWE-bench Verified 67.0% (thinking-off, Q5_K_M)
- **Base Qwen3.6-27B**: SWE-bench 77.2% (thinking-on), 70.3% (thinking-off reference for Qwen3-Coder-30B)
- **Delta: -10.2 percentage points** — clear regression

**Do NOT frame this as "coding specialist."** The specialization comes at a measurable cost. Correct framing:
- "SWE-bench 67.0% — this is 10.2% BELOW base. Pick this for agentic coding workflows where reasoning traces help, NOT for raw SWE-bench."
- The card itself shows repository breakdown (scikit-learn 84%, django 72%, sympy 64%) — that's useful context to include so readers see where it excels vs. where it regresses.

## Summary: What a Verified Variant Entry Looks Like

After all verification, a variant entry in the definitive guide should include:

```
**Author/Variant** — 131,380 downloads, 402 likes (HF verified)
https://huggingface.co/author/variant

What: one-sentence description

Quality vs base (HF card verified):
- KL divergence: [number vs base, interpret] OR
- Refusals: X/Y (vs Z/Y base) OR
- SWE-bench Verified: [number] (vs [base number]) — regression/improvement
- Per-quant table: [if card provides one]
- **Base model benchmarks listed on card:** [note if card only shows base numbers]

Best for: one reader-facing scenario
VRAM: [quant tier with file sizes]
WHY PICK IT: [one sentence combining the numbers above into an editorial recommendation]
```

**Sources section** should list every HF card consulted with its actual download/like count at the time of verification, and flag any cards that had no benchmark data for the variant ("no benchmark listed").
