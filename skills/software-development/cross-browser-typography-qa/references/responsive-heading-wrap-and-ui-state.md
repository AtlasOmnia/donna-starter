# Responsive Heading Wrap and Screenshot-State Acceptance

## Why this exists

A responsive heading can pass containment and overflow checks while still wrapping badly at a semantic hyphen. Interactive-state residue can also make a correct page look broken in screenshots: a mobile menu may remain visibly open for a frame after its toggle state changes.

## Failure pattern

At a 390 px viewport, a heading containing a product term such as `add-ins` wrapped as:

```text
Office add-
ins for …
```

The page had no horizontal overflow and the heading box was valid, so geometry-only checks passed. A clean screenshot exposed the defect.

Separately, a Safari screenshot taken immediately after closing the mobile menu captured the menu overlay still open. DOM counts and page-width checks passed, but the visual artifact obscured the hero.

## Stable repair for semantic hyphenation

Preserve the literal accessible text and wrap only the atomic token:

```html
<h2>Office <span class="word-keep">add-ins</span> for Hermes Agent workflows</h2>
```

```css
.word-keep {
  white-space: nowrap;
}
```

Prefer this over changing the visible string to a nonbreaking-hyphen character when exact-copy tests, translation keys, or search indexing expect the ordinary hyphen. Do not make an entire heading `white-space: nowrap`; protect only the semantic token and re-test the narrowest supported width.

## Contract-first regression pattern

1. Add a failing structural test requiring the protected span and CSS rule.
2. Capture the failing test result before editing production markup/styles.
3. Apply the narrow fix.
4. Re-run markup/CSS contracts.
5. Re-run Chromium, WebKit, and native Safari at the exact mobile width.
6. Inspect pixels; DOM containment alone is insufficient.

## Clean screenshot state after interaction

Test the mobile menu twice:

- **Open-state evidence:** click the toggle, wait for `aria-expanded="true"`, and require all intended links to be visible.
- **Closed-state visual evidence:** click again, then wait for both `aria-expanded="false"` and the menu to become non-displayed before taking the clean screenshot.

Selenium example:

```python
toggle.click()
WebDriverWait(driver, 5).until(
    lambda d: d.find_element(By.CSS_SELECTOR, ".nav-toggle")
    .get_attribute("aria-expanded") == "false"
)
WebDriverWait(driver, 5).until(
    lambda d: not d.find_element(By.CSS_SELECTOR, "#primary-nav").is_displayed()
)
```

A state-changing click followed immediately by `save_screenshot()` is not reliable evidence, especially in native Safari. Treat the captured UI state as part of the acceptance contract.

## Acceptance checklist

- Requested CSS viewport equals `innerWidth`.
- `document.documentElement.scrollWidth <= innerWidth`.
- Visible-element bounding boxes stay within the viewport.
- Hyphenated semantic terms remain atomic where required.
- Open mobile menu exposes every intended link.
- Closed-state screenshot contains no stale overlay.
- Screenshot is visually inspected and nonblank; successful screenshot API return alone is insufficient.
