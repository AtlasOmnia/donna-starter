---
name: local-discovery
description: local-discovery — Find local events, venues, and activities — ad-hoc web discovery when the user asks 'what's happening' or 'what should I do this weekend'.
version: 1.2.0
platforms:
- linux
- macos
- windows
metadata:
 hermes:
 tags:
 - Local-Events
 - Web-Discovery
 - Event-Search
 - Research
 - Local-Venues
 - Nightlife
---
# Local & National Discovery

Find events, activities, venues, and things happening in the user's area (default: the user's local area) or anywhere nationally. Covers two subdomains:

1. **Events** — concerts, festivals, comedy, things to do tonight/this weekend
2. **Venues** — bars, lounges, restaurants, nightlife spots matching specific criteria (vibe, amenities, atmosphere)

## When to Use

- User asks about local events, things to do tonight/this weekend
- "What's happening around here?" or similar discovery requests
- User asks for venue recommendations with specific criteria (e.g., "cigar lounge," "speakeasy," "classy bar") — local OR national
- User asks "find me X somewhere" without specifying a city — treat as national search
- Need to surface relevant activities based on user interests

## Venue Discovery Workflow

When the user asks for venues rather than events, use this approach:

### 1. Start with Google Maps for venue discovery (PRIMARY TOOL)

Navigate directly to Google Maps search:
```
browser_navigate(url="https://www.google.com/maps/search/cigar+lounge+near+<city>+<state>")
```

**Google Maps works reliably** even when Google Search CAPTCHAs. Returns listings with ratings, review counts, addresses, hours, phone numbers, and user-submitted photos. Click individual venues for detailed info, reviews, and photos (use "Vibe" photo filter for atmosphere shots).

### 2. Fall back to `web_search` if needed

Search using specific criteria keywords (e.g., `"cigar lounge"`, `"speakeasy bar"`). Collect names, addresses, and phone numbers from search results.

**PITFALL:** `web_search` relies on `ddgs` which is installed in the system Python (`~/Library/Python/3.9/...`) but Hermes runs from a venv that doesn't see it. If you get `"ddgs package is not installed"`, skip to step 3 immediately — don't retry or try to reinstall. This is a persistent env path issue, not transient.

### 3. Skip review aggregator sites for browser navigation — they CAPTCHA aggressively

**PITFALL:** Yelp, TripAdvisor, DuckDuckGo, and Bing ALL serve CAPTCHAs to browser sessions. Don't waste time trying to extract reviews or listings from them via `browser_navigate` — go straight to venue websites.

**EXCEPTION:** `web_extract` works on TripAdvisor despite browser CAPTCHA. For national/regional venue discovery, use `web_extract(urls=[tripadvisor_url])` instead of browser navigation.

### 4. Go directly to venue websites via `browser_navigate`

Venue websites are the most reliable source for accurate, current info:
- **Hours** — always verify from the official site, never trust Google's cached hours
- **Dress code** — many upscale venues post this explicitly
- **Age restrictions** — check before recommending
- **Contact info** — phone and email

### 5. Go beyond the algorithmic top-10 when the category is the city's identity

**PITFALL:** When a city is FAMOUS for a venue category (e.g. Louisville + bourbon, Nashville + music venues, NOLA + jazz clubs, Austin + BBQ, etc.), presenting just a Yelp/TripAdvisor top-10 feels insultingly thin. The user knows the city is dense in that category and expects the FULL directory — all options, organized by neighborhood.

**Recovery pattern:**
- Run multiple `web_search` queries with specific venue names and cross-streets to surface listings the algorithm may have buried
- Cross-reference Yelp snippets, TripAdvisor snippets, and niche directory sites (e.g., cigarlounges.co) from search results — even when `web_extract` fails on the full page, the search snippets carry review counts, ratings, and addresses
- Search for niche directory/blog articles specific to that category (e.g., "complete list of cocktail lounges", "every jazz club in New Orleans")
- Organize results by neighborhood/area — this adds massive value for the user planning a visit or crawl
- Present the full count upfront ("28 across the metro") so the user knows the list is comprehensive, not truncated

### 6. When the user wants **bar-first / coed / date-night** rather than a niche enthusiast scene

Do **not** keep feeding them classic category leaders if the venue photos or vibe read as male-dominated / hobbyist-only. Pivot the search intentionally:

- Reframe the target from **"cigar lounge"** to **"restaurant or cocktail lounge with cigar patio/garden/menu"**.
- Search local lifestyle/tourism sources for **date night**, **Restaurant Row**, **outdoor dining**, **nightlife**, **hotel lounges**, and **craft cocktails**.
- Check Reddit (`r/<metro>`) for lived-experience notes like *quiet*, *older crowd*, *good for couples*, *great restaurants around there*, *people watching*, or *bar hop after*.
- Distinguish three different classes clearly:
 1. **Guaranteed cigar infrastructure** — official site explicitly mentions cigar lounge/garden/menu/patio.
 2. **Bar-first with likely cigar compatibility** — local/tourism sources mention cigars, smoking patio, or cigar menu, but the venue is primarily a restaurant/bar.
 3. **Great vibe but cigar certainty weak** — good coed/date-night energy, but hookah/smoking policy or cigar policy is not verified.
- Be honest when a place is **hookah-forward** rather than cigar-verified.
- Prefer options where the venue identity reads **mixed crowd / couples / date night** over enthusiast-heavy cigar rooms when the user is going with a partner.

Useful source types for this pivot:
- official venue sites
- Visit <metro> / International Drive <metro> listings
- <metro> Date Night Guide / local lifestyle blogs
- old.reddit.com threads in `r/<metro>` when mainstream extractors do not support Reddit

### 7. Present results concisely

Format each venue with: name, address, phone, hours, vibe description, and why it fits the user's criteria. Group by neighborhood/area when the list is large. End with a clear recommendation based on their stated preferences.

## Workflow

### 1. Try `web_search` first (but expect failure)

```
web_search(query="events tonight in my city")
```

**PITFALL:** `web_search` relies on `ddgs` which is installed in the system Python (`~/Library/Python/3.9/...`) but Hermes runs from a venv that doesn't see it. If you get `"ddgs package is not installed"`, skip to step 2 immediately — don't retry or try to reinstall. This is a persistent env path issue, not transient.

### 0b (special case: niche-interest + multi-city search)

When the user asks for events around a specific interest (e.g., "cigar events," "car shows," "DJ night," "food festival") across multiple cities or statewide:

- Run parallel `web_search` calls with structured queries, e.g.:
 - `"cigar" event "<date>" <state>`
 - `"cigar" tasting <city> <date>`
 - `"cigar" event <metro> June 20-22 2026`
- Use `web_extract` on Eventbrite's city-specific pages:
 - `https://www.eventbrite.com/d/<state>--<city>/<category>/`
 - `https://www.eventbrite.com/d/<state>--<metro>/cigar/`
 - etc.
- Check niche vendors' event calendars (e.g., Cigars International, specialty lounges) — they regularly host tastings and live-music cigar nights that general aggregators miss.
- Present results grouped by city, then date; include only events with concrete details (date/time/location).

This avoids the "only the local metro" trap when user interest is statewide.

### 2. Fall back to `web_extract` on known event sources

These are the most reliable source types for a metro area's events:

- **The metro's major newspaper events page** — Weekly roundups published every Monday. Most reliable source. Extracts well via `web_extract`.
- **The regional visitor bureau's events calendar** — Has an events calendar but often redirects or blocks bots. Use as secondary.

### 3. If `web_extract` fails or returns sparse content, use `browser_navigate`

Navigate to the newspaper's events page directly. The page renders server-side so it loads without JS execution issues.

### 4. Filter and present results

- Group by date (tonight / Saturday / Sunday)
- Highlight free events prominently
- Include location, time, price, and link
- Give a brief recommendation based on what you know about the user's interests
- Keep it concise — one section per day, bullet format

### 4b. Late-night follow-up searches after a main event

When the user asks follow-ups like "anything after 10pm?" after fireworks, parades, festivals, or family events:

- Treat it as a **post-event nightlife / after-party search**, not just another pass over official civic event calendars.
- Search both general web and Eventbrite city/category pages, e.g. `site:eventbrite.com <metro> July 4 after party`, `<city> nightlife after fireworks`, and city-specific Eventbrite discovery URLs.
- Verify individual listings before recommending them. Eventbrite search snippets often surface irrelevant out-of-area events; open/extract the event page and confirm **city, venue, date, start/end time, and age restriction**.
- Be explicit if no late fireworks exist. Offer adjacent late options instead: bar crawls, waterfront bars, hotel/resort parties, clubs, live music, or festivals that continue after the fireworks.
- For late-night results, include **end time** prominently; it matters more than start time for this intent.

## Known Event Sources (metro example)

### Eventbrite (Niche + Multi-City Events)

- **Reliable for niche interests** (cigar tastings, car shows, themed nights, etc.) via city-specific search pages:
 - Example: `https://www.eventbrite.com/d/<state>--<city>/<category>/`
 - Example: `https://www.eventbrite.com/d/<state>--<city>/<category>/`
- Use `web_extract(urls=[eventbrite_url])` — it extracts event listings cleanly.
- Especially valuable when user interest spans multiple cities or is highly specific; general aggregators miss these events.

## Venue-Specific Sources

## Pitfalls

- **Don't retry `web_search` after a ddgs failure** — it's an env path issue, not transient. Switch tools immediately.
- **Many event sites are JS-heavy SPAs** (Eventbrite, Meetup) that return blank to the browser or 404 to extractors. Prefer the metro's major newspaper as primary source.
- **Bot detection is common** on visitor/tourism sites. If blocked, move to the next source rather than fighting it.
- **Don't over-research** — the user wants a quick scan, not an exhaustive database. 3–5 relevant items per day is enough.
- **Yelp and TripAdvisor CAPTCHA aggressively** (DataDome). Skip them for venue research — go straight to official websites.
- **Google Maps/Reviews often blocks browser sessions** with recaptcha. Use `web_search` for initial discovery, then navigate directly to venue sites.
- **Hours change frequently** — always verify from the official website, never trust cached or third-party data.
- **Social media login walls** — Instagram and Facebook require authentication to view any content (photos, posts, business page details). Skip entirely for venue research.
- **DuckDuckGo also CAPTCHAs** — "Select all squares containing a duck" challenge after first search. Don't waste time trying multiple searches.
- **Bing serves Cloudflare challenges** — same fate as Google Search. Use Google Maps instead.
- **`web_extract` works on TripAdvisor despite browser CAPTCHA** — `web_extract(urls=["https://www.tripadvisor.com/Attractions-g191-Activities-c20-t101-United_States.html"])` successfully extracts venue lists with ratings, locations, and review snippets even when browser navigation is blocked. Use this for national/regional venue discovery.
- **Magazine/lifestyle articles extract well** — Sites like Haute Living (`hauteliving.com`) produce curated venue lists that `web_extract` handles cleanly. Search DDG/Bing for article URLs, then extract via `web_extract`.
- **Venue concept mismatch is real** — some venue concepts (e.g., cigar bars with themed adult entertainment staff) don't exist in certain markets or nationally. After thorough research, report honestly rather than stretching a recommendation that doesn't fit the criteria.

## Output Format

User expects concise, direct results organized by date. No preamble beyond a one-line intro. Format:

**TONIGHT (day, date)**
- **Event Name** — Time, Location. Price. Brief note.

**SATURDAY, <date>**
- ...

End with a short recommendation based on user interests.
