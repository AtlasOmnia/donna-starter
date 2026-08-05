# Long-Goal Handoff and Public-Prep Acceptance

Use this when a long `/goal` campaign is preparing a public Hermes plugin or cross-platform desktop bridge.

## Safe handoff

1. Save the full specification to an absolute Markdown path, for example:
 `/Users/<user>/Desktop/project-public-prep-goal.md`
2. Start the goal with a short prompt:
 `Read and execute the complete specification at <absolute-path>. Treat that file as authoritative. Do not treat truncated display text as the task.`
3. Never copy a UI representation such as `[[ Prepare the curr.. [77 lines] .. ]]` into a worker prompt. That is a display/reference form, not reliable task content.
4. If the worker loads an unrelated skill or searches for a shortened note title, stop. The handoff is malformed; relaunch from the file.

## Independent acceptance

After the worker exits:

- Verify the exact checkout, branch, HEAD, dirty set, untracked files, and active writers.
- Treat exit code 0 and a worker summary as process evidence only, not release evidence.
- Re-run compile/tests and the decisive package gates independently.
- Run package commands from the directory containing the relevant manifest and record that working directory.
- Run `git diff --check` and a current tracked/public-tree privacy scan.
- Inspect manifests against runtime registration. For a hook registered in Python, confirm the manifest declares the matching `provides_hooks` entry.
- Check app/package identifiers, URLs, absolute paths, profile names, organization names, caches, and generated artifacts.
- Report each OS separately. Unavailable Windows evidence is `PENDING`, never `PASS`.
- Do not push, publish, sign, notarize, restart a gateway, or delete private source artifacts without the corresponding authorization.

## Completion language

Use three separate labels:

- **Code/test status:** what actually passed locally.
- **Public-readiness status:** whether privacy, packaging, manifest, and documentation gates pass.
- **Platform status:** Mac and Windows evidence separately.

A project can have green Mac tests and still be not ready for public repository review.
