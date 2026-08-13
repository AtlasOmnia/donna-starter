---
name: cross-browser-typography-qa
description: cross-browser-typography-qa — Diagnose and verify web typography rendering defects across Chromium, WebKit, and native Safari, including clipped glyphs, broken descenders, wrapping, font metrics, gradient text, and live-cache mismatches.
version: 1.0.0
license: MIT
tags:
- web-development
- typography
- cross-browser
- safari
- visual-qa
metadata:
 hermes:
 tags:
 - web-development
 - typography
 - cross-browser
 - safari
 - visual-qa
---
# Cross-Browser Typography QA

## Purpose

Use this skill when web text looks clipped, flattened, wrapped incorrectly, misaligned, or materially different between Chromium and WebKit/Safari. Treat text rendering as both a geometry problem and a visual paint problem: passing DOM bounds does not prove that every glyph is intact.

## Triggers

- Lowercase descenders such as **g**, **j**, **p**, **q**, or **y** appear cut off.
- Gradient or transparent text looks flattened at the baseline.
- A heading fits within its element but still looks clipped.
- Safari and Chromium disagree on line height, wrapping, button labels, or heavy font weights.
- A deployed fix appears absent despite a successful upload or publish message.

## Workflow

### 1. Reproduce the exact defect

1. Record the browser family, viewport, font family, weight, size, and exact text.
2. Use a string containing ascenders, rounded forms, punctuation, and descenders.
3. Capture a focused screenshot at the reported viewport before changing CSS.
4. Inspect the actual glyphs, not only the element rectangle.

### 2. Inspect layout and paint

Read computed values for:

- `font-family`, `font-size`, `font-weight`, and `line-height`;
- `display`, `overflow`, padding, transforms, and fixed heights;
- `background-clip`, `-webkit-background-clip`, and `-webkit-text-fill-color`;
- loaded font status and fallback-font substitution;
- the stylesheet URL/cache marker actually active in the page.

Use `Range.getClientRects()` for rendered-line counts and `getBoundingClientRect()` for containment, but never treat either as proof that glyph paint is complete.

### 3. Repair the cause

Choose the smallest stable repair:

- Treat a user's “is it meant to be sized like that?” reaction as a real visual-acceptance signal, not merely a request to confirm CSS intent. First verify the actual browser window bounds and distinguish normal viewport rendering from browser zoom or an accidentally narrow layout. If the viewport is normal but the display type dominates the first screen, make a bounded desktop-only scale/spacing adjustment while preserving explicit mobile overrides.
- For a hero-scale correction, adjust the heading `clamp()` and hero `padding-block` together; shrinking only the type can leave the composition oddly empty. Add an exact contract assertion before the CSS change so the intended scale is durable, prove RED, then rerun five-width Chromium and native-Safari geometry plus visual inspection.
- When the user asks to make a small, even-numbered product set “even,” prefer an equal two-column grid over editorial 7/5 nth-child spans. Encode the parity in a RED contract, remove obsolete asymmetric and breakpoint-reset rules, retain the one-column mobile override, update the stylesheet cache marker, and visually inspect paired card alignment—not only grid geometry.
- Increase the line box on the text-bearing element when font paint exceeds a tight line box.
- Remove fixed heights or hidden overflow that cut off glyphs.
- Avoid synthetic or unsupported font weights when they distort metrics.
- Rework pathological wrapping with width, balance, or explicit block structure.
- When a semantic hyphenated term breaks awkwardly, protect only that token with an inline span using `white-space: nowrap`; do not force the entire heading onto one line. Keep the ordinary hyphen when exact-copy tests, translation keys, or search indexing depend on the literal string.
- For `background-clip: text`, prefer line-height correction over outside padding; outside padding can enlarge the box without enlarging the painted glyph mask.
- If a decorative gradient remains unstable, use a solid accessible text color rather than preserving a fragile effect.
- When prose interleaves raw text with an inline emphasis element inside `display: flex`, wrap the entire sentence in one inline-flow child (for example, `<span>Press <strong>Start Session</strong> ...</span>`). Otherwise the browser can promote text fragments and the emphasis element to separate anonymous flex items, making intended spaces appear missing or incorrectly distributed. Verify the actual rendered glyph spacing in the packaged app, not only the JSX or DOM text.

### Mixed-inline-content spacing regression

Treat a screenshot showing `PressStart Sessionto...`-style spacing as a layout-structure defect before changing font metrics. Inspect the parent `display` mode and child structure; if text nodes surround an inline child in a flex container, use one wrapper element rather than inserting arbitrary literal spaces or changing `word-spacing`. Rebuild the production renderer and capture the exact installed process/window after replacement so stale or pre-fix surfaces cannot be mistaken for current evidence.

### 4. Verify locally

Test at minimum:

- 375 and 390 px mobile;
- the exact reported width;
- 1024 and 1440 px;
- Chromium and WebKit/Safari.

Before accepting any narrow screenshot, prove that the CSS viewport is actually narrow. Some headless Chromium invocations keep a minimum layout viewport around 500 CSS px and crop a `--window-size=390` screenshot to 390 physical pixels. In-page, read `innerWidth`, `document.documentElement.clientWidth`, and `document.documentElement.scrollWidth`. If `innerWidth` does not equal the requested width, use CDP `Emulation.setDeviceMetricsOverride`, assert the width again, and only then inspect the screenshot. When overflow is real, inspect element bounding boxes and repair intrinsic grid/flex sizing with `minmax(0, 1fr)` or `min-width: 0`; do not hide the defect with `overflow-x: hidden` before identifying its cause.

Require:

- naturally shaped descenders;
- no unexpected wrapping or overlap;
- balanced spacing below the text;
- no horizontal overflow or console errors;
- one intended semantic heading where applicable.

When visual evidence follows an interaction, make UI state explicit. For a mobile menu, capture the open state after `aria-expanded="true"` and visible-link checks, then close it and wait for both `aria-expanded="false"` and the menu to become non-displayed before taking the clean layout screenshot. A successful click or DOM-count pass does not prove the screenshot captured the intended state.

### 5. Verify production

1. Add a new stylesheet cache marker when deploying changed CSS.
2. Load a fresh production URL, preferably with a harmless query marker.
3. Read back the live stylesheet URL and computed values.
4. Capture a fresh live screenshot and inspect the originally failing glyphs.
5. Treat deployment success as transport evidence only; close the defect from live rendering evidence.

## Common pitfalls

- **Geometry-only false pass:** The element is on-screen and `overflow: visible`, but the glyph mask is clipped.
- **Padding-only false fix:** `padding-bottom` increases element height while gradient-painted descenders remain flattened.
- **Stale-tab confusion:** An old tab continues using a previous cache-busted stylesheet after a new deployment.
- **Local-only acceptance:** A local screenshot passes, but production serves an older stylesheet.
- **Browser-family substitution:** Chromium at Safari-like dimensions is not a Safari/WebKit acceptance gate.
- **Screenshot scale blindness:** Full-page screenshots can hide a one- or two-pixel baseline defect; inspect a focused crop or zoomed view.

## Verification snippet

```js
const el = document.querySelector('.gradient-text');
const cs = getComputedStyle(el);
const rect = el.getBoundingClientRect();
({
 stylesheet: document.querySelector('link[rel="stylesheet"]')?.href,
 fontFamily: cs.fontFamily,
 fontWeight: cs.fontWeight,
 lineHeight: cs.lineHeight,
 overflow: cs.overflow,
 backgroundClip: cs.backgroundClip,
 webkitTextFillColor: cs.webkitTextFillColor,
 rect: { top: rect.top, bottom: rect.bottom, height: rect.height }
});
```

This snippet confirms state; it does not replace visual inspection.

- `references/gradient-text-descenders.md` — focused diagnosis and repair pattern for clipped descenders in gradient display text.
- `references/responsive-heading-wrap-and-ui-state.md` — contract-first repair for awkward semantic-hyphen wrapping plus native-Safari open/closed screenshot-state acceptance.
- `references/desktop-hero-scale-calibration.md` — bounded desktop hero resizing from a real-browser acceptance signal, with RED contract, cache marker, five-width QA, and visible-tab refresh.
- `references/responsive-product-card-grid-parity.md` — user-driven conversion from asymmetric editorial spans to equal card rows, with RED contract, cache-busting, cross-browser QA, and local-Git closeout.
## Public support files

- `references/desktop-hero-scale-calibration.md`
- `references/gradient-text-descenders.md`
- `references/responsive-heading-wrap-and-ui-state.md`
- `references/responsive-product-card-grid-parity.md`
