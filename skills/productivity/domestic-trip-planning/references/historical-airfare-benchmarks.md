# Historical airfare benchmarks

Use this reference when a traveler asks whether a current fare is unusually high or whether the group should wait to book.

## Evidence hierarchy

1. **Official DOT/BTS city-pair data** — best public historical benchmark for a route and quarter.
2. **Google Flights route/date trend** — useful for the booking engine’s current high/typical/low signal, but not a public ledger of every fare previously offered.
3. **Commercial fare-history tools** — use only when the chart’s time range, methodology, and fare definition are visible. Reject charts that render an old or undocumented period.
4. **Generic search snippets** — route teasers such as “from $137” are not historical evidence and should not be used for exact holiday dates.

## DOT/BTS exact city-pair query

The DOT public Socrata dataset for Table 1 is:

- Dataset: `https://data.transportation.gov/resource/4f3n-jbg2.json`
- Catalog page: `https://data.transportation.gov/dataset/Consumer-Airfare-Report-Table-1-Top-1-000-Contiguo/4f3n-jbg2`

Query with `$where` and filter both city-order permutations because `city1` and `city2` are not guaranteed to follow the requested direction. Example pattern:

```text
$where=year='2025' AND quarter='4' AND
((city1 like '%Tampa%' AND city2 like '%Denver%') OR
 (city1 like '%Denver%' AND city2 like '%Tampa%'))
```

Useful fields:

- `fare`: average itinerary fare
- `carrier_lg`, `fare_lg`: largest-carrier and corresponding average fare
- `carrier_low`, `fare_low`: low-carrier and corresponding average fare
- `passengers`, `nsmiles`: market context
- `year`, `quarter`: reporting period

## Interpretation rules

- DOT/BTS fares are itinerary averages for the quarter, not the exact dates being planned. They mix travel dates, fare classes, booking times, and passenger itineraries.
- The data includes the ticket price and applicable taxes/fees at purchase but excludes optional baggage, seat selection, upgrades, and similar ancillary charges.
- A holiday-week quote for seven travelers can reasonably sit well above the quarterly average because Christmas/New Year demand and same-fare-bucket availability are different problems.
- Use the historical number as a sanity check and to contextualize a booking-engine “prices are high” signal—not as a promised target.

## Reproduction example

For the Colorado planning session, the DOT/BTS query returned the following TPA–DEN route averages:

| Period | Average itinerary fare |
|---|---:|
| Q4 2024 | $246.88 |
| Q1 2025 | $235.33 |
| Q2 2025 | $233.67 |
| Q3 2025 | $211.74 |
| Q4 2025 | $242.30 |

The current exact-date group quote was $388 per traveler. The correct conclusion was not “the fare will fall to $242”; it was “the current quote is above the historical route benchmark, so monitoring is justified, while holiday and seven-seat premiums remain.”

## Reporting template

```markdown
Historical benchmark:
- Official route/quarter average: $X per traveler
- Exact-date live group quote: $Y per traveler
- Difference: approximately Z% above/below benchmark

Interpretation:
- This is a route-level quarterly average, not a forecast for the requested holiday dates.
- Optional bags/seats are excluded unless priced separately.
- Recommendation: monitor / set a buy trigger / book now, with the trigger labeled as a planning judgment rather than verified future pricing.
```
