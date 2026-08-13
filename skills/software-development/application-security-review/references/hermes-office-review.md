# Hermes Office security review notes

Repository reviewed: tonbistudio/hermes-office

Why this example matters
- It is a clean example of an AI-enabled Office add-in whose real risk is trust boundaries, not classic frontend injection.
- The add-in sends workbook content to a Hermes backend and allows model output to propose workbook mutations.

Confirmed review pattern
1. Read README, manifest, proxy config, and client network helper first.
2. Confirm whether the backend is a restricted model endpoint or a full agent.
3. Trace workbook/document content into prompts.
4. Trace model output into mutations.
5. Audit proxy/origin rules and dependency versions.

Concrete findings captured from this review

1. High — prompt injection path from workbook data into a full-power agent
- Evidence:
  - excel/src/taskpane/taskpane.js serializes active-sheet data into the prompt.
  - README explicitly states the backend is Hermes API Server exposing the full agent, not a model-only proxy.
- Lesson:
  - Treat workbook data as untrusted prompt input.
  - Do not connect this class of UI to a full tool-enabled agent without a restricted profile/toolset.

2. High — localhost proxy converts local reachability into authenticated backend access
- Evidence:
  - Caddyfile.example injects Authorization for requests proxied from localhost:8643 to localhost:8642.
- Lesson:
  - CORS is not authentication.
  - Local-only binding reduces exposure but any local caller that can reach the proxy inherits agent access unless extra checks exist.

3. Medium — weak validation on model-generated actions before apply
- Evidence:
  - taskpane.js parses JSON actions from model output and executes them with limited schema/bounds validation.
  - Preview does not fully verify all writes.
- Lesson:
  - Require strict action schema validation, range caps, and before/after verification for mutation flows.

4. Medium — sensitive workbook data may leave the machine depending on backend model routing
- Evidence:
  - workbook data and custom-function inputs are sent to Hermes; whether they remain local depends on Hermes backend configuration.
- Lesson:
  - Flag data egress explicitly in the report and recommend local-only profiles for sensitive workbooks.

5. Medium — dev-toolchain vulnerabilities still matter, but label them correctly
- Evidence from npm audit:
  - request 2.88.2
  - webpack-dev-server 5.1.0
  - copy-webpack-plugin via serialize-javascript
- Lesson:
  - Separate runtime path risk from dev-only exposure; do not flatten them into the same severity story.

Good patterns seen
- UI rendering used textContent for displayed model/user text rather than innerHTML.
- Root .gitignore excluded Caddyfile, .env, and key material.

Recommended standard remediation language
- "Safe enough for local prototyping with low-trust data; not suitable as-is for sensitive business documents."
- "Restrict the backend profile/toolset before addressing polish issues."
