---
name: publication-link-audit
description: publication-link-audit — Verify every outbound URL in a Reddit post, megathread, guide, wiki page, or README before publication. Detects transcribed IDs, GitHub filename drift, and HuggingFace repo naming mismatches that HTTP status codes alone miss.
version: 1.0.0
license: MIT
platforms:
 - linux
 - macos
 - windows
metadata:
 hermes:
 tags:
 - reddit
 - link-verification
 - megathread
 - publication
 - preflight
 related_skills:
 - reddit-content-management
 - source-verification
 - hf-model-card-research
---

# Publication Link Audit

Use this when the user has a Reddit post, megathread, guide, wiki page, or any README that is about to be published — and needs every outbound URL verified before going live. Also use when a published post is reported to have broken links.

This skill exists because HTTP 200 is necessary but not sufficient: a link can return 200 and still resolve to the wrong destination when the URL's opaque identifier was transcribed incorrectly.

## When to use

Use when:
- A megathread or Reddit post is being finalized for publication.
- A guide/README/wiki references external model cards, GitHub repos, or other Reddit threads.
- the user reports "some links are wrong" after publication.
- A document contains more than ~5 outbound URLs (below that, spot-checking is usually enough).

Do not use for:
- Simple URL shortening or redirect chasing.
- Verifying a single cited source in an article (use `source-verification`).
- Pulling benchmark data from HF model cards (use `hf-model-card-research`).

## The three failure modes

### Mode 1: Reddit post-ID transcription errors

Reddit post IDs are 7-character opaque alphanumeric strings. A single transposed character produces a different thread entirely — not a 404.

**Symptom:** The link labeled "Model Civil War" opens a post about an unrelated topic. HTTP status is 200; the label lies.

**Detection pattern:** Extract the page's `<title>` tag for every Reddit URL. Compare the title against the surrounding link text. Any mismatch means the ID is wrong.

Example from production:
- Link text said "Model Civil War — local vs cloud vs hybrid"
- URL was `1upvlm3` (a thread titled "Accepted to this hermes event")
- Correct URL should have been `1uqd00s`

**Fix:** Search the target subreddit with the intended label as query; extract the correct post ID from search results.

### Mode 2: GitHub dot-vs-no-dot filename drift

Repository filenames can differ by character class in ways invisible in review: `qwen3.6-combined.md` vs `qwen36-combined.md`, or `main` vs `master`.

**Complication:** `requests.head()` can return 404 for a valid GitHub URL where `curl -sL` (follow-redirect GET) returns 200. Different HTTP methods produce different status codes.

**Detection pattern:**
1. Verify with `curl -sL -w "%{http_code}"` or browser navigation — not HEAD alone.
2. If a GitHub URL 404s on HEAD, retry with GET before declaring broken.
3. If still 404, browse the repo's `megathreads/` (or equivalent) directory listing to find the actual committed filename.

### Mode 3: HuggingFace repo-name prefix drift

Some HF authors use a `Huihui-` prefix in one repo but bare `Qwen3.6-...` in another; some always suffix with `-GGUF`, others don't. A 100-character repo URL can be wrong in a single hyphen.

**Detection pattern:** For each author in the document, query the HF API to list their actual repos:
```
requests.get("https://huggingface.co/api/models?author=<name>&search=<keyword>")
```
Match the exact `modelId` from the result — don't reconstruct URLs from guesses.

Public repos return 200 on HEAD; private/misspelled repos return 401 or 404.

## Workflow

1. **Extract.** Pull every URL from the document (regex: `https?://[^\s\)\]<>]+`). Group by host:
 - `reddit.com` / `old.reddit.com`
 - `huggingface.co`
 - `github.com`
 - other

2. **Pair.** For each URL, note the surrounding text that **claims** what it links to. The label-URL pairing is what you'll verify.

3. **Verify reachability (host-specific):**

 | Host | Method | Notes |
 |---|---|---|
 | Reddit (old.reddit.com) | `requests.head` with browser UA; batch ≤8 concurrent requests | Sequential is safer. `www.reddit.com` triggers bot-protection pages more aggressively than `old.reddit.com`. Expect 429s under parallel load — these are not broken links. |
 | HuggingFace | `requests.head` (no auth needed for public repos; 401/404 = repo ID wrong) | Use the `/api/models/<owner>/<repo>` endpoint for metadata. |
 | GitHub | `curl -sL -w "%{http_code}"` (GET, follow redirects) | HEAD is unreliable — see Mode 2. |

4. **Verify content matches label.** This catches Mode 1 and is the only step that finds transposed IDs:
 - Reddit titles: extract `<title>` tag from each URL's response.
 - HuggingFace titles: check model card name.
 - GitHub: check page content is present (raw file blob, rendered README, etc.).

5. **Resolve failures.** For every 404/401/mismatch, run a targeted search to find the correct URL:
 - Reddit: `old.reddit.com/r/<sub>/search?q=<label>&restrict_sr=on` (browser navigation — API search also works).
 - HuggingFace: `/api/models?author=<name>&search=<kwd>`.
 - GitHub: browse the repo tree or check commit history.

6. **Produce a final table** — one row per URL with: URL, status code, label match (✓/✗), corrective action (if any).

## Rate-limit and method gotchas

- **Reddit parallel 429 rate limiting:** More than ~8 concurrent `requests.head` calls to `old.reddit.com` often triggers 429. Spread by subreddit, or run sequentially with 0.5s delays. 429 is NOT a broken link — retry or use browser.
- **Reddit `www.reddit.com` vs `old.reddit.com`:** `old.reddit.com` is bot-friendly and returns JSON cleanly. `www.reddit.com` frequently serves HTML bot-protection pages to non-authenticated requests, including for `.json` endpoints. Prefer `old.reddit.com` for verification.
- **GitHub HEAD vs GET:** The GitHub blob API can return 404 on HEAD but 200 on GET for the same URL. Always use GET for final verification.
- **Unauthenticated GitHub limit:** ~60 requests/hour. Use browser navigation for large batches.

## Checklist (use before declaring "all links verified")

- [ ] Every URL verified reachable via the correct HTTP method (HEAD-is-insufficient for GitHub).
- [ ] Page title/`<title>` checked against surrounding label text for **every** URL — catches Mode 1 (transposed IDs).
- [ ] Any 404/401 failure resolved via host-specific search before declaring broken.
- [ ] Parallel Reddit rate-limits respected; 429s are not broken links.
- [ ] Cross-reference check: where the document has multiple URLs to the same host, verify they point to **distinct intended content** (catches duplicate/copy errors).
- [ ] GitHub filename verified against actual committed tree — dots, hyphens, and suffixes matter.
- [ ] HuggingFace model IDs verified against HF API author search — don't reconstruct from guesses.
- [ ] Reddit post IDs verified against subreddit search — opaque IDs can't be eyeball-checked.

## Pitfalls

1. **Trusting HTTP status alone.** A 200 from a transcribed post ID gives a false sense of security. The label-vs-content check is the real verification.

2. **Stopping at HEAD for GitHub.** GitHub's blob endpoint can legitimately return 404 on HEAD and 200 on GET. Use GET.

3. **Treating Reddit 429 as broken.** Parallel `requests.head` to Reddit will get 429s. These are rate-limits, not missing pages. Retry.

4. **Reconstructing HF URLs from partial recall.** Don't guess `huihui-ai/Qwen3.6-35B-A3B-abliterated` from memory — query the HF API to get the exact `modelId`. Prefix drift, capitalization, and `-GGUF` suffixes are unreliable.

5. **Assuming post IDs are stable.** Reddit post IDs are permanent. But transcribing them from handwritten lists or chat history is where errors creep in. Verify every single one.

6. **Skipping the "label matches content" step.** This is the most valuable step and the one most likely to be skipped because it's the slowest. It is the step that catches Mode 1, which is the highest-impact failure mode.

7. **Bulk-parallel without stagger.** Batching 45 HF URLs in one parallel call is fine. Batching 45 Reddit URLs in one parallel call is not — you'll get 429 floods and lose signal.

8. **Publishing before verification passes.** If any URL fails both reachability and label match, do not publish. Fix first, verify again, then publish.
