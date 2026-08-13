# Cross-Repository Contract Reconciliation

Use this when one component consumes another repository’s health, identity, lifecycle, authentication, or packaging contract. A locally green implementation can still be guaranteed to fail when producer and consumer encode different schemas.

## Core rule

Treat the producer’s accepted runtime contract—not the consumer’s test fixture—as authoritative. Before accepting either side, write one shared contract matrix:

| Surface | Producer emits/accepts | Consumer expects/sends | Exactness | Runtime proof |
|---|---|---|---|---|
| Public health | exact fields/types | exact parser mode | ordinal / bounded | producer endpoint + consumer fixture |
| Auth diagnostics | auth mechanism + allowlist | token/key acquisition | fail closed | unauthenticated and authenticated probes |
| Service identity | service/protocol/host semantics | expected values | no aliases | wrong-service adversarial test |
| Lifecycle state | no-listener/healthy/connected/conflict | classifier mapping | unknown owner never idle | occupied-port fixture |
| Ownership | absolute entry/root/lock markers | process parser | semantic + process proof | real command-line fixtures |

## Review sequence

1. Freeze and name both candidate SHAs or working-tree fingerprints.
2. Read the producer’s actual endpoint/CLI/script implementation and accepted tests.
3. Read the consumer parser/classifier and every fixture that represents the producer.
4. Diff field-by-field: names, required/forbidden fields, types, casing, paths, ports, auth, bounds, and failure semantics.
5. Add a consumer test using the producer’s **minimal exact real payload**, not a hand-expanded convenience fixture.
6. Add producer tests for the public allowlist and forbidden fields. Extra fields can be a privacy defect even when the consumer ignores them.
7. Run adversarial variants: missing field, wrong case, wrong service/protocol/port/path, malformed body, timeout, unknown occupied listener, and unauthenticated diagnostics.
8. Run both repositories’ focused and canonical gates at their recorded fingerprints. Do not combine evidence from different snapshots.
9. Accept only when the matrix is closed and the integration payload passes end to end; otherwise report HOLD with the exact mismatch.

## Tests must reach production decisions

A helper exported only for tests is not proof of executable behavior. For script-heavy integrations:

- Have scripts call one bounded production decision CLI/module, then execute that same CLI/module with fixtures.
- Static-link tests should prove the script invokes the shared decision surface.
- Keep OS-only mutation in the OS script, but share parsing/classification/ownership decisions where feasible.
- Test temporary real locks/processes for concurrency and stale-lock decisions; string-presence assertions are supplementary only.
- If the OS runtime is unavailable, label native execution unverified. Do not call static checks a Windows PASS.

## Health-contract pitfall

Do not reuse an Office-style parser for a Chrome-style endpoint merely because both are called `/health`. For example, a producer contract such as:

```json
{"status":"ok","service":"hermes-chrome-gateway","protocolVersion":"1.0","uptimeMs":123}
```

must not be tested with invented `ok: true` or `host` fields. Prefer an explicit endpoint-specific parser over a generic parser with many nullable flags; generic optionality tends to weaken unrelated identities.

## Process and commit disposition

A background process exiting `0` means only that it ended. Independently inspect its complete report, live Git state, exact scope, staging, parent, author/committer, tests, privacy, locks, listeners, and clean-tree evidence. If the agent reports HOLD or leaves no commit, preserve the bounded dirty candidate and start a narrow single-writer repair; never promote wrapper success to acceptance.

## Final verdict language

- **PASS:** producer and consumer contracts match, connected tests and repository gates pass, immutable fingerprints reconcile.
- **PASS WITH NATIVE GAP:** source contracts and cross-platform tests pass, but explicitly required OS execution remains unverified.
- **HOLD:** any exact contract mismatch, dead test helper, unsafe unknown-owner state, unauthenticated diagnostic path, missing commit boundary, or dirty/unreconciled tree remains.
