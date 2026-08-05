---
name: notion
description: "Notion API + ntn CLI: pages, databases, markdown, Workers."
version: 2.0.0
author: community
license: MIT
platforms: [linux, macos, windows]
prerequisites:
 env_vars: [NOTION_API_KEY]
metadata:
 hermes:
 tags: [Notion, Productivity, Notes, Database, API, CLI, Workers]
 homepage: https://developers.notion.com
---

# Notion

Talk to Notion two ways. Same integration token works for both — pick by what's available.

◆ **`ntn` CLI** — Notion's official CLI. Shorter syntax, one-line file uploads, required for Workers. macOS + Linux only as of May 2026 (Windows support "coming soon"). **Default when installed.**
◆ **HTTP + curl** — works everywhere including Windows. **Default fallback** when `ntn` isn't installed.

## Setup

### 1. Get an integration token (required for both paths)

1. Create an integration at https://notion.so/my-integrations
2. Copy the API key (starts with `ntn_` or `secret_`)
3. Store in `${HERMES_HOME:-~/.hermes}/.env`:
 ```
 NOTION_API_KEY=ntn_yo...re
 ```
4. **Ensure the integration is connected to the workspace** — before sharing any pages, verify the integration appears in your workspace's connection list:
 - Open any page in Notion → click **Share** (top-right) → **⚙️ Settings** → **Connections** tab
 - The integration should appear under **Connected apps**. If NOT listed, the API key is valid but the integration has no workspace linkage — every API call will return `404 object_not_found` regardless of page sharing.
 - To connect: go to **https://notion.so/my-integrations** → click your integration → in the **Connected pages** section, enable **"Full workspace access"** (or connect individual top-level pages manually).
 - After connecting, verify it shows up in the Connections panel before proceeding.

5. **Share target pages/databases with the integration** in Notion: page menu `...` → `Connect to` → your integration name. Without this, the API returns 404 for that page even though it exists.

### 1b. Grant workspace-wide access (optional, recommended for single-user workspaces)

To avoid connecting pages one by one, grant the integration full workspace access:
1. Open **https://notion.so/my-integrations**
2. Find your integration → click it
3. Change access from *Selected pages* to **Full workspace access** (exact label may vary — look for a toggle or dropdown)
4. This makes all existing and future pages visible to the integration by default

**Tip:** For single-user workspaces, Option 1b is the cleanest approach. For shared workspaces, connect individual top-level pages instead — child pages inherit access from their parent.

5. **For full workspace access (single-user workspaces):** Open https://notion.so/my-integrations → click your integration → enable **"Full workspace access"** in the Connected pages section. This avoids having to manually connect every page. Child pages inherit access from their parent, so connecting top-level pages is sufficient if you prefer granular control.

### 2. Install `ntn` (preferred path on macOS / Linux)

```bash
### 2. Install `ntn` (preferred path on macOS / Linux)

```bash
# Recommended — use custom install dir if /usr/local/bin needs sudo
curl -fsSL https://ntn.dev | bash

# Or to a user-writable location (fallback when /usr/local/bin is locked):
curl -fsSL "https://ntn.dev" | NTN_INSTALL_DIR="$HOME/.local/bin" bash

# Or via npm (needs Node 22+, npm 10+)
npm install --global ntn

ntn --version # verify
```

**macOS note:** On recent macOS, `/usr/local/bin` may require `sudo`. Use `NTN_INSTALL_DIR="$HOME/.local/bin"` as a fallback — just ensure `$HOME/.local/bin` is on your `PATH`.

**Skip `ntn login` — use the integration token instead.** This works headlessly, no browser needed:
```bash
export NOTION_API_TOKEN=*** # ntn reads NOTION_API_TOKEN (not NOTION_API_KEY)
export NOTION_KEYRING=0 # don't try to use the OS keychain
```

Add those exports to your shell profile (or to `${HERMES_HOME:-~/.hermes}/.env`) so every session inherits them.

> **Pitfall:** On macOS, `curl -fsSL https://ntn.dev | bash` fails with "Could not install to /usr/local/bin" — use `NTN_INSTALL_DIR="$HOME/.local/bin"` instead. Ensure `$HOME/.local/bin` is on your PATH.

### 3. Choose path at runtime

```bash
if command -v ntn >/dev/null 2>&1; then
 # use ntn
else
 # fall back to curl
fi
```

Windows users: skip step 2 entirely until native `ntn` ships — Path B works fine. If you want CLI ergonomics now, install `ntn` inside WSL2.

## API Basics

`Notion-Version: 2025-09-03` is required on all HTTP requests. `ntn` handles this for you. In this version, what users call "databases" are called **data sources** in the API.

## Path A — `ntn` CLI (preferred, macOS / Linux)

### Raw API calls (shorthand for curl)
```bash
ntn api v1/users # GET
ntn api v1/pages parent[page_id]=abc123 \ # POST with inline body
 properties[title][0][text][content]="Notes"
ntn api v1/pages/abc123 -X PATCH archived:=true # PATCH; := is non-string (bool/num/null)
```

Syntax notes:
- `key=value` — string fields
- `key[nested]=value` — nested object fields
- `key:=value` — typed assignment (booleans, numbers, null, arrays)

### Search
```bash
ntn api v1/search query="page title"
```

### Read page metadata
```bash
ntn api v1/pages/{page_id}
```

### Read page as Markdown (agent-friendly)
```bash
ntn api v1/pages/{page_id}/markdown
```

### Read page content as blocks
```bash
ntn api v1/blocks/{page_id}/children
```

### Create page from Markdown
```bash
ntn api v1/pages \
 parent[page_id]=xxx \
 properties[title][0][text][content]="Notes from meeting" \
 markdown="# Agenda

- Q3 roadmap
- Hiring"
```

### Patch a page with Markdown
The current endpoint uses a command-style discriminated union. For a full replacement:
```bash
ntn api v1/pages/{page_id}/markdown -X PATCH \
 type=replace_content \
 replace_content[new_str]="## Update

Shipped the prototype."
```
For pages containing child pages or databases, prefer `insert_content` or `update_content`; `replace_content` refuses to delete protected child content unless `allow_deleting_content=true`.

### Query a database (data source)
```bash
ntn api v1/data_sources/{data_source_id}/query -X POST \
 filter[property]=Status filter[select][equals]=Active
```

For complex queries with `sorts`, multiple filter clauses, or compound logic, pipe JSON in:
```bash
echo '{"filter": {"property": "Status", "select": {"equals": "Active"}}, "sorts": [{"property": "Date", "direction": "descending"}]}' | \
 ntn api v1/data_sources/{data_source_id}/query -X POST --json -
```

### File uploads (one-liner — biggest CLI win)
```bash
ntn files create < photo.png
ntn files create --external-url https://example.com/photo.png
ntn files list
```

Compare to the 3-step HTTP flow (create upload → PUT bytes → reference).

### Useful env vars
| Var | Effect |
|---|---|
| `NOTION_API_TOKEN` | Auth token (overrides keychain) — set this to your integration token |
| `NOTION_KEYRING=0` | File-based creds at `~/.config/notion/auth.json` instead of OS keychain |
| `NOTION_WORKSPACE_ID` | Skip the workspace picker prompt |

## Path B — HTTP + curl (cross-platform, default on Windows)

All requests share this pattern:

```bash
curl -s -X GET "https://api.notion.com/v1/..." \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2025-09-03" \
 -H "Content-Type: application/json"
```

On Windows the `curl` shipped with Windows 10+ works as-is. PowerShell users can also use `Invoke-RestMethod`.

### Search
```bash
curl -s -X POST "https://api.notion.com/v1/search" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2025-09-03" \
 -H "Content-Type: application/json" \
 -d '{"query": "page title"}'
```

### Read page metadata
```bash
curl -s "https://api.notion.com/v1/pages/{page_id}" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2025-09-03"
```

### Read page as Markdown (agent-friendly)

Easier to feed to a model than block JSON.

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}/markdown" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2025-09-03"
```

### Read page content as blocks (when you need structure)
```bash
curl -s "https://api.notion.com/v1/blocks/{page_id}/children" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2025-09-03"
```

### Create page from Markdown

`POST /v1/pages` accepts a `markdown` body param.

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2025-09-03" \
 -H "Content-Type: application/json" \
 -d '{
 "parent": {"page_id": "xxx"},
 "properties": {"title": [{"text": {"content": "Notes from meeting"}}]},
 "markdown": "# Agenda\n\n- Q3 roadmap\n- Hiring\n\n## Decisions\n- Ship MVP Friday"
 }'
```

### Patch a page with Markdown
The endpoint uses a command-style discriminated union. For a full replacement:
```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}/markdown" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2026-03-11" \
 -H "Content-Type: application/json" \
 -d '{"type":"replace_content","replace_content":{"new_str":"## Update\n\nShipped the prototype."}}'
```
To prepend without deleting child pages/databases, use `{"type":"insert_content","insert_content":{"content":"...","position":{"type":"start"}}}`. Use `update_content` for targeted search-and-replace edits.

### Create page in a database (typed properties)
```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2025-09-03" \
 -H "Content-Type: application/json" \
 -d '{
 "parent": {"database_id": "xxx"},
 "properties": {
 "Name": {"title": [{"text": {"content": "New Item"}}]},
 "Status": {"select": {"name": "Todo"}}
 }
 }'
```

### Query a database (data source)
```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2025-09-03" \
 -H "Content-Type: application/json" \
 -d '{
 "filter": {"property": "Status", "select": {"equals": "Active"}},
 "sorts": [{"property": "Date", "direction": "descending"}]
 }'
```

### Create a database
```bash
# For workspace-root databases:
curl -s -X POST "https://api.notion.com/v1/databases" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2025-09-03" \
 -H "Content-Type: application/json" \
 -d '{
 "parent": {"type": "workspace"},
 "title": [{"text": {"content": "My Database"}}]
 }'

# For child databases under a page:
curl -s -X POST "https://api.notion.com/v1/databases" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2025-09-03" \
 -H "Content-Type: application/json" \
 -d '{
 "parent": {"type": "page_id", "page_id": "xxx"},
 "title": [{"text": {"content": "My Database"}}]
 }'

# ⚠️ Properties passed at creation may return 200 but only save the default Name.
# Add properties post-creation using ntn CLI (see API Version section above).
```

### Update page properties
```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2025-09-03" \
 -H "Content-Type: application/json" \
 -d '{"properties": {"Status": {"select": {"name": "Done"}}}}'
```

### Append blocks to a page
```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2025-09-03" \
 -H "Content-Type: application/json" \
 -d '{
 "children": [
 {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello from Hermes!"}}]}}
 ]
 }'
```

### File uploads (3-step flow)
```bash
# 1. Create an upload object (returns id + upload_url)
curl -s -X POST "https://api.notion.com/v1/file_uploads" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2026-03-11" \
 -H "Content-Type: application/json" \
 -d '{"mode":"single_part","filename":"photo.png","content_type":"image/png"}'

# 2. POST multipart content to the send endpoint (do NOT PUT raw bytes)
curl -s -X POST "https://api.notion.com/v1/file_uploads/{file_upload_id}/send" \
 -H "Authorization: Bearer $NOTION_API_KEY" \
 -H "Notion-Version: 2026-03-11" \
 -F "file=@photo.png;type=image/png"

# 3. Reference {file_upload_id} as type=file_upload in a page property or child block
```

Uploaded files must be attached within one hour. For single-part uploads, the successful send response should report `status: uploaded`; no separate completion call is required.

## Property Types

Common property formats for database items:

- **Title:** `{"title": [{"text": {"content": "..."}}]}`
- **Rich text:** `{"rich_text": [{"text": {"content": "..."}}]}`
- **Select:** `{"select": {"name": "Option"}}`
- **Multi-select:** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
- **Date:** `{"date": {"start": "2026-01-15", "end": "2026-01-16"}}`
- **Checkbox:** `{"checkbox": true}`
- **Number:** `{"number": 42}`
- **URL:** `{"url": "https://..."}`
- **Email:** `{"email": "user@example.com"}`
- **Relation:** `{"relation": [{"id": "page_id"}]}`

## API Version 2025-09-03 — Databases vs Data Sources

- **Databases became data sources.** Use `/data_sources/` endpoints for queries and retrieval.
- **Database container IDs and data source IDs are distinct in current API responses.** `POST /v1/databases` returns a database container `id` plus `data_sources[0].id`. Use the container ID for page creation (`parent: {"database_id": "..."}`) and the data source ID for schema PATCH/query (`/v1/data_sources/{data_source_id}`).
- **Creating databases:** Use `POST /v1/databases` (NOT `/v1/data_sources`). For workspace-root databases, use `"parent": {"type": "workspace"}`. For child databases under a page, use `"parent": {"type": "page_id", "page_id": "..."}`.
- **Properties at creation:** Properties passed in the `POST /v1/databases` body may return 200 but only save the default `Name` property. **Always add properties post-creation** using PATCH (see below).
- **Adding properties after creation:** Use `ntn` CLI with PATCH on the data source:
 ```bash
 # Select with options — use bracket syntax for each option
 ntn api v1/data_sources/{id} -X PATCH \
 'properties[Status][select][options][0][name]=Backlog' \
 'properties[Status][select][options][1][name]=Done'

 # Empty-type properties (rich_text, date, url) — use := with JSON object
 ntn api v1/data_sources/{id} -X PATCH 'properties[Notes][rich_text]:={}'
 ntn api v1/data_sources/{id} -X PATCH 'properties[Due Date][date]:={}'
 ntn api v1/data_sources/{id} -X PATCH 'properties[URL][url]:={}'

 # Checkbox — use := with empty object (not a boolean)
 ntn api v1/data_sources/{id} -X PATCH 'properties[Done][checkbox]:={}'

 # Number with format — use := for the type config
 ntn api v1/data_sources/{id} -X PATCH 'properties[Budget][number][format]=dollar'
 ```
- **Property names with spaces:** URL-encode spaces as `%20` in `ntn` bracket syntax: `'properties[Showcase%20Ready][checkbox]:={}'`.

## Notion Workers (advanced, requires `ntn`)

Workers are TypeScript programs Notion hosts for you. One worker can expose any combination of:
- **Syncs** — pull data from external APIs into a Notion database on a schedule (default 30 min).
- **Tools** — appear as callable tools inside Notion's Custom Agents.
- **Webhooks** — receive HTTP events from external services (GitHub, Stripe, etc.) and act in Notion.

**Plan / platform gating:**
- CLI works on all plans. **Deploying Workers requires Business or Enterprise.**
- `ntn` is macOS/Linux only as of May 2026. Windows users need WSL2 or to wait for native support.
- Free through August 11, 2026; metered on Notion credits after.

### Minimal Worker

```bash
ntn workers new my-worker # scaffold
cd my-worker
# Edit src/index.ts
ntn workers deploy --name my-worker
```

`src/index.ts`:
```typescript
import { Worker } from "@notionhq/workers";

const worker = new Worker();
export default worker;

worker.tool("greet", {
 title: "Greet a User",
 description: "Returns a friendly greeting",
 inputSchema: { type: "object", properties: { name: { type: "string" } }, required: ["name"] },
 execute: async ({ name }) => `Hello, ${name}!`,
});
```

### Webhook capability

```typescript
worker.webhook("onGithubPush", {
 title: "GitHub Push Handler",
 execute: async (events, { notion }) => {
 for (const event of events) {
 // event.body, event.rawBody (for signature verification), event.headers
 console.log("got delivery", event.deliveryId);
 }
 },
});
```

After deploy: `ntn workers webhooks list` shows the URL Notion generates. Treat that URL as a secret — anyone with it can POST events unless you add signature verification.

### Worker lifecycle commands

```bash
ntn workers deploy
ntn workers list
ntn workers exec <capability-key> -d '{"name": "world"}'
ntn workers sync trigger <key> # run a sync now
ntn workers sync pause <key>
ntn workers env set GITHUB_WEBHOOK_SECRET=...
ntn workers runs list # recent invocations
ntn workers runs logs <run-id>
ntn workers webhooks list
```

When asked to build a Worker, scaffold with `ntn workers new`, write the code in `src/index.ts`, set any secrets with `ntn workers env set`, and deploy. Notion's docs at https://developers.notion.com/workers cover the full API surface.

## Notion-Flavored Markdown (used by `/markdown` endpoints)

Standard CommonMark plus XML-like tags for Notion-specific blocks. Use **tabs** for indentation.

**Blocks beyond CommonMark:**
```
<callout icon="🎯" color="blue_bg">
	Ship the MVP by **Friday**.
</callout>

<details color="gray">
<summary>Toggle title</summary>
	Children indented one tab
</details>

<columns>
	<column>Left side</column>
	<column>Right side</column>
</columns>

<table_of_contents color="gray"/>
```

**Inline:**
- Mentions: `<mention-user url="..."/>`, `<mention-page url="...">Title</mention-page>`, `<mention-date start="2026-05-15"/>`
- Underline: `<span underline="true">text</span>`
- Color: `<span color="blue">text</span>` or block-level `{color="blue"}` on the first line
- Math: inline `$x^2$`, block `$$ ... $$`
- Citations: `[^https://example.com]`

**Colors:** `gray brown orange yellow green blue purple pink red`, plus `*_bg` variants for backgrounds.

Headings 5/6 collapse to H4. Multiple `>` lines render as separate quote blocks — use `<br>` inside a single `>` for multi-line quotes.

## Choosing the Right Path

| Task | mac / Linux | Windows |
|---|---|---|
| Read/write pages, search, query databases | `ntn api ...` | curl |
| Read a page for an agent to summarize | `ntn api v1/pages/{id}/markdown` | curl `/markdown` endpoint |
| Upload a file | `ntn files create < file` | 3-step HTTP flow |
| One-off API exploration | `ntn api ...` | curl |
| Build a sync / webhook / agent tool hosted by Notion | `ntn workers ...` | WSL2 + `ntn workers ...` |

## Full Workspace Export

When the user wants to back up or migrate their entire workspace before rebuilding:

1. **Search all pages/databases:** `POST /v1/search` with empty query, sorted by `last_edited_time`
2. **For each page:** fetch `/v1/pages/{id}/markdown` (fallback: `/v1/blocks/{id}/children` if markdown endpoint fails)
3. **For each data_source:** fetch schema via `GET /v1/data_sources/{id}`, then query all records via `POST /v1/data_sources/{id}/query` (handle pagination with `has_more` + `next_cursor`)
4. **Save to vault** under a structured directory (e.g. `~/Notes/Notion-Export/{pages,databases}/`)
5. **Create an INDEX.md** with database records rendered as markdown tables

**Use Python with `urllib.request` for the export script** — it handles JSON cleanly and avoids shell quoting issues. Run it through a `terminal` heredoc from a profile that permits host-side execution; do not route it through a blocked sandboxed Python surface. Name files with the first 8-12 chars of the page/database ID prefix to avoid collisions (many pages share names like "(untitled)").

**Rate limit:** sleep 0.35s between API calls (~3 req/sec). For 100+ items, this takes ~40 seconds.

request pattern to create databases with full property schemas (avoids ntn CLI sandbox issues).

## Notes

- Page/database IDs are UUIDs (with or without dashes — both accepted).
- Rate limit: ~3 requests/second average. The CLI doesn't bypass this.
- The API cannot set database **view** filters — that's UI-only.
- Use `"is_inline": true` when creating data sources to embed them in a page.
- Always pass `-s` to curl to suppress progress bars (cleaner agent output).
- Pipe JSON through `jq` when reading: `... | jq '.results[0].properties'`.
- Notion also ships an MCP server now (`Notion MCP`, ~91% more token-efficient on DB ops than the previous version) — wire it via Hermes' MCP support if you want streaming Notion access from inside a session, but the paths above are enough for most one-shot tasks.

## Pitfalls

- **`ntn` CLI in restricted profiles:** The `ntn` binary installed to `$HOME/.local/bin` may not resolve in a restricted environment. Use `curl` directly or call via full path `~/.local/bin/ntn` from a profile that permits host-side execution.
- **Shell quoting with API keys:** When exporting `NOTION_API_KEY` from `.env`, the shell can mangle the token in complex one-liners. Source the env file first (`source ~/.hermes/.env`) or use Python to read it cleanly.
- **Name collisions on export:** Many pages share names ("(untitled)", duplicate titles). Always prefix filenames with a short ID (first 8-12 chars of UUID) to avoid overwrites.
- **Database rows vs pages:** Search returns database row pages as `"object": "page"` with non-standard properties (no `title` property — look for the first property with `title[]` or `rich_text[]` content instead). Database schemas themselves are `"object": "data_source"`.
- **Empty search results after connecting integration:** After granting workspace access, it can take a moment for pages to appear in search. If initial search returns empty, retry after 5 seconds.
- **Properties at database creation return 200 but don't persist:** `POST /v1/databases` with a `properties` object may succeed (200) but only the default `Name` property is saved. Always add properties post-creation via `ntn api v1/data_sources/{id} -X PATCH`.
- **`ntn` PATCH syntax for empty-type properties:** Use `:=` with JSON object literal — `'properties[Notes][rich_text]:={}'`, not `'properties[Notes][rich_text]{}'`. Same for `date`, `url`, and `checkbox`.
- **Checkbox PATCH needs empty object, not boolean:** `'properties[Done][checkbox]:={}'` works; `'properties[Done][checkbox]:=true'` fails with validation error.
- **Property names with spaces need URL encoding in ntn:** Use `%20` for spaces: `'properties[Showcase%20Ready][checkbox]:={}'`.
- **Ghost pages from deleted databases:** Database rows whose parent database was deleted still appear in search but return `404 object_not_found` on archive. These are stale search index entries — they'll clear within 24-48 hours automatically. Collect unique parent database IDs first and archive those before their rows to avoid ghosting.
- **Integration exists but has no workspace connection:** Having a valid API key does NOT mean the integration is connected to your workspace. Verify by opening any page → **Share** → **⚙️ Settings** → **Connections** tab — the integration must appear under **Connected apps**. If absent, every API call returns `404 object_not_found` with "Make sure the relevant pages and databases are shared with your integration". The fix: go to https://notion.so/my-integrations → click your integration → enable **"Full workspace access"** in the Connected pages section.
- **Integration not discoverable in UI search:** When trying to add an integration via "Add people" or "Connectors" in the Share panel, the integration name may return "No results found" even though it exists. This happens when the integration was created but never connected to the workspace. The fix is the same: enable full workspace access at https://notion.so/my-integrations.
- **CUA computer control for Notion integration setup:** When the API key is valid but pages return `404 object_not_found`, use CUA (`computer_use`) to share a parent page with the integration via the Notion UI: open Safari → navigate to the page → click **Share** (top-right) → look for **"Add people"** and search for the integration name. If it returns "No results found" in both "Add people" and "Connectors", the integration needs workspace-level connection: go to https://notion.so/my-integrations → click your integration → enable **"Full workspace access"**. Once connected, grab the page ID from the browser URL (format: `app.notion.com/p/<user>/<page_id>`) and proceed with API calls. The CUA path is useful for diagnosing *why* the integration isn't visible — it reveals whether the issue is page sharing vs. workspace connection.
- **Bot integrations cannot create workspace-root pages OR databases:** The API v2025-09-03 requires `parent.page_id` or `parent.database_id` for all page AND database creation. Bot integrations (internal, not public) have no `member_page`. To create top-level content, you MUST first have a manually-created parent page shared with the integration — then nest everything under it. The workspace-parent shortcut (`"parent": {"type": "workspace"}`) works for neither pages nor databases on bot integrations — both return `validation_error` asking for `parent.page_id`.
- **ntn CLI headless auth requires TWO env vars:** `NOTION_API_TOKEN` (the integration key) AND `NOTION_WORKSPACE_ID` (from `/v1/users/me` → `bot.workspace_id`). Without `NOTION_WORKSPACE_ID`, ntn errors with "No workspace selected." Set both:
 ```bash
 export NOTION_API_TOKEN=***
 export NOTION_WORKSPACE_ID=43fdcda6-42dc-4f8b-bd24-443447939eae
 ```
- **Archived data_sources are stuck:** Once a database (data_source) is archived via `PATCH /v1/data_sources/{id}`, it cannot be unarchived through any endpoint — `/v1/pages/`, `/v1/databases/`, and `/v1/data_sources/` all return 400 or 404. Recreate instead of trying to restore.
- **Bulk archiving hits type mismatches:** When searching for items to archive, database rows appear in search results but their IDs may not resolve on `/v1/pages/` (404) nor on `/v1/data_sources/` (wrong type). The reliable path: collect unique parent database IDs from search results and archive the parent databases — their rows disappear with them.
