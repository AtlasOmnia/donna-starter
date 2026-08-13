# Desktop hero scale calibration

Use this pattern when a hero is technically responsive but feels oversized in the user's real desktop browser.

## Decision sequence

1. Read the actual browser window bounds before blaming zoom or breakpoints.
2. Compare the observed window to the tested matrix. A normal desktop window rendering huge text means the composition itself is oversized.
3. Keep the mobile rule unchanged when mobile already passes; adjust only the base/desktop declaration.
4. Reduce headline scale and hero vertical padding together so the composition remains balanced.
5. Add exact CSS contract assertions first and prove the targeted test fails before changing CSS.
6. Rerun the full suite, `git diff --check`, five-width Chromium checks, and native Safari checks.
7. Inspect at least one desktop screenshot visually; geometry alone cannot judge perceived dominance.
8. Change the stylesheet query marker so the eventual direct deployment cannot be mistaken for a stale cached version.
9. Reload the user's actual visible browser tab and verify its URL after the refresh.
10. Commit and push only through the repository's established canonical remote; source-control completion remains separate from deployment.

## Example bounded adjustment

A successful correction reduced a desktop hero from:

```css
.hero-content {
  padding-block: clamp(5rem, 9vw, 7rem) clamp(3.5rem, 7vw, 5rem);
}

h1 {
  font-size: clamp(3rem, 6vw, 5rem);
}
```

to:

```css
.hero-content {
  padding-block: clamp(4rem, 7vw, 5.5rem) clamp(2.75rem, 5vw, 3.75rem);
}

h1 {
  font-size: clamp(3rem, 5vw, 4.25rem);
}
```

This is an example, not a universal token. Calibrate against the actual typeface, line count, viewport, and desired first-screen content.

## Acceptance evidence

Require zero overflow, clipping, broken imagery, console/network errors, and unexpected small targets at 375, 390, 1024, 1280, and 1440 px in Chromium. Repeat native Safari geometry at those widths and visually inspect non-black screenshots. Preserve mobile menu interaction and reduced-motion checks.
