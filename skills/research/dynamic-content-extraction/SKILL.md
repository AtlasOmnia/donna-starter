---
name: dynamic-content-extraction
description: dynamic-content-extraction — Extract structured data from JavaScript-heavy sites where prices, text, or key fields don't appear in the standard accessibility tree. Covers browser_snapshot(full=true), TreeWalker text-node extraction, lazy-load handling, and React split-text recovery.
version: 1.0.0
platforms:
- linux
- macos
- windows
metadata:
 hermes:
 tags:
 - Web-Scraping
 - Data-Extraction
 - Browser-Automation
 - JS-Heavy-Sites
---
# Dynamic Content Extraction

Extract structured data (prices, listings, product details) from JavaScript-heavy sites where key data is rendered by React/Vue/Angular and doesn't appear in compact accessibility snapshots.

## When to Use

- Extracting prices, inventory, or listings from booking/retail/travel sites (IHG, Marriott, Booking.com, Amazon, etc.)
- Data is visible on screen but absent from `browser_snapshot` (compact mode)
- `web_extract` times out or returns empty content
- Direct API calls are blocked by CDN/WAF (Akamai, Cloudflare)
- Vision model reads are inconsistent for exact numeric data
- the user asks for browser/search/internet tool inventory, fallback order, or says to check the vault for web tooling
- Estimating market-wide keyword demand when the request is phrased as “check Google Analytics” or a chart/API is rendered only in page JavaScript

References:
- If a browser/search/internet tool inventory or fallback order is needed, inspect the environment's own tool catalog at runtime rather than relying on a static vault note.
- distinguishes Analytics, Search Console, Keyword Planner, Trends, and SEO volume datasets; it includes same-origin Google Trends widget extraction and concise reporting guidance.
- documents the live OpenRouter model-performance endpoint, extraction code, metric interpretation, specialty-model screening, and Nitro routing.

## Workflow

### 1. Start with full snapshot

`browser_snapshot(full=true)` — compact mode (`full=false`, the default) often omits dynamically-injected prices and numbers. Full mode surfaces text from the complete accessibility tree.

**Pitfall:** Full snapshots on listing pages are often truncated (300-500 lines). Accept this and scroll + re-extract in batches.

### 2. Scroll to trigger lazy loading

Modern sites (IHG, Airbnb, Expedia) only render ~5-15 cards initially. Scroll 4-6 times before extraction:

```
browser_scroll(direction='down') # repeat 3-6 times
```

Then wait 2-3 seconds for React to hydrate new cards.

### 3. Extract via TreeWalker (React split-text recovery)

React and similar frameworks often split text across sibling elements. Example from IHG:
```html
<span><span>156</span><span> USD</span></span>
```
The number "156" and "USD" are separate text nodes — regex on parent textContent works but may merge adjacent values.

**Preferred pattern — TreeWalker for leaf text nodes:**

```js
(() => {
 const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
 const results = [];
 let node;
 while (node = walker.nextNode()) {
 const text = node.textContent.trim();
 // Match data patterns (prices, ratings, etc.)
 if (/^\d{2,4}$/.test(text) && node.parentElement.textContent.includes('USD')) {
 const price = parseInt(text);
 // Walk up to find container card
 let card = node.parentElement;
 for (let i = 0; i < 15 && card; i++) {
 const h2 = card.querySelector('h2');
 if (h2) {
 results.push({ name: h2.textContent.trim(), price });
 break;
 }
 card = card.parentElement;
 }
 }
 }
 return results;
})()
```

### 4. Walk up from data nodes to cards

Data nodes (price, rating) live deep inside React component trees. Walk up 10-15 levels to find the card container, then query inside it for other fields (name, distance, reviews).

Pattern:
```
price text node → parent → ... (walk up) → card container → querySelector('h2')
```

### 5. Cross-validate with snapshot data

Use `browser_snapshot` to cross-check hotel names and amenities, since the accessibility tree reliably captures headings and static text labels — just not the prices.

### 6. Discover and query same-origin frontend data APIs

When the page offers a useful sort/filter but the accessibility tree omits the underlying numbers:

1. Inspect `performance.getEntriesByType('resource')` for same-origin frontend/API requests.
2. If the UI's internal sort value is unclear, search loaded JavaScript chunks for the visible option label and recover its enum or query parameter.
3. Reproduce the request with `fetch()` inside `browser_console`, inspect the response shape, then join records through stable IDs rather than parsing rendered cards.
4. Preserve metric window, percentile, sample count, provider, and units in the result. Live rankings without those fields are easy to overstate.
5. Classify specialized entries before recommending them; a raw throughput leader may be a moderation, image, code-apply, or multi-agent model rather than a general assistant.

## Pitfalls

- **Confirm the active browser target on multi-tab/social sites.** `browser_console` can evaluate against the wrong tab or a browser new-tab surface after redirects/login flows. If the snapshot shows the target page but console reads `chrome://new-tab-page/` or unrelated content, call `browser_cdp(method='Target.getTargets')`, pick the `type='page'` target with the desired URL, then run `Runtime.evaluate` against that `target_id` to extract `document.body.innerText`.
- **For login-gated social pages, separate access verification from management actions.** After the user signs in, first verify the resolved URL, visible page title/name, follower/like counts, description/about text, and whether management controls are present. Do not switch profiles, edit settings, create ads, send messages, or otherwise mutate the account unless the user explicitly asks.
- **Don't trust vision for exact numbers.** Vision models conflate similar hotel names (avid ↔ EVEN), misread prices, and hallucinate hotels that aren't on screen. Use vision only as a last resort for layout questions.
- **web_extract fails on SPAs.** JS-heavy booking sites routinely time out (60s). Don't retry — go straight to browser tools.
- **CDP Network domain may be unavailable.** Don't assume `Network.getAllCookies` or `Network.getResponseBody` work in all browser sessions. Fall back to in-console `fetch()` calls from the same origin.
- **Direct API calls get Akamai/Cloudflare blocks.** Don't waste time on `curl` to booking-site APIs. Use the browser's authenticated session via `browser_console` `fetch()`.
- **Sort dropdowns may not respond to `browser_click`.** React-controlled custom dropdowns often ignore synthetic clicks. Try URL parameter manipulation instead (look for `qSrt`, `sort`, `order` params).
- **Lazy loading means one extraction never gets everything.** Scroll → wait → extract in a loop. Accept partial coverage and report how many of the total were captured.
- **textContent merging corrupts adjacent fields.** When "rating 4.5" and "2920 reviews" appear in sibling elements, `textContent` returns "rating 4.52920 reviews". Extract from leaf text nodes individually instead.
