---
name: local-app-github-publishing
description: local-app-github-publishing — Safely publish local apps, prototypes, and substantial local branches to GitHub for the first time.
version: 1.0.1
author: Hermes Agent
license: MIT
platforms:
- macos
- linux
- windows
metadata:
 hermes:
 tags:
 - GitHub
 - Git
 - repositories
 - first-push
 - app-projects
 - secrets
 related_skills:
 - github-repo-management
 - github-auth
---
# Local App GitHub Publishing

Use this when the user asks to push a local app/prototype/project to GitHub for the first time, especially Electron, iOS/Xcode, mobile, desktop, or AI/API-integrated apps.

This skill complements the protected `github-repo-management` skill with the user-specific first-push hygiene: publish the useful source, not the machine's junk drawer wearing a trench coat.

## Core Rule

Before the first commit, sanitize and verify. Generated builds, dependency folders, local Xcode state, and API credentials do not belong in the initial history.

## Default Behavior

- **Default visibility: private** unless the user explicitly asks for public.
- Use a simple repo name matching the user's wording when possible, normalized to GitHub style, e.g. “iOS translator” → `ios-translator`.
- If the repo name exists, choose the closest available variant only if the user gave broad wording; otherwise ask.
- Set a repo-local git identity if global `user.name` / `user.email` are missing.
- Verify the pushed remote before reporting success.

## First-Push Workflow

1. **Confirm project and GitHub auth**
 ```bash
 cd /path/to/project
 git --version
 gh auth status
 GH_USER=$(gh api user --jq .login)
 gh api user --jq .id
 ```

2. **Check whether the target repo exists**
 ```bash
 gh repo view "$GH_USER/REPO" --json nameWithOwner,url,visibility 2>&1 || true
 ```

3. **Create or tighten `.gitignore` before `git add`**

 Include at least:
 ```gitignore
 # Dependencies
 node_modules/
 .venv/
 .venv-*/

 # Build outputs
 dist/
 dist-*/
 release/
 release-*/
 *.tsbuildinfo

 # Local caches/logs
 .npm-cache/
 .npm-logs/
 *.log

 # Xcode / Apple local state
 .DerivedData/
 DerivedData/
 *.xcuserstate
 xcuserdata/
 .DS_Store

 # Environment / secrets
 .env
 .env.*
 !.env.example
 *.pem
 *.p8
 *.p12
 *.mobileprovision
 ```

4. **Run a source-only secret scan**

 Exclude generated/dependency directories. Search for common key patterns:
 - `AIza` — Google/Gemini keys
 - `sk-` — OpenAI-style keys
 - `ghp_`, `github_pat_` — GitHub tokens
 - `hf_` — Hugging Face tokens
 - `-----BEGIN ... PRIVATE KEY-----`

 If a real secret is found, stop and remove/rotate before committing.

5. **Initialize git and stage**
 ```bash
 git init -b main 2>/dev/null || git init
 git add -A
 git status --short
 ```

6. **Verify staged content before committing**
 ```bash
 git diff --cached --name-only | wc -l
 git check-ignore -v node_modules release dist-renderer dist-electron .DerivedData .DS_Store 2>/dev/null || true
 python3 - <<'PY'
 import os, subprocess
 files = subprocess.check_output(['git','diff','--cached','--name-only'], text=True).splitlines()
 found = False
 for f in files:
 if os.path.exists(f) and os.path.getsize(f) > 20*1024*1024:
 print(f, os.path.getsize(f))
 found = True
 if not found:
 print('No staged files over 20MB')
 PY
 ```

7. **Set repo-local identity if needed**
 ```bash
 GH_USER=$(gh api user --jq .login)
 GH_ID=$(gh api user --jq .id)
 git config user.name "$GH_USER"
 git config user.email "${GH_ID}+${GH_USER}@users.noreply.github.com"
 ```

8. **Commit and push**
 ```bash
 git commit -m "Initial app commit"
 gh repo create REPO --private --source . --remote origin --push --description "Short description"
 ```

9. **Verify remote**
 ```bash
 git status --short --branch
 git ls-remote origin refs/heads/main
 gh repo view "$GH_USER/REPO" --json nameWithOwner,url,visibility,defaultBranchRef,pushedAt
 ```

## Publishing a Long-Running Local Branch for the First Time

Use this before the first remote push of a substantial campaign, repair, or autoresearch branch in an existing repository—not only before a repository’s initial push.

1. Verify the complete branch range, not just the working tree:
 - `git diff --check main...HEAD` catches whitespace already committed.
 - Scan `git log -p --format= main..HEAD` for credential patterns; scanning only current files misses secrets added and later removed.
 - Inventory local filesystem paths, machine-local emails, and personal identifiers separately from actual credentials. Private branches may intentionally retain diagnostic paths, but public publication requires sanitizing them.
2. Inspect author **and committer** metadata across `main..HEAD`. If an unpushed branch contains automatic workstation identities, normalize it before first push:
 - create a local backup ref;
 - record `HEAD^{tree}` and `git rev-list --count main..HEAD`;
 - rewrite only the unpushed branch to the established noreply identity;
 - require the final tree hash and commit count to remain identical;
 - rerun the full gate afterward.
 Never rewrite already-shared history without explicit authorization.
3. Confirm the remote branch does not already exist with `git ls-remote --heads` before deciding whether a normal push or coordinated force-with-lease workflow applies.
4. Push the named branch only, then verify local HEAD equals `git ls-remote` for that exact ref and that the working tree tracks the intended remote branch.
5. Update any campaign state/report that records final SHAs after metadata normalization or push. Record branch push separately from PR, merge, tag, release, and deployment; do not imply one from another.

## Merging a Completed Branch into Protected Main

When the user asks to merge a named feature branch:

1. Resolve the branch's actual repository before acting. If it is absent from the current repository, search session history for the exact branch name instead of concluding it does not exist.
2. Fetch/prune, compare `origin/main...origin/<branch>`, and inspect the complete commit range.
3. On the feature branch, run both `git diff --check origin/main...HEAD` and `git diff --check`; the former catches committed whitespace defects while the latter validates any unstaged cleanup.
4. Run the repository's canonical tests and an independent security/privacy review for substantive public changes. Normalize public commit identity to the established GitHub noreply address.
5. Open a PR, wait for all required checks, then merge—prefer squash when cleanup-only commits should not survive as separate history.
6. Pull `main --ff-only`, verify the PR merge state and live default-branch files, and wait for post-merge `main` CI. PR checks and post-merge checks are separate gates.
7. Treat local branch deletion as optional housekeeping. If an approval gate denies it, stop and report that only the local branch remains; do not retry or misreport the merge as incomplete.

## Public README Readiness

Before making a repository public, make the README understandable to someone who has no session context:

1. The first paragraph must explain in plain language what the project does, what input/action it takes, how success is determined, and what happens to the result. Prefer concrete verbs over labels such as “provider-agnostic harness” or “iterative framework.”
2. State consequential boundaries early—for example, whether changes are committed locally, reverted, uploaded, pushed, or published automatically.
3. For a non-trivial loop or architecture, place one explanatory diagram near the top. Prefer an accessible SVG with a native `viewBox`, embedded by relative path and supplied with useful Markdown alt text.
4. Verify the diagram in a real browser at its native aspect ratio; square thumbnail generators can crop wide SVGs and produce a false visual failure.
5. After merge, inspect the rendered GitHub repository page, not only the source Markdown. Confirm the image resolves with expected dimensions and alt text. If `raw.githubusercontent.com` briefly serves stale content, verify the default-branch SHA and use GitHub's Contents API with `?ref=main` or the exact commit SHA before concluding the merge failed.

### README SVG quality gate

For a hand-authored architecture/flow SVG:

1. Validate the XML before visual review: `xmllint --noout docs/diagram.svg`.
2. Render at the SVG's native aspect ratio. On macOS, prefer `sips -s format png docs/diagram.svg --out /tmp/diagram.png`; `qlmanage -t` creates square thumbnails and can crop or mis-scale a wide diagram, producing misleading QA evidence.
3. Use portable SVG text styling (`font-family`, `font-size`, `font-weight`) rather than a complex `font:` shorthand. Include Arial/Helvetica/sans-serif fallbacks so GitHub and native rasterizers agree more closely.
4. Inspect the raster for clipped labels, card overflow, connector lines crossing unrelated cards, ambiguous arrow direction, and readable contrast at README width.
5. Embed responsively, for example `<img src="docs/diagram.svg" alt="..." width="100%">`; avoid forcing a fixed 1200-pixel width inside GitHub's narrower content column.
6. Have an independent reviewer compare every diagram claim against the current implementation and check the changed diff for secrets/PII before publication. Resolve accuracy and rendering findings before commit.

## Separating Products After an Accidental Merge

When a feature conversion landed in the original product repository but the user intended two distinct applications, preserve the converted product before restoring the original:

1. Clone the verified conversion commit into a sibling directory.
2. Create and push a new private repository from that clone.
3. Restore the original repository with `git revert`, not reset/force-push.
4. Validate, smoke-test, audit, and verify CI independently for both repositories.

Treat “separate programs” literally: distinct repositories, application identities, local data boundaries, release cycles, and launchers. Shared architecture does not imply one executable with selectable courses or modules.

## App Verification Notes

- Run reasonable pre-push checks if available, but do not block publication on unrelated packaging quirks once source integrity is confirmed.
- For Xcode/iOS projects on machines where `xcode-select` points at Command Line Tools, use:
 ```bash
 DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild ...
 ```
- For CI/source validation when provisioning profiles are unavailable, use `CODE_SIGNING_ALLOWED=NO` to verify compilation without signing:
 ```bash
 DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
 xcodebuild -project App.xcodeproj -scheme App -destination 'generic/platform=iOS' CODE_SIGNING_ALLOWED=NO build
 ```
- If an app build/minification step hangs but source checks pass, record the exact workaround and mention it as a follow-up, not as a reason to invent success.

## Public GitHub profile linkage

When a newly published product site should become the commercial destination for an established GitHub identity:

1. Read the existing profile before changing anything:
 ```bash
 gh api user --jq '{login,name,bio,blog,company,location,html_url}'
 ```
2. GitHub exposes the profile **Website** field as `blog`. Change only that field unless the user explicitly requests broader profile edits:
 ```bash
 gh api --method PATCH user -f blog='https://example.com' \
 --jq '{login,bio,blog,html_url}'
 ```
3. Verify the public representation, not only the authenticated response:
 ```bash
 GH_USER=$(gh api user --jq .login)
 gh api "users/$GH_USER" --jq '{login,bio,blog,html_url}'
 ```

For the user's value-first commercial funnel, the Website field should point to the canonical owned commercial hub; the bio can retain community/moderator positioning. Link public product repositories back to specific product or documentation pages, while keeping the storefront source repository private by default.

## Static Website Deployment and Domain Handoff

When the first-published project is a static commercial website, continue through hosting and live-domain verification rather than stopping at source control. Determine the deployment source **before changing remotes**: a Cloudflare-hosted site may use Direct Upload even when a historical GitHub repository exists.

- For Git-connected Cloudflare Pages plus an external registrar, use , including DNS/mail-record preservation, apex/`www` canonicalization, and live HTTPS verification.
- When the user specifies local Git plus direct Cloudflare deployment, use : make the private Mac-hosted bare repository canonical `origin`, retain GitHub only as a reference remote, verify checkout/local-remote SHA parity, and treat Cloudflare publication as a separate gate.

Never assume that pushing GitHub updates the live Cloudflare site. Verify whether the project is Git-integrated or Direct Upload, and keep source-control completion distinct from deployment completion.

Before deployment, verify that every commit uses the user's established GitHub noreply identity. A syntactically “noreply”-looking custom-domain address is not automatically the correct public identity.

## Retiring Remote Repositories Safely

When the user explicitly authorizes deleting a GitHub repository, treat retirement as a recoverability and least-privilege workflow: inspect every remote ref and local clone, create and verify a complete Git bundle, preserve dirty/untracked local work separately, delete repositories serially with an absence check after each one, and retain local copies unless separately authorized for deletion. GitHub repository admin permission does not imply that the active OAuth token has `delete_repo`; request that scope only for the deletion, require the user to approve the device flow, then remove the scope and verify it is absent from `gh auth status`.

## Pitfalls

- Never commit `release/` or generated `.exe`/installer artifacts by accident on the first push.
- Do not trust a clean-looking top-level directory; Xcode and Electron often leave large generated folders beside source.
- Do not print or include secret values in reports. Say whether a scan found hardcoded key patterns.
- Do not promise public availability if the repo was created private.
- Do not conflate source-patch recovery with deployed-binary recovery. A post-update Git hook may reapply source changes successfully while leaving an installed Electron/macOS/Windows application on the old build; inspect and document the rebuild/reinstall path separately.

- `references/local-app-first-push.md` — condensed checklist and command transcript pattern from a successful Electron+iOS translator app first push.
- `references/private-upstream-patch-repository.md` — package a verified upstream repair as a small private patch repo with an idempotent worktree-safe apply script, artifact-integrity checks, and local macOS packaging gates.
- `templates/idempotent-git-patch-apply.sh` — starter installer for fail-closed, worktree-safe, idempotent patch application.
## Public support files

- `references/local-app-first-push.md`
- `references/private-upstream-patch-repository.md`
- `templates/idempotent-git-patch-apply.sh`
