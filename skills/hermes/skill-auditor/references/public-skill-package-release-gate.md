# Public Skill Package Release Gate

Use this when a skill is being prepared as a standalone GitHub repository rather than edited in-place inside the installed skill library.

## Staging sequence

1. Build in a dedicated staging directory with no remote.
2. Keep the root `SKILL.md` directly installable from a future raw GitHub URL.
3. Add only support files that improve execution: `references/`, `templates/`, `scripts/`, tests, README, license, and CI.
4. Validate the local file directly. A registry-oriented `hermes skills inspect ./SKILL.md` invocation may print a lookup error while returning process status 0; require explicit success output, not exit status alone.
5. Exercise every shipped script:
 - dry-run produces no writes;
 - real run creates the promised artifact;
 - second run is idempotent and preserves user edits;
 - forced overwrite behavior is tested;
 - managed paths reject POSIX symlinks and Windows reparse points/junctions when writes could escape the target root.
6. Run a privacy scan over every file for credentials, personal paths, private IPs, internal business terms, unresolved placeholders, and unintended identity metadata.
7. Run an independent read-only reviewer. Tell it explicitly when the package is only a staging directory so missing `.git` metadata is not misclassified as a defect.
8. Resolve every concrete HOLD, then rerun the full suite and reviewer from the final state.
9. Initialize Git only after the package passes. Set the intended public author and noreply email locally before the first commit.
10. After committing, run an immutable gate: record the SHA, rerun validation/tests/privacy checks, remove generated caches, require a clean tree, and confirm the SHA did not change.
11. Stop before creating a remote or pushing unless the user separately authorizes publication.

## Reviewer-output handling

- A reviewer summary is provisional until its claimed file/line is inspected.
- If a reviewer returns only `HOLD — file:line`, read its session or request the full reason before changing code.
- Do not accept a reviewer PASS if tests failed or the reviewer skipped the shipped scripts.
- Do not keep retrying the same oversized review prompt. Bound tools and scope, and exclude irrelevant web or Git checks when the stage does not need them.

## Local validation fallback

A small repository-owned validator should check at least:

- frontmatter starts at byte zero and closes;
- lowercase hyphenated name within the supported limit;
- non-empty description within the supported limit;
- non-empty body within the content-size limit;
- expected sections such as Overview, When to Use, Common Pitfalls, and Verification Checklist.

After the skill is installed or published, also run the Hermes-native audit against the registered name:

```bash
hermes skills audit <skill-name> --deep
```
