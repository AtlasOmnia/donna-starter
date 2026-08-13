# Load-Bearing Assumption Spikes for Implementation Plans

Use this when reviewing a plan before implementation, especially when later tasks encode an external runtime/API behavior into schemas, tests, or multiple product ports.

## Identify load-bearing assumptions

Mark an assumption as load-bearing when failure would invalidate several downstream tasks, such as:

- a server actually runs a tool loop rather than merely accepting a request;
- a plugin is loaded into the API/runtime path being used;
- request metadata reaches a plugin handler;
- an opaque/session identifier is propagated exactly;
- an authenticated diagnostics or restart contract exists;
- a browser/Office host can persist the required identity across reopen;
- a production package can preserve a stable extension/add-in identity.

Documentation proving an endpoint exists is not proof of the required behavior. Plugin installation-path documentation is not proof that the running API process loads or executes that plugin.

## Convert assumptions into an early spike

Before implementation tests cement the contract:

1. Build the smallest inert probe (for example, a strict echo tool with no filesystem or app mutation).
2. Exercise the real runtime, provider/model, API endpoint, restart path, and stream format.
3. Capture exact request/response/event schemas and runtime version.
4. Run negative, cancellation, restart, parallel-session, and identifier-fidelity cases.
5. Commit a concise contract document with raw evidence paths/hashes.
6. Gate dependent tasks on the spike.

If the desired deterministic channel does not exist, stop and plan the missing platform/core capability. Do not quietly substitute model prompt copying for trusted request metadata.

## Threat-model discipline

A security finding is blocking only inside the stated threat model. Distinguish:

- remote peers and hostile web origins;
- stale/foreign local processes that must never be killed or adopted;
- code already running as the same OS user, which may already read user files and current-user secrets.

Do not claim to defend against hostile same-user malware with Origin headers, DPAPI-current-user storage, or a secret served to JavaScript. Also do not move a server-side secret into JavaScript merely to satisfy an authentication checkbox. State the boundary and design credentials appropriate to it: random per-session credentials for panes, separate server-side plugin keys, no session enumeration, and bounded registration.

## Review verdict

- `PASS`: load-bearing contracts are already proven and cited.
- `PASS WITH GAPS`: architecture is sound, but one or more cheap prerequisite spikes or threat-model clarifications must land before dependent work.
- `FAIL`: the plan requires a platform behavior known not to exist or has no safe replacement path.

For every gap, name the first downstream task that must be blocked and the smallest spike that resolves it.
