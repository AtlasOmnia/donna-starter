---
name: macos-storage-management
description: macos-storage-management — Use when freeing Mac storage or moving files to SSDs.
---
# macOS Storage Management

Safely reclaim local Mac storage without mistaking cloud placeholders for resident data, losing File Provider content, or flattening metadata onto an incompatible external filesystem.

## Trigger

Load this skill when the user asks to free space on a Mac, move Documents/Desktop/Downloads to an external SSD, archive iCloud/File Provider folders, migrate between APFS and ExFAT, or explain conflicting Finder, `du`, and `df` storage figures.

## Safety Principles

1. **Measure the live Data volume, not only `/`.** On modern macOS, use `df -h "$HOME"` because `/System/Volumes/Data` carries user data.
2. **Inspect the destination filesystem before choosing a copy method.** ExFAT does not preserve native macOS symlinks, ownership, permissions, extended attributes, resource forks, or every filename semantic.
3. **Treat File Provider folders specially.** A logical file can be `dataless` with zero allocated blocks. Its apparent size is not reclaimable local space until downloaded.
4. **Never delete on a partial copy.** Copy/archive, independently verify, re-check source identity/state, then remove only verified source objects.
5. **Do not force cloud hydration onto a critically full disk.** If placeholders materially exceed free space, move only resident files or free space elsewhere first.
6. **Report actual reclaimed capacity.** Compare `df` before/after; do not equate logical file size with local blocks released.

## Diagnosing an oversized “System Data” category

Treat the Storage Settings number as a classification clue, not a filesystem path. Before recommending cleanup:

1. Compare the sealed System volume with the writable Data volume using `diskutil apfs list` and `df -h "$HOME"`.
2. Check both Time Machine and APFS snapshots; do not assume snapshots are responsible.
3. Rank `$HOME`, `~/Library`, `/private/var`, `/Library`, and hidden application roots with allocated-block measurements.
4. Drill into app containers, group containers, caches, developer runtimes, cloud storage, and `/private/var/folders`.
5. Inspect large files stored directly at a root such as `~/.hermes`; directory-only rankings can hide backup multiplication.
6. Separate rebuildable caches/temp data from app-managed stores and live databases before proposing deletion.

## Workflow

### 1. Establish scope and capacity

- Confirm the user-authorized source and mounted external destination.
- Run `df -h "$HOME" /Volumes/*` and `du -sh "$HOME/Documents"` (or the requested tree).
- Rank top-level source items with `du -sh`.
- Inspect the external volume with `diskutil info` for filesystem, read-only state, and free capacity.
- Check whether the intended destination path already exists before writing.

### 2. Detect File Provider and placeholder state

Check source directory extended attributes and representative files:

```bash
ls -ldO@ "$SOURCE"
ls -lO@ "$FILE"
stat -f 'flags=%Sf size=%z blocks=%b fileid=%i' "$FILE"
```

Important signals:

- `com.apple.file-provider-domain-id` on the folder;
- `dataless` in file flags;
- `blocks=0` with nonzero logical `size`;
- `Resource deadlock avoided` while a copy/archive tool tries to open cloud-only data.

Inventory resident regular files without opening placeholders: use `lstat`, require regular-file mode, and select `st_blocks > 0`. Count resident allocated bytes as `st_blocks * 512`. Separately count zero-block/dataless logical bytes and symlinks.

### 3. Select a transfer strategy

#### APFS destination

A direct metadata-preserving copy may be appropriate. Still verify before source removal. For a newly formatted external SSD intended to hold live Git repositories, first run a sustained multi-gigabyte write → `sync` → destination SHA-256 readback gate; a successful format, mount, SMART result, or `diskutil verifyVolume` does not prove the USB cable/port/power path is stable under load. Restore cold Git archives through hidden same-volume staging, repair linked-worktree metadata only after verifying the common repository has no writer, and keep source archives intact until Git acceptance passes.

#### ExFAT destination

- For ordinary files with portable names, copy into a structured destination and verify hashes.
- For macOS-heavy trees containing symlinks, app bundles, aliases, resource forks, or metadata, use an archive on ExFAT rather than pretending a direct folder copy is equivalent.
- If File Provider placeholders are present and cannot be hydrated safely, archive **resident regular files only** and leave placeholders untouched.
- For flat files without macOS metadata significance (databases, archives, logs), hash-verify the destination against the source before removing anything, and run these transfers as background execution — they are often large.

### 4. Classify application data before moving it

A large application directory is rarely one safe unit. Split candidates into:

1. **Movable inactive archives:** dated backups, pre-update snapshots, legacy checkpoints, and completed export bundles.
2. **Rebuildable cleanup:** caches, temporary build trees, DerivedData, and unused simulators—normally delete rather than move.
3. **App-managed storage:** Docker disks, OneDrive local availability, Photos libraries, Voice Memos, Notes databases—use the owning application's migration or cleanup controls.
4. **Live state:** current profiles, session databases, memory stores, logs, active worktrees, and open project checkouts—do not generically relocate.

Before moving an inactive archive, record its size and modification time, check exact destination-name collisions, and verify no process has an open file beneath the source. A dated name is evidence, not proof of inactivity.

For macOS-heavy archive trees on ExFAT, create one uncompressed PAX tar plus a companion manifest per source. Process sources sequentially so each verified tree is an independent commit point and a later failure cannot compromise earlier or untouched sources.

#### Inactive Git repositories and worktrees

Treat Git checkouts as macOS-heavy preservation trees, not ordinary portable folders. Before archiving, discover nested repositories/worktrees; record branch and HEAD; require clean status unless the user explicitly approves a dirty-state archive; inspect both exact-path open files and process command lines for incumbent writers, watchers, test runners, or controller scripts; and exclude current canonical checkouts. A dated or `final` name is not enough by itself.

On ExFAT, archive each bounded source as its own uncompressed PAX tar rather than moving the checkout directly. Verify every intended regular-file hash and symlink target against a source manifest, re-check the complete source identity and Git cleanliness immediately before deletion, then finalize the tar and companion manifest atomically. Report intentionally excluded active or dirty trees at closure.

#### Resource-bounded batched moves to an external SSD

When the user explicitly wants data **moved**, preserve that objective. Classify candidates first, but do not substitute deletion or a cloud-only toggle unless moving has a concrete safety or compatibility blocker.

On a critically full Mac, process eligible archives sequentially or in explicit size-limited batches. Copy directly to a destination `.partial`, hash-verify it, re-check source identity, atomically finalize, persist one manifest record, and only then remove that source file. Do not create a second large staging artifact on the Mac. Use one exact selector for inventory, open-file checks, transfer, and closure so sidecars do not inflate counts or make totals disagree.

Long bounded transfers should run as tracked background work with completion notification. Persist the manifest after **every** committed file, and reconcile source, destination, manifest, and stale `.partial` files before resuming after interruption.

#### Temporary builds and cache cleanup

Treat `/private/tmp` as mixed-risk, not automatically disposable. Before selecting completed build trees, check open files, process current-working-directories, and recent modification times. If provenance is uncertain, archive only quiet top-level trees to the SSD with the same fail-closed manifest/hash sequence used for inactive backups.

For rebuildable caches, use an explicit target allowlist and one `lsof -Fn` snapshot. Skip any target with an open file rather than terminating applications just to reclaim space. Measure cleanup candidates and results using allocated blocks (`st_blocks * 512`). Never generically clear CloudKit, cloud-provider stores, browser profiles, application databases, Docker disks, or live Hermes state.

Large dependency trees may contain hundreds of thousands of tiny files. Emit entry-count progress during inventory and verification, and expect the job to be metadata-bound even when total bytes are modest. See `scripts/cleanup-inactive-caches.py`.

#### Docker Desktop sparse-disk diagnosis and cleanup

Docker Desktop normally concentrates its Mac-side storage in `~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`. Treat this as an app-managed sparse disk:

1. Compare logical capacity (`st_size`) with physical allocation (`st_blocks * 512`). The logical value may be hundreds of GiB without consuming that much Mac storage.
2. With Docker running and authorized, attribute internal usage using `docker system df -v`, `docker compose ls -a`, `docker ps -a`, `docker volume ls`, and `docker buildx du`.
3. Before removing a Compose project, inspect container labels, compose working/config paths, bind mounts, named versus anonymous volumes, networks, and image references. Preserve images shared by unrelated running services.
4. Treat containers, images, Docker-managed volumes, project networks, build cache, and ordinary host folders as separate deletion scopes. A Docker-context removal defaults to Docker artifacts only; do not infer permission to delete similarly named host folders.
5. Remove an explicitly retired project in dependency-safe order: containers with attached anonymous volumes, owned named volumes, project network, exclusive images, then eligible build cache.
6. Preserve generic dependency images such as PostgreSQL, MySQL, language runtimes, and search services until both container ancestry and compose-file references have been checked. A stopped test container can be the only remaining owner of a multi-gigabyte runtime image.
7. Never use `docker system prune --volumes` as a blind shortcut on a machine with unrelated services, and never manually delete `Docker.raw` unless the user explicitly intends a complete Docker reset.
8. Verify by readback rather than exit status alone: confirm target containers/images/volumes/networks are absent, unrelated services remain healthy, `Docker.raw` allocated blocks declined, and `df -h "$HOME"` shows actual reclaimed Mac capacity. Docker deletion is not complete merely because internal objects disappeared.

### Cloud sync versus cloud backup

When a user asks whether cloud storage should replace an unstable external SSD, separate three roles before recommending a provider:

1. **Active workspace:** high-I/O Git worktrees, databases, Docker disks, simulators, build trees, and virtual machines stay on a known-good local APFS volume. Do not place them inside Google Drive, OneDrive, iCloud Drive, Dropbox, or another file-provider sync root.
2. **Cloud Git host:** GitHub or GitLab can preserve committed source, branches, issues, reviews, and releases, but a remote Git repository does not contain uncommitted, untracked, ignored, or machine-managed state. Use Git LFS or release assets only for bounded binaries; do not turn Git history into a whole-drive backup.
3. **Off-site archive/backup:** Google Drive, OneDrive, iCloud Drive, Backblaze B2, R2, or a dedicated backup application can hold dated archives and large assets. A sync folder is not automatically an independent backup: deletions and corruption can propagate to every device.

For Apple-centric personal data, an existing iCloud Drive quota is a practical archive destination, especially for dated encrypted archives, exports, installers, and documents. Treat Optimize Mac Storage and cloud-only placeholders as expected File Provider behavior, not as proof that a local working copy exists. Apple iCloud Drive deletion propagates across connected devices; retain separate date-stamped snapshots and verify each upload with an independent download/readback before retiring local data. Keep employer/business data in its authorized tenant (for example, the employer's OneDrive) rather than mixing it into a personal iCloud account.

When the source disk is failing under load, first preserve the source and copy critical data to a qualified local destination. Then create a layered layout: healthy local active copy, cloud Git remote for committed source, and dated cloud archive for non-Git data. Qualify the replacement SSD with a sustained multi-gigabyte write, sync, and cryptographic readback before treating it as the active workspace; a SMART pass or successful mount alone does not prove the USB cable, port, enclosure, power, or thermal path is stable.

### 5. Fail closed

Use a temporary destination name such as `.partial`. The operation must follow this order:

1. enumerate eligible source files;
2. record source path, size, mtime, inode, and a content hash;
3. write archive/copy to the external disk;
4. test archive structure/CRC;
5. independently read destination content and compare cryptographic hashes;
6. atomically rename the verified temporary artifact to its final name;
7. re-check each source object's size, mtime, and inode;
8. remove only those verified, unchanged source files;
9. remove empty directories only when truly empty;
10. sync and measure reclaimed local capacity.

Any read, copy, verification, or source-identity failure must preserve the source.

### 6. Verify and close out

Report the exact destination path, resident files and allocated bytes moved, verification result, source objects removed, cloud placeholders retained, source size before/after, Mac free space before/after, and whether remaining free space is still operationally low.

Start completion answers with **Yes** or **No**. Separate completed work from remaining storage risk.

## Common Pitfalls

### `du` versus `df`

`du` can show figures that do not explain APFS snapshots, purgeable data, File Provider state, or Data-volume pressure. Use both; `df "$HOME"` is the closure metric.

### Interruptions during large external-drive transfers

Do not size a foreground tool timeout from the byte count and hope it is sufficient; USB speed, filesystem overhead, hashing, and metadata vary. Run long bounded transfers as tracked background work with completion notification. Resume from per-file durable commits, not from process exit status. Before restarting, reconcile any final destination file or `.partial` with the source and manifest; apparent size alone is not proof of a completed copy — hash-verify the destination against the source before removing anything.

### Blind `mv` across filesystems

A cross-volume `mv` is copy-then-delete. It can fail halfway and does not solve ExFAT metadata incompatibility. Never use it as the unverified safety mechanism for mixed macOS trees.

### Treating `unzip -t` as full proof

CRC validation proves archive readability, not necessarily that every intended resident source was included. Compare the archive entry set and cryptographic hashes against an explicit source manifest.

### Retrying `ditto` after placeholder errors

`Resource deadlock avoided` in a File Provider tree is a diagnostic signal, not a reason to keep retrying the same bulk copy. Inspect `dataless` flags and allocated blocks, remove any failed partial artifact only after a separate verified transfer exists, then use a resident-only strategy.

### Deleting cloud placeholders to reclaim space

Dataless placeholders usually consume negligible local data blocks; deleting them may remove cloud originals while reclaiming little space. Leave them untouched unless the user explicitly wants cloud deletion.

## Supporting Material

- See `scripts/archive-resident-files.py` for a generic fail-closed resident-file archiver with SHA-256 destination verification.
- See `scripts/cleanup-inactive-caches.py` for a dry-run-first cache cleaner that skips targets with open files.
## Public support files

- `scripts/archive-resident-files.py`
- `scripts/cleanup-inactive-caches.py`
