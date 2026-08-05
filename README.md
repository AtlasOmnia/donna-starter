# Donna — a starter Hermes profile

Donna is a pre-configured Hermes profile for people who want a capable,
opinionated assistant without building their own from scratch. She ships with:

- **A persona** — sharp, discreet, outcome-focused executive assistant (see `SOUL.md`).
- **73 curated skills** — Hermes configuration & troubleshooting, plugin development,
  theming, computer-use automation, research & source verification, document/productivity
  workflows, Reddit content operations, GitHub workflows, trip planning, and more.
  The bundled `hermes-starter-onboarding` skill guides first-run identity, memory,
  integrations, tool choices, daily briefings, wellness check-ins, health reminders,
  and stock-quote schedules without shipping personal settings.
  (Session-specific `references/` archives are included for 10 flagship skills plus the Google Workspace reference —
  plugin development, memory ops, config editing, context optimization, session
  maintenance, model selection, gateway troubleshooting, skill auditing, macOS
  automation, and community writing — scrubbed of personal data.)
- **The Hermes Token Router** — deterministic pre-LLM toolset routing that keeps the
  model's attention on your request instead of a wall of tool descriptions.
  **Installed but disabled by default** — to turn it on, add `hermes-token-router`
  to `plugins.enabled` in `config.yaml` and set `enabled: true` for your profile in
  `plugins/hermes-token-router/config.yaml`.
- **A skin and profile avatar** — `skins/donna.yaml` theme, `assets/donna-profile.png`.

No API keys, credentials, sessions, or personal memory are included. The profile
starts with generic community defaults (style, discipline, operating practices)
and learns what you tell it — nothing identity-specific is pre-seeded.

## Requirements

- Hermes Agent installed (`hermes --version` — see https://hermes-agent.nousresearch.com/docs)
- macOS recommended; several skills are macOS-specific

## Install (4 steps)

1. **Clone the profile**

   ```bash
   mkdir -p ~/.hermes/profiles
   git clone https://github.com/<owner>/donna-starter.git ~/.hermes/profiles/donna
   ```

   This repository *is* the profile — clone it straight into your Hermes
   profiles directory under the name `donna`. Updates later are just
   `git -C ~/.hermes/profiles/donna pull`.

2. **Add your model provider**

   ```bash
   hermes setup
   ```
   Pick a provider you have a key for (DeepSeek, OpenAI, etc.). The profile
   defaults to `deepseek` — change it anytime:

   ```bash
   hermes --profile donna config set model.default <model>
   hermes --profile donna config set model.provider <provider>
   ```

3. **Say hello**

   ```bash
   hermes --profile donna chat
   ```

4. **Sync the standard library (once)**

   ```bash
   hermes update
   ```

   The standard Hermes skill library (documents, spreadsheets, PDFs, email,
   travel, planning, and more) syncs into the profile automatically. The
   curated Donna skills are tracked as user-modified and are never overwritten.

## First things to try

- "Help me set up my profile" — run the guided onboarding flow for identity, memory,
  integrations, tool capabilities, and optional scheduled jobs.
- "What skills do you have?" — see the curated library load.
- "Summarize what this profile does and where its config lives."
- `hermes --profile donna skills list` — full skill inventory.
- Add your own skills anytime: `hermes skills install <name>` or drop folders
  into `~/.hermes/profiles/donna/skills/`.

## Notes

- **Memory starts with generic defaults.** Donna ships with neutral style and
  operating-practice seeds in `memories/` (no personal data) and builds a
  profile-scoped Mnemosyne store as you work. `hermes --profile donna memory`
  manages it.
- **Credentials live in `.env`.** Copy `.env.example` to `.env` and fill in the
  keys you need (model provider, Reddit, integrations). Never commit it.
- **Manual approvals are on** (`approvals.mode: manual`) — Donna asks before
  destructive or irreversible actions. Tune in `config.yaml`.
- **No OpenRouter** by default — direct provider calls only.
- The bundled `mnemosyne` plugin ships with Hermes; if your install predates it,
  run `hermes plugins install mnemosyne` (or `hermes setup plugins`).

## License & credits

- Profile: MIT — see `LICENSE`.
- The Donna persona is an original assistant archetype *inspired by* the character
  Donna Paulsen from *Suits* (operating style only — no dialogue, catchphrases, or
  copyrighted material is reproduced).
- The profile avatar was generated for this project; swap in your own if you prefer.
- Skills and tooling were battle-tested by the r/hermesagent community.
