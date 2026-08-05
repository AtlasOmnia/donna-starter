---
name: github-workflows
description: github-workflows — Consolidate GitHub auth, repository management, PR lifecycle, issues, and code review workflows.
version: 1.1.0
author: Hermes Agent
license: MIT
platforms:
- linux
- macos
- windows
metadata:
 hermes:
 tags:
 - GitHub
 - Repositories
 - Pull-Requests
 - Issues
 - Code-Review
 - CI/CD
 - Automation
 related_skills:
 - github-auth
 - github-code-review
 - github-issues
 - github-pr-workflow
 - github-repo-management
---
# GitHub Workflows

Use this skill for the full GitHub operating loop:
1) authenticate, 2) manage repos and remotes, 3) open and review PRs, 4) work on issues, and 5) monitor CI.

## Why this umbrella exists

The old project-specific skills (`github-auth`, `github-repo-management`, `github-pr-workflow`, `github-issues`, `github-code-review`) all target the same operational domain: repository setup, PR lifecycles, issue triage, and review. Consolidating them avoids fragmented workflows and makes the sequence from local repo state to merged code explicit.

## Core entrypoints

1. **Authentication first**
 - Set up GitHub access with `gh` where available, or token-based/SSH fallback.
 - Confirm auth method before attempting repo/PR operations.

2. **Repository foundation**
 - Clone, create, or fork repositories and confirm remotes.
 - Configure defaults, visibility, topics, secrets, branch protection, and releases.

3. **Issue workflow**
 - List/search/triage issues.
 - Create labels, assignments, and status updates.
 - Use templated issue creation for bug reports and feature requests.

4. **PR execution**
 - Create topic branches with naming conventions.
 - Push changes and open PRs.
 - Monitor checks and handle failures.
 - Merge with explicit strategy once checks are green.

5. **Code review loop**
 - Review local diffs and remote PR diffs.
 - Post general and inline comments.
 - Provide a structured review outcome: critical / warning / suggestion / looks good.

## Recommended practical sequence

- **Project-idea incubation:**
 - Use one private incubator repository for exploratory technical ideas.
 - Give each idea its own folder while it is being researched or lightly prototyped.
 - Promote a validated independent product into its own repository, leaving a compact link and decision record behind.

- **New repository work:**
 - `github-auth` equivalent setup → `github-repo-management` operations.
- **Feature delivery:**
 - Branch and commit changes → `github-pr-workflow` to open PR.
 - Track checks; on failure, fix and repush.
 - Post review comments and finalize via merge.
- **Maintenance and support:**
 - Use issues to triage incoming work and route effort.
 - Use code review skill patterns before merging any externally contributed change.

## PR + issue operating matrix

When a task spans both code and tracking, prefer this order:

1. Ensure repo auth is valid.
2. Confirm branch and remote are current.
3. If needed, create/clone the repo and verify contributor permissions.
4. For new work, open or update an issue first, then PR.
5. Run or track CI before requesting final merge.
6. Post review and close loop with state updates.

## Curated staging and PR-body safety

Before the first commit in a public repository, verify `git config user.name` and `git config user.email`. If either is empty or would fall back to a machine-local identity such as `user@hostname.local`, set the repository-local identity to the authenticated GitHub account and its noreply address before committing. If caught after a local commit but before push, amend with `git commit --amend --no-edit --reset-author`, then verify both author and committer fields.

For large working trees, do not default to `git add .`. Stage an explicit path list, then:

1. Run `git status --short` and investigate every `MM` entry. If a generator ran after staging, restage the final generated output so the committed file is the one that was actually tested.
2. Run `git diff --cached --check` and scan the **staged diff** for secrets.
3. Compare `git diff --cached --name-only` against a forbidden list covering credentials, result bundles, agent-session directories, build output, and known duplicate files.
4. After push, verify local `HEAD` equals the remote branch SHA.

For multiline PR descriptions—especially Markdown containing backticks, `$()`, or shell metacharacters—write the body with the file tool and call `gh pr create --body-file <path>` or `gh pr edit --body-file <path>`. Do not pass rich Markdown inside a double-quoted `--body` shell argument: command substitution can execute text inside backticks and silently corrupt the PR description. Read the PR back with `gh pr view --json body,url,state` before reporting success.

If `gh pr checks` reports that no checks exist, say so explicitly; a successful push is not CI verification.

## Public GitHub profile setup

Treat a GitHub profile as two separate deliverables:

1. **Account metadata** — display name, bio, website, and optional location, updated through `PATCH /user`.
2. **Profile README** — `README.md` in a public repository whose owner and repository names exactly match the authenticated username.

Preflight with `gh auth status` and `gh api user`; do not assume repository scopes permit profile edits. The REST profile endpoint requires the OAuth `user` scope. If `PATCH /user` returns HTTP 404 with a scope hint, request only that scope using `gh auth refresh -h github.com -s user -c`. GitHub's device authorization must be approved by the user; do not enter credentials or approve permission dialogs on their behalf. Resume only after the refresh exits successfully and `gh auth status` confirms the scope.

For the profile README, use the established public/noreply Git identity, scan the staged content for secrets and PII, push it, then verify the rendered public profile rather than only the repository API response. Keep community-facing profiles credibility-first: concise project summaries, verified links, and an affiliation disclaimer when independent community work could be mistaken for an official vendor account.

## Quick fallbacks when `gh` is unavailable

- Keep GH token/env credentials ready from secure sources (`GITHUB_TOKEN` in `.env` or the OS keychain).
- Use `curl` REST endpoints for auth-required actions and include explicit owner/repo extraction.
- Preserve scope boundaries: issue endpoints and PR endpoints are intentionally separate and should not be mixed with repo creation commands.

## Multi-repository sync and reconciliation

When asked to scan “all repos,” treat it as an inventory and classification task rather than repeating `git pull` blindly:

- State the filesystem roots scanned and any exclusions.
- Discover both `.git` directories and `.git` files, then deduplicate fetches with `git rev-parse --git-common-dir` so linked review worktrees do not trigger redundant network operations.
- Fetch first, calculate exact ahead/behind counts, inspect tracking **and no-upstream** branches, and check live GitHub PR mergeability.
- Separate canonical clones from duplicate clones, backups, malformed refs, detached campaign worktrees, and archival branches.
- Never infer “needs merge” from ancestry counts or `git branch -r --no-merged` alone; compare patch IDs and final trees when squash merges or duplicate commits are possible.
- Do not modify dirty or diverged repositories during a scan-only request.

When the user asks to continue into reconciliation:

- preserve tracked and untracked work outside the repository plus a stash/archive branch before changing ancestry;
- evaluate reapplied WIP against current source and gates rather than assuming every local change should be published;
- refuse to merge stale work that reintroduces regressions merely to make the tree clean;
- repair malformed refs only after recording reachability and preserving unique commits;
- finish with repository gates, staged/public privacy scans, remote-SHA equality, clean canonical checkouts, and a fresh all-PR/all-branch scan;
- distinguish Git blockers, product release gates, dependency advisories, and intentional archives in the report.

### Destructive cleanup and archive retirement

Treat synchronization and archival cleanup as separate phases. A canonical repository can be fully reconciled even while duplicate snapshots, campaign worktrees, backup branches, or stashes remain intentionally preserved.

1. Prove the canonical clone is clean and equal to its remote before touching any duplicate.
2. Preserve unique branch tips with a verified `git bundle`, and preserve dirty work with an external patch/tar archive.
3. Execute destructive operations **serially**, never in a parallel batch. Approval systems may allow one deletion and deny another, leaving partial state that must be re-read before continuing.
4. After every approved deletion, verify the path/ref is absent and the canonical clone is unchanged.
5. If an approval is denied, do not rephrase or route around it. Stop that cleanup item, leave the archive classified as noncanonical, and continue only with read-only verification.
6. A directory containing `.git` files may be an unregistered review copy even when `git worktree list` shows only the canonical checkout. Classify it from both views before removal.

### Staged privacy-scan precision

Do not scan staged diffs with an unbounded `grep 'sk-'`: ordinary package-lock names such as `task-*` can match and create false alarms. Use token boundaries and realistic minimum lengths (for example `(?<![A-Za-z])sk-[A-Za-z0-9_-]{20,}`), scan without printing matched secret values, and keep local-path/PII checks separate from credential checks.

For explicitly authorized deletion of whole remote GitHub repositories, including complete `git bundle` backups, dirty-work sidecars, the `delete_repo` OAuth device flow, serial DELETE calls, and absence verification, follow the deletion steps in this skill.

## Investigating “branched but not on main” reports

Treat this as a provenance question, not merely a branch-name search:

1. Resolve the exact repository first. If the name is uncertain, search session history or the authenticated account’s repository list; once an exact `owner/repo` is known, query it directly with `gh repo view owner/repo`. Broad repository-enumeration filters can omit private, transferred, archived, or otherwise unexpectedly classified repositories.
2. Inspect all three surfaces:
 - current branches: `gh api --paginate repos/OWNER/REPO/branches?per_page=100`
 - PR history: `gh pr list --repo OWNER/REPO --state all`
 - raw refs: `git ls-remote https://github.com/OWNER/REPO.git`
3. Inspect repository events and main history when the expected branch is absent:
 - `gh api --paginate 'repos/OWNER/REPO/events?per_page=100'`
 - `gh api 'repos/OWNER/REPO/commits?sha=main&per_page=30'`
 A local-only topic branch may have been fast-forwarded or pushed directly to `main`, leaving no remote branch and no PR. A deleted branch may still appear in repository events or `refs/pull/*`.
4. Prove ancestry before concluding anything: record the old base, current main SHA, commit parents, and compare range. Distinguish “merged through a PR,” “fast-forward/direct push to main,” “branch exists but is unmerged,” and “local-only work not present on GitHub.”
5. If the change is already on `main`, say plainly that nothing needs merging. Separately flag process concerns such as bypassing PR review; do not manufacture a merge task merely because the work began on a branch.

## Self-hosted runner deployment

Use self-hosted runners to preserve GitHub PR/check workflows without consuming GitHub-hosted minutes.

- Personal-account repositories only support repository-level runners. Organization-level runners are required for one runner pool shared across multiple repositories.
- Restrict persistent self-hosted runners to private, trusted repositories. Route jobs with both `self-hosted` and a machine-specific custom label; never rely on an OS label alone.
- Download runner packages from the official `actions/runner` release and verify the release asset SHA-256 digest before extraction.
- Treat registration tokens as short-lived secrets. For remote Windows setup, transfer the token through a protected temporary file, consume it locally, and delete it immediately; command-line quoting can corrupt tokens and expose them in process listings.
- On macOS, register as the normal user and install the provided LaunchAgent with `svc.sh`. Confirm both `launchctl` state and GitHub's runner API status.
- On Windows, prefer the runner's `NETWORK SERVICE` service mode over `LocalSystem`. If tests require symlink creation, enable Windows Developer Mode rather than elevating the runner service. Match GitHub-hosted tooling explicitly (for example, checksum-verified portable PowerShell 7 when workflows use `shell: pwsh`).
- A WSL user-systemd service may disappear when the distro idles after the initiating shell exits. If that occurs, use a Windows logon scheduled task that keeps `wsl.exe ... run.sh` in the foreground, then verify the runner remains online after the administration session disconnects.
- Do not stop at an online status check. Route a real branch/PR workflow, fix environmental parity failures, merge only after all jobs pass, and verify the post-merge `main` run on the deployed workflow.

## Verification checklist

- auth method validated (`gh auth status` or equivalent token path)
- repo and remotes inspected before creating PRs
- issue/PR state checked before merging
- branch/merge strategy chosen intentionally (`merge`, `squash`, `rebase`)
- review outcomes stored with severity buckets
- security-sensitive steps (secrets) handled through approved tools and approvals

## Support-file equivalents from merged skills

Legacy skill assets now live in the archived originals under:
- `github-auth`: inline auth setup block
- `github-code-review`: inline review checklist
- `github-issues`: templates/bug-report.md and templates/feature-request.md
- `github-pr-workflow`: PR templates
- `github-repo-management`: repo setup checklists

## When not to use this skill

- If the request is only a one-off `gh` command, use the direct `gh` call.
- For non-GitHub issue/PR tasks, use the project-specific skill that matches the actual domain
 (e.g., local code review logic, testing, or architecture workflows).
