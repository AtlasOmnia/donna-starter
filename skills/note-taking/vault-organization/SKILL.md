---
name: vault-organization
description: vault-organization — Structure a new Obsidian vault (PARA taxonomy, MOCs, starter folder tree) and audit/clean up/reorganize an existing one — identify bloat, consolidate duplicates, remove empty shells, update MOCs and stale references.
platforms:
- macos
---
# Vault Organization

Audit and reorganize the user's Obsidian vault. Run when asked to organize, clean up, or audit the vault structure — or to set up a sensible structure for a new/empty vault.

## Vault path

Confirm the actual vault location first — do not assume `~/Documents/Obsidian Vault`. Ask or check Obsidian's settings if the path is not known.

## Structuring a vault (new or from scratch)

When the user asks "how should I organize my vault?" or is starting fresh, recommend a structure before touching anything. Use **PARA** as the default taxonomy — it maps cleanly onto how an assistant actually uses a vault:

- **Projects/** — short-lived efforts with a goal and an end (a trip, a launch, a repair). One folder per project; archive when done.
- **Areas/** — ongoing responsibilities with no end date (Health, Finance, Home, a business, a role). These persist and get maintained.
- **Resources/** — reusable reference material not tied to one project: research, guides, templates, snippets, "how I do X."
- **Archive/** — completed projects and superseded material, kept out of the active tree but searchable.

Conventions that make the vault work for both a human and an agent:

- **MOCs (Maps of Content).** Put an `MOC.md` (or `Index.md`) at each major folder root that links to its key notes. This is the table of contents the agent reads first to navigate. Keep MOCs updated when notes move.
- **Daily notes** live in their own folder (e.g. `Journal/` or `Daily/`) and are *capture* space, not organization space. Promote anything durable out of a daily note into its PARA home; don't let knowledge rot in dated files.
- **One canonical home per thing.** A note lives in exactly one place. Link to it from elsewhere rather than duplicating it — duplicates drift.
- **Names over cleverness.** Plain, predictable folder and note names (`Areas/Health/`, not `02_Health_V2/`). The agent finds things by reading names; make them say what's inside.
- **Generated artifacts stay out.** The vault stores durable knowledge, not repeatable build/test output (screenshots, renders, Lighthouse runs, backups). Those go under `~/Projects/<project>-artifacts/<date>/` with a pointer note in the vault.

Offer a starter tree and let the user rename/rearrange before creating anything:

```text
<vault>/
  Projects/
  Areas/
  Resources/
  Archive/
  Journal/        # daily notes / capture
  MOC.md          # top-level map linking the four PARA roots
```

Create only the folders the user approves, then write a short top-level `MOC.md` that links them.

## Audit workflow

1. **Map directory tree** — `find <vault> -maxdepth 3 -type d | sort`
2. **Count files/size per top-level dir** — Python script walking the tree, skipping hidden dirs (`.obsidian`, `.hermes`, `.Vault`). Sort by file count descending to find where bulk lives.
3. **Identify bloat** — Look for:
 - Large projects with venvs/site-packages (Python, Node)
 - Duplicate content across directories
 - Empty shell directories after moves
4. **Execute structural changes** — Move files, remove empty dirs, consolidate duplicates.
5. **Update MOCs and mappings** — After structural changes, scan all MOC/Index/Indexing files for stale references to moved directories. Update them to reflect current structure. Legacy MOCs at old locations should become redirect stubs pointing to the canonical location.
6. **Audit skills and operational files** — Scan Hermes skills (`~/.hermes/skills/**/*.md`) for vault path references that point to moved directories. Patch stale paths in active files; leave historical records (daily notes, `.hermes/plans`, audit transcripts) untouched since they document what happened at the time.

## Execution rules

- Always present findings before making changes — show size/file counts, list empty dirs, identify duplicates.
- If the user authorizes end-to-end execution ("proceed"), present the plan once, then execute to completion. Only pause for genuinely ambiguous decisions where multiple valid approaches exist with different trade-offs.
- When moving projects out of the vault, leave a markdown note with a link to the new location so Obsidian still references it.
- Report before/after file counts and sizes when done.

## PARA for external knowledge repositories

When a GitHub repository holds maintained guides, comparisons, community research, or website source material, PARA is an appropriate lifecycle system outside the Obsidian vault as well. Distinguish temporary outcomes (`Projects`) from ongoing editorial responsibilities (`Areas`), reusable source material and automation (`Resources`), and superseded editions (`Archives`). Prefer structured canonical data that generates both GitHub and website output. Preserve old public paths during migrations, and establish the user's editorial authority before assuming that a different public author account makes the material third-party-owned.

## Generated-artifact storage rule

The vault stores durable knowledge, reports, decisions, and selected final assets — not repeatable build/test output. Website screenshots, Lighthouse runs, visual-regression matrices, preview renders, backups, and discarded image candidates belong under `~/Projects/<project>-artifacts/<date>/`. Leave a pointer note in the canonical vault workspace and retain human-readable reports plus approved production assets there.

When consolidating duplicate business ventures, use a single canonical home (for example `Business/Side-Hustles/`). Marketing material may link to a venture but should not own a duplicate business plan. Keep root MOC redirect stubs for backlink compatibility.
