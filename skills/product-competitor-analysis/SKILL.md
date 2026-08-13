---
name: product-competitor-analysis
description: product-competitor-analysis — Conduct codebase-grounded competitive assessments for iOS/macOS apps by inventorying implemented behavior, mapping user needs, extracting differentiators, identifying blockers, and producing a positioning summary with line-grounded evidence.
version: 1.0.0
author: Nous Research
license: MIT
platforms:
- macOS
- iOS
metadata:
 category: software-development
 tags:
 - competitive-analysis
 - product-readiness
 - architecture-review
 - localization
 - security
 related_skills:
 - source-verification
 - specification-compliance-review
 - hermes-self-evaluation
---
# Product Competitor Analysis

## What this skill covers
Use this skill when asked to compare a local app/product to mainstream alternatives from local evidence only (or with explicit permission to use external research). It is intentionally structured for **code-first competitive assessments** where output should cite files, line ranges, and concrete implementation details.

## Core principle
Every claim in the final analysis must be traceable to one of:
- concrete local code artifacts (files + line ranges)
- local config/docs
- command output that is itself grounded in local files

## Category separation: native integration versus standalone replacement
When comparing an in-host integration to a standalone AI application, classify the products before scoring features. Do not treat “AI edits Office files” as the category; distinguish:

- **Standalone replacement:** owns its document, spreadsheet, or presentation engine; typically wins on convenience, breadth, cross-platform independence, and zero host-app requirements.
- **Native integration:** operates against the live host application's object model; can win on active-document context, fidelity to existing business files, in-place workflows, and verified host mutations, but carries more installation and compatibility complexity.

State the customer segment explicitly. A native integration is not universally superior: it is materially stronger for customers already dependent on the host application and its existing templates, while a standalone replacement may be better for users seeking an Office alternative. Avoid declaring a moat from architecture alone; translate the difference into an observable before/after workflow and identify the host-acceptance, onboarding, and reliability gates required to make the advantage real.

For this comparison pattern, apply the comparison framework in this skill.

## Preflight
Before analysis:
1. Confirm target slice and language scope (e.g., iOS, macOS, CLI).
2. Confirm whether external validation is allowed.
 - If user says “no web research” (or equivalent), perform **conceptual only** comparisons against mainstream categories.
3. Capture project shape first (top-level files, app layers, active targets).
4. Identify authoritative README(s), architecture notes, and build metadata.

## Required evidence buckets
Collect evidence in these buckets and keep each bucket grounded:

- **Feature inventory**
 - UI controls and state toggles
 - Runtime states/lifecycle
 - Input/output pipelines
 - Persisted settings and storage

- **User/jobs-to-features mapping**
 - Map likely jobs-to-be-done to concrete paths and controls
 - Separate “implemented in code today” vs “present in docs only”

- **Differentiators**
 - What the app does materially differently from baseline competitors
 - Include provider architecture, route controls, feedback loops, anti-echo handling, etc.

- **Missing table-stakes**
 - Compare against mainstream competitor categories to identify must-haves absent here

- **Security / distribution blockers**
 - Secrets handling, key material pathways, packaging risks
 - Permissions and entitlement impacts
 - Store/review/readiness gaps

- **UX/reliability risks**
 - failure states visible to users
 - onboarding and setup friction
 - session lifecycle interruptions

- **Positioning**
 - A concise 1–2 sentence positioning for store/market fit

## Evidence format
For every major claim, include:
- `file path` + `line range`
- short phrase describing what is observed
- confidence level (`implemented`, `partial`, `docs-only`, `inferred`)

## Standard execution flow

### 1) Discover layout and project shape
Use local discovery only:
- app entrypoint(s)
- domain folders (App/Providers/Audio/Resources)
- runtime entry config (`project.yml`, `.xcscheme`, `Info.plist`)

### 2) Inventory implementation
Extract the following types first:
- status/state enums
- provider protocol + implementations
- session manager/view model
- audio capture and routing layer
- key settings/state persistence mechanisms

### 3) Produce analysis sections in fixed order
Use this section order in final response:
1. **Feature inventory**
2. **Target users + use cases**
3. **Differentiators**
4. **Missing table-stakes features**
5. **Security/distribution blockers**
6. **UX risks**
7. **Overall positioning**
8. **Confidence/risk callouts**

### 4) Keep comparisons constrained when requested
If user says no web research:
- do conceptual benchmarking only
- avoid naming external products as facts unless user supplied
- do not cite ungrounded feature claims

### 5) Close with concise verdict
End with a short, non-hedged “where this ships well today” vs “what must ship before broad consumer release”.

## Strong constraints
- Do not assert unsupported metrics (latency, MAU, retention) without evidence from test artifacts.
- Avoid inventing competitor feature details from memory.
- Keep line-citation references consistent across the report.
- If a required evidence bucket is empty, call that explicitly and avoid padding.

## Pitfalls
- Comparing platform-specific behavior to unrelated desktop behavior without separating targets.
- Mixing `docs` and `runtime` evidence as equivalent.
- Forgetting direct dependency on permissions (microphone, audio routes, background modes).
- Ignoring production security posture and focusing only on functional parity.

## Deliverable template

### Feature inventory
- [feature] – [evidence]

### Use cases
- [persona/use case] – [mapped controls/settings]

### Differentiators
- [claim] – [mechanism / path]

### Missing table-stakes
- [feature gap] – [impact + priority]

### Security & distribution
- [risk] – [where implemented or missing]

### UX risks
- [risk] – [user-facing consequence]

### Positioning
- [1–3 sentence positioning + likely store category]

## Reuse assets
- : compact checklist + session examples for quick copy-paste.

## Validation checklist
- [ ] At least 5 evidence citations across at least 2 feature domains
- [ ] At least one distribution/security block identified if credentials are user-provided in-app
- [ ] At least one clear non-negotiable blocker and one “nice-to-have but not blocking” item
- [ ] No uncited claim in final report
