#!/usr/bin/env python3
"""Delete explicitly named inactive cache trees after an open-file check.

Dry-run by default. Pass --apply to delete. Targets must live under known
cache roots or Xcode DerivedData unless --allow-outside-cache-roots is set.
"""

import argparse
import os
import shutil
import subprocess
from pathlib import Path

HOME = Path.home().resolve()
ALLOWED_ROOTS = [
    HOME / ".cache",
    HOME / ".npm",
    HOME / "Library/Caches",
    HOME / "Library/Developer/Xcode/DerivedData",
]


def allocated_bytes(path: Path) -> int:
    if not path.exists() and not path.is_symlink():
        return 0
    total = 0
    try:
        total += path.lstat().st_blocks * 512
    except OSError:
        pass
    if path.is_dir() and not path.is_symlink():
        for dirpath, _, filenames in os.walk(path, followlinks=False):
            for name in filenames:
                try:
                    total += (Path(dirpath) / name).lstat().st_blocks * 512
                except OSError:
                    pass
    return total


def open_paths() -> list[str]:
    result = subprocess.run(
        ["/usr/sbin/lsof", "-Fn"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    return [line[1:] for line in result.stdout.splitlines() if line.startswith("n/")]


def under_allowed_root(path: Path) -> bool:
    for root in ALLOWED_ROOTS:
        root = root.resolve()
        if path == root or root in path.parents:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", action="append", required=True,
                        help="Exact cache directory; repeat for multiple targets")
    parser.add_argument("--apply", action="store_true",
                        help="Delete eligible targets; default is dry-run")
    parser.add_argument("--allow-outside-cache-roots", action="store_true")
    args = parser.parse_args()

    targets = [Path(raw).expanduser().resolve() for raw in args.target]
    opened = open_paths()
    eligible = []
    total = 0

    for target in targets:
        if target == HOME or target == HOME / "Library":
            raise SystemExit(f"Refusing broad target: {target}")
        if not args.allow_outside_cache_roots and not under_allowed_root(target):
            raise SystemExit(f"Outside allowed cache roots: {target}")
        if not target.exists() and not target.is_symlink():
            print(f"MISSING target={target}")
            continue
        prefix = str(target).rstrip("/") + "/"
        active = [p for p in opened if p == str(target) or p.startswith(prefix)]
        size = allocated_bytes(target)
        if active:
            print(f"SKIPPED_OPEN target={target} open_files={len(active)} allocated_bytes={size}")
            continue
        eligible.append((target, size))
        total += size
        print(f"ELIGIBLE target={target} allocated_bytes={size}")

    print(f"eligible_targets={len(eligible)} allocated_bytes={total}")
    if not args.apply:
        print("DRY_RUN: add --apply to delete eligible targets")
        return 0

    removed = 0
    for target, size in eligible:
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
        removed += size
        print(f"REMOVED target={target} allocated_bytes={size}")
    os.sync()
    print(f"CACHE_CLEANUP_COMPLETE allocated_bytes_removed={removed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
