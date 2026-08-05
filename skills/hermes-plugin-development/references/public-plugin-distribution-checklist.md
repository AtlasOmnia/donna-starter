# Public Hermes plugin distribution checklist

Use when preparing a local/dogfood Hermes plugin for GitHub or other public distribution.

## Clean-room export

- Create a fresh public repo/staging directory instead of publishing the live `~/.hermes/plugins/<name>/` directory directly.
- Copy only source, manifest, sample config, tests, docs, and packaging files.
- Exclude local artifacts: `__pycache__/`, `.pytest_cache/`, backups, archived one-off migrations, logs, local profile state, and any `.env`/credential files.
- Initialize git only after the public tree is sanitized.

## Generalize configuration

- Make public `config.yaml` disabled-by-default.
- Avoid profile-specific names from the user's environment; use `global:` plus a generic `profiles.default` example.
- Document how to enable the plugin in `plugins.enabled` and where to put the plugin directory.
- If the repo directory name differs from the plugin install name, say so explicitly in README copy commands.

## README accuracy for router plugins

For tool/router plugins, explicitly distinguish:

- Deterministic-only behavior: no model/API key required, but only obvious intent patterns route narrowly; uncertain turns fail open to the full toolset.
- Full routing behavior: requires a small, fast router model and credentials/provider support.

Document the router model requirement plainly:

- Use a small low-latency model; roughly 7B-12B class or equivalent hosted classifier is the target.
- Prefer strong JSON-following and sub-second classification latency.
- Avoid large/slow models because the router runs before the main call and can erase token savings with latency.
- Document supported providers and whether a local OpenAI-compatible endpoint requires code changes.

## Privacy and data egress

- If the plugin sends prompt text or metadata to an external router/provider, add an explicit README section describing:
 - exactly what leaves the local process;
 - when no data leaves local execution;
 - conservative/sensitive-profile settings;
 - credential/env vars required for external calls.
- Do not rely on generic provider notes as privacy disclosure.
- Search not just body text but also headers/metadata such as OpenRouter `HTTP-Referer`, package names, namespace URLs, and badges; these can leak private org/project names even when source text is clean.
- Treat intentional public identity (author name/noreply email) separately from accidental local identity (machine hostnames, local emails, local paths).

## Public distribution files

Minimum useful set:

- `README.md` with purpose, requirements, install, config, privacy, safety, test commands, file map.
- `LICENSE`.
- `.gitignore` covering Python caches, test caches, local env files, OS junk.
- `requirements.txt` or `pyproject.toml` for reproducible dependencies.
- `plugin.yaml` with `provides_hooks:` (not `hooks:`), tools, license, and description.
- Disabled-by-default sample `config.yaml`.
- Smoke tests that do not require the user's live Hermes profile or credentials.

## Schema and toolset consistency

- Keep recovery-tool enum choices aligned with real documented/canonical toolset names.
- Test that recovery enum choices have descriptions and that descriptions are represented in the enum.
- Watch for legacy aliases (`skill` vs `skills`, `delegate` vs `delegation`, `video` vs `video_gen`, etc.) and either normalize them or document/test aliases.

## Verification commands

From the public staging repo:

```bash
python3 -m py_compile *.py tests/*.py
python3 tests/smoke_hardening.py
python3 -m pytest tests -q
grep -RInE '/Users|\.hermes/profiles|backups|API_KEY=[A-Za-z0-9]|sk-[A-Za-z0-9]|ghp_[A-Za-z0-9]' . --exclude-dir='.git' --exclude-dir='__pycache__' --exclude-dir='.pytest_cache' || true
git status --short --branch
```

Optional but useful: ask the dev profile or a reviewer to inspect the staging repo read-only for public-readiness issues before committing.

## Commit hygiene

- Set repo-local `user.name` and `user.email` before public commits if the default hostname-based identity is not appropriate.
- If a commit was made with the wrong author, fix before publishing:

```bash
git config user.name "<Public Name>"
git config user.email "<public-or-noreply-email>"
git commit --amend --reset-author --no-edit
```
