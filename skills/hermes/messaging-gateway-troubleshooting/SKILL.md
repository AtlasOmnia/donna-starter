---
name: messaging-gateway-troubleshooting
description: messaging-gateway-troubleshooting — Troubleshoot Hermes messaging gateway platform adapters, webhooks, authorization, delivery, and loop-prevention behavior.
version: 1.0.0
license: MIT
platforms:
- macos
- linux
- windows
metadata:
 hermes:
 tags:
 - hermes
 - gateway
 - messaging
 - webhooks
 - troubleshooting
---
# Messaging Gateway Troubleshooting

Use this when Hermes messaging platforms are installed/configured but messages do not arrive, are ignored, do not reply, or appear to risk reply loops.

## Operating principles

1. Verify the live path end to end before assuming config is wrong:
 - Gateway service is running.
 - Platform server/client is running.
 - Local webhook/listener is bound.
 - Health endpoint responds if available.
 - Platform has the webhook registered.
 - Gateway logs show the adapter connected.
2. Separate transport, authorization, and adapter filtering:
 - Transport failure: no webhook hit / listener closed.
 - Authorization failure: sender not allowed or pairing pending.
 - Adapter filtering: message acknowledged but intentionally skipped, e.g. group mention gating, tapback filtering, or self-message loop guard.
3. For user-visible claims, verify with real command output: `hermes status`, listener checks, webhook health, and gateway logs.
4. When changing Hermes gateway config or adapter code, restart the gateway and verify the adapter reconnects.
5. For gateway slash-command failures, inspect session-origin scope separately from transport health:
 - Compare `source`, `user_id`, `chat_id`, `thread_id`, and `origin_json` in the live session database.
 - Trace both the listing path and the action path; a session browser is still broken if it lists a target that `/resume` rejects.
 - In forum/threaded platforms, distinguish same-parent-chat ownership from exact-thread isolation rather than weakening origin checks globally.

## Telegram forum session browsing

- A fresh Telegram forum topic can have no prior exact-thread sessions even when the same owner has many titled sessions in sibling topics of the same parent chat.
- Do not diagnose this from session history alone. Correlate gateway send logs, live DB origin columns, and the gateway routing origin.
- Cross-topic browsing must be Telegram-specific, same-parent-chat, and same-owner; `thread_sessions_per_user=false` permits sharing within one thread, not across sibling threads.
- Keep `/sessions` visibility and `/resume` authorization aligned, including persisted-only rows.
- See `references/telegram-forum-session-scope.md` for the reproduction, authorization contract, TDD matrix, and safe activation procedure.

## BlueBubbles / iMessage notes

- BlueBubbles may mark messages from the Mac's own Apple ID/iMessage identity as `isFromMe=true`.
- A blanket `isFromMe` skip prevents reply loops but also prevents the owner from texting Hermes from that same iMessage identity.
- The safer loop guard is outbound-ID based: remember Hermes-sent `tempGuid` and returned `guid`/`messageGuid`, then ignore only inbound webhook echoes whose IDs match that cache.
- On macOS, do not assume `localhost` reaches an IPv4-only Hermes webhook. BlueBubbles/Electron/Node may resolve `localhost` to IPv6 `::1`, causing `connect ECONNREFUSED ::1:<port>` while `curl http://127.0.0.1:<port>/health` still works. Register local BlueBubbles webhooks as `http://127.0.0.1:<port>/...` unless Hermes is listening on IPv6 too.
- See `references/bluebubbles-self-imessage-loop-guard.md` for the concrete fix pattern, localhost/IPv6 pitfall, stale-webhook cleanup, and verification loop.
- See `references/memory-context-injection-probes.md` for probe handling when recalled-memory wrappers, formatting-failure echoes, or outbound test messages appear in a live platform chat.

## Verification checklist

- `hermes status` shows the platform configured.
- Gateway process/service is running under the expected profile/home.
- Listener exists for the adapter webhook port/path.
- Webhook health returns success if implemented.
- Platform-side webhook registration points at the active Hermes listener.
- Logs show adapter connected and webhook registered.
- A test message reaches the adapter or produces a pairing/authorization signal.

## Pitfalls

- Do not confuse “gateway open” with “message authorized.” A listener can be healthy while the sender is ignored by allowlist/pairing logic.
- If Telegram is fast for text but a photo/image turn appears to run forever, inspect `agent.log` for repeated API calls ending in `TypeError: expected string or bytes-like object, got 'list'` from `_interim_assistant_visible_text` → `strip_think_blocks`. This was a multimodal block-list regression introduced by Codex interim-commentary handling; a current upstream release fixes the loop. Stop the affected turn, update Hermes through the normal update-safe procedure, reapply local patches, restart the gateway, and verify with a real photo+caption message. Transport latency and gateway health can look completely normal while this retry loop burns up to the agent iteration cap.
- Do not persist negative claims like “BlueBubbles ignores self messages” as a permanent tool limitation. The durable lesson is the loop-guard design.
- Do not edit protected bundled skills; place Hermes-gateway-specific operational learnings here when bundled skills cannot be patched.
## Public support files

- `references/bluebubbles-self-imessage-loop-guard.md`
- `references/memory-context-injection-probes.md`
- `references/telegram-forum-session-scope.md`
