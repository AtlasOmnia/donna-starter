---
name: vault-organization
description: vault-organization — Audit, clean up, and reorganize an Obsidian vault — identify bloat, consolidate duplicates, remove empty shells, update MOCs and stale references.
platforms:
- macos
---
# Vault Organization

Audit and reorganize the user's Obsidian vault. Run when asked to organize, clean up, or audit the vault structure.

## Vault path

Confirm the actual vault location first — do not assume `~/Documents/Obsidian Vault`. Ask or check Obsidian's settings if the path is not known.

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
