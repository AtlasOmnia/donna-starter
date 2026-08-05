#!/usr/bin/env python3
"""Archive locally resident regular files from a File Provider tree.

Dry-run by default. Use --delete-source only when the user explicitly
requested a move. Source deletion occurs only after destination SHA-256
verification and a source identity re-check.
"""

import argparse
import hashlib
import json
import os
import stat
import sys
import zipfile
from pathlib import Path

CHUNK = 4 * 1024 * 1024
MANIFEST_NAME = "MOVE_MANIFEST.json"


def resident_files(root: Path):
    selected = []
    placeholders = 0
    links = 0
    placeholder_logical = 0
    for dirpath, _, filenames in os.walk(root, followlinks=False):
        for name in filenames:
            path = Path(dirpath) / name
            st = path.lstat()
            if stat.S_ISLNK(st.st_mode):
                links += 1
            elif stat.S_ISREG(st.st_mode):
                if st.st_blocks > 0:
                    selected.append((path, st))
                else:
                    placeholders += 1
                    placeholder_logical += st.st_size
    return selected, placeholders, placeholder_logical, links


def hash_stream(stream):
    digest = hashlib.sha256()
    size = 0
    while True:
        block = stream.read(CHUNK)
        if not block:
            break
        digest.update(block)
        size += len(block)
    return size, digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination_zip", type=Path)
    parser.add_argument("--delete-source", action="store_true")
    parser.add_argument("--prune-empty-dirs", action="store_true")
    args = parser.parse_args()

    root = args.source.expanduser().resolve()
    final = args.destination_zip.expanduser()
    temp = final.with_name(final.name + ".partial")

    if not root.is_dir():
        raise SystemExit(f"Source is not a directory: {root}")
    if final.exists():
        raise SystemExit(f"Destination already exists: {final}")
    final.parent.mkdir(parents=True, exist_ok=True)
    if temp.exists():
        temp.unlink()

    files, placeholders, placeholder_logical, links = resident_files(root)
    allocated = sum(st.st_blocks * 512 for _, st in files)
    print(f"resident_files={len(files)}")
    print(f"resident_allocated_bytes={allocated}")
    print(f"cloud_or_zero_block_files={placeholders}")
    print(f"cloud_or_zero_block_logical_bytes={placeholder_logical}")
    print(f"symlinks_untouched={links}")

    if not args.delete_source:
        print("DRY_RUN: add --delete-source to perform verified move")
        return 0
    if not files:
        print("No resident regular files selected; nothing to move.")
        return 0

    manifest = []
    try:
        with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as zf:
            for index, (path, initial) in enumerate(files, 1):
                rel = (Path(root.name) / path.relative_to(root)).as_posix()
                info = zipfile.ZipInfo.from_file(path, arcname=rel)
                info.compress_type = zipfile.ZIP_STORED
                digest = hashlib.sha256()
                size = 0
                with path.open("rb") as src, zf.open(info, "w", force_zip64=True) as dst:
                    while True:
                        block = src.read(CHUNK)
                        if not block:
                            break
                        dst.write(block)
                        digest.update(block)
                        size += len(block)
                if size != initial.st_size:
                    raise RuntimeError(f"Source changed while archiving: {path}")
                manifest.append({
                    "archive_path": rel,
                    "source_path": str(path),
                    "size": size,
                    "sha256": digest.hexdigest(),
                    "mtime_ns": initial.st_mtime_ns,
                    "inode": initial.st_ino,
                })
                if index % 100 == 0 or index == len(files):
                    print(f"archived={index}/{len(files)}", flush=True)
            zf.writestr(MANIFEST_NAME, json.dumps(manifest, indent=2))

        with zipfile.ZipFile(temp, "r") as zf:
            bad = zf.testzip()
            if bad:
                raise RuntimeError(f"ZIP CRC failure: {bad}")
            for index, item in enumerate(manifest, 1):
                with zf.open(item["archive_path"], "r") as src:
                    size, digest = hash_stream(src)
                if size != item["size"] or digest != item["sha256"]:
                    raise RuntimeError(f"Archive mismatch: {item['archive_path']}")
                if index % 100 == 0 or index == len(manifest):
                    print(f"verified={index}/{len(manifest)}", flush=True)

        os.replace(temp, final)

        # Fail before deleting anything if any source identity changed.
        for item in manifest:
            path = Path(item["source_path"])
            st = path.lstat()
            if (
                not stat.S_ISREG(st.st_mode)
                or st.st_size != item["size"]
                or st.st_mtime_ns != item["mtime_ns"]
                or st.st_ino != item["inode"]
            ):
                raise RuntimeError(f"Source changed before removal: {path}")

        for item in manifest:
            Path(item["source_path"]).unlink()

        if args.prune_empty_dirs:
            for dirpath, _, _ in os.walk(root, topdown=False, followlinks=False):
                try:
                    Path(dirpath).rmdir()
                except OSError:
                    pass

        os.sync()
        print(f"MOVE_COMPLETE destination={final} files_removed={len(manifest)}")
        return 0
    except Exception:
        print("MOVE_ABORTED_SOURCE_PRESERVED", file=sys.stderr)
        raise


if __name__ == "__main__":
    sys.exit(main())
