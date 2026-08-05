# Definitive Model-Variant Guide Format

## The Format That Works

Two proven posts on r/hermesagent:
- Qwen3.6-27B Community Variants — The Definitive Guide for Limited Hardware
- Qwen3.6-35B-A3B Community Variants — The Definitive Guide for Limited Hardware

Both well-received. Single model, exhaustive variant catalog, hard data per variant.

## Why It Works

1. ONE model, ONE post. Readers know exactly what they're getting.
2. Categories first (uncensored, heretic, abliterated, distilled, MTP), then variants within each category.
3. Hard data per variant: HF download counts, like counts, benchmark scores, VRAM at each quant level.
4. User-facing voice — tells them "download THIS" not "X is an option worth considering."
5. Caveats minimal and relegated to specific "Watch For" subsections.
6. Quick-pick table at end for fast readers.

## What Failed: Mac Research Doc (Anti-Pattern)

The compiled research document at mac-hermes-model-guide-2026.md (586 lines) was NOT ready to publish because:

### Internal briefing language
Lines like "For public wording:", "Public advice: recommend stock/instruct first", "The megathread should..." — these are research notes to the author, not content for readers.

### Caveat saturation
Every recommendation hedged: "MLX is fast, but...", "MTP is worth testing, not worth promising", "Ollama is easiest, not best." After 20 hedges, the reader trusts nothing.

### Too broad
Four model families × multiple tiers × multiple backends × multiple quants = shallow on each. The definitive guides go deep on one model and are useful because of it.

### Variant catalog missing
Mentions Heretic and HauhauCS but doesn't say: "HauhauCS Aggressive, 3.8M downloads, Q4_K_M is X GB, needs Y GB VRAM, download from THIS HF link." The definitive guides list every quant for every variant with exact sizes.

## Checklist: Research Notes → Published Definitive Guide

- [ ] Strip ALL meta-language ("public wording", "megathread should", "recommend for users")
- [ ] Pick ONE base model (or split into weekly series, one per model)
- [ ] Get hard numbers from HuggingFace API: downloads, last month downloads, likes
- [ ] Calculate VRAM estimates per quant level (model file + context overhead)
- [ ] Reorganize into: Categories → Variants (ranked by downloads) → Quick-pick table → Sources
- [ ] Rewrite every "might be good for" into "download this if..."
- [ ] Move caveats to a single "Watch For" section or inline footnotes per variant
- [ ] Remove all "treat as secondary source" / "verify locally" disclaimers from body text
- [ ] Final test: would a reader with a 24GB Mac know exactly which file to download after reading this?

## Weekly Series Strategy

One model per day rather than one mega-dump:
- Monday: Qwen3.6-27B on Mac
- Tuesday: Qwen3.6-35B-A3B on Mac
- Wednesday: Gemma 4 on Mac
- Thursday: DeepSeek V4 Flash on Mac
- Local: Qwen3.5-9B on a Mac

Each post: same definitive guide structure + Mac-specific RAM/bandwidth/backend framing.
Spread engagement, cleaner comments, easier moderation, each post self-contained.

## Combined-guide exception

The "one model, one post" rule is the default, but the guide author will COMBINE two tightly-related models into a single post when the total stays under ~60,000 characters — for example, a dense model plus its MoE sibling from the same family: same niche, deduped shared sections (Categories, Blackwell/NVFP4-MTP frontier, deep-thinking loop fix, Quick-Pick table, VRAM matrix, Notable Absences) and split per-model Variant lists under one "THE VARIANTS" header.

Rules when combining:
- Only combine siblings that share a use case and audience (e.g. same model family, dense + MoE). Do NOT combine unrelated models (Gemma + DeepSeek + Llama) — that's the "too broad" anti-pattern.
- State the combined char count up front; if it would exceed ~60k, split back into per-model posts.
- Keep one Quick-Pick table and one VRAM matrix that span both; list variants per-model so readers can scan their model.
- The NVFP4-MTP "frontier" subsection (Blackwell-only, hard Ampere/Ada exclusion) is the centerpiece when the guide's author daily-drives an NVFP4-MTP build — lead it as a shared section, then per-model variant catalogs.

## START-HERE ranked block + Community Verdicts
A definitive variant guide that ONLY catalogs variants will not RANK — and ranking is what drives SEO pickup and community trust. Two sections turn a combined refresh from a catalog into a ranking guide:

### START HERE — what to actually download (ranked)
Insert a short ranked block near the top (after the opener, before THE BASE MODELS) that answers "I have one 24GB-class GPU, download THIS" with a 5–7 line ranked list by hardware class + use case. Lead with a field-tested daily driver. This is the single highest-value SEO/usability addition — it gives a mobile/tap reader the answer in 6 lines.

### COMMUNITY VERDICTS — real pull-quotes from the last 2 weeks
Add a "COMMUNITY VERDICTS (last 2 weeks, real reports)" section with ATTRIBUTED quotes pulled from r/LocalLLaMA and r/localllm threads (not the author's opinion). These are the ranking signals a catalog lacks:
- Use `browser_navigate` to `<post-url>.json` with the Safari session — the old.reddit JSON endpoint returns raw JSON as page text reliably this way. The direct `requests.get('.json')` path from terminal now returns no data (likely unauthenticated-style throttle); reading `.env` directly in terminal triggers a credential guard that denies the whole command — do NOT retry that path; use browser tools or an explicitly authorized profile route.
- Extract real benchmark quotes (e.g. "DFlash 98 tok/s 2.2x but dips below baseline on creative text", "27B > 35B-A3B for instruction-following") and cite the u/<author> handle + thread date.
- State explicitly these are field signals, not benchmarks, and not the author's opinion.
- Fold the key nuances back into the variant entries (e.g. the DFlash creative-text dip belongs in the DFlash variant note; the 27B>35B instruction-following verdict belongs in both variant openers or the START HERE block).
- If a variant carries a public controversy, describe it in neutral terms: cite any allegation as unverified community discussion, state what is independently checkable (e.g. the download count), and point newcomers to a clean alternative. Do not assert allegations as fact.

### Verification discipline for the combined/refreshed guide
- Every HF link must resolve (200) — verify via a bounded terminal request in a profile that permits execution or through browser tools, not by eye. A past refresh caught 3 stale v2 repo IDs that would have 404'd; corrected them against live root-repo counts.
- "Ranked by downloads" headers must actually be descending; a cheaper verification delegate will catch out-of-order entries (e.g. a 15K variant listed before a 340K one). Re-sort strictly, or relabel the daily-driver as a featured lead and sort the rest.
- One-line changelog at the bottom citing what changed since the prior version (e.g. "v3 combined: NVFP4-MTP frontier, verified root-repo counts, deep-thinking loop fix, next-model heads-up").

## NVFP4-MTP frontier subsection pattern

When the guide covers NVFP4-MTP (Blackwell-native 4-bit float + multi-token prediction), make it a dedicated shared subsection, not a footnote:
- State NVFP4 requires Blackwell (RTX 50xx / B-series); NOT Ampere (RTX 30/40xx) or Ada (RTX 40xx) — those use FP8/FP16. NVFP4 files will not load off-Blackwell.
- List the verified NVFP4-MTP family with root-repo download counts (official nvidia/RedHatAI references first, then community grafts).
- Attribute "near-FP8 quality" to the publisher/NVIDIA — do NOT state NVFP4 quality as an established fact.
- Keep any "field-tested" tok/s as first-person author experience ("I run this daily and see ~1.7–2.0x over no-MTP"), not as a universal benchmark.
