---
name: marketplace-purchase-vetting
description: "marketplace-purchase-vetting — Search/discover AND vet Facebook Marketplace/Craigslist/private-party purchases. Two modes: find the best live options in the area within a budget, then vet promising candidates for too-good-to-be-true risk. Covers vehicles, boats, trailers, equipment, and other high-dollar local listings."
tags:
- marketplace
- facebook-marketplace
- craigslist
- used-vehicles
- boats
- private-party
- scam-check
---
# Marketplace Purchase Vetting

Use this when the user asks whether a local listing is a scam, "too good to be true," worth looking at, or a good deal. Also use this when he asks you to **find** options — search/discover candidates, then vet the best ones. The goal is not a generic buying guide; it is a practical risk read with clear next steps.

Two modes: **Discovery** (find me options) and **Vetting** (check this listing). Run them in sequence when the user hasn't identified a specific listing.

---

## Mode 1: Discovery — Search for candidates in the area

Run this first when the user says "find me a car/suv/truck for $X in our area" without a specific link. The output is a ranked shortlist of the best live options.

### Facebook Marketplace search procedure

Read before a broad or tightly constrained vehicle hunt; it documents radius conversion, ignored filters, regional partitioning, feed virtualization, and dealer/down-payment traps.

1. **Set up the search URL.** Facebook Marketplace uses structured URL parameters:
 ```
 https://www.facebook.com/marketplace/{city}/vehicles?minPrice={min}&maxPrice={max}&sortBy=creation_time_descend&exact=false
 ```
 - Default to the user's nearest metro area as the city slug; ask when unclear.
 - Set price range with ~$500 buffer below max budget (e.g. $3,000--$4,000 for a $3.5k budget) so the floor filters out junk but the ceiling doesn't miss negotiable listings.
 - `sortBy=creation_time_descend` shows newest first — gives the freshest picks.

2. **Navigate in a logged-in browser session.** Facebook Marketplace requires authentication to show results. Use the browser tool (Chrome CDP). Navigate to the constructed URL.

3. **Scrape the results page via CDP `Runtime.evaluate`** — much faster than clicking each listing:
 ```javascript
 JSON.stringify(Array.from(document.querySelectorAll(
 'a[href*="/marketplace/item/"]'
 )).map(a => ({
 text: a.innerText.trim(),
 url: (a.href.match(/marketplace\/item\/(\d+)/) || [])[1]
 })).filter(x => x.text))
 ```
 This returns all visible listings' title, price, location, item ID as one JSON blob.

4. **Filter noise and verify every hard constraint from the detail page.** Results include motorcycles, boats, ATVs, golf carts, parts, and misleading dealer/down-payment listings. Facebook's generic `/search?query=...` page may show results that ignore vehicle-only parameters such as `minYear` and `maxMileage`; treat those URL parameters as hints, not proof. Never report an exact match until its detail page confirms year, full purchase price, mileage, and location.

5. **Convert large search radii correctly.** Facebook's `radius` query parameter is kilometers even when the interface displays miles: `radius=100` renders as about 62 miles; use `radius=161` for about 100 miles. Verify the rendered location control says `Within 100 mi`. If a broad make query is noisy, run model-family searches (for example Corolla, Camry, Yaris, Matrix, Prius, and RAV4) and deduplicate by item ID.

6. **Use a search matrix when exact inventory is scarce.** Run each important model separately with both newest-first and price-highest-first sorting; lowest-price sorting is usually dominated by dealer down-payment ads. Partition a large area into regional searches while enforcing the user's true distance from the requested ZIP code. A page showing “Within 100 mi” proves the radius but not its center: never claim it is centered on the requested ZIP unless the Marketplace location control was actually set to that ZIP. When using nearby city slugs for discovery, independently validate each finalist’s distance from the requested ZIP and exclude anything outside the hard limit.

7. **Extract each visible batch before scrolling and control tab count.** Facebook virtualizes long feeds and may remove earlier cards from the DOM. Save each batch of item IDs and card text before moving farther down the page. Independent model/region searches can be opened in separate tabs and evaluated in parallel, but keep the live tab set bounded (prefer one reusable search tab plus a small batch of detail tabs). Close detail targets after extraction; dozens of Facebook tabs/renderers can make Chrome’s CDP endpoint unresponsive and turn a fast search into a browser-recovery exercise.

8. **Open individual listings for the top candidates** and read `document.body.innerText` via CDP. Parallel CDP tabs are useful when several candidates need independent inspection. Extract:
 - Exact mileage, transmission, title status (clean/rebuilt/salvage)
 - Whether the displayed amount is the full cash price, a down payment, or excludes mandatory dealer fees
 - Seller's description text (often reveals undisclosed issues)
 - Seller name + account age ("Joined Facebook in 20XX")
 - "Highly rated" / "Very responsive" badges
 - Listed age ("Listed X hours/days ago")
 - VIN when available

9. **Cross-check implausibly good results before ranking them.** Search the VIN, inspect the dealer's own inventory, review price history, and search complaint/review sources. A third-party listing that says “clean title” or “all-in price” is not enough when the price is dramatically below market. Duplicate listings with identical mileage, photos, and copy under different seller accounts are a high-risk signal; report the duplication and require VIN/title/identity verification before recommending travel.

10. **Maintain a rejection ledger.** Record every opened listing's item ID and the failed criterion: actual mileage, year, cash price vs down payment, title, defects, duplicate post, dealer fees, or distance. This prevents reopening the same bad inventory and makes the final exact-match/near-match separation auditable.

### Evaluating candidates

Prioritize these objective measures over listing description polish:

| Factor | Weight |
|---|---|
| **Japanese make** (Toyota/Honda/Mazda > Hyundai/Kia > domestic) | High |
| **Clean title** (rebuilt title = cut estimated resale in half) | High |
| **Mileage** (under 160k ideal, 160-200k acceptable, over 200k requires very low price) | Medium |
| **Seller account age + responsiveness badge** | Medium |
| **Number of owners** (1-2 is ideal) | Low |
| **Recently replaced parts** (tires, battery, starter, brakes) | Situational |

### Discovery output format

**Headline:** [Pick 1 / Pick 2 / also consider] with numbered medaling.

Each entry:
```
### #. **Year Make Model** -- $Price
- City | XXXk mi | Auto/Manual | Title status
- Key pros (2 lines max)
- Key cons (1 line if any)
- **[Message seller](link)**
```

End with:
- **My recommendation:** which one to message first and why
- **Avoid:** listings with dealbreaker issues and why
- Offer to drill into any listing further

If no credible exact match survives detail-page verification, say so plainly. Honor hard year, price, mileage, and distance limits strictly; do not silently relax them. A replacement engine does not reset chassis mileage—report odometer/chassis mileage and claimed engine mileage separately. Separate:
- **Credible exact matches**
- **Exact on paper but high-risk/misleading**
- **Near matches rejected** (state the failed constraint)

Do not medal or positively rank a listing merely because its headline fits. For a suspicious duplicate or implausible dealer price, give the direct link plus the exact verification gate (VIN, title photo, odometer/cold-start video, seller-ID match, written out-the-door price) that must be cleared before travel.

---

## Mode 2: Vetting — Check a specific listing

Run this when the user already has a link.

## Default workflow

1. Open the listing directly when possible.
 - For Facebook Marketplace, use browser automation if web extraction/search cannot see the listing.
 - If a login modal appears, close it and use the visible public listing text. Do not ask the user to log in unless messaging/seller profile access is essential.
 - Extract: title, year/make/model, price, prior price, location, listed age, condition label, description, included/excluded items, title/ownership claims, test-drive availability, and delivery/transport claims.

2. Compare against market reality.
 - Search web comps from at least two source types when available: dealer marketplaces, valuation guides, forums, sold/current listings, or model-specific pages.
 - Separate exact-year/model comps from adjacent-year/model comps.
 - Note when a source includes items the listing excludes, e.g. trailer included in valuation but listing has no trailer.

3. Classify signals.
 - Green flags: title in hand, in-person inspection, cold start/test drive/sea trial offered, maintenance receipts, detailed description, local pickup, serial/HIN/VIN consistency.
 - Yellow flags: low but plausible price, condition label worse than description, recent maintenance on starting/electrical parts, price drop, no trailer/accessories, seller offering transport only after purchase.
 - Red flags: deposit before inspection, title excuses, "selling for someone else," refusal of mechanic inspection, no cold start/test drive, copied photos/text, mismatched location/title, pressure tactics, payment app/shipper weirdness.

4. Give a short verdict first.
 - Preferred shape: "Short answer: [not automatically a scam / likely scam / worth seeing but only if...]."
 - Then list the decisive facts and the exact conditions under which the user should proceed.
 - Be direct and practical. Avoid long buyer-education essays unless asked.

## High-dollar local purchase guardrails

For Canadian/foreign-market vehicles, missing U.S. import paperwork, or proposed junk/rebuilt/donor-title workarounds, read before giving a verdict. State title branding does not cure missing federal importation, and a third party's attempted retroactive Customs entry can create seizure exposure.

- Never recommend sending a deposit before the user or a trusted inspector verifies the item and ownership documents in person.
- Treat "transport/delivery available after purchase" as neutral only after title/item inspection; otherwise it is a common pressure point.
- If ownership paperwork is involved, require seller ID/name to match the title/registration or a clean documented chain of sale.
- Recommend a mechanic/specialist inspection when repair exposure can exceed the purchase price.
- If the deal only works because the user ignores one expensive unknown, call that out plainly.

## Boats and marine listings

Key extra checks:
- HIN/title/registration match seller identity.
- Cold start and water test/sea trial, not just "runs on hose."
- Transom, deck/floor, and stringer softness or flex.
- Engine compression/leakdown when practical.
- Sterndrive/outdrive: bellows, gimbal bearing, shifting, corrosion, prop shaft, gear oil condition.
- Trailer inclusion/condition because a missing trailer can change the real price by thousands.
- Saltwater exposure, flushing history, storage, lift vs trailer, and marina receipts.

## Output template

Short answer: [verdict].

Listing facts:
- [price/year/model/location]
- [condition/age/title/test-drive]
- [notable included/excluded items]

My read:
- [green flags]
- [yellow/red flags]
- [market/comps context]

Only pursue if:
1. [verification condition]
2. [inspection/test condition]
3. [paperwork/payment condition]

Walk if:
- [hard stop]
- [hard stop]

Bottom line: [one-sentence recommendation].
