# Recovering iCloud-offloaded files for local automation

Use this when a local macOS job targets a repository or script under Desktop, Documents, or another iCloud/File Provider location and normal reads fail with `Resource deadlock avoided`, Git reports `not a git repository` despite `.git` existing, or files appear present but behave as empty/unreadable placeholders.

## Recognize the condition

Check representative files rather than assuming the directory is usable:

```bash
stat -f '%N flags=%Sf size=%z' /path/to/repo/.git/HEAD \
 /path/to/repo/.git/config \
 /path/to/repo/scripts/job.py
```

The durable signal is the `dataless` flag, often alongside `compressed`. Confirm actual readability:

```bash
python3 - <<'PY'
from pathlib import Path
for p in [Path('.git/HEAD'), Path('.git/config'), Path('scripts/job.py')]:
 try:
 print(p, len(p.read_bytes()), 'bytes readable')
 except OSError as e:
 print(p, 'UNREADABLE', repr(e))
PY
```

Do not trust path existence, reported logical size, or a suspiciously silent command exit by itself. An offloaded script can appear present while its contents are not locally available.

## Materialize files with Foundation

Requesting download only for the top-level directory may hydrate directory metadata or only a few children. Enumerate the tree and request each regular file:

```bash
swift - <<'SWIFT'
import Foundation

let root = URL(fileURLWithPath: "/absolute/path/to/repo", isDirectory: true)
let keys: [URLResourceKey] = [
 .isRegularFileKey,
 .isDirectoryKey,
 .isUbiquitousItemKey,
 .ubiquitousItemDownloadingStatusKey
]

let enumerator = FileManager.default.enumerator(
 at: root,
 includingPropertiesForKeys: keys,
 options: [],
 errorHandler: { url, error in
 print("ENUMERR \(url.path): \(error)")
 return true
 }
)!

var requested = 0
for case let url as URL in enumerator {
 do {
 let values = try url.resourceValues(forKeys: Set(keys))
 if values.isRegularFile == true {
 try FileManager.default.startDownloadingUbiquitousItem(at: url)
 requested += 1
 }
 } catch {
 print("REQERR \(url.path): \(error)")
 }
}
print("requested=\(requested)")
SWIFT
```

`brctl download <directory>` may be useful as a first request, but do not treat its lack of an error as proof that every descendant has materialized. Foundation per-file requests are the reliable fallback.

## Poll readiness, then rerun from scratch

Poll a small set of prerequisite files until their bytes can actually be read:

```bash
python3 - <<'PY'
import time
from pathlib import Path

paths = [Path('.git/HEAD'), Path('.git/config'), Path('.git/index'), Path('scripts/job.py')]
for attempt in range(45):
 failures = []
 for p in paths:
 try:
 p.read_bytes()
 except OSError as e:
 failures.append(f'{p}: {e}')
 if not failures:
 print('materialized')
 raise SystemExit(0)
 print(f'attempt {attempt}: ' + '; '.join(failures), flush=True)
 time.sleep(2)
raise SystemExit('files did not materialize in time')
PY
```

After materialization:

1. Re-run prerequisite probes such as `git rev-parse --show-toplevel`.
2. Re-run the original sync/build/script from the beginning; discard any earlier silent or partial result.
3. Verify artifacts with `git status --short`, file timestamps, counts, or task-specific checks.
4. For a push, compare `git rev-parse HEAD` with `git ls-remote origin refs/heads/<branch>`.

## Pitfalls

- Directory hydration is not recursive proof of file hydration.
- A logical file size does not mean bytes are resident locally.
- Do not record “Git/Python is broken.” The actionable condition is an iCloud/File Provider dataless placeholder.
- Avoid killing iCloud/File Provider daemons as an early fix. Request materialization and verify readability first.
- Do not clone elsewhere unless the remote and working-tree state are known; an unpushed local change could be lost from the workflow.
