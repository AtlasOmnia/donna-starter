# IHG.com Hotel Price Extraction

IHG.com is a React SPA with aggressive bot protection. Standard tools fail consistently, but a specific browser-based extraction pattern works.

## What Fails

| Method | Result |
|--------|--------|
| `web_extract` | Times out after 60s |
| `curl` to API endpoints | "Access Denied" (EdgeSuite WAF) |
| `curl` with browser cookies | Blocked — CDP Network domain unavailable |
| `browser_vision` on screenshots | Hallucinates hotel names and prices — unreliable |
| Direct API URL manipulation (`qSrt=sPR`) | Returns "0 Hotel Found" |
| Compact snapshots (`full=false`) | Prices missing from accessibility tree |

## What Works: Full Snapshot + JS Extraction

### Step 1: Navigate and wait for dynamic load
```
browser_navigate → search results URL
wait 4-5 seconds for React hydration
```
The page initially shows "0 Hotel Found" then loads results. Capture the snapshot after the count appears.

### Step 2: Full snapshots show prices
Compact snapshots (`full=false`) omit dynamically-loaded price data. Use `full=true` — the prices appear as:
```
StaticText "156 USD"
StaticText "per night"
```

### Step 3: JS extraction via TreeWalker
The prices are split across separate text nodes:
- `<span>156</span><span> USD</span>` — number and currency in different nodes

Extraction pattern:
```javascript
const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
while (node = walker.nextNode()) {
  const text = node.textContent.trim();
  if (!/^\d{2,4}$/.test(text)) continue;        // pure number 50-9999
  const parent = node.parentElement;
  if (!parent || !parent.textContent.includes('USD')) continue;
  const price = parseInt(text);

  // Walk up to find h2 hotel name
  let card = parent;
  for (let i = 0; i < 15 && card; i++) {
    const h2 = card.querySelector('h2');
    if (h2) { /* extract name, price, rating */ break; }
    card = card.parentElement;
  }
}
```

### Step 4: Cross-reference with snapshot data
JS extraction gets prices and names accurately. For distances, ratings, and reviews, the full snapshot text provides the canonical values. The snapshot shows these cleanly:
```
StaticText "1.03 mi (1.65km) from destination"
button " rating 4.5"
button "2920 reviews"
```

### Lazy Loading
IHG lazy-loads hotel cards. Only ~19 of 43 were extracted in one session. To get all:
- Scroll aggressively (`browser_scroll` 4-6 times)
- `window.scrollTo(0, document.body.scrollHeight)`
- Re-run extraction after each scroll batch

### Sort Parameter Notes
The URL `qSrt` parameter accepts:
- `sAV` = Availability (default, works)
- `sPR` = Price low-to-high (returned 0 results — may need specific rate codes)
- `sDS` = Distance (default used in this session)

## Key Pitfalls
- **Never trust `browser_vision` for hotel names/prices.** It hallucinates — confused "avid hotels" with "EVEN Hotel Orlando International Airport South" and fabricated prices.
- **Compact snapshots hide prices.** Always use `full=true` for IHG pages.
- **Don't bother with CDP Network domain.** It's not available in the browser session for IHG.
- **Rating/reviews text concatenation.** textContent merges "rating 4.5" and "2920 reviews" into "rating 4.52920 reviews" — use `rating\s+(\d+\.\d)` not `(\d+\.?\d*)`.
