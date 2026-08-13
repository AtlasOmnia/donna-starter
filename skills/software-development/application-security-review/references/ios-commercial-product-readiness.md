# Native iOS Commercial Product-Readiness Review

Use this reference when reviewing a SwiftUI/AVFoundation app intended for paid App Store distribution, especially realtime voice or AI products.

## Review scope

A successful review must cover more than compile health or AppSec. Inspect four layers together:

1. **Runtime engineering** — architecture, concurrency, audio/network lifecycle, reconnect behavior, performance, battery, and tests.
2. **Trust and privacy** — credentials, broker design, cloud data flow, retention, consent, telemetry, and sensitive logs.
3. **App Store readiness** — StoreKit, entitlements, privacy disclosures, purpose strings, background modes, localization, accessibility, support/legal metadata, and reviewer instructions.
4. **Commercial product fit** — onboarding, customer-facing complexity, monetization, unit economics, positioning, retention loops, and differentiation.

## Proven workflow

1. Read repository guidance (`AGENTS.md`/README), project manifest, `Info.plist`, and app entry points.
2. Enumerate Swift sources, test targets, StoreKit references, privacy manifests, localization resources, and background capabilities.
3. Trace microphone audio and transcript data from capture through every provider or broker.
4. Identify whether long-lived provider credentials are customer-entered, bundled, Keychain-stored, or exchanged for short-lived broker credentials.
5. Inspect the retail UI for developer-facing controls: API keys, model names, provider pickers, broker URLs, raw VAD/audio settings.
6. Verify with a generic unsigned device build. If Command Line Tools is selected, use the repository-safe per-command override rather than changing global `xcode-select`:

```bash
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
  xcodebuild -project App.xcodeproj \
  -scheme App \
  -destination 'generic/platform=iOS' \
  CODE_SIGNING_ALLOWED=NO \
  build
```

7. Check for test targets and real-device acceptance requirements. Simulator/build success does not validate Bluetooth routes, interruptions, lock-screen behavior, weak networks, or sustained realtime sessions.
8. Treat successful-build warnings as release work rather than noise. For orientation warnings, either support landscape—often valuable for tabletop captions—or explicitly require full-screen portrait mode with a documented product rationale.
9. Write a durable Markdown report in the repository root with P0/P1/P2 priorities, exact `file:line` evidence, effort/impact, good-news controls, release phases, and go/no-go criteria.
10. Verify the report by reading it back and checking `git status`; do not imply source was untouched if the report itself is a new repository file.

## High-value findings for realtime voice products

### Credential and broker posture

- Keychain is appropriate for development/BYOK storage but does not make long-lived cloud keys suitable for a retail product.
- Production apps should normally use an authenticated broker issuing short-lived, capability-limited session credentials.
- Keep provider selection, model versions, quotas, failover, rate limits, replay protection, and spend ceilings server-side.
- Hide provider/model/key/broker controls from retail users; preserve them only in internal/debug builds when useful.

### Monetization and cost control

- Search explicitly for StoreKit 2, product configuration, purchase/restore flows, grace periods, server validation, and quota enforcement.
- For metered voice inference, avoid claiming unlimited use before measuring cost per active minute.
- Entitlements and quotas must be enforced server-side before the broker issues session access.
- A StoreKit transaction ID alone is not entitlement proof; send signed StoreKit JWS/App Store server-verifiable evidence to the broker.
- Do not model free usage as an invented zero-price IAP. Enforce free minutes/quotas server-side and reserve StoreKit products for genuine paid offerings.
- Product IDs, production endpoints, legal URLs, credentials, and signing assets must come from real configuration; never invent values that appear deployable.

### Multi-model implementation gates

DeepSeek Flash is effective for Swift implementation and broad source review, but may overstate Apple/compliance requirements. When using it as an economical implementation workforce:

1. Controller defines architecture and exact task specification.
2. Implementer follows RED → GREEN → REFACTOR and does not commit/push.
3. Independent spec reviewer inspects actual diffs, not the implementer summary.
4. Fix all spec gaps before code-quality review.
5. Controller independently runs XCTest and unsigned device builds; tool output is authoritative.
6. Reject claims of secure Swift `String` zeroization—copy-on-write/immutable backing prevents that guarantee. Minimize credential lifetime and never persist or log secrets instead.

### XcodeGen synchronization

When `project.yml` and a checked-in `.xcodeproj` coexist, changing only `project.pbxproj` is incomplete: regeneration can erase targets/settings. Update the manifest source of truth, regenerate the project, verify the shared scheme, run XCTest and generic unsigned build, then inspect regeneration churn.

When adding characterization tests, test semantic invariants directly. For ordered enums such as low/medium/high sensitivity, compare the named cases (`low > medium > high`); never sort values before asserting order, because that turns the test into a tautology. Test names must describe what the assertion can actually fail on—a threshold assertion is not proof that the ViewModel uses that case as its default.

### Privacy and consent

- Document where live audio and transcripts go, what providers process them, retention behavior, and whether history is persisted.
- Require first-run disclosure and an obvious active-listening indicator for two-person conversation use.
- Check Privacy Policy, Terms/EULA, support, deletion/contact path, App Store privacy labels, and whether `PrivacyInfo.xcprivacy` is required by final APIs/SDKs.
- Do not treat the absence of a privacy manifest as automatically fatal; tie the conclusion to actual required-reason APIs and included SDKs.
- Do not infer required-reason API usage from ordinary `Date()` calls or AVAudioEngine alone; inspect the actual API categories Apple lists.
- Certificate pinning is defense-in-depth, not a universal App Store requirement. Prioritize short-lived broker credentials and standard TLS first unless the threat model justifies pinning and its rotation/availability cost.
- Do not add `NSLocalNetworkUsageDescription` solely because the app uses remote WebSockets. Verify whether the final implementation actually performs covered local-network discovery/access.
- Treat export-compliance and background-audio metadata as current-policy decisions to verify, not plist keys to add mechanically.

### Reliability

- Look for bounded reconnect/backoff, `NWPathMonitor`, actionable error categories, retry controls, session-state preservation, and quota/auth expiry behavior.
- Provider protocols built from untyped dictionaries and string event names need fixture-based encoding/decoding tests because contract drift will compile cleanly.
- Preview model identifiers should not be hardcoded as permanent retail defaults; pin supported production models server-side.

### Realtime audio performance

- Flag allocations, locks, `Date` creation, per-sample Swift loops, UI callbacks, or unbounded task creation on audio callbacks.
- Flag semaphore-wrapped WebSocket send/receive operations on serial speech queues. Finite 10–30 second timeouts prevent an infinite hang but can still freeze every later phrase behind a stalled request; prefer cancellable structured concurrency, bounded send/first-audio timeouts, and generation/session IDs that reject late frames after stop or interruption.
- Backpressure must preserve user meaning. If one TTS request is active, keep or coalesce one latest-pending phrase and run it next; do not silently drop new speech under the false assumption that an already-started request contains it.
- Prefer a narrow provider-specific injectable transport seam for deterministic tests. Do not create a generic WebSocket framework unless multiple providers genuinely need it.
- Retain the worker `Task` handle when stop/interruption must cancel work. Cancelling only the socket is insufficient if an untracked worker can continue, race a new generation, or mutate worker-claimed state after restart. Review `stop → enqueue` races explicitly: a stopped generation must not release or overwrite the ownership state of a newer worker.
- Make async tests deterministic with injected clocks, continuations, or explicit readiness signals. Arbitrary `Task.sleep` delays can pass locally while masking scheduling races; green sleep-based tests are not proof of one-active-worker or cancellation invariants.
- Timeout helpers must cancel and await the losing operation cleanly. Verify that cancellation reaches the underlying WebSocket receive/send rather than merely returning a timeout while the transport continues in the background.
- Prefer reusable buffers/ring buffers and platform conversion primitives (`AVAudioConverter`, Accelerate) after profiling.
- Verify queue backpressure so slow networks do not create memory growth or increasing latency.
- Require Instruments measurements for energy, thermal state, dropped frames, queue depth, RTT, and end-to-end translation latency.

### Background audio

- If `UIBackgroundModes` includes audio, verify the product intentionally supports lock-screen/background operation, visible mic state, Now Playing/stop controls, lifecycle handling, and abandoned-session cost safeguards.
- If background translation is not a product requirement, stop cleanly and remove the entitlement/capability.

### Consumer product UX

- Developer controls are not onboarding. Translate technical modes into customer jobs such as Practice, Understand Someone, or Speak to Someone.
- Keep the live screen centered on Start/Stop, direction, captions, connection status, output destination, and remaining usage.
- Realtime translation products should consider full-screen captions, replay, slower playback, correction, source/translation turn pairing, and privacy-preserving history controls.
- A Spanish-English product should normally launch with both English and Spanish interface localization, plus VoiceOver, Dynamic Type, contrast, and landscape/tabletop testing.

## Reporting distinctions

Label every item as one of:

- **Confirmed code/config finding** — supported by exact paths and lines.
- **Verification gap** — cannot be proven by source/build alone; requires device, provider, or App Store testing.
- **Commercial opportunity** — recommendation, not a defect.

A clean build is good news, not evidence of product readiness.