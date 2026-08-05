---
name: mnemosyne-maintenance
description: mnemosyne-maintenance — Upgrade, troubleshoot, and maintain Mnemosyne memory provider — version mismatches, slow/hung consolidation, missing embeddings, import shadowing.
version: 1.0
tags:
- hermes
- mnemosyne
- maintenance
- troubleshooting
---
# Mnemosyne Maintenance

Use when: upgrading Mnemosyne, diagnosing slow/hung consolidation (mnemosyne_sleep), fixing missing embeddings, or troubleshooting import/version mismatches.

## Triggers

- mnemosyne_sleep hanging for >2 minutes
- Diagnose reports "fastembed not available" or "sqlite_vec not available" despite being installed
- Version mismatch: pip shows newer version than runtime
- Embeddings_available=NO when deps are present

## Core troubleshooting (in order)

1. Run diagnostics:
 - mnemosyne_diagnose
 - Look for: missing fastembed, sqlite_vec, ctransformers; embeddings_available status; mnemosyne_version

2. Check for local dev shadowing:
 - A local ~/mnemosyne directory will shadow the pip-installed package because Python adds ~ to sys.path on macOS.
 - Confirm with:
 python -c "import mnemosyne, inspect; print(mnemosyne.__file__)"
 If it prints ~/mnemosyne/..., that's the problem.

3. Fix shadowing (if present):
 - Rename or move local dev copy:
 mv ~/mnemosyne ~/mnemosyne-local
 - Ensure PYTHONPATH prioritizes site-packages in gateway plist:
 plutil -replace "EnvironmentVariables.PYTHONPATH" -string "~/.hermes/hermes-agent/venv/lib/python3.11/site-packages" ~/Library/LaunchAgents/ai.hermes.gateway.plist
 - Restart gateway:
 launchctl stop ai.hermes.gateway && launchctl start ai.hermes.gateway

4. Remove stale plugin symlinks:
 - Old setups may have:
 ~/.hermes/plugins/mnemosyne -> ~/mnemosyne/hermes_memory_provider
 Modern Mnemosyne (3.8+) includes Hermes integration in the package; this symlink is unnecessary and can break imports.
 - If present, remove it:
 rm ~/.hermes/plugins/mnemosyne

5. Upgrade Mnemosyne + deps:
 - From venv:
 pip install --upgrade "mnemosyne-memory[embeddings]" sqlite-vec
 - If version mismatch persists (pip shows new, runtime still old):
 - Uninstall and reinstall cleanly:
 pip uninstall -y mnemosyne-memory && pip install --upgrade "mnemosyne-memory[embeddings]" sqlite-vec

6. Restart gateway after changes:
 - launchctl stop ai.hermes.gateway && launchctl start ai.hermes.gateway

7. Verify:
 - Run:
 python -c "import mnemosyne; print(mnemosyne.__version__, mnemosyne.__file__)"
 Confirm it loads from site-packages and shows expected version.
 - Run mnemosyne_diagnose again.
 - Test consolidation:
 mnemosyne_sleep (dry_run=true)

## Embeddings

- If episodic_vectors=0, future operations will be slow on large DBs.
- Enabling embeddings requires:
 - MNEMOSYNE_VEC_TYPE set to "fastembed" in .env (not just sqlite_vec)
 - sqlite-vec and fastembed installed
 - A migration pass to vectorize existing memories

### Enable embeddings (step-by-step)

1. Add env var (use Python to avoid overwriting):
 - python -c "
 import os
 path = os.path.expanduser('~/.hermes/.env')
 with open(path, 'a') as f:
 f.write('MNEMOSYNE_VEC_TYPE=fastembed\n')
 "

2. Restart gateway:
 - launchctl stop ai.hermes.gateway && launchctl start ai.hermes.gateway

3. Run auto-fix diagnostics (ensures deps and vec indexes are healthy):
 - ~/.hermes/hermes-agent/venv/bin/mnemosyne diagnose --fix

4. Plan reindex (dry run first):
 - ~/.hermes/hermes-agent/venv/bin/mnemosyne reindex --dry-run
 Confirms model, dimensions, and memory counts before writing.

5. Execute reindex to vectorize existing memories:
 - ~/.hermes/hermes-agent/venv/bin/mnemosyne reindex --yes
 This can take several minutes on large DBs; it is safe and non-blocking for Hermes runtime.

6. Verify:
 - mnemosyne_diagnose → embeddings_available=OK, episodic_vectors > 0

## Pitfalls

- Never trust pip show alone; always verify with import mnemosyne + __file__.
- Do not leave a local ~/mnemosyne directory in place if you intend to use the pip-installed version.
- After any Mnemosyne change, restart the gateway — Hermes caches imports at startup.
- mnemosyne_diagnose can lie about versions and deps when a local dev copy shadows site-packages (it reads from whatever import mnemosyne resolves to). Always confirm with:
 python -c "import mnemosyne; print(mnemosyne.__version__, mnemosyne.__file__)"
 If it prints ~/mnemosyne/... instead of site-packages, your diagnosis is using the wrong package.
- On large DBs (40K+ working memories) without embeddings, mnemosyne_sleep can hang for 30+ minutes doing brute-force FTS + LLM passes. Treat this as a hard signal to enable embeddings, not just "wait longer."
- The mnemosyne reindex command may default to ~/.mnemosyne/data/ instead of ~/.hermes/mnemosyne/data/, causing backup or DB-not-found errors. Fix by:
 - Setting MNEMOSYNE_DATA_DIR=~/.hermes/mnemosyne, or
 - Using --no-backup if you're confident in the DB integrity and just need to reindex.
- A stale plugin symlink at ~/.hermes/plugins/mnemosyne -> ~/mnemosyne/hermes_memory_provider will break imports on modern Mnemosyne (3.8+), which bundles Hermes integration directly. Remove it if present.
- Hermes currently bundles mnemosyne 3.0.0 internally, so even after upgrading the pip package to 3.8+, the runtime may still report 3.0.0 and refuse to fully activate embeddings. In that case:
 - Ensure PYTHONPATH in gateway plist points to site-packages.
 - Add MNEMOSYNE_VEC_TYPE=fastembed via plutil (see "Embeddings" section).
 - Run reindex with MNEMOSYNE_DATA_DIR set explicitly.
 - If mnemosyne_sleep runs fast and no longer hangs, the fix worked even if diagnose still says 3.0.0.
- When using a local dev copy of Mnemosyne (e.g., ~/mnemosyne-dev), ensure its __init__.py delegates to the real package instead of shadowing it:
 - Remove sys.path.insert(0, repo_root) lines that bring in the inner mnemosyne/ subpackage.
 - Import everything from the installed mnemosyne-memory package via "from mnemosyne import *" so Hermes gets the latest version.

## Hard-learned rules (from live sessions)

- Trust behavior over version numbers:
 - If mnemosyne_sleep completes quickly and no longer hangs, the fix worked — even if diagnose still reports 3.0.0 or embeddings_available=NO.
 - Hermes bundles its own older mnemosyne internally; pip upgrades alone won't change what diagnose prints. What matters is whether operations are fast and non-blocking.
- When reindex fails with "Database not found" or backup errors:
 - It's using ~/.mnemosyne/data/ instead of ~/.hermes/mnemosyne/data/.
 - Either set MNEMOSYNE_DATA_DIR=~/.hermes/mnemosyne before running, or use --no-backup if you're confident in DB integrity.
- If all deps are installed and fastembed/sqlite_vec show OK but embeddings_available=NO:
 - Likely Hermes is loading its bundled mnemosyne 3.0.0 instead of the pip-installed 3.8+.
 - Ensure PYTHONPATH in gateway plist points to site-packages, remove stale plugin symlinks, restart gateway, then verify with a live mnemosyne_sleep run rather than diagnose output alone.
