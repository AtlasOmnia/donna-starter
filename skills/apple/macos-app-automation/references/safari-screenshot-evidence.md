# Safari Screenshot Evidence Validation

Use this when Safari WebDriver loads a page and DOM/geometry checks pass, but screenshot evidence may be unreliable.

## Failure signature

- `webdriver.Safari()` starts normally.
- Navigation, title, computed styles, `innerWidth`, `scrollWidth`, and element rectangles are correct.
- `save_screenshot()` returns `True`, yet the PNG is entirely or nearly black.
- Reusing a session after dramatically resizing the Safari window (especially to document-height for a pseudo-full-page capture) can make later screenshots unreliable.

Do not treat `save_screenshot() == True` as proof that the image contains rendered page pixels.

## Evidence ladder

1. **Run native Safari structural checks first**
 - Verify page title and expected H1.
 - Read `innerWidth`, `innerHeight`, `scrollWidth`, and `scrollHeight`.
 - Check visible-element `getBoundingClientRect()` containment.
 - Confirm no console/page errors when the harness exposes them.

2. **Capture at a normal viewport before extreme resizing**
 - Start a fresh Safari WebDriver session.
 - Set the intended viewport/window size before navigation.
 - Capture the normal viewport first.
 - Avoid growing one Safari window to the entire document height and then reusing that session for mobile captures.

3. **Validate the screenshot pixels**
 - Inspect the PNG with vision or a deterministic luminance/color histogram.
 - Reject an all-black or near-uniform image even if WebDriver reported success.

4. **Retry with a fresh session**
 - Create a new driver for each materially different viewport class (desktop vs. mobile).
 - Navigate again, wait briefly for paint, then capture.

5. **Separate native conformance from visual evidence when necessary**
 - Keep Safari as the source of truth for Safari DOM, sizing, overflow, and geometry.
 - If Safari PNG output remains invalid, use an exact-viewport Playwright/Chromium screenshot only for visual inspection.
 - Report the split honestly: e.g., “native Safari geometry passed; visual screenshot review used Chromium because Safari returned black PNGs.” Never label the Chromium image a Safari screenshot.

## Exact-viewport Chromium fallback

Prefer Playwright over raw `chrome --headless --window-size=...`; raw Chrome window sizing can produce a screenshot whose bitmap width does not match the effective CSS viewport.

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
 browser = p.chromium.launch(headless=True)
 page = browser.new_page(
 viewport={"width": 390, "height": 844},
 device_scale_factor=1,
 )
 page.goto("http://127.0.0.1:8080/", wait_until="networkidle")
 dims = page.evaluate("({iw: innerWidth, sw: document.documentElement.scrollWidth})")
 assert dims["iw"] == 390
 assert dims["sw"] == dims["iw"]
 page.screenshot(path="mobile.png")
 browser.close()
```

## Acceptance rule

A responsive browser pass requires both:

- deterministic geometry/overflow evidence at every target width; and
- at least one visually inspected, non-blank screenshot at desktop and mobile.

When browser-specific appearance matters, a valid native screenshot is still required; fallback screenshots cannot prove Safari-only rendering fidelity.