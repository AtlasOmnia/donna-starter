# Live date-specific flight pricing

Use this when the user needs an actual fare for exact dates and passenger count rather than a generic route estimate.

## Procedure

1. Search the exact airport pair, dates, cabin, and passenger count. For a group, set the real count before reading prices; the default one-passenger result is not sufficient.
2. Prefer Google Flights or another live booking engine over search-result snippets. Search-result phrases such as “from $137” are route-level teasers and often do not apply to the requested holiday dates.
3. If browser refs become stale or calendar selection fails, use CDP `Runtime.evaluate` in the active page to click visible controls by stable attributes/text:
   - destination: `li[aria-label="Denver International Airport (DEN)"]`
   - dates: visible elements with full date aria labels, e.g. `Tuesday, December 29, 2026`
   - passenger control: `button[aria-label="Add adult"]`
   - then click the visible `Done` and `Search` controls.
4. Read the rendered results text after the page reports that results are loaded. Capture route, exact dates, passenger count, airline, nonstop/connection, total round-trip price, and any statement about taxes, bags, and optional charges.
5. Report the lowest practical option and at least one alternative. Divide the total by traveler count and, when the group pays in subgroups, show each subgroup’s share.
6. Label live fares as volatile and distinguish the verified fare from any planning buffer for baggage, seats, or later price movement. Do not invent optional charges; retrieve them at checkout or label them unpriced.

## Pitfalls

- Do not quote a generic airfare teaser as the price for the requested dates.
- Do not leave the passenger count at one when pricing a family/group trip.
- Do not silently treat children as adults; if ages are unknown, say which passenger category was searched and flag the need to recheck.
- Search the actual departure airport. If the user says St. Pete, verify whether PIE has a practical route; do not silently substitute TPA without explaining it.
