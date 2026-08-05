# Public plugin repo replacement workflow

Use when a sanitized/public-ready local Hermes plugin exists, but GitHub already has an older public repo with an obsolete structure or historical packaging snapshot.

## Recommended handling

1. Inspect the existing GitHub repo before pushing.
 - Confirm owner/name, default branch, visibility, description, pushed date, and current file layout.
 - Clone shallow to a temp directory and read the README/manifest so you know whether it is a real release, an overlay snapshot, or stale packaging.

2. Preserve the old state before replacing `main`.
 - Create a branch from current remote `main`, e.g. `legacy-router-overlay-YYYY-MM`.
 - Create a tag, e.g. `legacy-overlay-YYYY-MM-DD`.
 - Push both branch and tag.

3. Push the clean public plugin tree as the new main.
 - Add the existing GitHub repo as `origin` in the sanitized local repo.
 - Use `git push --force-with-lease origin main`, not blind `--force`.
 - This is appropriate only after preserving the old state and when the repo has no meaningful public release history that must remain as default.

4. Update GitHub metadata.
 - Description should describe the standalone plugin, not the old packaging folder.
 - Add topics such as `hermes-agent`, `plugin`, `tool-routing`, `llm-tools`, `prompt-optimization`.
 - Optionally create a `v0.1.0` release after push.

## Example commands

```bash
# Preserve old GitHub state
rm -rf /tmp/hermes-tool-router-remote
gh repo clone OWNER/REPO /tmp/hermes-tool-router-remote -- --depth 1
git -C /tmp/hermes-tool-router-remote checkout main
git -C /tmp/hermes-tool-router-remote branch legacy-router-overlay-2026-05
git -C /tmp/hermes-tool-router-remote tag legacy-overlay-<date>-28
git -C /tmp/hermes-tool-router-remote push origin legacy-router-overlay-2026-05
git -C /tmp/hermes-tool-router-remote push origin legacy-overlay-2026-05-28

# Replace main with sanitized local tree
cd /path/to/sanitized-plugin-repo
git remote add origin https://github.com/OWNER/REPO.git
git push --force-with-lease origin main

# Refresh repo metadata
gh repo edit OWNER/REPO \
 --description "Standalone Hermes Agent plugin that reduces tool-schema prompt overhead with pre-turn toolset routing, small-model classification, fail-open fallback, and request_toolset recovery." \
 --add-topic hermes-agent,plugin,tool-routing,llm-tools,prompt-optimization
```

## Pitfalls

- Do not publish the live `~/.hermes/plugins/<name>/` directory directly; stage a clean tree first.
- Do not leave an old overlay/patch repo as default `main` if the public audience needs the standalone plugin.
- Do not force-push over old content without a branch/tag escape hatch.
- After any amend/force-ready operation, clear local reflogs if earlier commits contained local hostnames or private author metadata:
 `git reflog expire --expire=now --expire-unreachable=now --all && git gc --prune=now --aggressive`.
- Search for org/project identifiers in headers and examples as well as obvious source/docs content. OpenRouter `HTTP-Referer` headers can leak old/private org names.
