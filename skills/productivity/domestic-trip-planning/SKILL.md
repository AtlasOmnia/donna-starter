---
name: domestic-trip-planning
description: domestic-trip-planning — Research and plan a multi-day domestic trip — hotels, attraction tickets, itineraries, driving distances, local tips, and budget estimates. Covers the ground-level logistics that air-travel-planning and short-term-rental-search don't touch.
version: 1.0.0
license: MIT
platforms:
- linux
- macos
- windows
metadata:
 hermes:
 tags:
 - travel
 - trip-planning
 - itinerary
 - attractions
 - hotels
 - road-trip
 - research
 category: productivity
 requires_toolsets:
 - web
 - browser
---
# Domestic Trip Planning

Research and plan a multi-day domestic trip — hotels, attraction tickets, itineraries, driving distances, local tips, and budget estimates. Designed for family/personal trips where the user wants a clear, actionable overview before committing to anything.

## When to Use

- User wants a multi-day trip plan with attractions, hotel, and logistics
- Trip involves a mix of booking elements (hotel + tickets + transport)
- User asks for pricing, tips, itineraries, and "what to know" from multiple sources
- User asks "Step 1 — Research" before making decisions

## Core Workflow

1. **Lock the trip frame before pricing**
 - Record exact check-in and checkout dates, calendar days, and nights. Preserve the user's stated checkout date exactly; never silently substitute a shorter stay because an earlier search used different dates. If the duration or dates change, announce the change and recompute every dependent line item; do not carry forward the earlier night count.
 - Record traveler count and payment structure: one household, per-person split, or separate teams/families paying their own shares.
 - Record unknown ages and likely skiers separately; do not silently price children as adults.

2. **Clarify geography first**
 - If the user names a city that doesn't match the attraction (e.g. "Nashville" for Graceland in Memphis), flag it early — it may affect the trip shape or they may have a split-city plan
 - Confirm driving distance from home airport/city so expectations are set upfront
 - Verify the actual departure airport. When the user names a city with a nearby secondary airport, check the smaller regional airport code before recommending the major hub; explain any airport substitution.

3. **Parallel source gathering**
 - Use `web_search` first with multiple targeted queries (ticket prices, hotel rates, Reddit tips, itineraries)
 - Pull data from **search result snippets** — for JS-heavy travel sites (booking engines, hotel pages, attraction ticketing), the snippets often contain the actual pricing even when the full page won't load
 - Search for official attraction pages and third-party aggregators simultaneously

3.5. **Benchmark airfare against historical data when the user asks whether to wait**
 - Do not treat a route-level “from” fare or a booking-engine high/low label as a historical archive.
 - Use official DOT/BTS city-pair data when available. The Socrata Table 1 dataset (`4f3n-jbg2`) supports exact city-pair and year/quarter queries; filter both city-order permutations and report the quarter’s average itinerary fare, largest-carrier fare, and low-carrier fare only when useful.
 - Explain that quarterly route averages combine all travel dates, fare classes, booking times, and passenger itineraries; they are benchmarks, not forecasts for a holiday week or a seven-seat search. They exclude optional baggage and seat fees.
 - Pair the official benchmark with the live exact-date/group-size fare and Google Flights’ current trend signal. Convert the comparison into a clearly labeled planning trigger or buffer, never a promised future fare.
 - If a third-party history chart renders an old or undocumented time range, say so and exclude it from the decision rather than presenting stale figures as last year’s evidence.

4. **Pivot strategy when web extraction fails**\n Travel/hotel/booking/airline pages commonly block both `web_extract` and `browser_navigate` with Cloudflare or aggressive bot detection. When it does:\n - First try: `web_search` with more specific queries — Google's result snippets often surface ticket prices, hotel starting rates, and package descriptions from structured data markup\n - Second try: `browser_navigate` to the page, then `browser_snapshot` to read the rendered content. Dismiss cookie dialogs before snapshotting.\n - Third try: `web_search` with `site:` operator to find third-party aggregators that write human-readable articles with the same data (e.g. `site:wonderfulmuseums.com graceland tickets`)\n - **When browser is also blocked** (e.g. Cloudflare challenge page like "Just a moment..."): search snippets become your ONLY reliable source. Also search for **press releases / news articles** on the official site (`site:graceland.com offers` or `site:graceland.com elvis-news`) — these are text-heavy and often accessible where the main booking page is blocked.\n - **Do not** repeatedly retry `web_extract` on the same failing URL — change strategy immediately after 2 failures.\n - **Do not** retry `browser_navigate` more than once on a Cloudflare-blocked page — re-navigating won't bypass the challenge.

5. **Organize findings by decision dimension**
 Present a structured breakdown:
 - **Location & getting there** — airport, driving time, distance
 - **Ticket pricing** — tiers with adult/child/senior pricing
 - **Hotel options** — rates, fees, packages/bundles
 - **How many days needed** — per-attraction time estimates → recommended trip length
 - **Top tips** — best times to visit, discounts available, gear to bring
 - **Nearby attractions** — other things to fill a multi-day trip
 - **Active deals** — any current promos or packages

5.5. **Screen hotel policies before ranking reviews**
 A high cleanliness score is not enough when the traveler has allergy or accessibility constraints.
 - Verify each finalist’s current pet policy on the property’s official page—not just a booking-site “pet friendly” badge.
 - For the user, exclude properties where cats or dogs may occupy all guest-room categories because he is allergic to both. A hotel with designated pet rooms can remain a candidate only if a non-pet room is explicitly available, but a genuinely non-pet property is preferable.
 - Remember that service animals may still be present at any U.S. hotel; describe the policy accurately rather than promising an animal-free building.
 - Compare recent cleanliness evidence, pet policy, total price (including parking/resort fees), distance, and review volume together. Do not recommend first and investigate a disqualifying policy afterward.
 - For business travel, if the cleanest medically suitable option costs more, preserve a concise expense justification: the closer/lower-cost alternatives accept pets and conflict with the traveler’s allergy needs.

### Family Holiday Ski-Trip Addendum

For family/group trips during Christmas or New Year's week:
- Treat the named city as the arrival gateway unless it is also the lodging destination. For Colorado ski travel, Denver is usually the airport; compare Winter Park, Keystone, Breckenridge, and similar resort towns rather than pricing a Denver hotel.
- Count the party and nights explicitly before estimating: check-in to check-out, calendar days, travelers, likely skiers, children/seniors, and required sleeping/bathroom configuration.
- When people pay separately, produce both a per-person figure and subgroup/team totals. Split shared cabin and transportation costs using an explicit rule (normally per person unless bedroom use differs), and do not present one household total as if one person is paying it.
- Prefer a cabin-style townhome or condo inside the resort shuttle network over a remote cabin when the party includes an older traveler or children. **However, if the user explicitly requires a log cabin/authentic log home, property type becomes a hard filter: label townhomes/condos only as compromises and do not present them as matches.** Screen for steep access roads, winter driving, parking, hot tub, kitchen, laundry, fireplace, and distance to lifts.
- When a true log cabin is requested, require explicit listing evidence of log construction; a “cabin” title, rustic decor, chalet label, or cabin-style architecture alone is insufficient. If the user says a result is not a log cabin, treat that as a hard correction: remove it from exact matches, acknowledge the category error, and restart the screen rather than rebranding the same property as a compromise without his asking.
- Price the trip in layers: base snow getaway (airfare, lodging, ground transport, food, non-ski activities) followed by an optional ski add-on (lift access, rentals, lessons). This keeps the proposal usable when only some of the group skis.
- If the lodging strategy changes from a cabin to a resort, preserve the bedroom requirement and branch in this order: (1) search the official resort collection for one shared 4–5-bedroom home or residence; (2) search true ski hotels and base-lodge condos; (3) show a multi-room or multi-unit plan only as a separate fallback. A hotel room block, resort-managed home, ski-in/ski-out condo, resort-area townhouse, and private cabin are distinct categories and must not be relabeled. Never present two unverified units as a 4–5 bedroom exact match; adjacency and both date-specific totals must be verified. If the resort's official date widget does not expose a rate, label the property as a verified lead with rate pending and use same-market live listings only as a planning benchmark.
- Use a realistic holiday-week range, not an ordinary-season low. Separate verified public signals from date-specific estimates, and state when a live booking quote was not retrievable.
- For the final shareable budget table, show Team A and Team B rows for airfare, lodging, shared transport, food, non-ski activities, base total, and optional ski add-on. State the shared-cost split (normally 4/7 and 3/7) and charge ski costs only to actual skiers.
- When the requested departure airport lacks a practical nonstop route, compare the nearest major airport with the stated airport and recommend the option that reduces connections and risk for a large group; do not silently substitute airports.
- Include a fallback trip for the smaller subgroup if the larger party does not commit. Give both totals in one decision table and identify the booking deadline pressure created by peak-season inventory.

6. **Surface the hotel + ticket package when it exists**
 Many major attractions offer bundled "Stay Packages" (hotel + tickets). When available:
 - Quote the package discount percentage
 - Compare it against separate booking to show if it's worth it
 - Flag any date restrictions or coupon codes needed

7. **End with a "what's next" handoff**
 After Step 1 research, explicitly prompt for decisions:
 - Preferred dates
 - Driving vs. flying
 - Travel party size (affects ticket tier and hotel room type)
 - Budget ballpark

8. **Handle the "anything else [theme]" follow-up**
 After the initial research, the user may ask for more attractions related to the trip's theme. When they do:
 - Do **not** re-list what you already covered
 - Give new themed-specific options only
 - If nothing new remains, offer a themed restaurant, historic site, or offbeat spot — not generic city filler
 - Exception: if the user asks "what else is in [city]" (not themed), then provide general recommendations

## Output Style For This User

- Start with **the biggest correction or surprise** (e.g. wrong city)
- Use **tables for pricing and comparisons**
- Bullet points, not prose blocks — user skims fast
- Lead with the recommendation, then the details
- Include real-dollar pricing wherever found, not ranges
- For group trips, show per-person cost and each paying subgroup/team’s total, with the split rule stated
- Flag what's verified (snippet text, official page text, live booking result) vs. what's estimated (third-party article claims or planning range)
- If a discount or package is active, call it out in **bold**

## Pitfalls

- **Nashville ≠ Memphis.** Always verify the correct city for the attraction the user names. Graceland is Memphis.
- **Don't over-optimize before Step 1.** The user asked for research first — don't dive into exact date picking, flight booking, or reservation forms until they ask for Step 2.
- **Progressively confirm each phase.** User wants: research → confirm itinerary → confirm day count → confirm Elvis extras → THEN pricing. Do not jump to pricing until the itinerary is agreed. When the user says "y" or similar short confirmation, that's their signal to proceed to the next phase.
- **web_extract timeout trap.** Booking/travel pages (Booking.com, KAYAK, hotel sites, attraction ticketing) are JS-heavy and time out regularly. Do not retry more than twice before switching to browser or snippet-based strategies.
- **Cloudflare kills browser too.** Some travel/airline sites (Allegiant, directflights.com, etc.) show a Cloudflare challenge page even in `browser_navigate`. When page title is "Just a moment...", don't retry — switch to search snippets + press releases.
- **IHG.com hotel pages require full snapshots + TreeWalker JS extraction.** Compact snapshots hide prices. `browser_vision` hallucinates hotel names and rates. Prices are split across text nodes (`<span>156</span><span> USD</span>`). Lazy loading means only ~19 of 43 hotels load at a time — scroll aggressively and re-extract.
- **Don't claim a price from a third-party aggregator as official.** Third-party blog articles may list outdated pricing. Prefer official site snippets or browser-visible text.
- **Airport correction pattern.** If the user asks about a different airport, research it quickly without assuming they'll use it. They may just be curious. After reporting the findings, they may pick the regional option anyway — accept the pivot and move on without re-explaining.
- **Cross-trip recall ambiguity.** If the user later asks something like "what dates did you say were good for this month?", do not answer with bare dates unless the destination is explicit. Review the prior session/topic first and restate the context in the answer: e.g. "For the Memphis/Graceland trip, the dates were…". This user may have multiple live trip threads, so unlabeled dates are easy to misapply.
- **Carry the destination label forward.** When you present date recommendations, include the trip name/city in the heading or first sentence (e.g. "Suggested Memphis dates") so a later skim/search is unambiguous.
- **Elvis Week / special events.** Major attractions have peak-event weeks (e.g. Graceland: August 8-16 for Elvis Week). If the user wants to avoid crowds, flag these. If they're a superfan, offer it as an option.
- **Ticket tier confusion.** Don't assume the user knows what each ticket tier includes. When presenting pricing, add one line per tier explaining what's covered. Example: "$85 standard ticket = mansion tour + exhibit complex + airplanes, ~3.5-4 hrs". This prevents "the house is the museum right?" questions.

- `references/web-extract-fallback-strategies.md` — specific fallback strategies for when web_extract fails on JS-heavy travel/booking sites.
- `references/ihg-hotel-scraping.md` — IHG.com-specific extraction technique: full snapshots, TreeWalker JS pattern, pitfalls (vision hallucination, lazy loading, sort params).
- `references/live-flight-pricing.md` — exact-date, group-size airfare workflow using live booking results, with CDP fallback selectors and fare-reporting rules.
- `references/historical-airfare-benchmarks.md` — DOT/BTS city-pair queries, historical-fare interpretation, and the live-vs-quarterly comparison template.
## Public support files

- `references/historical-airfare-benchmarks.md`
- `references/ihg-hotel-scraping.md`
- `references/live-flight-pricing.md`
- `references/web-extract-fallback-strategies.md`
