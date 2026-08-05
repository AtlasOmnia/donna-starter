---
name: reddit-browse-and-post
description: reddit-browse-and-post — Browse Reddit, search, read threads and comments, and create posts through the agent's own authenticated session or OAuth app. Account-agnostic; no credentials in the skill.
platforms:
- linux
- macos
- windows
triggers:
- browse reddit
- reddit search
- create a reddit post
- post to reddit
- read reddit thread
---
# Reddit Browse & Post

Let an agent read Reddit and publish posts using the user's own Reddit account. Everything here is account-agnostic: the user supplies their credentials through environment variables or a browser login, never through chat.

## Hard rules

- **Never ask the user to paste a Reddit password, token, or cookie into chat.** Credentials go into environment variables (profile `.env`) or the user logs in via the browser themselves.
- **Posting is an irreversible publish action.** Draft the title and body, show the user exactly what will be posted and where, and get explicit approval before submitting. No exceptions for "the user already asked."
- **Never edit, delete, vote, or mod-queue anything without explicit approval.**
- Respect subreddit rules: read the sidebar / rules (or `about/rules.json`) before posting to a subreddit you have not posted to.
- Respect rate limits: keep requests under ~1/second for reads; wait at least a minute between post attempts. Respect 429/403 responses and back off.
- Do not post spam, affiliate links, or promotional content unless the user explicitly directs it.
- Vote manipulation, ban evasion, and buying/selling accounts are off-limits.

## Reading Reddit

Reddit's public JSON endpoints (`/r/<sub>/.json`, `/search.json`, `/comments/<id>.json`) work without credentials **when the network allows it** — but Reddit's anti-bot layer frequently returns a 403 HTML block page for plain `curl` requests, even with a custom User-Agent. **Do not fight it:** try one curl probe, and if it comes back as HTML/403, switch immediately to one of the reliable paths below.

Reliable paths, in order:

1. **Authenticated API** (recommended — works from any network): get an OAuth token (setup below) and read through `https://oauth.reddit.com` with `Authorization: bearer $TOKEN`. Same endpoints, dramatically higher rate limits, and it doubles as the posting path.
2. **Hermes browser tools** — navigate to the target page; the browser session passes Reddit's checks. Good for JS-gated pages and logged-in work.

If a plain-curl probe does work from the user's network:

```bash
# Subreddit listing
curl -s -A "hermes-agent/1.0 by <username>" "https://www.reddit.com/r/<subreddit>/.json?limit=25"

# Search
curl -s -A "hermes-agent/1.0 by <username>" "https://www.reddit.com/search.json?q=<query>&sort=relevance&limit=25"

# Single thread (includes top-level comments in the second JSON block)
curl -s -A "hermes-agent/1.0 by <username>" "https://www.reddit.com/r/<subreddit>/comments/<post_id>.json?limit=100"

# Subreddit rules (check before posting)
curl -s -A "hermes-agent/1.0 by <username>" "https://www.reddit.com/r/<subreddit>/about/rules.json"
```

Tips:
- **Always send a unique, descriptive User-Agent** — Reddit blocks generic clients (e.g. `python-requests`) aggressively.
- Prefer `old.reddit.com` for JSON stability if a request is blocked or returns HTML.
- `limit` max is 100. Paginate with `after=<fullname>` (e.g. `t3_abc123`).
- If a listing returns 403/429, wait several seconds and retry once; then fall back to the OAuth or browser path.

## Authenticated posting (OAuth app — recommended)

### One-time setup (user does this)

1. Create a **script** app at https://www.reddit.com/prefs/apps (name anything; type: script; redirect uri: `http://localhost:8080` — unused for script apps).
2. Copy the client ID (under the app name) and secret.
3. Put them in the profile's `.env`:

```
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USERNAME=...
REDDIT_PASSWORD=...
```

Script apps use the account's own password grant; no separate consent flow needed.

### Getting a token (from the agent)

```bash
TOKEN=$(curl -s -u "$REDDIT_CLIENT_ID:$REDDIT_CLIENT_SECRET" \
 -d "grant_type=password&username=$REDDIT_USERNAME&password=$REDDIT_PASSWORD" \
 -A "hermes-agent/1.0 by $REDDIT_USERNAME" \
 https://www.reddit.com/api/v1/access_token | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
```

Do not print `$REDDIT_CLIENT_SECRET` or the token; read them from env only.

### Submitting a post

```bash
# Self/text post
curl -s -X POST "https://oauth.reddit.com/api/submit" \
 -H "Authorization: bearer $TOKEN" \
 -A "hermes-agent/1.0 by $REDDIT_USERNAME" \
 -d "api_type=json&sr=<subreddit>&title=<URL-encoded title>&kind=self&text=<URL-encoded body>&resubmit=false"

# Link post
curl -s -X POST "https://oauth.reddit.com/api/submit" \
 -H "Authorization: bearer $TOKEN" \
 -A "hermes-agent/1.0 by $REDDIT_USERNAME" \
 -d "api_type=json&sr=<subreddit>&title=<URL-encoded title>&kind=link&url=<URL-encoded URL>&resubmit=false"

# With a flair (if the sub requires one — check rules first)
# -d "flair_id=<flair_template_id>"
```

The response is JSON: `{"json": {"errors": []}}` on success (empty errors), with `json.data.url` pointing at the live post.

### Verifying a post

- Fetch the returned URL (or `https://www.reddit.com/comments/<id>.json`) and confirm the title/body render.
- Report the final URL to the user.
- If `errors` is non-empty, read the error strings (e.g. `RATELIMIT`, `NO_TEXT`, `SUBREDDIT_NOTALLOWED`), fix, and retry only after the user re-approves.

## Browser-session option (no API app)

If the user does not want an OAuth app, they can log into Reddit in the Hermes browser once:

1. Have the user log in through the browser (agent never sees the password).
2. The agent uses that logged-in session: navigate to the target subreddit's submit page, fill title/body (or flair selector), and show the user a full-screen draft for approval.
3. The user clicks Submit themselves — or explicitly tells the agent to click it.
4. Verify the post exists by fetching its URL afterwards.

Browser sessions do not persist across restarts; the user may need to log in again.

## Workflow summary

1. Understand the goal — find the right subreddit and read its rules.
2. Read existing threads to check for duplicates and learn the format.
3. Draft the post (title + body, markdown) and show it to the user.
4. Get explicit approval: exact subreddit, title, body, flair.
5. Submit via OAuth or browser; never via unauthenticated endpoints.
6. Verify the live post and report the URL.

## Pitfalls

- Reddit blocks default User-Agents; always set a custom one — but note that a 403 **HTML block page** (the `theme-beta` page) can still appear from some networks regardless of UA; that is IP-level anti-bot blocking, not a request bug. Switch to the OAuth or browser path rather than retrying endlessly.
- `api_type=json` is required or the error format is unparseable.
- New accounts and accounts with low karma may hit `RATELIMIT` or shadow-removal; if a post 404s right after success, it was likely removed — report it honestly rather than claiming success.
- Link posts to the same URL repeatedly are blocked (`resubmit=false` helps only for edits).
- Do not store tokens in skill files, memory, or chat — only in env.
