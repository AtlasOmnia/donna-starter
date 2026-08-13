---
name: destination-trip-planning
description: destination-trip-planning — Research a specific destination/attraction, gather pricing/logistics, and build a themed trip itinerary tailored to the traveler's profile.
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
 - itinerary
 - research
 - attractions
 - trip-planning
 category: productivity
 requires_toolsets:
 - web
 - browser
---
# Destination Trip Planning

Plan themed trips to specific attractions or destinations with real pricing, logistics, and a tight itinerary focused on the theme — not a generic city guide.

## When to Use

- User wants to plan a trip to a specific attraction, event, or themed destination (e.g., Graceland, a national park, a festival, a resort)
- User asks for "what to do there" at a given destination
- User needs a go/no-go recommendation on trip length and budget
- User wants to know what's nearby that fits the same theme

## Core Workflow

### Phase 1: Lock the Destination and Constraints

Clarify up front:
- **Exact destination** — confirm the city/location (Graceland = Memphis, not Nashville)
- **Traveler profile** — age, mobility, energy level, interests
- **Time window** — exact check-in and checkout dates, calendar days, and number of nights; if the user corrects the duration, recompute the entire budget
- **Traveler and payment structure** — total headcount, ages, likely activity participants, and which person/team pays which share
- **Budget sense** — looking for deals vs. full-service package
- **2–3 day trip** vs longer

### Phase 1.5: Clarify What "The Attraction" Actually Is

First-time visitors often don't know the attraction's layout. Preempt "is it just a house?" or "the house is the museum, right?" moments by describing the physical campus up front:

- Is the attraction one building or a campus spread across multiple sites?
- What's the ticket actually cover? (e.g., Graceland's $85 Elvis Experience = mansion across the street + 200K sq ft exhibit complex + two airplanes + on-site dining/shopping)
- Are there free areas (gravesite, gates, grounds)?
- Can the traveler see everything without re-entering or is it split across days?

This matters more for older travelers — they need to know if there's significant walking, shuttles, or stairs between components.

### Phase 2: Gather Destination Research

For the **primary attraction**:
- Ticket pricing tiers (standard vs VIP vs all-access)
- How long the full experience takes
- Peak vs off-peak times
- Available discounts (senior, AAA, military, promo codes)
- Parking / shuttle / accessibility info

For **on-site hotel** (if applicable):
- Lead with the **official property name first** when the user asks for "the [attraction] hotel" (for Graceland: **The Guest House at Graceland**)
- **Separate the hotel from the attraction clearly:** answer whether the hotel is **required** or merely **part of the fuller themed experience**. State this explicitly when the user asks some version of "do we have to stay there?"
- Room rates and resort fees
- Package deals bundling tickets + hotel
- Current promos (seasonal savings, flash sales)
- Proximity to the attraction (walkable?)
- Amenities for an easy stay (no need to leave)
- If exact stay-date pricing is not directly retrievable, give the **best grounded public price signal** you can find, label it as approximate, and do **not** imply it is a verified date-specific rate
- When useful, frame the decision as **experience vs cost efficiency**: themed on-site stay vs cheaper off-site hotel vs attraction-only day trip

For **travel logistics**:
- Distance from user's home city → drive vs fly
- Drive time with realistic traffic
- Nearest airport and transit from airport to attraction
- If driving: split the trip with overnight stops

### Phase 3: Build the Themed Itinerary

**CRITICAL RULE: When the trip has a theme, every suggestion must serve the theme.**

When the user asks "what would she do there" or "anything else related":
- List ONLY attractions, restaurants, and activities related to the theme
- Do NOT mix in generic city recommendations (parks, unrelated museums, shopping districts, tourist attractions)
- If you're not sure, ask "is she also interested in [city] stuff, or just [theme]?"
- Label each recommendation with its thematic connection (e.g., "where Elvis recorded his first song")

For each recommendation, give:
- What it is and why it matters
- How long it takes
- Distance from the hotel / attraction hub
- Walkability for an older traveler

### Phase 4: Present the Itinerary

Structure by day:
1. **Day 1** — Arrive, settle in, easy evening
2. **Day 2** — Main attraction day (full, relaxed pace)
3. **Day 3** — Morning theme-option + depart

No "must see everything" pressure. For older travelers, prioritize:
- Short distances between stops
- Seating available
- Minimal walking / stairs
- Easy Uber or shuttle access
- Afternoon rest time

### Output Style

- Lead with "here's what she'd actually do" — concrete, not conceptual
- Use tables for pricing comparisons
- Use bullet lists for attraction lineups
- Clearly separate the primary attraction from optional extras
- Before moving from research to pricing, confirm the itinerary with the user
- For unstable group decisions, do not wait for perfect commitment before helping: present a provisional primary-trip budget plus a clearly separated fallback for the smaller subgroup, with assumptions, optional activity add-ons, and the decision deadline that matters for peak inventory
- When the party includes older travelers or children, favor resort-accessible lodging and simple transport over an isolated property, even if the isolated cabin appears cheaper

## Pitfalls

- **Do not assume the destination city is the attraction city.** Graceland = Memphis, not Nashville. Confirm geography early.
- **Do not suggest generic city attractions on a themed trip.** When someone asks for Elvis stuff, give them Elvis stuff — not Beale Street blues clubs or the Civil Rights Museum unless they ask.
- **Travel/attraction websites frequently block web_extract and even browser_navigate.** They use Cloudflare or JS-heavy rendering. Fallback chain: search-result snippets → press releases on the official site → third-party aggregator articles. For JS-heavy blog-type sites that web_extract times out on, try `curl -sL -H "User-Agent: Mozilla/5.0 ..." <url>` to pull raw HTML — the content is often inline despite the SPA shell. Do not keep retrying web_extract, and don't re-navigate a Cloudflare-blocked page.
- **Do not overbuild.** A 70-year-old who wants to see Elvis doesn't need a 12-stop scavenger hunt. 2-3 meaningful things plus Graceland is plenty.
- **Duration and payer drift.** When the user changes a trip from one number of days/nights to another, recompute flights, lodging, meals, transport, activities, and all subgroup totals. When teams pay separately, do not report only a combined household total.
- **Airport handoff pattern:** When you suggest an airport and the user asks about a different one, research it quickly and neutrally — don't argue for your original suggestion. After reporting the data (connecting, more expensive), the user may pick the regional option anyway — accept without re-explaining the comparison.
- **Confirm each phase before proceeding.** User wants to confirm: research findings → itinerary → day count → themed extras → THEN pricing. When they reply with a short affirmative like "y" or "k," that's their signal to move to the next phase. Do not jump ahead.
- **Do not bury the practical info under blog-style prose.** Give ticket prices, hours, and how-to-book in the first pass.
- **When the user asks "anything else [theme]-related?" do NOT re-list what you already told them.** Give new specific themed options only. If you already covered them all, say so and offer a themed restaurant, historic site, or offbeat spot — not generic city stuff unless they explicitly ask for it.
- **Do not assume the user knows what the ticket price includes.** When presenting pricing, add one clear line about what each tier actually covers (e.g., "$85 standard ticket = mansion tour + exhibit complex + airplanes, ~3.5-4 hrs"). This prevents the "the house is the museum right?" confusion.

## Verification

Before presenting:
- Primary attraction pricing confirmed from at least one source
- Hotel package deal checked against bundle vs separate pricing
- Themed attractions only — no generic city filler
- Realistic pace for the traveler's profile

## Total Trip Estimate

After pricing is finalized, deliver a **one-table budget estimate**:

| Category | Estimated Cost |
|----------|:-------------:|
| ✈️ Flights (round trip) | $xxx |
| 🏨 Hotel (N nights) | $xxx |
| 🎫 Attraction tickets | $xxx |
| 🚕 Local transport (Uber/shuttle) | $xxx |
| 🍔 Meals (N days) | $xxx |
| **Total (approx)** | **~$xxx** |

- Use real fares and rates where available, rounded estimates where not
- For groups paying separately, show per-person cost and each paying subgroup/team total, with an explicit split rule for shared lodging and transportation
- State the exact dates and nights in the budget heading; do not reuse an earlier duration after the user corrects it
- Label which numbers are verified vs. estimates
- Include a suggested date range (midweek preferred, event dates to avoid)
