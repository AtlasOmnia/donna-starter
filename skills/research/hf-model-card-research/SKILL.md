---
name: hf-model-card-research
description: hf-model-card-research — Pull structured benchmark metadata, download stats, and quality claims from HuggingFace model cards for comparison across model variants.
version: 1.0.0
platforms:
- macos
- linux
- windows
metadata:
 hermes:
 tags:
 - HuggingFace
 - Model-Research
 - Benchmark-Analysis
 - LLM-Comparison
 - Data-Extraction
 - Model-Cards
---

# HF Model Card Research

Extract structured metadata — downloads, likes, benchmark claims, file sizes, author statements — from HuggingFace model cards. Used when the user asks you to "check these models on HF", "pull benchmarks for these variants", or "compare what authors claim."

## When to Use

- User provides a list of authors and model families (e.g. "pull metadata for these Qwen3.6 variants")
- You need to compare benchmark claims across multiple fine-tunes of the same base model
- You need up-to-date download counts, likes, or file sizes for model variants
- Verifying what a model card claims vs what other sources say
- Surveying the ecosystem around a new base model release

## Workflow

### 1. Discover model repo names

Search HF for each author's models using `site:huggingface.co` queries:

```
site:huggingface.co <author> <model-family> <variant-keyword>
```

Try variant-specific keywords: the author's handle, the model name, key terms like "uncensored", "abliterated", "Opus", "NVFP4", "MTP", etc.

For community quantizers (mradermacher, unsloth, byteshape), search with: `site:huggingface.co <author> Qwen3.6-27B`.

If search results are sparse, try the author's HF profile page directly: `https://huggingface.co/<author>/models` — use `web_extract` on that.

### 2. Pull structured stats via HF API

The HF API endpoint returns the metadata you need. Pull JSON, don't scrape the web view for stats:

```
https://huggingface.co/api/models/{owner}/{repo}
```

Returns JSON with:
- `downloads` — download count
- `likes` — like count
- `pipeline_tag` — model type (text-generation, image-text-to-text)
- `tags`, `cardData`, `config`, `gguf`, `safetensors`, `siblings` (file list), `createdAt`/`lastModified`
- `spaces` (linked HF Spaces)
- `model-index` (evaluation results when present)

**Pitfall — delegated subagents hit terminal guardrails on HF pulls.** Three dispatched subagents (each on different HF research tasks, all variants) hit `same_tool_failure_halt` after 4 repeated terminal retries on failed HF calls. The failure mode is predictable: subagents loop on the same failing `terminal` (curl to HF API) because they think "retry the same call until it works." The per-turn tool guardrail halts them after 4 non-progressing attempts with zero data produced. This happened across three separate delegations in the same session.

**Fix — use a bounded host-side Python script through `terminal` in a profile that permits execution (or a no-agent cron script), not delegation for HF pulls.** When you need stats for a list of repos, run the loop as one bounded process with direct `requests.Session()` and per-repo exception handling so one failure does not stop the rest.

**Working pattern (copy-pasteable):**

```python
import json, requests, time, pathlib

repos = [
    ("owner1", "repo1"),
    ("owner2", "repo2"),
    # ... one tuple per repo
]

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) HermesResearch/1.0"})

lines = ["# HuggingFace Model Stats", ""]
for owner, repo in repos:
    try:
        r = s.get(f"https://huggingface.co/api/models/{owner}/{repo}", timeout=20)
        if r.status_code != 200:
            lines.append(f"## {owner}/{repo}\n**Error:** HTTP {r.status_code}\n")
            time.sleep(0.5); continue
        j = r.json()
        lines.append(f"## {owner}/{repo}")
        lines.append(f"- **URL:** https://huggingface.co/{owner}/{repo}")
        lines.append(f"- **Downloads:** {j.get('downloads', 0):,}")
        lines.append(f"- **Likes:** {j.get('likes', 0):,}")
        ggufs = [f for f in [x.get('rfilename','') for x in j.get('siblings',[])] if f.lower().endswith('.gguf')]
        if ggufs:
            lines.append(f"- **GGUF files ({len(ggufs)}):** {', '.join(ggufs[:6])}" + ("…" if len(ggufs) > 6 else ""))
        lines.append("")
    except Exception as e:
        lines.append(f"## {owner}/{repo}\n**Error:** {e}\n")
    time.sleep(0.3)

out = pathlib.Path("~/Desktop/hf-verified-stats.md")
out.write_text("\n".join(lines))
print(f"Wrote {out}")
```

**Why this works where delegation fails:**
- One bounded process handles per-repo exceptions; a failed repo does not stop the next 21
- The script can persist partial results even if the session ends partway
- A single bounded run is easier to verify than repeated tool retries

**When delegation IS still appropriate for HF research:** Extracting README prose (benchmarks, claims) via `web_extract` on the web-view URL. One failed `web_extract` URL → move on, don't retry. For the stats-only pass (downloads/likes/file list), use the same bounded host-side Python path. For README benchmark prose extraction, `web_extract` on individual web-view URLs still works fine from the parent because the failure mode is different (one URL at a time, not a list).

**Batching for the web_extract README pass:** After the stats pass, you may want README content (benchmarks, claims) that isn't in the API JSON. Pass up to 5 URLs per `web_extract(urls=[...])` call against the web view (`https://huggingface.co/{owner}/{repo}`). `char_limit=8000` gets the head + tail of large cards; look for the footer line showing where the full text is cached and `read_file` the middle if needed.

**Pitfall — "base model benchmark" cards.** Many fine-tune cards list the *base model's* official benchmarks (e.g., "Qwen3.6-27B SWE-bench 77.2, AIME 94.1") without providing any delta data showing how the distilled/uncensored variant compares to base. Always flag when a card's benchmark numbers are for the BASE model, not the variant itself. Confirmed examples from July 2026: rico03 Opus 4.6 Distilled lists base Qwen3.6-27B's benchmarks only; lordx64 Opus 4.7 Distilled lists NO benchmark deltas at all. Only DavidAU Heretic (KL=0.0469, 4/100 refusals, per-quant accuracy table) and Jackrong Qwopus v2 (30-question throughput bench) provided variant-vs-base numbers among the top 22 variants checked.

### 3. Extract README benchmark claims

The README at `https://huggingface.co/{owner}/{repo}/resolve/main/README.md` is where authors publish benchmark tables.

**Key fields to look for:**

- **SWE-bench Verified** — the most common agentic coding benchmark
- **AIME 2024/2025/2026** — competition math
- **MMLU-Pro / GPQA Diamond** — knowledge & reasoning
- **ARC-c / ARC-e** — common-sense reasoning (DavidAU uses these prominently)
- **GSM8K / MATH-500** — math
- **LiveCodeBench** — coding
- **KL divergence** — for abliterated/heretic models: how much the uncensored version drifted
- **Refusal rate** — for uncensored variants: X/100 or X/465
- **Quant accuracy** — "Same Top P %", "Mean KLD", quant-specific benchmarks
- **Throughput (tok/s)** — MTP speed claims

**Pitfalls:**
- Many fine-tune/quant model cards have `model-index: null` in the API — they don't publish formal eval results. In those cases, only the README text has benchmarks.
- Some cards only list the *base model's* official benchmarks (not the fine-tune's own results). Flag this.
- "Pending" results are common for recently released models.
- Some authors (DavidAU) publish their own in-house benchmark suite (arc-c, arc-e, boolq, hswag, obkqa, piqa, wino) not standard HF eval.
- Cards in Chinese or with markdown image embeds for benchmark tables — `web_extract` may not capture image-based tables.

### 4. Get file sizes for recommended quants

From the HF API JSON, check `siblings` array for file names and sizes. For GGUF repos, the README often has a download table with explicit sizes.

Alternatively, use `gguf.totalFileSize` from the API for the total repo size.

### 5. Compile structured output

**For each variant, report:**
- Author, exact repo name
- Downloads, likes
- Pipeline type / multimodality
- Base model (exact HF ID if declared)
- Recommended quant size (e.g. Q4_K_M ~15 GB)
- "What this variant is for" statement from card
- Benchmark table (SWE-bench, AIME, MMLU-Pro, GPQA, ARC-c, GSM8K, etc.) — or "no benchmark listed"
- Refusal rate / KL divergence (for uncensored variants)
- Any quant accuracy claims

**Signal wording rules:**
- If a card reproduces the base model's benchmarks (not the fine-tune's), say "card shows base model benchmarks only"
- If benchmarks are pending/coming soon, say "pending"
- If no benchmark table exists, say "no benchmark listed"
- Never fabricate numbers

### 6. Cross-check claims across variants

When the user wants a comparison, produce a summary table at the end grouping:
- Variants with actual SWE-bench/AIME numbers
- Variants with refusal-rate data
- Most popular models (by downloads)
- Models that claim benchmark deltas vs the base

## Pitfalls

- **Don't treat all benchmark tables equally.** Some are from official eval harnesses, some are in-house 30-question smoke tests. Note the methodology where visible.
- **Some repos have `model-index` in the API but with empty results.** Check `model-index.results` array length.
- **README extraction can be truncated** for very large cards. Use `read_file` on the cached output to page through the middle.
- **`web_extract` automatically handles truncation** by saving the full text to a cache file. Look for the footer line showing the file path.
- **API quota is not an issue** on HF's public API — but avoid hammering it. Batch your calls.
- **GGUF-only repos** (no safetensors) have `gguf` metadata but no `safetensors` block.
- **License field** is in `cardData.license`, not always in `tags`.
- **Some repos ship MTP heads as separate tensors** — check `siblings` for `mtp`-related filenames.
- **Refusal-rate tests use different methodologies** (100-prompt, 465-prompt). Note the test size when comparing.
- **"0 downloads" can happen** on newly-published repos with Xet-based storage that doesn't track downloads the same way.
