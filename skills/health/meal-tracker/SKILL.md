---
name: meal-tracker
description: "meal-tracker — Track meals and calories from a photo or text description. Vision-based portion estimates, daily calorie/macro budget, markdown food log."
platforms:
- macos
- linux
- windows
triggers:
- meal photo
- food log
- track calories
- calorie budget
- macros
- what did i eat
---
# Meal Tracker

Log meals from a photo or a text description, track calories and macros against the user's daily budget, and keep a dated markdown food log.

## Setup (ask once, then remember)

- **Daily calorie target** and optional macro targets (protein/fat/carbs in grams).
- **Log location** — the user's notes app or a folder (for example an Obsidian vault, `~/Food Logs`, or their notes directory). Ask once; do not assume a path.
- If the user later changes the target, update the stored value and the current log header.

## Meal logging workflow

### Photo input (user sends image)
1. Use `vision_analyze` with the image — ask: "Identify each food item, estimate portion sizes in common units (oz, cups, pieces), and provide calorie + macro breakdown per item."
2. If the photo is clearly a **Nutrition Facts label**, skip broad estimation and use the exact visible label values: serving size, calories, protein, fat, carbs, and useful notes (sodium/fiber/sugar). Treat one visible bag/container as one serving unless the user says otherwise.
3. If the user combines text + image (e.g. "add 1 coffee and this"), log both in the same timestamped meal/snack section.
4. For quick repeated "Add" messages with a label photo, use the visible label values, append a timestamped snack/drink section to today's log, recalculate totals, and verify the file. Do not ask for product names when the label gives enough to log an accurate entry.
5. A bare food/label image after an active food-log exchange is an implicit "add this" — log one serving/container from the visible label unless the image suggests multiple servings.
6. If today's log is missing but the chat already contains same-day entries, reconstruct the daily log from the conversation before appending.
7. Parse the response into structured entries, log to the daily file, and report: items logged, calories used, remaining for the day.

### Text input (user describes a meal)
1. Estimate portions from common serving sizes when not specified; flag uncertain estimates.
2. Use standard nutrition values (USDA) for known foods.
3. For recurring packaged items ("the protein bars", "same coffee"), reuse the most recent matching line item's calories/macros and mention that briefly.
4. Log to the daily file and report remaining calories.

### Batch corrections (user says "make sure X total" or "log N of these")
1. Read the current daily log.
2. Adjust line items so the count matches the user's stated total.
3. Recalculate subtotals and daily totals across all macros, not just calories.
4. Rewrite the whole section so the math is self-consistent — never leave stale subtotals.

## Daily log format

```markdown
# [YYYY-MM-DD] Food Log

**Daily Target:** <target> cal | Protein <P>g | Fat <F>g | Carbs <C>g

## Meals

### Breakfast (~[time])
- Item: ~cal | P: Xg | F: Xg | C: Xg
*Subtotal: XXX cal / PXg / FXg / CXg*

### Lunch (~[time])
- ...

### Dinner (~[time])
- ...

### Snacks (~[time])
- ...

## Daily Totals
**Calories:** XXX/<target> (XXX remaining)
**Protein:** XX/<P>g | **Fat:** X/<F>g | **Carbs:** XX/<C>g
```

## Response format

When logging a meal, respond with:
- What was logged (brief item list)
- Calories used from the target
- Remaining calories for the day
- Flag if over target or running low on protein

Example: "Logged lunch — chicken salad (~520 cal). Down 780/1800 today. 1020 remaining. Protein at 92/140g, still need 48g."

## Edge cases

- **Unclear portions:** estimate conservatively and flag it: "Estimated small bowl — could be more if larger portion."
- **Restaurant meals:** use chain nutrition data when available; estimate otherwise and note uncertainty.
- **Drinks with calories:** count them (coffee drinks, alcohol, juice). Water/unsweetened tea/coffee = 0 cal.
- **User corrects a total** ("make sure X bars total"): rewrite the log to match and recalculate all subtotals + daily totals from scratch.
- **Recurring ambiguous items:** reuse the most recent matching entry when available instead of asking for brand details every time; state the estimate source.

## Weekly review (when asked)

- Average daily calories
- Protein hit rate (share of days hitting the target)
- Estimated trend (from daily totals, not medical claims)
- Suggested adjustments

## Privacy and safety

- Food logs are personal health data: store them only in the user's own files; never send them to third parties or share automatically.
- This skill tracks food intake only. It is not medical advice: no diagnosis, no supplement or medication interaction guidance, no dosing. Refer the user to a qualified professional for health decisions.
