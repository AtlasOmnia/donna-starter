---
name: application-security-review
description: application-security-review — Review application repos for concrete security issues, especially trust-boundary failures, prompt-injection paths, auth/proxy mistakes, validation gaps, and risky dependencies.
version: 1.5.0
license: MIT
platforms:
- linux
- macos
- windows
metadata:
 hermes:
 tags:
 - security
 - appsec
 - code-review
 - dependency-audit
 - prompt-injection
 - validation
 - proxy
---
# Application Security Review

Perform a practical source-level security review of an application repository. Favor confirmed issues over speculative ones. The goal is a useful operator-facing report: severity, file/line references, exploit path, impact, and remediation.

## Use when
- The user asks to "scan for security issues", "review for security", or "audit this repo/app".
- The user asks whether a native app or realtime AI/voice prototype is ready to sell, ship, distribute, or submit to an app store.
- Reviewing AI-integrated apps, browser/UIs, add-ins, extensions, native mobile apps, or local proxies.
- Evaluating whether a prototype is safe for local-only use vs real deployment.

For native iOS commercial-readiness reviews, load and follow the readiness checklist. It expands the audit beyond security into StoreKit, App Store compliance, realtime audio reliability, consumer UX, unit economics, and release gates.

## Review priorities
1. Trust boundaries first.
 - What input is untrusted?
 - What backend capabilities sit behind the UI?
 - Can model output or user-controlled content trigger side effects?
2. Auth and exposure.
 - Localhost services, reverse proxies, injected auth headers, CORS, TLS, origin restrictions.
3. Validation before execution.
 - JSON/action parsing, schema checks, range/size limits, before/after verification, allowlists.
4. Data handling.
 - What leaves the machine, what is logged, whether sensitive user data is silently sent to cloud backends.
 - For public-release reviews, scan both tracked source and git metadata for PII: local hostnames, personal emails, profile names, private org/business names, absolute user paths, and secret/token patterns.
5. Dependencies.
 - Separate runtime risk from dev-toolchain risk.

## Workflow
1. Read top-level README and manifests/config first to understand architecture.
2. Locate network entry points and auth flow.
3. Trace untrusted input to powerful sinks:
 - LLM prompts
 - filesystem/terminal/network tools
 - code execution
 - document/workbook mutations
4. Search for:
 - fetch/XHR/API calls
 - proxies and bearer-token injection
 - JSON.parse on model output
 - eval/Function/innerHTML/dangerous DOM sinks
 - wildcard CORS or broad allowlists
 - dependency versions with known advisories
5. For public-release/privacy scans, include repository metadata and the actual remote publication surface as well as source:
 - Before first push, inspect staged/tracked files, local author metadata, and reachable history to catch accidental local-hostname identities and workstation paths.
 - Scan tracked/source files for emails, hostnames, `<user-home>/...`, `C:\\Users\\<name>`, private profile names, internal org names, token prefixes, and generated run artifacts.
 - After push or history rewrite, make the publication verdict from a fresh remote clone/mirror, every public branch/tag and PR ref, PR text, commit metadata, and all reachable blobs. Do not count ignored files, virtual environments, local reflogs, or stale remote-tracking refs as currently published content.
 - Use an independent-model review when practical, then verify findings yourself; classifiers often mislabel loopback, placeholder paths, or code symbols as PII.
 - Confirm the update reaches the intended default/publication branch rather than remaining only on a feature branch.
 - Distinguish generic loopback (`127.0.0.1`), contextual test IPs, GitHub noreply identities, placeholder fixtures, and code symbols ending in `.local` from real PII or private-machine identifiers.

6. Run dependency audit when package managers/lockfiles exist.
7. Distinguish:
 - confirmed issue
 - lower-confidence concern / defense-in-depth note
8. End with deployment posture:
 - safe for toy local use
 - needs hardening before sensitive/internal use
 - not suitable as-is

## Type alignment across trust boundaries
- When the same domain type (e.g. `ProviderMode`, `CredentialKind`, `ActionType`) is defined independently on BOTH sides of a trust boundary (renderer ↔ backend, client ↔ server), search for ALL definitions.
- A type that drifts creates silent acceptance bugs: one side accepts a value the other cannot handle, or a new value is added on one side but not the other.
- **Evidence pattern:** search for the same union-type literal strings across multiple files in different process contexts. Count the files. Flag any mismatch.
- **Fix:** Extract a single shared definition in a neutral module. When cross-import is architecturally blocked (e.g. renderer cannot import electron types), enforce alignment with a CI snapshot test, a duplicate-detection script, or at minimum a comment chain linking the duplicated definitions.

## Inconsistent URL validation across similar provider endpoints
- When an application lets the user configure multiple API or LLM endpoint URLs (local LLM, OpenRouter, custom proxy, etc.), verify that EACH endpoint is validated with the same depth:
 - URL parsing (not just string-length check)
 - Protocol allowlist (`http:`/`https:` only, reject `file:`, `data:`)
 - Hostname restriction (loopback, private-LAN, or explicit production allowlist)
 - Credential rejection (reject URLs with embedded `user:password@`)
- A field that only checks string length while sibling fields have full `new URL()` + hostname validation is a fragility/SSRF risk — it looks validated to future readers.
- **Evidence pattern:** search for `assertString` or string-length-only validation on fields named `*Endpoint`, `*Url`, `*BaseUrl` while nearby similar fields parse the URL and check the hostname.
- **Fix:** Apply the same validator (or a documented subclass) to all semantically similar URL-bearing fields. When secondary validation exists downstream, the upstream should still be consistent — defense-in-depth.

## Two-phase validation (upstream gate + downstream gate)
- Sometimes a validation function passes a field with only a string-length check because a downstream function does the real URL/hostname validation. This is acceptable only when the division of responsibility is EXPLICITLY documented and every code path that consumes the validated result goes through the downstream gate.
- **Risk:** A future code path that reuses the validated output without passing through the downstream gate inherits the weaker check. Trace all consumers.
- **Fix:** Either move the full validation upstream, or add a comment on the minimal check explaining why it is intentionally deferred and naming the downstream function that provides the real gate.

## Prototype-sensitive dictionaries at trust boundaries
- Treat every attacker-controlled property name as hostile when code indexes a trusted configuration/alias/allowlist object.
- Flag `trustedMap[inputKey]` on ordinary objects unless the lookup first proves an own data property of the expected type. Inherited `Object.prototype` entries—or prototype pollution—can turn an unknown field into an approved alias or capability.
- Flag `result[inputKey] = value` when arbitrary keys are materialized. The special `__proto__` setter can mutate the result prototype or erase the field before a downstream validator sees it.
- Preferred repair: inspect the trusted map with `Object.getOwnPropertyDescriptor`, accept only own data descriptors, and create output keys with `Object.defineProperty` as ordinary enumerable/writable/configurable data properties.
- Require production-entry regressions for polluted prototype key → approved key, polluted key → `__proto__`, JSON-parsed own `__proto__`, and an existing canonical key plus the polluted unknown key. Restore temporary prototype mutations in `finally`.
- Green schema validation alone is insufficient when preprocessing runs first. Verify unknown fields survive preprocessing and reach the authoritative validator unchanged except for explicitly approved syntax normalization.

## AI-integrated app checklist
- For desktop applications that export diagnostics or a user-shareable Support Report, follow the guidance covering main-process authority, exact allowlisted schemas, code-only diagnostic storage, payload-free renderer IPC, atomic export, consent/disclosure rules, adversarial tests, and bounded independent-review recovery.
- For local AI desktop apps that ingest documents, maintain a managed source vault, expose course/task-oriented IPC, perform grounded generation, or persist packet-bound assessment, review the guidance covering canonical path/symlink handling, ZIP-bomb limits, UTF-8 chunking, immutable course authority, exact citations, persisted-draft publishing, packet-scoped assessment, real model-client integration, and controller verification after model review.
- For profile-scoped local-agent desktop apps, review the guidance; it covers legacy authority routes, server-side profile binding, source provenance, secure-storage edge cases, and deletion-derived state.
- Treat document/spreadsheet/page content as untrusted prompt input.
- If the backend is a full agent, check whether prompt injection can reach tools or side effects.
- If model output drives actions, require strict schema validation and operator review.
- Verify previews actually match what will be written.
- Check whether the app silently transmits sensitive content to cloud models depending on backend config.
- For Office task panes with native Hermes/plugin routing, require out-of-band binding between the originating turn and the exact pane/session. A UUID carried in model-visible text is not authorization; add a two-pane negative test even when every identifier is syntactically valid.
- For credential-injecting loopback proxies, audit wildcard CORS, missing body/concurrency limits, arbitrary plaintext upstream overrides, and predictable credential fallbacks. Loopback-only binding does not prevent cross-origin web access.

## Self-hosted agent control-plane checklist

When the reviewed application is a multi-tenant agent ledger/control plane, inspect the deployment boundary as carefully as the HTTP routes:

- Resolve the effective Compose/Kubernetes environment after `environment` overrides `env_file`; do not trust redacted tool output as literal source content.
- Treat Docker-socket mounts, host PID/IPC/network modes, privileged containers, and in-app self-update endpoints as host-capability boundaries. An admin-only route may still be a critical trust boundary when it can pull images, execute commands, create/stop/delete containers, or replace the running service.
- Compare image tags with immutable digests/signatures and inspect whether update code verifies provenance. `:latest` plus a privileged updater is a supply-chain and rollback concern, not merely a convenience feature.
- Verify that encryption keys are mandatory before sensitive credentials are accepted or stored. A documented plaintext fallback is a deployment blocker for sensitive/internal use.
- Treat company/workspace bearer tokens as the authenticated principal. Do not assume agent names, request-body `agentId`, Hermes profiles, or model fields provide security isolation unless the server enforces those bindings.
- For every webhook or message route accepting a resource ID, prove tenant ownership in the same query or an explicit check. A foreign key proving that a thread/task/artifact exists does not prove it belongs to the caller's tenant.
- Report these as confirmed defects only when the code path demonstrates the missing check; otherwise label them as defense-in-depth or verification gaps.

- First classify deployment posture: stdio/local-only, loopback HTTP, tunneled remote, or production/shared. A sidecar can be acceptable locally while still being a blocker for remote exposure.
- Check auth and exposure: loopback binding, non-loopback hard-fail vs warning, tunnel docs, `noauth`, `proxy_headers`, and trusted forwarded IP settings.
- Trace MCP tools to powerful local sinks: file read/search/write/patch, terminal execution, memory writes, session search, profile/skill enumeration.
- Verify risky tools are hidden by default **and** direct function calls remain gated; registration gates alone are not enough.
- For profile-specific installs, require wrapper launchers that force the intended `HERMES_HOME` and explicitly clear dangerous feature env vars unless the user asks for a supervised high-risk session.

## Office/add-in specific checklist
- Inspect manifest permissions and app domains.
- Verify localhost assumptions: same-machine only vs remote machine.
- Review dev-cert and HTTPS proxy setup.
- Check whether proxy auth is just header injection for any local caller.
- Review workbook/document mutation flow for TOCTOU, cross-sheet/document scope, and oversized writes.

## Reporting format
For each finding provide:
- Severity
- Title
- Why it matters
- Evidence (path:lines)
- Practical fix

For public-repository questions, give **separate verdicts** so release-quality advice is not mistaken for a privacy finding:
1. **Privacy/secrets verdict** — whether personal information, credentials, private endpoints, or machine-specific artifacts are present in current reachable publication surfaces.
2. **Public-release readiness verdict** — legal, documentation, security-warning, CI, and branch-hardening gaps.

Use precise blocker language:
- A missing `LICENSE` file is not personal information and does not technically prevent changing GitHub visibility, but it is a pre-publication blocker when the intent is reusable open source because downstream permissions remain unclear.
- Missing CI, templates, `SECURITY.md`, Dependabot, or branch protection are normally hardening recommendations, not automatic barriers to visibility.
- Intended arbitrary-command execution is not itself a vulnerability. Verify whether the project clearly warns users that commands/configs must be trusted and that an edit allowlist is not an execution sandbox; misleading safety claims can be a release-readiness blocker.

End with one direct sentence answering the user's actual question (for example, “No privacy barrier; fix the license and command-safety warning before publishing as reusable open source.”).

Also provide a short "good news" section for controls that are already sane.

## Test infrastructure integrity
- Security-critical tests that import from compiled output (`dist-electron/`, `dist/`) instead of TypeScript source risk running against stale code after a rebuild failure.
- **Evidence pattern:** `.mjs` or `.js` test files importing from `../../dist-*` directories while sibling test files import from `.ts` source directly.
- **Fix:** Use a TypeScript runner or force a `pretest` rebuild step. When the renderer tests already import `.ts` directly, the electron/main-process tests should follow the same pattern. At minimum, add a CI guard that fails on stale dist.

## Browser-harness and skill-package release reviews
- Treat a validator's PASS as a claim that must be tested adversarially, not as proof of the documented state. If the schema says `tested: true` requires full replay, every mandatory step, and a recovery path, construct temporary fixtures that set `tested: true` while omitting or contradicting those evidence fields; the validator must reject them.
- Require negative tests for semantic cross-field invariants, not only syntax: passed-step counts must match numbered steps, recovery evidence must be present when verification is true, final side-effect status must remain false, and safety checklist/status claims must agree.
- Distinguish Hermes profile isolation from browser/session isolation. A profile scopes Hermes state, not filesystem or website permissions. Browser isolation is backend-specific: managed Camofox persistence can be profile-scoped, while CDP attachments and externally managed browser identities may be shared. Never describe a profile as a general browser sandbox.
- For direct HTTP(S) skill installs, inspect the actual installer/source implementation to learn how referenced support files are discovered. Verify that every `references/`, `templates/`, `scripts/`, or `assets/` path is expressed in a recognized reference form, that the raw URLs return the files anonymously, and that the documented command works from the installed package root.
- Capture the exact review target at the start and end (`git status`, index/worktree diff, and SHA). If the tree changes during a read-only review, report the drift and review the final exact SHA rather than silently treating the original target as unchanged.

## Dev-only npm advisory release disposition
- First separate **runtime/production reachability** from **toolchain presence**. Confirm whether the affected package is in `dependencies` or only `devDependencies`, whether the lockfile marks every node as `dev`, whether `npm ls --omit=dev <package>` is empty, and whether the application source/bundle imports it.
- Run both audits when a lockfile and installed tree exist:
 - `npm audit --omit=dev --audit-level=high` answers the production-artifact question.
 - `npm audit --audit-level=high` answers the complete workspace/toolchain question.
- Treat stale `node_modules` and the lockfile as separate evidence. A lockfile-only pass does not prove a clean install, and a local installed-tree failure may reflect an unrefreshed tree. Capture both `npm audit --package-lock-only` and a clean-install verification (`npm ci` in isolated CI, then ordinary `npm audit`).
- When a patched transitive release exists but upstream packages pin older exact versions, prefer a narrowly scoped root override over `npm audit fix --force` if the override preserves the public APIs used by the consumers. Do not declare it release-safe until the clean install, full tests, build, and validation pass with the override.
- Reject audit-generated major downgrades as an automatic fix. Inspect the proposed versions and dependency graph; a downgrade can remove the advisory while regressing the toolchain or changing behavior.
- For a high-severity decompression/resource-exhaustion advisory, document both the actual local attack path (which tools process untrusted archives) and the production posture. “Dev-only” is a release disposition, not proof that developer machines are safe.
- Preserve exact candidate identity and report concurrent working-tree drift. A lockfile override present only in an uncommitted worktree is not a fix in the reviewed commit.

## Electron packaging and release-readiness reviews

When reviewing an Electron packaging/release commit, use this checklist:

- Freeze and re-check the exact commit. If a concurrent writer changes the worktree, report the drift and keep the verdict anchored to the requested SHA.
- In strict read-only mode, do not install, build, generate artifacts, or edit. Run only non-mutating source tests and clearly separate tests present, tests executed, and packaging verification that remains unexecuted.
- Check `package.json`, `package-lock.json`, and `electron-builder.yml` together. A shipped Electron runtime can be declared under `devDependencies` while still requiring inclusion in license/SBOM scope.
- Treat generated icons, entitlements, license files, and SBOMs as explicit packaging inputs. Verify every supported OS produces every required input; warning-and-continue generation is not a release gate.
- Require packaged smoke tests to fail closed when artifacts are absent, to clean the full process tree on timeout/failure, and to clean temporary user data on every exit path. Electron `app.exit()` skips `before-quit` and `will-quit`, so cleanup registered only there is insufficient.
- Reject source-substring/regex tests as proof of runtime behavior. Require behavioral checks for generated artifact contents, package identity, SBOM scope, license completeness, and platform targets.
- Reconcile macOS hardened runtime, entitlements, signing, and notarization configuration with the actual CI secret path. Separate Actions artifacts from published releases in documentation.

## Read-only desktop controller candidate reviews

For a Windows tray/controller candidate reviewed without build/test/install side effects, inspect the dirty worktree as the exact candidate, including untracked files, and treat structural verification separately from runtime verification. Use this sequence:

1. Capture `HEAD`, status, changed/staged/untracked paths, and `git diff --check` at the start and end; report any drift.
2. Read the production entrypoint, UI context, command/state layer, disposal path, lifecycle runner boundary, manifest, and test project together. Do not rely on `git diff` alone because untracked candidate files are omitted.
3. Trace every UI event to its first asynchronous boundary. An `async` method is not sufficient: if an operation is invoked before the first incomplete `await`, network/process work can still begin on the WinForms UI thread.
4. Model polling and lifecycle actions as competing writers. Check whether polling skips pending hosts or uses per-host generations/serialization; otherwise a stale classification can overwrite a newer action result.
5. Audit disposal in three layers: controller task tracking/awaiting, queued UI callbacks (generation/disposed checks inside the callback), and owned `IDisposable` resources created by the composition root. Unsubscribing an event does not cancel already-posted callbacks.
6. Verify pending-state UX at every command surface, not only a status window. Tray menu actions and bulk actions need explicit pending references and updates; backend rejection alone does not satisfy a UI-disable contract.
7. For diagnostics/privacy, inspect the final serialization sink. Sanitizing arbitrary strings is not a fixed allowlist. Test untrusted values in display names and error/code fields, not only in obviously omitted URL/path/token fields.
8. If runtime tests are prohibited, label tests as not executed and report only static/structural conclusions. Do not infer Windows visual behavior from a cross-platform test project or from stale build artifacts.

Typical blocking evidence patterns:
- `Publish()` checks `IsDisposed` and then invokes outside the same synchronization boundary.
- A tray callback posts to a UI context but checks only an exit flag, while disposal can occur through another path.
- `DisposeAsync()` awaits polling but not fire-and-forget action/restart tasks.
- A public `PollOnceAsync()` can run concurrently with the internally started polling loop.
- A diagnostics string includes config-derived names/codes without explicit safe-value mapping.

## Pitfalls
- Do not over-index on XSS if the bigger problem is trust-boundary collapse.
- Do not present dev dependency CVEs as equivalent to a live remote exploit path; label them accurately.
- Do not call CORS "authentication".
- Do not stop at package audit output; connect findings to actual code paths.
- In App Store reviews, do not promote plausible risks into universal requirements. Privacy manifests, local-network purpose strings, certificate pinning, Now Playing metadata, and export-compliance keys each depend on the final APIs, data flow, threat model, and current Apple policy.
- Separate **confirmed defect**, **verification gap**, **commercial blocker**, and **product opportunity** so recommendations are not misreported as rejection risks.
- When types that represent authentication scopes or resource access (`CredentialKind`, `PermissionScope`, `Role`) appear on both sides of a trust boundary, verify they define exactly the same set of values. A drift that omits a kind from the renderer side means the renderer can never request that kind — confusing but not a vulnerability. A drift that includes extra kinds on the renderer side means the renderer can request access that the backend does not recognize as valid — silent auth bypass.

## Support files
- `references/privacy-safe-support-reports.md` — exact allowlisted diagnostic schemas, code-only recording, payload-free privileged IPC, atomic export, consent/disclosure rules, adversarial tests, and bounded reviewer recovery.
- `references/hermes-office-review.md` — example review notes for an Office add-in that proxies to a full Hermes agent.
- `references/profile-bound-ai-desktop-review.md` — legacy IPC authority, canonical AI-profile binding, provenance persistence, secure-storage edge cases, and deletion-derived state.

## Public support files

- `references/hermes-office-review.md`
- `references/privacy-safe-support-reports.md`
- `references/profile-bound-ai-desktop-review.md`
