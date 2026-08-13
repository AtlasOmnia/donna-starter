# web_extract Fallback Strategies

JS-heavy travel/booking/hotel/attraction sites frequently time out on `web_extract`. Here's the proven fallback chain.

## First: web_search with targeted queries

Google search result snippets are surprisingly data-rich. Even when a page won't load, its search snippet often contains ticket prices, hotel starting rates, and package descriptions from structured data.

**Good patterns:**
- `"Graceland" "$85" adult ticket 2026` — prices often appear verbatim in snippets
- `"Guest House at Graceland" $182 night` — hotel rates in price-structured snippets
- `site:wonderfulmuseums.com graceland tickets` — third-party aggregators with clean text content

## Second: browser_navigate → browser_snapshot

JS-heavy sites that kill web_extract often render fine in the browser:
1. `browser_navigate(url)` — loads the full page
2. `browser_snapshot()` — reads the accessibility tree with visible text content
3. If the content is below the fold, `browser_scroll(direction='down')` first
4. Try `browser_vision(question='what prices are shown?')` as a visual fallback when the AX tree is too sparse

**Limits:** Complex navigation overlays and cookie consent dialogs can obscure content. Dismiss them before snapshotting.

## Third: Read search result snippets as primary data

When a search result description reads: "Ultimate VIP Tour. $240 Before 1:30pm | $215 After 1:30pm. Elvis Entourage VIP Tour. $148 All Ages. Elvis Experience Tour. $85 Adults | $49 Kids" — that's real data from the page's meta description or structured data markdown. It's reliable for factual pricing.

**Label it clearly:** "From Google's official page snippet" so the user knows the source scope.

## Fourth: When browser is also blocked by Cloudflare

Some travel/airline/booking sites (Allegiant Air, directflights.com, etc.) show a Cloudflare "Just a moment..." challenge that blocks even `browser_navigate`. When the page title is "Just a moment...", **do not retry** — re-navigating won't bypass the challenge.

When browser is blocked, your only remaining sources are:

1. **Search result snippets** — Google's meta descriptions and structured data often surface:
   - Ticket prices (e.g. `$85 Adults | $49 Kids`)
   - Hotel starting rates (e.g. `from $182 per night`)
   - Current deals (e.g. `20% off`)

2. **Press releases / news articles on the official site** — Search for:
   - `site:graceland.com offers` or `site:graceland.com elvis-news`
   - `site:guesthousegraceland.com special-offers`
   - These text-based article pages are less aggressive with bot detection than booking engines
   - They often contain specific promo codes, discount percentages, and date windows

3. **Third-party review/aggregator articles** — Sites like KAYAK, TripAdvisor, blog posts, and news outlets that quote the official pricing. Label these clearly as "from a third-party source" in your output.

## What NOT to do

- Do not retry web_extract more than 2x on the same failing URL
- Do not retry browser_navigate more than once on a Cloudflare-blocked page
- Do not fabricate a price from memory
- Do not switch to computer_use / desktop automation just because a page is blocked — search snippets are sufficient
- Do not claim a price as "official" when it came from a third-party article
