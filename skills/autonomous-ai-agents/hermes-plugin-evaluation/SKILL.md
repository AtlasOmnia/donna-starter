---
name: hermes-plugin-evaluation
description: 'hermes-plugin-evaluation — Evaluate third-party Hermes Agent plugins before installation: cost, licensing, required services, data flow, dependencies, and setup risk.'
version: 1.0.0
platforms:
- macos
- linux
- windows
metadata:
 hermes:
 tags:
 - hermes
 - plugins
 - evaluation
 - security
 - setup
 - pricing
 related_skills:
 - hermes-agent
 - hermes-config-editing
---
# Hermes Plugin Evaluation

Use this when the user asks about installing, trusting, pricing, or using a third-party Hermes Agent plugin or integration.

## Goal

Give a practical go/no-go read before touching the live Hermes gateway. Separate:

- **Plugin code cost/license** — whether the repository itself is public/open-source/free to install.
- **Service cost** — required SaaS account, usage billing, phone/SMS/voice costs, model API costs, tunnels, hosted routing, or paid feature gates.
- **Operational risk** — what data leaves Hermes, whether the plugin opens public webhooks/tunnels, and whether it modifies gateway behavior.

## Fast evaluation workflow

1. **Load authoritative Hermes context first** when the task involves Hermes plugins:
 - Load `hermes-agent` if available.
 - Prefer official Hermes docs for CLI syntax and plugin lifecycle.
2. **Inspect the repository without installing it**:
 - README / docs
 - `plugin.yaml`
 - `pyproject.toml`, `package.json`, lockfiles
 - `LICENSE`, `NOTICE`, or equivalent
 - setup wizard files and `after-install` notes
 - tool definitions, platform adapter files, webhook/tunnel code
3. **Answer cost precisely**:
 - Say “plugin appears free/public” only for the repo/installable code.
 - Do **not** infer the hosted service is free just because the plugin is public.
 - Identify paid dependencies: phone numbers, SMS/MMS, voice minutes, hosted tunnels, OpenAI/Anthropic/etc. APIs, storage, or managed accounts.
4. **Check for a public pricing page, but treat absence as unknown, not free**:
 - If pricing is missing/404/gated, say “pricing not publicly obvious; confirm with vendor.”
5. **Report required credentials and data paths**:
 - Required env vars/API keys.
 - Optional credentials that change cost or data flow.
 - Whether inbound messages/calls pass through vendor infrastructure.
6. **Recommend a safe rollout**:
 - Test in a non-critical Hermes profile or disabled gateway first.
 - Avoid putting it on the main gateway until pricing, credentials, and data flow are understood.
 - Run plugin-specific `doctor`/diagnostics before enabling public channels.

## Response shape the user prefers

Keep it concise and decisive:

- **Short answer** first: free, paid, mixed, or unclear.
- **What I verified** as bullets.
- **Cost implication** as bullets.
- **Recommended next step** if installation/security matters.

Avoid broad explanations of Hermes unless he asks. He usually wants the practical answer.

## Pitfalls

- **Public repo ≠ free service.** Many plugins are just glue to a paid platform.
- **No LICENSE file means unclear license**, even if GitHub visibility is public.
- **Phone/SMS/voice are rarely free at scale.** Assume carrier/service costs unless docs explicitly say otherwise.
- **Hosted tunnels/webhooks imply external data flow.** Flag this before installation.
- **Do not install first just to answer pricing/trust questions.** Inspect first, then ask/confirm before side effects.
