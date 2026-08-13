# Profile-Bound AI Desktop Trust Review

Use this checklist for Electron/native desktop applications that generate lessons, workflows, or assessments through a profile-scoped local AI agent.

## Enumerate every authority route

- Inventory every preload/context-bridge method and every corresponding main-process handler.
- A new pending-only or main-derived path is not a fix if a legacy split endpoint still accepts completed state, scores, mastery, next actions, or other authoritative conclusions.
- Test route absence as well as validation on the preferred route.
- Review the full IPC envelope: unknown top-level/nested fields, byte limits, identifier syntax, canonical ownership, and immutable retry identity.

## Bind requests to server-side identity

- Derive required profile/policy from the main-process canonical catalog; never from renderer fields.
- Treat OpenAI-compatible request `model` fields as potentially cosmetic.
- For Hermes API Server, `GET /v1/models` advertises the active profile. Read it with bounded JSON helpers, authenticate from the vault, and require an exact profile match before requesting confidential content.
- Reject missing identity, mismatch, nonlocal endpoint, malformed metadata, and secret-bearing errors before content generation.
- Keep generic assistant/profile requests separate from course-bound requests so a strict course policy does not accidentally alter unrelated flows.

## Source validation and provenance

- A nonempty manifest is not traceability. Source-required packets need bounded `sourceId`, title, version, and section, or an explicitly approved immutable locator.
- Optional locators should reject filesystem/file URLs, embedded credentials, localhost/loopback, query strings/fragments carrying secrets, and control characters. Prefer HTTPS without credentials/query/fragment or a narrowly validated URN.
- Validate packet IDs with the same canonical identifier rules used by later persistence; otherwise a packet can teach successfully but fail at session save.
- Persist validated provenance with the session/outcome independently of an evictable lesson cache.
- Export nonsecret provenance only—not packet bodies, proprietary source text, prompts, credentials, or session-cache values.

## Credential storage edge cases

- Load and retain encrypted ciphertext even when OS secure storage is temporarily unavailable.
- Operations requiring encrypt/decrypt should fail closed, but an unavailable runtime must not replace the in-memory encrypted record set with `{}` and later overwrite unrelated keys.
- Add an unavailable→available test proving that saving one credential preserves all ciphertext loaded earlier.
- Enforce secret-key rejection at both IPC validation and persistence-layer setting APIs.

## Deletion and derived conclusions

- If deleting or expiring a session removes the evidence but leaves competency scores, review items, lesson completion, or revision state, the privacy control is semantically incomplete.
- Attribute derived rows to source sessions or transactionally rebuild all affected derived state from remaining outcomes.

## Verification

- Verify reviewer findings in live source; distinguish exploitable defects from defense-in-depth notes.
- Run focused tests plus the canonical build/smoke/audit gate.
- During dirty repair use `git diff <remote> --check`; after commit use `git diff --check <remote>...HEAD`.
- Inspect the complete diff for adjacent handler deletions after broad patches.
