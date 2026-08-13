---
name: daily-news-digests
description: daily-news-digests — Build and maintain local scheduled news/research digest scripts that collect fresh items from multiple public sources and save Markdown locally.
version: 1.0.0
license: MIT
platforms:
- macos
- linux
metadata:
 hermes:
 tags:
 - research
 - monitoring
 - news
 - markdown
 - cron
 - launchd
 - github
 - x
 - reddit
---
# Daily News Digests

Use this skill when the user asks for a recurring local news/research monitor that pulls fresh items from X/Twitter, GitHub, Reddit, Hacker News, RSS, release notes, forums, or other public sources and saves a Markdown digest locally.

The deliverable is a working collector plus verified scheduling, not a suggestion list.

## Default outcome

Create:

1. A deterministic script under `~/scripts/` or an explicitly requested project folder.
2. A dated Markdown output directory under the relevant vault area.
3. A `latest.md` copy for quick viewing.
4. A scheduler:
 - macOS local/background: `launchd` LaunchAgent.
 - Hermes/gateway-delivered work: Hermes cron only when delivery or LLM reasoning is needed.
5. A verified test run with real output, logs, and exit status.

## Source selection pattern

Prefer primary or near-primary feeds before broad web search:

1. Official GitHub repo:
 - releases
 - issues
 - pull requests
 - commits
 - GitHub search
 - Atom feeds for releases/commits
2. Official docs/blog/release notes RSS or sitemap if available.
3. X/Twitter via `xurl` when installed and authenticated.
4. Reddit public JSON search for relevant subreddits and global mentions.
5. Hacker News Algolia search.
6. Other forums/community sources only if the topic warrants it.

For X/Twitter, do not read or print `~/.xurl`. Check only `xurl auth status`; if auth is unavailable, make the script skip X cleanly and explain how the user can enable it outside the agent session.

## Implementation steps

1. Decide output path based on domain ownership.
 - Assistant/system monitoring: `~/Notes/<Topic>/`
 - Personal: `~/Notes/...`
 - Work/finance/safety domains: delegate or ask the owning profile if needed.
2. Write a standalone script with:
 - Configurable window, e.g. `HERMES_NEWS_DAYS`.
 - Configurable output directory, e.g. `HERMES_NEWS_DIR`.
 - Configurable max items per source.
 - Per-source exception handling so one failing source does not kill the digest.
 - Deduplication by canonical URL.
 - Markdown grouped by source.
 - A clear note that collection is not verification.
3. Run syntax validation:
 - Python: `python3 -m py_compile <script>`.
4. Run the script manually and verify:
 - Exit code is 0.
 - Dated Markdown file exists and is non-empty.
 - `latest.md` exists and is non-empty.
 - Output includes real collected item counts.
5. Schedule it.
6. Kickstart/run the scheduled job once and verify scheduler logs.

## macOS launchd pattern

Use LaunchAgents for per-user local Markdown collectors:

- File: `~/Library/LaunchAgents/<reverse-domain-label>.plist`
- Validate: `plutil -lint <plist>`
- Load/reload:
 ```bash
 UID_NUM="$(id -u)"
 launchctl bootout "gui/$UID_NUM/<label>" 2>/dev/null || true
 launchctl bootstrap "gui/$UID_NUM" "$HOME/Library/LaunchAgents/<label>.plist"
 launchctl enable "gui/$UID_NUM/<label>"
 launchctl kickstart -k "gui/$UID_NUM/<label>"
 ```
- Verify:
 ```bash
 launchctl print "gui/$(id -u)/<label>"
 tail -50 ~/Library/Logs/<name>.log
 tail -50 ~/Library/Logs/<name>.err.log
 ```

Include a robust PATH in the plist EnvironmentVariables so Homebrew/user tools are found:

```xml
<key>PATH</key>
<string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin</string>
```

## Hermes cron vs launchd

Use launchd when:

- The task is local-only.
- It writes files locally.
- No LLM reasoning or gateway delivery is required.
- the user asked to “handle it” and “test it.”

Use Hermes cron when:

- The job should summarize, classify, or decide using an LLM each run.
- The output should be delivered to Telegram/Discord/etc.
- The job should chain from another Hermes cron job.

CLI sessions have no live delivery channel. Do not promise that default `deliver='origin'` cron jobs will message the user in the terminal.

## Verification checklist before final response

Report the actual evidence:

- Script path.
- Scheduler plist/job path.
- Output Markdown path.
- Last scheduler exit code or equivalent status.
- Log paths.
- Count of collected items if available.
- Whether stderr is empty.

Avoid saying “it should run.” Say either “it is loaded and tested” or state the blocker.

## Pitfalls

- Do not stop at a plan; create and run the collector.
- Do not let X/Twitter auth failure break the whole digest. Skip X with a note.
- Do not print credentials or auth files.
- Do not treat collected social posts as verified facts; mark the digest as collection-only.
- When a terminal command exits non-zero because a final diagnostic command was missing or shell-specific, inspect the useful output first. If service status and logs show success, do not over-correct a working scheduler.
