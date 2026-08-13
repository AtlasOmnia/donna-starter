from __future__ import annotations

"""Validate SKILL.md packages and their public support-file manifests.

The manifest is the package contract: every support file physically shipped under
an individual skill package must be named in a Support/References section, and
every explicitly named relative support path must exist. Source-tree commands,
URLs, wildcard examples, and cross-skill prose are intentionally ignored.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
RECOMMENDED_HEADINGS = (
    "## Overview",
    "## When to Use",
    "## Common Pitfalls",
    "## Verification Checklist",
)
HEADING_VARIANTS = {
    "## Overview": ("## overview",),
    "## When to Use": ("## when to use",),
    "## Common Pitfalls": ("## common pitfalls", "## pitfalls"),
    "## Verification Checklist": ("## verification checklist", "## verification"),
}
SUPPORT_DIRS = frozenset({"references", "scripts", "templates", "assets", "examples"})
PATHLESS_BULLET_RE = re.compile(r"^\s*-\s+—\s+")
SUPPORT_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])((?:references|scripts|templates|assets|examples)/[A-Za-z0-9_./-]+)"
)
DANGLING_SCRUB_RE = re.compile(r"(?i)\bsee\s*;")


def _manifest_paths(body: str) -> set[str]:
    """Extract literal package-relative support paths from manifest sections only."""
    paths: set[str] = set()
    in_manifest = False
    for line in body.splitlines():
        heading = re.match(r"^\s*#{2,3}\s+(.+?)\s*$", line)
        if heading:
            title = heading.group(1).lower()
            in_manifest = title in {
                "support files",
                "public support files",
                "references",
                "reference files",
            }
            continue
        if not in_manifest:
            continue
        for match in SUPPORT_PATH_RE.finditer(line):
            rel = match.group(1).rstrip(".,;:)")
            if "*" not in rel and not rel.endswith("/") and "<" not in rel:
                paths.add(rel)
    return paths


def _physical_support_paths(package: Path) -> set[str]:
    return {
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_file()
        and path.name != "SKILL.md"
        and any(part in SUPPORT_DIRS for part in path.relative_to(package).parts)
    }


def validate_skill(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return ["must start with YAML frontmatter at byte zero"], []
    marker = content.find("\n---\n", 4)
    if marker < 0:
        return ["frontmatter is not closed"], []
    frontmatter = content[4:marker]
    body = content[marker + 5 :]
    name_match = re.search(r"(?m)^name:\s*([^\n]+)$", frontmatter)
    description_match = re.search(r"(?m)^description:\s*([^\n]+)$", frontmatter)
    name = name_match.group(1).strip().strip("\"'") if name_match else ""
    description = description_match.group(1).strip().strip("\"'") if description_match else ""
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        errors.append("name must be 1-64 lowercase letters, digits, or hyphens")
    if name and path.parent.name != name:
        errors.append(f"directory name {path.parent.name!r} does not match skill name {name!r}")
    if not description:
        errors.append("description is required")
    elif len(description) > 1024:
        errors.append("description exceeds 1024 characters")
    if not body.strip():
        errors.append("skill body is empty")
    if len(content) > 100_000:
        errors.append("SKILL.md exceeds 100,000 characters")
    if any(PATHLESS_BULLET_RE.match(line) for line in body.splitlines()):
        errors.append("pathless support bullet found; use an explicit relative path or remove the pointer")
    if DANGLING_SCRUB_RE.search(body):
        errors.append("dangling scrub remnant found: 'see ;'")

    manifest = _manifest_paths(body)
    physical = _physical_support_paths(path.parent)
    for rel in sorted(manifest - physical):
        errors.append(f"missing explicitly referenced support file: {rel}")
    for rel in sorted(physical - manifest):
        errors.append(f"physically shipped support file is not explicitly referenced: {rel}")

    lower = body.lower()
    for heading in RECOMMENDED_HEADINGS:
        variants = (heading,) + HEADING_VARIANTS[heading]
        if not any(variant.lower() in lower for variant in variants):
            warnings.append(f"missing recommended heading: {heading}")
    return errors, warnings


def main() -> int:
    paths = sorted(SKILLS.rglob("SKILL.md"))
    if not paths:
        print("ERROR: no skill packages found")
        return 1
    failures = 0
    for path in paths:
        errors, warnings = validate_skill(path)
        for warning in warnings:
            print(f"WARNING: {path.relative_to(ROOT)}: {warning}")
        if errors:
            failures += 1
            for error in errors:
                print(f"ERROR: {path.relative_to(ROOT)}: {error}")
        else:
            print(f"SKILL_VALIDATION=PASS path={path.relative_to(ROOT)} chars={len(path.read_text(encoding='utf-8'))}")
    if failures:
        print(f"COLLECTION_VALIDATION=FAIL skills={len(paths)} failures={failures}")
        return 1
    print(f"COLLECTION_VALIDATION=PASS skills={len(paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
