# Profile-Safe Manual Consolidation

Use this when manually consolidating a named Hermes profile or when a delegated profile must operate on another profile's Mnemosyne store.

## Core invariant

Mnemosyne memory banks are profile-scoped. Running `mnemosyne_sleep` inside a named profile operates on that profile's bank, not the default profile's bank. A successful `no_op` with zero counts can therefore mean **wrong profile/store**, not “nothing needs consolidation.”

## Procedure

1. **Resolve the target profile first.** Confirm its `memory.provider` and Hermes home:
 - Default: `~/.hermes`
 - Named profile: `~/.hermes/profiles/<name>`
2. **Capture before-stats from the target store.** Record working total, consolidated, unconsolidated, episodic total/last, and vector count.
3. **Sanity-check scale.** If expected counts are large but the command reports zeros/null timestamps, stop: the wrong profile, bank, or database is selected.
4. **Run one consolidation only.** Use the target profile's supported CLI/tool path with `--all-sessions`; do not run a dry-run concurrently because both may contend for the same SQLite/store resources.
5. **Expect long runtime.** Large stores can remain CPU-active for tens of minutes. A parent `hermes chat` or terminal timeout does not prove failure; inspect the child process and target stats before terminating it.
6. **Monitor progress without restarting.** Healthy evidence includes increasing `consolidated`, episodic, and vector counts plus decreasing `unconsolidated`. Use a background completion monitor when the operation will outlive the interactive turn.
7. **Verify after completion from the same target bank.** Record exact start/end timestamps, result status, sessions/items consolidated, summaries created, errors, and before/after counts.

## Direct API fallback

When the CLI/profile wrapper cannot target the desired store, a delegated engineering profile may use Mnemosyne's Python API with an explicit target database and bank. Keep this scoped to the child process; do not alter live configuration.

Conceptual pattern:

```python
from pathlib import Path
from mnemosyne.core.memory import Mnemosyne

path = Path.home() / ".hermes/mnemosyne/data/mnemosyne.db"
mem = Mnemosyne(
 session_id="manual_default_consolidation",
 db_path=path,
 bank="default",
)
before = mem.get_stats()
result = mem.sleep_all_sessions(dry_run=False, force=False)
after = mem.get_stats()
```

API signatures may change; inspect the installed package or CLI help before execution rather than assuming arguments.

## Reporting rules

- Distinguish **triggered**, **actively progressing**, and **completed**.
- A log line saying “running consolidation” proves only an attempt started.
- Do not report completion until the process exits and after-stats/result are read back.
- If a delegated profile first hits its own empty bank, state that clearly and retarget the intended store; do not present the zero-count no-op as the requested result.
