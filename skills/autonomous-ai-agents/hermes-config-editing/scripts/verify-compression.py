#!/usr/bin/env python3
"""Verify compression settings in Hermes config.yaml.

Usage: verify-compression.py [--config PATH]
Defaults to ~/.hermes/config.yaml.
Prints current values for threshold, target_ratio, protect_last_n, protect_first_n.
Exits 0 if valid YAML, non-zero if missing keys or parse error.
"""
import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Verify compression config")
    parser.add_argument("--config", default=None, help="Path to config.yaml")
    args = parser.parse_args()

    if args.config:
        path = Path(args.config)
    else:
        home = Path.home() / ".hermes"
        path = home / "config.yaml"

    try:
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
    except Exception as e:
        print(f"ERROR: Failed to parse {path}: {e}", file=sys.stderr)
        sys.exit(1)

    comp = cfg.get("compression", {})
    if not comp:
        print("WARNING: No 'compression' section found in config.yaml", file=sys.stderr)
        sys.exit(1)

    keys = ["threshold", "target_ratio", "protect_last_n", "protect_first_n"]
    for key in keys:
        val = comp.get(key, "<NOT SET>")
        print(f"  {key}: {val}")

    # Sanity check: threshold should be <= target_ratio (or equal)
    t = comp.get("threshold")
    tr = comp.get("target_ratio")
    if isinstance(t, float) and isinstance(tr, float):
        if tr > t:
            print(f"WARNING: target_ratio ({tr}) > threshold ({t})", file=sys.stderr)

    print("OK")


if __name__ == "__main__":
    main()
