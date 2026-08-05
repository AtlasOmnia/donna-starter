---
name: meta-business-posting
description: meta-business-posting — Publish posts to a Facebook Page through the agent's own logged-in browser session or the Meta Graph API. Account-agnostic; no credentials in the skill.
platforms:
- linux
- macos
- windows
triggers:
- post to facebook
- facebook page post
- meta business suite
- publish to our facebook page
---
# Meta / Facebook Page Posting

Publish posts to a Facebook Page using the user's own account. Two paths: the
**browser session** (primary — works for everyone) and the **Graph API**
(power users with a Meta app).

## Hard rules

- **Never ask the user to paste a Facebook password, 2FA code, or token into chat.** The user logs in through the browser themselves; tokens live in `.env`.
- **Posting is an irreversible publish action.** Draft the full post (text, link, image), show the user exactly what will be published and to which Page, and get explicit approval before submitting.
- **Post as the Page, not as the user's personal profile**, unless the user explicitly says otherwise.
- **Never delete or edit a published post without explicit approval.**
- Respect platform policies: no engagement bait, spam, or misleading claims; no posting to Pages the user does not administer.
- If a login, 2FA, or app-review wall appears, stop and hand it to the user — never work around security checkpoints.

## Path 1 — Browser session (recommended)

Facebook's business surfaces are heavily JS-gated; the Hermes browser tools handle them naturally.

1. **User logs in once:** navigate to `facebook.com` (or `business.facebook.com`) in the Hermes browser and have the user complete login and any 2FA themselves. The agent never sees credentials.
2. **Locate the composer:** navigate to the Page (e.g. `facebook.com/<page>` → `Create post`, or Meta Business Suite → Content → Create post).
3. **Draft:** compose text, optionally attach an image via the page's file input (Hermes browser `set_input_files` / upload control). Do not publish yet.
4. **Confirm identity:** check the "Posting as" selector shows the intended Page, not the personal profile.
5. **Get approval:** show the user the drafted post and the target Page; publish only on explicit approval.
6. **Publish and verify:** click Publish (or have the user click it), then verify the post appears in the Page's feed and capture its permalink for the user.

Browser sessions do not persist across restarts — the user may need to log in again.

## Path 2 — Graph API (power users)

Requirements (user-side setup, one-time):
- A Meta app in the developer console with the `pages_manage_posts` permission.
- A **long-lived Page access token** (60 days) for the target Page.
- Note: production Page posting typically requires Meta app review; if the app is in Development mode, only admin/test users can post. If review is not feasible, use Path 1.

Environment variables (profile `.env`):

```
META_PAGE_ID=...
META_PAGE_TOKEN=...
```

Publishing:

```bash
# Text/link post
curl -s -X POST "https://graph.facebook.com/v21.0/$META_PAGE_ID/feed" \
 -H "Authorization: Bearer $META_PAGE_TOKEN" \
 -d "message=<URL-encoded text>" \
 -d "link=<URL-encoded URL>"

# Photo post (upload then attach)
curl -s -X POST "https://graph.facebook.com/v21.0/$META_PAGE_ID/photos" \
 -H "Authorization: Bearer $META_PAGE_TOKEN" \
 -F "url=<public image URL or local file>" \
 -F "message=<URL-encoded text>"
```

The response returns an `id` (e.g. `<page-id>_<post-id>`). Verify:

```bash
curl -s -H "Authorization: Bearer $META_PAGE_TOKEN" "https://graph.facebook.com/v21.0/$POST_ID?fields=permalink_url,created_time,message"
```

Report the `permalink_url` to the user. If the response contains `error` (e.g. `(#200) Missing permissions`, `(#190) token expired`), report the exact error and stop — do not retry endlessly.

## Workflow summary

1. Confirm the target Page and that the user administers it.
2. Draft the post (text, link, image) and show the user.
3. Get explicit approval: exact text, media, Page, schedule (now vs later).
4. Publish via browser (default) or Graph API.
5. Verify the live post and report its permalink.

## Pitfalls

- Facebook blocks automation aggressively on the login surface; if a checkpoint appears (2FA, "confirm it's you"), hand it to the user.
- The personal profile composer is different from the Page composer — use the Page or Business Suite surface.
- Images must be attached through the upload control; pasting a URL into the text box does not attach media.
- A post that succeeds via API but is immediately hidden is likely flagged — report the permalink and visibility honestly.
- Tokens expire (60 days for long-lived page tokens) — refresh through the user's setup flow, never by scraping.
