# Responsive Product-Card Grid Parity

Use this pattern when a curated product directory has a small, even number of cards and the user rejects an editorial/asymmetric grid.

## Acceptance signal

A question such as “can you not make them even?” means card-width parity is the intended composition. Do not defend alternating 7/5 spans as deliberate design once the preference is clear.

## Repair pattern

1. Confirm the checkout is clean and has no active writer.
2. Add or update a CSS contract test first:
   - require `grid-template-columns: repeat(2, minmax(0, 1fr))`;
   - reject asymmetric `grid-column: span 7` / `span 5` rules;
   - preserve the mobile `grid-template-columns: 1fr` override.
3. Run the focused test and require RED before editing CSS.
4. Replace the 12-column/nth-child composition with one equal two-column rule. Remove obsolete nth-child resets at intermediate breakpoints rather than leaving dead CSS.
5. Change the stylesheet cache marker so the visible browser and eventual static deployment cannot retain the prior grid.
6. Run the full suite plus five-width Chromium and native-Safari checks.
7. Visually inspect a wide full-page screenshot: equal CSS widths are not enough; paired card bodies, image crops, and row alignment must look balanced.
8. Refresh the user-visible browser tab, then commit and push only to the approved remote.

## Required evidence

- Equal two-column rows at 1024, 1280, and 1440 px.
- Single-column mobile at 375 and 390 px.
- Zero clipping, horizontal overflow, broken images, duplicate image requests, console/network errors, or undersized hit targets.
- Clean worktree and accepted remote SHA parity after the local commit.
