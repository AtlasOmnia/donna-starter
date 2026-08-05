# Donna — a starter Hermes profile

Donna is a pre-configured [Hermes Agent](https://hermes-agent.nousresearch.com/docs)
profile for people who want a capable, opinionated assistant without building one
from scratch. Clone it, point it at a model provider, and a guided first-run
orientation walks you through enabling exactly the capabilities you want.

She ships with:

- **A persona** — sharp, discreet, outcome-focused executive assistant (see `SOUL.md`).
- **73 curated skills** — Hermes configuration, plugin development, research,
  documents, GitHub workflows, Reddit, trip planning, local models, and more
  (full list below).
- **A guided first-run orientation** — the `hermes-starter-onboarding` skill asks
  who you are, then walks you through **every toolset one at a time**, sets up web
  search, memory, and any integrations you choose. Nothing is enabled silently.
- **The Hermes Token Router** — an optional plugin that narrows the tool surface
  the model sees on each turn. **Installed but disabled by default** — turn it on
  during orientation (details below).
- **A skin and profile avatar** — `skins/donna.yaml`, `assets/donna-profile.png`.

No API keys, credentials, sessions, or personal memory are included. The profile
starts with generic community defaults and learns what you tell it.

## Requirements

- Hermes Agent installed (`hermes --version` — see the
  [docs](https://hermes-agent.nousresearch.com/docs))
- macOS recommended; several skills are macOS-specific
- A model provider account (DeepSeek, OpenAI, Anthropic, a local server, …)

## Install

```bash
mkdir -p ~/.hermes/profiles
git clone https://github.com/<owner>/donna-starter.git ~/.hermes/profiles/donna
```

This repository *is* the profile — clone it straight into your Hermes profiles
directory under the name `donna`. Updates later are just
`git -C ~/.hermes/profiles/donna pull`.

Then:

```bash
hermes setup                  # add your model provider key
hermes --profile donna chat   # first run — starts the orientation
hermes update                 # once: sync the standard Hermes skill library
```

The standard library (documents, spreadsheets, PDFs, email, travel, planning, and
more) syncs into the profile automatically on `hermes update`. The curated Donna
skills are tracked as user-modified and are never overwritten.

## First-run orientation

On the first chat, the `hermes-starter-onboarding` skill offers a guided setup.
It is a **capability planner, not a blind installer** — it asks, you approve, it
applies, it verifies. You can also trigger it any time with
*"help me set up my profile."*

It covers, in order:

1. **Identity** — what Donna calls you, what you call her, reply style.
2. **Your main jobs** — research, writing, coding, notes, organization, voice, etc.,
   so she can point you at the capabilities and integrations that matter to you.
3. **Toolset review** — every CLI toolset is **already enabled by default**, so the
   profile works out of the box. Donna walks each one in plain language — `web`,
   `browser`, `terminal`, `file`, `code_execution`, `computer_use`, `memory`,
   `session_search`, `delegation`, `skills`, `cronjob`, `todo`, `kanban`,
   `image_gen`, `video_gen`, `vision`, `tts`, `video`, `clarify` — and you peel
   back only the ones you don't want. Toolsets that need a backend or key are not
   reported as working until that dependency is actually present.
4. **Web search backend** — `web` needs a search provider. Choose self-hosted
   **SearXNG** (private, no key — you supply your own instance URL), a hosted
   search API (Brave / Tavily / Exa), or let `hermes setup` walk the choice.
   Verified with a real query before it's called working.
5. **Memory** — Donna asks whether you already have a memory provider. If not, she
   recommends **Mnemosyne** (local-first, profile-scoped, no external account — the
   provider her memory skills are written around) and sets it up, or uses your own.
6. **Integrations** — Obsidian, calendar, reminders, email, voice — only the ones
   you pick, each pausing at its own credential/permission gate.
7. **Token Router (optional)** — offered here; see the next section.
8. **Optional scheduled jobs** — daily briefing, wellness check-in, health
   reminders, stock quotes. None are created by default.

## The Token Router (optional, off by default)

Hermes exposes a large tool surface, and every tool schema costs the model
attention on every turn. The bundled **Hermes Token Router** plugin narrows that
surface: on the first turn it predicts which toolsets your request needs and
exposes only those, keeping the rest out of the prompt. It fails open (if unsure,
it shows everything) and can recover a tool mid-session if one turns out to be
needed.

It is **installed but disabled by default**, so the profile works identically to
stock Hermes until you opt in. The orientation offers to enable it for you. To do
it manually:

1. Add `hermes-token-router` to `plugins.enabled` in `config.yaml`.
2. Set `enabled: true` for your profile in `plugins/hermes-token-router/config.yaml`.
3. Start a fresh session.

**It works best alongside a hosted provider API.** Out of the box the router is
fully deterministic (no network call) and already trims the surface, but its
optional classifier — which resolves ambiguous requests the deterministic rules
can't — is designed to run against a cheap hosted model. **OpenRouter** is the
natural fit: one API key gives you access to many low-cost models for the
classifier. Any OpenAI-compatible provider or a local endpoint works too. The
classifier is opt-in (`classifier.enabled` in the plugin config); leave it off to
stay fully deterministic.

Leave the router off entirely if you prefer the full tool surface always visible,
or if you run a model that handles large tool contexts well.

## What's loaded — the skill library

73 skills, organized by category. Each is a reusable procedure Donna loads when
the matching task comes up — you do not call them by hand.

### Getting the most out of Hermes
- **hermes-starter-onboarding** — the guided first-run setup (orientation)
- **hermes-agent** — configure, extend, and troubleshoot Hermes itself
- **hermes-config-editing** — change settings, compression, providers safely
- **hermes-context-optimization** — trim startup/context cost
- **hermes-session-maintenance** — manage session history and storage
- **hermes-self-evaluation** — audit and optimize your own setup
- **hermes-overnight-autonomy** — unattended continuity and watchdogs
- **hermes-autoresearch-loops** — self-improving research loops
- **hermes-plugin-development** / **hermes-plugin-evaluation** / **hermes-desktop-plugins** — build and vet plugins
- **hermes-themes** — author color themes
- **hermes-mnemosyne** / **mnemosyne-maintenance** — the memory provider
- **messaging-gateway-troubleshooting** — Telegram/Discord/etc. adapter issues
- **skill-auditor** — grade and review skills
- **hermes-nightly-self-check-decisions** — record self-check decisions

### Research & verification
- **source-verification** — separate what a source says from what you infer
- **hf-model-card-research** — benchmark and quality metadata for models
- **local-model-selection** — pick local LLMs by VRAM tier and use case
- **external-model-review** — reproducible independent plan/code reviews
- **daily-news-digests** — scheduled news/research digests
- **dynamic-content-extraction** — pull data from JS-heavy sites
- **site-mapping** — map a website's full structure
- **local-discovery** — find local events and venues
- **marketplace-purchase-vetting** — vet Marketplace/Craigslist listings
- **evidence-based-replies** — check a claim against its cited source

### Documents & productivity
- **google-workspace** — Gmail, Calendar, Drive, Docs, Sheets
- **notion** — Notion via API/CLI
- **obsidian** / **daily-note-wrapup** / **vault-organization** — notes and vault care
- **office-document-review** — proofread office documents
- **maps** — geocoding, POIs, routes, timezones
- **domestic-trip-planning** / **destination-trip-planning** — trip research
- **discord-connect** — put Hermes on Discord
- **session-artifact-indexing** — index what a session produced

### Coding & GitHub
- **github-workflows** / **github-auth** / **github-issues** / **github-pr-workflow** / **github-code-review** / **github-pre-push-gates** / **github-readme-maintenance** / **github-repo-management** — the full GitHub lifecycle
- **codebase-inspection** — inspect repos with pygount
- **local-app-github-publishing** — publish local apps safely
- **subagent-driven-development** — delegate coding to sub-agents
- **coding-worktree-recovery** — recover interrupted/overlapping agent work
- **specification-compliance-review** / **application-security-review** — audit implementations and security
- **stale-patch-reconciliation** — rebase stale patches onto a moved checkout
- **cross-browser-typography-qa** / **inspecting-hermes-desktop-dom** — web/desktop debugging
- **hermes-agent-skill-authoring** — write new skills
- **opencode** — delegate coding to the OpenCode CLI
- **dogfood** — exploratory QA of web apps

### Computer use & macOS
- **computer-use** — drive the desktop GUI in the background
- **macos-app-automation** — AppleScript, URL schemes, System Events
- **macos-storage-management** — free space, move files to SSDs
- **apple-reminders** — Apple Reminders
- **imessage** — send/receive iMessage/SMS
- **notes-automation-workflows** — bulk Apple Notes automation

### Creative & community
- **content-style** — write for r/hermesagent and similar communities
- **claude-design** — one-off HTML artifacts (landing pages, decks, prototypes)
- **marketing-collateral-design** — design/critique/export collateral

### Social
- **reddit-browse-and-post** — browse, read, and post to Reddit
- **xurl** — X/Twitter
- **meta-business-posting** — publish to a Facebook Page
- **publication-link-audit** — verify every outbound link before publishing

### Health & personal
- **meal-tracker** — log meals and calories from a photo or description

### Competitive analysis
- **product-competitor-analysis** — codebase-grounded competitor assessments

> Note: `hermes update` adds the standard library (docx, xlsx, pdf, email, plan,
> and more) on top of these. The full inventory any time:
> `hermes --profile donna skills list`

## Notes

- **Memory starts empty and generic.** Donna ships with neutral style and
  operating-practice seeds in `memories/` (no personal data) and builds a
  profile-scoped Mnemosyne store as you work.
- **Credentials live in `.env`.** Copy `.env.example` to `.env` and fill in the
  keys you need. Never commit it — `.gitignore` already excludes it.
- **Manual approvals are on** (`approvals.mode: manual`) — Donna asks before
  destructive or irreversible actions. Tune in `config.yaml`.
- **No OpenRouter by default** — direct provider calls only.

## License & credits

- Profile: MIT — see `LICENSE`.
- The Donna persona is an original assistant archetype *inspired by* the character
  Donna Paulsen from *Suits* (operating style only — no dialogue, catchphrases, or
  copyrighted material is reproduced).
- The profile avatar was generated for this project; swap in your own if you prefer.
- Skills and tooling were battle-tested by the r/hermesagent community.
