# Chromium file-upload fallback through direct cua-driver

Use when a browser upload is blocked by a native macOS file chooser, the ordinary browser wrapper exposes no upload action, or a full `dom_refs_v1` snapshot times out on a large dynamic page.

## Preferred route

1. Bind the exact Chromium window with direct `cua-driver call get_browser_state` using a stable session, PID, and native window ID. Require `binding_quality: exact` and `mutation_allowed: true`.
2. If `dom_refs_v1` times out, retry the same tab with `snapshot_format: "semantic_v2"` and a narrow `query`. This avoids treating a large-page DOM timeout as a browser-wide failure.
3. Query the upload trigger (for example, `Add photo/video`) to obtain a fresh `p<snapshot>:<index>` ref.
4. When the site's real file input is transient or CSS-hidden, intercept `HTMLInputElement.prototype.click` in the page before activating the upload trigger:
 - capture only `input[type=file]` clicks;
 - append that exact input to the document;
 - give it a unique accessible label and visible fixed positioning;
 - preserve the original prototype method for cleanup.
5. Activate the upload trigger with typed `browser_click`. If the trusted route refuses because it would foreground standalone Chromium, use `input_route: "dom_event"` only for this bounded trigger click.
6. Query the unique accessible label with `semantic_v2`; require a ref whose actions include `upload`.
7. Call `browser_set_input_files` with that fresh ref and the absolute regular-file path. Require `status: ok` and the expected `file_count`.
8. Restore `HTMLInputElement.prototype.click`, remove the temporary visible input if still attached, and verify the application's own media preview or attachment state before publishing.

## Safety and verification

- Never publish text-only when an image is required; fail closed if attachment verification is absent.
- A successful `browser_set_input_files` proves assignment to the input, not that the application accepted/rendered the media. Verify the site's preview before clicking Publish.
- Refs are invalidated by newer snapshots or navigation. Query immediately before each typed browser action.
- Close accidental duplicate composer tabs before exact binding; duplicate matching URLs can make target selection ambiguous.
- Do not preserve transient timeout claims. The durable lesson is the fallback ladder: exact bind → narrow `semantic_v2` → typed file assignment → application-level verification.
