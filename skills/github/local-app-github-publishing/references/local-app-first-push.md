# Local App First-Push Reference

Use this as a compact transcript pattern for first-time publishing of local app projects.

## Scenario Captured

A local Spanish-English translator app had both Electron/React/TypeScript source and a native iOS SwiftUI/Xcode project. It was not a git repo yet and had generated folders and installers beside source.

## Safe Sequence

1. Verify project and GitHub auth.
2. Confirm desired repo name is available.
3. Tighten `.gitignore` before staging.
4. Run a source-only secret-pattern scan excluding generated and dependency directories.
5. Initialize git, set local identity from GitHub noreply if global identity is unset.
6. Stage, inspect file count, ignored directories, and large staged files.
7. Run available source/build checks.
8. Commit.
9. Create private GitHub repo and push with `gh repo create --source . --remote origin --push`.
10. Verify with `git ls-remote` and `gh repo view`.

## Useful `.gitignore` Patterns

```gitignore
node_modules/
.venv/
.venv-*/
dist/
dist-*/
release/
release-*/
*.tsbuildinfo
.npm-cache/
.npm-logs/
*.log
.DerivedData/
DerivedData/
*.xcuserstate
xcuserdata/
.DS_Store
.env
.env.*
!.env.example
*.pem
*.p8
*.p12
*.mobileprovision
```

## Secret Scan Patterns

Search source/docs for:

- `AIza` — Google/Gemini
- `sk-` — OpenAI-style
- `ghp_`, `github_pat_` — GitHub
- `hf_` — Hugging Face
- `-----BEGIN ... PRIVATE KEY-----`

Exclude `node_modules`, generated bundles, releases, DerivedData, and build outputs to avoid noise.

## Verification Notes

- `npm run typecheck` is a useful source sanity check for Electron/TS apps.
- For iOS compile verification without signing:
  ```bash
  DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
    xcodebuild -project SpanishTranslator.xcodeproj -scheme SpanishTranslator \
    -destination 'generic/platform=iOS' CODE_SIGNING_ALLOWED=NO build
  ```
- If `xcodebuild` says the active developer directory is CommandLineTools, set `DEVELOPER_DIR` for the command rather than changing global machine state.
- If a packaging/build step hangs but source checks pass, report the hang and workaround explicitly. Do not pretend the original command succeeded.

## Remote Verification Pattern

```bash
git status --short --branch
git ls-remote origin refs/heads/main
gh repo view OWNER/REPO --json nameWithOwner,url,visibility,defaultBranchRef,pushedAt
```
