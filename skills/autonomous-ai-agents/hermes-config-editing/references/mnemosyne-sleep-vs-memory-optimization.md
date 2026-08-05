# Mnemosyne Sleep vs Legacy Memory Optimization

Use this reference when a Hermes session involves memory provider behavior, Mnemosyne “dreaming,” or warnings about memory optimization cron.

## Key distinction

- **Legacy memory optimization cron**: manages the injected `MEMORY.md` / `USER.md` style memory files. If disabled, that only means the old file-management optimizer should not run.
- **Mnemosyne sleep/dreaming**: runs Mnemosyne consolidation, typically via `mnemosyne_sleep`, moving/summarizing working memories into longer-lived layers. This is a separate mechanism from legacy file optimization.

Do not conflate the two. A warning such as “memory optimization cron is disabled” is not evidence that Mnemosyne sleep should be avoided.

## Diagnostic pattern

1. Check active provider/status:
 - `hermes memory status`
 - Relevant config keys: `memory.provider`, `memory.memory_enabled`, `memory.user_profile_enabled`.
2. Check Mnemosyne state if tools are available:
 - stats/counts tell whether working/episodic stores are being populated.
 - `mnemosyne_sleep(dry_run=true)` proves whether consolidation would happen without mutating memory.
3. If dry-run reports items/summaries but last episodic consolidation is old, the likely issue is not capability; it is that no scheduler/cron/session hook is calling sleep.
4. If scheduling is requested, treat it as a Mnemosyne sleep job, not as re-enabling the legacy memory optimization cron.

## Communication guidance

Be precise:

- Good: “Mnemosyne can consolidate manually; no enabled scheduler appears to be calling `mnemosyne_sleep`.”
- Bad: “It is blocked because memory optimization cron is disabled.”

If the user corrects this distinction, update the skill immediately; it is a workflow pitfall for Hermes memory troubleshooting.
