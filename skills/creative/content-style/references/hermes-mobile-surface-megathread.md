# Hermes mobile / lightweight-interface megathread workflow

Use when drafting r/hermesagent megathreads about phone/mobile access, gateways, WebUI/native clients, voice, always-on assistants, or remote dashboard access.

## Required research shape

1. Treat this topic as fast-moving. Verify current behavior from official docs and current repos before using community memory.
2. Separate these surfaces explicitly:
 - Official Hermes gateway surfaces: Telegram, Discord, Slack, WhatsApp, BlueBubbles/iMessage, API Server, Open WebUI integration, Voice Mode, Cron, Sessions/Handoff.
 - Community WebUI ecosystem: `nesquena/hermes-webui`, `get-hermes.ai`, Bridge API, Hermex, Hermes-Android.
 - Community prototypes / unverified claims: HMAI-style posts unless a repo/app/release is verified.
3. Build a current status matrix before drafting:
 - Interface/client
 - Official or community
 - iOS
 - Android
 - Web/browser
 - Requires self-hosting
 - Requires VPN/Tailscale
 - Notifications
 - Voice support
 - Current source link
 - Caveats
4. Treat “phone use” as an operator decision guide, not an app roundup. The post should answer: which interface should I actually use today, what do I gain/lose, and how do I connect safely?

## Source checklist

Official Hermes docs to check:
- Messaging overview and platform capability table
- Telegram / Discord / Slack / WhatsApp / BlueBubbles docs
- API Server docs
- Open WebUI integration docs
- Voice Mode and voice guide
- Sessions / handoff docs
- Cron docs
- Current GitHub releases, especially latest patch after the major release

Community/client sources to check:
- Hermex repo and site/App Store landing page
- Hermes WebUI repo and setup/API docs
- Hermes-Android repo/README/releases
- HMAI or other claimed apps only if a current repo/listing can be verified
- Tailscale docs only for private remote-access mechanics

## Reddit extraction notes

- Prefer authenticated old-Reddit JSON via Safari cookies when public Reddit returns 403.
- For each representative thread, capture title, date, score, comment count, URL, top comments/themes, and what workflow/problem it illustrates.
- If a representative thread returns 404/deleted, do not use it as factual evidence. Mention only as unavailable if necessary.
- For comment evidence, link directly to the comment permalink when possible.

## Recent-change pitfalls

- Do not say WhatsApp needs old Chromium/Puppeteer if current docs say the Baileys bridge does not.
- Check latest patch releases for gateway/mobile/client fixes before describing a limitation as current.
- Do not say “no mobile app” if community clients like Hermex/Hermes-Android are current; instead say no official Hermes Agent mobile app was verified.
- Do not present Hermex/Hermes-Android as official unless official docs explicitly say so.
- Do not present HMAI-style posts as released unless repo/app/release evidence exists.
- Voice is no longer just DIY: official Hermes docs cover CLI voice, Telegram/Discord spoken replies, and Discord voice channels. Full-duplex always-on mobile assistant is still a stronger claim and needs caveats.

## Security framing

Every mobile-access megathread needs a security/trust-boundary section:
- Do not expose dashboards unauthenticated.
- Prefer Tailscale/VPN over raw public ports for private home-server access.
- Treat bot tokens, API server keys, WhatsApp sessions, BlueBubbles passwords, and WebUI passwords as credentials.
- Gate sensitive actions triggered from phone/voice: sends, deletes, posts, purchases, payments, credentials, payroll/tax/financial work.
- Warn about phone loss and notification previews.
- State where tools run: for API/WebUI-style clients, tools execute on the server/runtime host, not the phone.

## Verification before delivery

- Save drafts to `~/Desktop/hermes_<topic>_megathread.md`.
- Run a link sanity pass; for Reddit links, verify through authenticated old-Reddit JSON when normal `www.reddit.com` returns 403.
- If requested critic models fail because of config/auth/model-name issues, report that directly and perform a local evidence-based critic pass rather than claiming external review happened.
