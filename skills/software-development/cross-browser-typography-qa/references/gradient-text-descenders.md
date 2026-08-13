# Gradient Text Descenders

## Failure signature

Heavy display text using `background-clip: text` may flatten lowercase descenders even when:

- the element fits within the viewport;
- computed `overflow` is `visible`;
- DOM geometry reports extra room below the line;
- `padding-bottom` visibly increases the element height.

The paint mask can still be constrained by the line box. Inspect letters such as **g** and **y** directly.

## Preferred repair

Increase the line box on the gradient-bearing element instead of adding outside padding:

```css
.gradient-text {
  display: block;
  line-height: 1.22;
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

Treat `1.18`–`1.22` as a starting range, not a universal constant. Tune against the actual font, weight, and viewport. Remove ineffective compensating padding and re-check the content gap below the heading.

If the gradient remains unreliable, replace it with a solid accessible color.

## Acceptance recipe

1. Render desktop and mobile screenshots in Chromium and WebKit/Safari.
2. Zoom or crop around the baseline; confirm each descender has its natural tail.
3. Check mobile wrapping for overlap or excessive line gaps.
4. Confirm `scrollWidth === innerWidth` and no console errors.
5. Deploy with a new stylesheet cache marker.
6. On production, read the active stylesheet URL and computed `line-height`.
7. Capture a fresh live screenshot and inspect the same letters again.

A deployment-success page proves upload completion, not that the custom domain is rendering the corrected CSS.
