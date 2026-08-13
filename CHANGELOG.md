# Donna Starter — Changelog

Date format: `YYYY-MM-DD`. One section per run/campaign. Append newest at the top.
Each run records what happened and the verification evidence tied to its exact
commit range, so we always know the state we resume from.

---

## 2026-08-13 — Remove autoresearch-loop skill (category cleanup)

**Driver / controller:** FRIDAY (default profile) — public repo reorganization
**Branch:** `main`
**Change:** Removed `skills/autonomous-ai-agents/hermes-autoresearch-loops/`. The
autoresearch harness is an autonomous loop project, not an installable skill; it
lives solely in `AtlasOmnia/hermes-autoresearch`. README skill count 73 → 72.
**Status:** ACTIVE (public starter profile repo).

---

## 2026-08-05 — Current state (CHANGELOG established)

**Driver / controller:** FRIDAY (default profile) — convention seed
**Branch:** `main`
**Head SHA:** `e7c41c5eec88d9a4ba6081d261bea5009af7c6fd`
**Status:** ACTIVE (public starter profile repo). Tree clean.
**Most recent commit:** `e7c41c5 Persona: first-contact orientation offer; README trigger wording`
**Next-run resume point:** verify exact checkout/branch/HEAD/clean tree and single
writer before any edit. This file was seeded for the changelog convention; the
current-state entry above reflects HEAD at seed time.

---

<!-- Template for future entries — duplicate the YYYY-MM-DD block above when a
new run starts, and keep it at the top of the section history. -->
