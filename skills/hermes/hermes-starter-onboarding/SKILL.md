---
name: hermes-starter-onboarding
description: Use when a new Hermes profile needs guided first-run setup, identity choices, memory preferences, optional integrations, a step-by-step toolset walkthrough, web-search backend setup, or recurring daily briefing, wellness check-in, and stock-quote jobs. Plan the setup conversationally, obtain approval, apply only the selected changes, and verify every result.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms:
- linux
- macos
- windows
metadata:
 hermes:
 tags:
 - hermes
 - onboarding
 - setup
 - integrations
 - tools
 - memory
 - cron
 - daily-briefing
 - health
 - stocks
 related_skills:
 - hermes-agent
 - hermes-mnemosyne
 ---
# Hermes Starter Onboarding

## Overview

Use this skill to turn a blank or lightly configured Hermes profile into a setup chosen by its owner. The workflow is conversational and consent-gated: learn the user's identity and priorities, recommend a small capability bundle, show the proposed changes, apply only what the user approves, and verify the result.

This is a **capability planner**, not a blind installer. A Hermes toolset exposes a capability, a skill provides operating instructions, a plugin or MCP server provides an integration, and a desktop application such as Obsidian is a separate dependency. Explain that distinction in plain language when it matters.

The setup must work for a public starter profile. Never assume the user's name, location, timezone, businesses, accounts, vault paths, tickers, health history, credentials, or preferred assistant name. Ask instead.

## When to Use

- A new user starts a Donna or other Hermes starter profile.
- The user says "set me up," "configure my assistant," "what tools should I enable," or asks what Hermes can connect to.
- The user wants to choose memory, notes, browser, terminal, voice, calendar, reminders, email, or other integrations.
- The user asks to add or change a daily briefing, daily wellness check-in, recurring health reminder, or stock-quote schedule.
- The user asks to review or change an existing starter setup.

**Don't use for:**

- Installing Hermes itself or repairing the Hermes runtime; use `hermes-agent`.
- Diagnosing an already configured integration; load the matching integration or troubleshooting skill.
- Making medical decisions, diagnosing symptoms, or monitoring an emergency.
- Placing trades, giving personalized investment advice, or treating a quote as a trading signal.
- Creating a cron job from an incomplete request when the delivery destination, schedule, or content would be ambiguous.

## Operating Rules

1. Ask one small group of related questions at a time. Do not present a forty-item questionnaire.
2. Start with the user's goals, then recommend capabilities. Do not ask users to choose toolset names they have never seen.
3. Explain what will happen before it happens. No installation, account connection, credential request, or persistent cron creation without explicit approval.
4. Never ask the user to paste a password, API key, OAuth code, payment information, or private token into chat. Use the provider's official setup flow and pause at the credential gate.
5. Read-only discovery is allowed before approval when it does not access private account content. Do not silently read connected accounts, note vaults, calendars, mailboxes, or health records.
6. Keep setup choices local to the active profile. Do not edit another Hermes profile or global configuration unless the user explicitly requests that scope.
7. After a persistent toolset or provider change, tell the user whether a new session or gateway restart is required. Do not claim a new tool is available until a fresh-process check confirms it.
8. A cron job runs in a fresh session with no current-chat context. Every LLM-driven cron prompt must be self-contained.
9. Do not put memory writes in cron prompts. Mnemosyne is provider-injected, not a toolset, and cron contexts intentionally skip Mnemosyne tools. Health responses must not be stored automatically.
10. Never use `enabled_toolsets: ["mnemosyne"]`; that is not a valid configuration. Use the `memory` provider setup for memory and the `cronjob` tool for schedules.

## Phase 0 — Inspect Before Changing Anything

Before proposing changes, inspect only the active profile:

1. Use `hermes config get onboarding` if the CLI supports the key. If it is absent, do not treat that as an error; the profile can still use this skill.
2. Use `hermes memory status` to identify the active memory provider and whether it is installed.
3. Use `hermes tools` to view the current toolset selection. This is the supported interactive toolset configuration surface; do not hand-edit a nested toolset list merely to avoid the selector.
4. Call `cronjob(action="list")` before creating any recurring job. Look for existing jobs with the same purpose, schedule, or name.
5. If the user mentions a specific integration, inspect the installed skill inventory with `skills_list()` or search the active profile's `skills/` directory. Do not assume that a desktop application or account is installed because a skill exists.

Report the starting state briefly. Do not dump credentials, full environment files, private account data, or the entire skill library.

## Phase 1 — Ask the Human Questions

Use this order, adapting to answers already given.

### Identity

Ask:

- "What should I call you?"
- "What would you like to call me?"
- "Do you prefer concise, conversational, formal, or highly detailed replies?"

If the user skips a question, use a neutral default and say what was assumed. Store identity and style only in the active profile after approval; do not write them into the public package.

### Main jobs

Ask what the assistant is mainly for. Offer plain-language choices:

- Research and current web answers
- Writing and documents
- Personal organization and reminders
- Notes and knowledge management
- Coding and technical work
- Local files and computer tasks
- Voice conversations
- Business or professional workflows

The user may choose more than one. Recommend the smallest sufficient capability bundle rather than enabling everything automatically.

### Memory

Ask:

> "Should I remember useful preferences between conversations, or keep each conversation more separate?"

Explain the choices:

- **No persistent memory:** disable profile memory with `hermes config set memory.memory_enabled false`.
- **Local persistent memory:** enable profile memory with `hermes config set memory.memory_enabled true`, then verify with `hermes memory status`. If the profile uses Mnemosyne, keep its data profile-scoped and do not expose it as a cron toolset.
- **Another supported provider:** run `hermes memory setup` and let the user choose and authenticate through the provider's own flow.

Do not silently switch from local memory to an external provider. If Mnemosyne is unavailable, report that exact status and offer the supported setup path; do not invent a package name or installation command.

### Notes and Obsidian

Ask:

> "Do you already use Obsidian or another notes system?"

If yes, ask which system and, for Obsidian, which vault the user wants to connect. Do not read the vault before the user identifies and approves it. Check whether the corresponding skill is already present with `skills_list()`.

- If the skill is bundled, enable/use it; do not reinstall a copy.
- If it is missing, show the exact skill name and ask before running `hermes skills install <name>`.
- Installing or enabling a skill does not install the Obsidian desktop application.
- Treat the vault path as private profile configuration, never as a package default.

### Capability boundaries

Ask only about capabilities relevant to the user's goals:

- **Web research:** web search and source retrieval.
- **Browser automation:** website interaction; explain that browser access is broader than web search.
- **Local files:** read and write files in approved locations.
- **Terminal:** run local commands; explain that this is a higher-trust capability.
- **Voice:** speech recognition and/or text-to-speech, subject to provider setup.
- **Calendar, reminders, email, or other accounts:** connect only the specific service requested, with the user completing authentication.

For persistent toolset changes, use `hermes tools` rather than guessing a configuration key. For a one-off session, use the documented `hermes chat --toolsets "web,terminal"` form when appropriate instead of changing the profile.

### Toolset walkthrough — match the reference setup, one toolset at a time

The goal is a profile that works as smoothly as a fully configured reference setup. Do not stop at "enable web" — walk the user through **every toolset the reference profile ships with**, one at a time, and ask for an explicit yes/no on each. Explain what each does in plain language before asking.

First, list what the profile currently has so the user sees the starting point:

```bash
hermes tools
```

Then walk this reference set (the CLI toolsets this starter profile pre-enables). For each, say what it's for and ask: "Enable <name>?"

| Toolset | Plain-language purpose |
|---|---|
| `web` | Web search and fetching page content. Needs a search backend (below). |
| `browser` | Drive a real browser: click, fill forms, log into sites. Broader than `web`. |
| `terminal` | Run shell commands. Higher-trust; explain the risk before enabling. |
| `file` | Read and write local files. |
| `code_execution` | Run Python for data work, calculations, multi-step scripts. |
| `computer_use` | Drive the desktop GUI in the background (click apps, screenshots). macOS. |
| `memory` | Remember preferences and facts across conversations. |
| `session_search` | Search past conversations. |
| `delegation` | Spawn sub-agents for parallel or specialist work. |
| `skills` | Load reusable procedures (the skills in this profile). |
| `cronjob` | Scheduled/recurring tasks (briefings, reminders). |
| `todo` | Track multi-step tasks within a session. |
| `kanban` | Durable multi-session task boards for longer projects. |
| `image_gen` | Generate images from text. Needs an image backend/key. |
| `video_gen` | Generate short video clips. Needs a video backend/key. |
| `vision` | Read images the user shares. |
| `tts` | Text-to-speech voice output. Needs a TTS provider/key. |
| `video` | Analyze video files. |
| `clarify` | Ask the user structured multiple-choice questions mid-task. |

Apply the approved selections through `hermes tools`. Some toolsets only appear there when their dependency is present (an API key, a backend, a driver) — if a toolset the user wants is missing from the list, say so and move to its setup step rather than pretending it is enabled.

#### Web search backend (required for `web` to return results)

`web` needs a search provider. This is a **global** Hermes setting, not profile config — set it once and every profile uses it. Ask the user which they have:

- **Self-hosted SearXNG** — private, free, no key. Ask for *their* instance URL, then configure the web-search backend to use it. Never hardcode or assume an instance address.
- **A hosted search API** (Brave, Tavily, Exa, etc.) — ask them to complete the provider's own key flow; never take the key in chat.
- **Not sure** — point them to `hermes setup`, which walks the search-backend choice interactively.

Verify with a real query afterward (e.g. `web_search("Hermes Agent")`) and confirm results come back before calling it working.

#### Provider / model

Confirm the model provider works end-to-end. The profile defaults to `deepseek`; if the user uses another provider, set it and run one real chat turn to confirm the key is valid. Do not ship or assume any specific API key.

#### Optional integrations with their own setup

Some capabilities need more than a toolset toggle. Offer each and pause at its credential/permission gate:

- **Voice** (`tts`, and speech recognition if wanted) — needs a voice provider.
- **Image/video generation** — needs the matching backend key.
- **Calendar / reminders / email** — connect only the specific service requested, user completes auth.
- **Browser automation** — needs a browser backend available on the machine.

## Phase 2 — Present the Setup Plan

Before applying anything, show a compact plan in this shape:

```text
Proposed setup

Identity:
- Call you: <name>
- Call me: <assistant name>
- Reply style: <style>

Capabilities:
- Enable: <plain-language capabilities>
- Leave off: <capabilities not selected>

Memory:
- <off / local persistent / selected provider>

Integrations:
- <Obsidian, calendar, reminders, voice, or none>

Scheduled jobs:
- <daily briefing / wellness check-in / recurring health reminder / stock quotes / none>
- Delivery: <origin chat or explicitly selected destination>
- Timezone: <timezone>

I will not install applications, connect accounts, or create recurring jobs until you approve this plan.
```

A clear response such as "yes," "apply it," or an equivalent approval is required before applying persistent changes. If the user changes one item, revise the plan and request approval again.

## Phase 3 — Apply and Verify

Apply only the approved items, in this order:

1. Identity and style in the active profile.
2. Memory choice with `hermes config set` or `hermes memory setup`.
3. Approved skill or integration setup, pausing at all credential and permission gates.
4. Toolset selection through `hermes tools` if a persistent capability change is required.
5. Existing cron inventory with `cronjob(action="list")`.
6. New or updated scheduled jobs using the templates below.
7. A final readback and concise status report.

After each action, verify its actual result:

- Config changes: read the relevant non-secret key back with `hermes config get <key>`.
- Memory: run `hermes memory status`; if Mnemosyne is selected, verify the active profile's provider status and data location without printing secrets.
- Skills: call `skills_list()` or `hermes skills list` and confirm the exact skill name.
- Toolsets: reopen `hermes tools` or start a fresh session and verify the capability is present.
- Cron: use `cronjob(action="list")` and confirm the exact name, schedule, prompt purpose, and delivery target. Do not treat a returned job ID alone as proof that a job will deliver.

If a change requires a new session, say `New session required` rather than pretending the current context has reloaded it.

## Scheduled Setup Options

These are optional jobs. They are not created by default.

### Daily briefing

Ask for:

- Delivery time and timezone.
- Whether it should run every day or weekdays.
- Sections wanted: calendar/agenda if connected, reminders/tasks, weather if a location is provided, current news, local events, and/or selected stock quotes.
- Delivery destination. Omit `deliver` for the normal origin destination; never guess a chat ID.

The briefing prompt must say:

- Use only sources and integrations that are actually available.
- Clearly label unavailable sections instead of fabricating them.
- Cite or link current sources for news and market data.
- Keep the result concise unless the user requests detail.
- Do not expose account contents beyond the requested summary.

Example creation call after approval:

```python
cronjob(
 action="create",
 schedule="0 8 * * *",
 name="Daily Briefing",
 prompt="""You are running the user's scheduled daily briefing. It is <weekday or every day> at <time> in <IANA timezone>. Produce a concise briefing with only these approved sections: <sections>. Use configured integrations only when they are available and authorized. Use web search for current news or weather only when needed, and include source links and the retrieval date/time. If a section is unavailable, say so plainly rather than guessing. Do not write memories or ask for credentials. Do not provide financial or medical advice. Deliver only the final briefing.""",
 enabled_toolsets=["web"]
)
```

Use `enabled_toolsets=["web"]` only when the user selected current web content. Add other toolsets only when the installed profile and the approved plan require them. If the user wants a calendar section but has not connected a calendar, create the briefing without that section or pause for explicit integration setup.

### Daily wellness check-in

Offer this as a non-clinical check-in, not as medical monitoring. Ask for:

- Delivery time and timezone.
- Every day or weekdays.
- Whether the message should ask about sleep, energy/mood, movement, hydration, or a user-supplied wellness goal.

Use a short, low-pressure prompt. Do not include the user's health history in the cron prompt. Do not automatically save replies to memory. If the user wants longitudinal tracking, ask separately for explicit consent and configure an appropriate health-tracking workflow in a normal session.

Example:

```python
cronjob(
 action="create",
 schedule="0 9 * * *",
 name="Daily Wellness Check-In",
 prompt="""Send a short, supportive daily wellness check-in. Ask only about these approved topics: <sleep, energy, movement, hydration, or goal>. Keep it non-clinical and optional. Do not diagnose, prescribe, infer a condition, or claim to monitor the user's health. Do not write the response to memory. If the user reports an immediate danger or crisis, advise contacting local emergency services or an appropriate crisis/medical professional; do not attempt to manage the emergency. Deliver one concise check-in question or checklist."""
)
```

A health check-in should not use `no_agent=True`; it needs an LLM to phrase the message. It also should not use Mnemosyne tools from the cron context.

### Recurring health reminder

If the user asks for a medication, appointment, exercise, hydration, or other health-related reminder, treat it as a reminder only. Ask for the exact wording, schedule, timezone, and destination. Do not infer medication names, doses, diagnoses, or treatment plans. The reminder must state only what the user explicitly supplied.

Example:

```python
cronjob(
 action="create",
 schedule="<approved schedule>",
 name="Health Reminder - <neutral label>",
 prompt="Deliver this exact user-approved reminder: <exact wording>. Do not add medical advice, dosage instructions, or a diagnosis. If the user asks a medical question in response, answer only with general safety guidance and recommend a qualified clinician when appropriate."
)
```

Do not put sensitive details in a job name when a neutral label will work. The job definition is stored locally and may be visible to anyone who can read the profile's cron configuration.

### Stock quotes

Ask for:

- Exact ticker symbols and exchanges when ambiguity is possible.
- Currency preference.
- Delivery time and timezone.
- Every day or weekdays.
- Whether the quotes belong in the daily briefing or should be a separate message.

Validate the ticker list before creating the job. Do not infer a ticker from a company name when multiple listings are plausible; ask. Use web search or an explicitly configured market-data integration at run time. Every quote message must include the source, retrieval date/time, and whether the data is delayed. If a source is unavailable, report that rather than filling in a number.

Example:

```python
cronjob(
 action="create",
 schedule="0 16 * * 1-5",
 name="Stock Quotes",
 prompt="""Provide the user's scheduled quote summary for these exact listings: <ticker/exchange list>. Use an available current web or market-data source. Report the quote, currency, source link, retrieval date/time, and any delayed-data notice. If any listing cannot be verified, say so and omit the number. Do not fabricate prices, predict movements, recommend trades, or present this as financial advice. Do not write memories or request credentials in the cron message. Deliver a concise table.""",
 enabled_toolsets=["web"]
)
```

Stock quotes may be attached to the daily briefing instead of creating a separate job. If the user selects both, ask whether they want one combined message or two scheduled messages; do not create duplicates.

## Managing Existing Jobs

Before creating a job, call:

```python
cronjob(action="list")
```

If an equivalent job exists:

- Ask whether to keep, update, pause, or remove it.
- Use the exact returned job ID when names are ambiguous.
- Use `cronjob(action="update", job_id="<id>", ...)` for an approved change.
- Use `cronjob(action="pause", job_id="<id>")` to stop delivery without deleting history.
- Use `cronjob(action="resume", job_id="<id>")` to restart a paused job.
- Use `cronjob(action="remove", job_id="<id>")` only after explicit approval because removal deletes the schedule.

After creating or updating a job, use `cronjob(action="list")` again. For a first-run smoke test, use `cronjob(action="run", job_id="<id>")` only when the user explicitly requests an immediate test; the real schedule is not proven until a completed execution appears in the cron history.

Cron schedules use the configured host/gateway timezone unless the deployment supports an explicit timezone field. If the user's timezone differs from the host timezone and the scheduler has no per-job timezone support, explain the limitation and convert only after the user approves the resulting local schedule. Never silently shift a reminder by hours.

## Common Pitfalls

1. **Double onboarding:** Hermes already has a built-in `onboarding.profile_build: ask` first-touch offer. Let that handle the consent-gated profile-build offer, then use this skill for capability and schedule choices. Do not create a second competing first-run identity interview. The internal `onboarding.seen` state is managed by Hermes; do not hand-edit it.

2. **Treating a skill as an application installer:** A bundled Obsidian skill does not install Obsidian. Confirm the app and vault separately, and never read a vault before approval.

3. **Creating duplicate crons:** Cron jobs run in fresh sessions and do not remember that a similar job was created earlier. Always call `cronjob(action="list")` first and compare purpose, schedule, and destination.

4. **Using memory in cron:** Mnemosyne is not a valid toolset and is intentionally skipped in cron contexts. Do not promise that a wellness response was remembered. Offer an explicit normal-session tracking setup instead.

5. **Fabricating current information:** Stock quotes, news, weather, calendar data, and market status are time-sensitive. Use an available source at run time, include source/time, and report unavailable data.

6. **Cron approval confusion:** The starter profile may retain `approvals.cron_mode: deny`. That setting blocks dangerous commands in headless cron runs; it is not a reason to enable unsafe approval mode. Do not change it to `approve` merely to make a web-based briefing work.

7. **Credential leakage:** Never place API keys, tokens, OAuth codes, or full account contents in a cron prompt, job name, response, skill file, or package artifact.

8. **Medical overreach:** A daily health cron is a reminder or voluntary wellness check-in, not a clinician, emergency monitor, medication manager, or diagnostic system.

9. **Assuming the current session sees changes:** Toolset and skill discovery can be cached. Verify with a fresh session or an explicit listing command before reporting the capability as active.

## Verification Checklist

- [ ] Identity and style choices were confirmed before being written.
- [ ] No credentials, private account contents, health history, vault paths, or personal identifiers entered the public package.
- [ ] Memory choice was explicitly selected and verified with `hermes memory status`.
- [ ] Obsidian or other integrations were distinguished from their Hermes skills and configured only after approval.
- [ ] Toolset changes used `hermes tools` or a documented one-off toolset override.
- [ ] Each toolset in the reference walkthrough was individually accepted or declined by the user.
- [ ] The web-search backend was explicitly chosen (SearXNG URL, hosted API, or `hermes setup`) and verified with a real query.
- [ ] Toolsets that need a backend/key were not reported as enabled until their dependency was present.
- [ ] Existing jobs were listed before any recurring job was created.
- [ ] Daily briefing, wellness check-in, health reminder, and stock-quote jobs were created only when individually approved.
- [ ] Every LLM-driven cron prompt is self-contained and does not depend on current-chat memory.
- [ ] Health cron prompts are non-clinical and do not write memory.
- [ ] Stock prompts require verified tickers, source links, timestamps, delayed-data notices, and no trading advice.
- [ ] Post-change config, skill, toolset, and cron state were read back.
- [ ] Any required fresh-session or gateway-restart gate was reported honestly.
