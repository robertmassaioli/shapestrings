#!/usr/bin/env python3
"""Bump version across project files modified in commit 47ec423.

Updates the following files:
 - freecad/ShapeStrings/Misc/Version.py
 - package.xml
 - pyproject.toml

Usage:
    ./bump_version.py 1.2.3 [--date 2025-12-30] [--git]

If --git is provided the modified files will be staged and committed with
message "Bumped version to 1.2.3".
"""
from __future__ import annotations

import argparse
import datetime
import re
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
FILES = {
    "version_py": ROOT / "freecad" / "ShapeStrings" / "Misc" / "Version.py",
    "package_xml": ROOT / "package.xml",
    "pyproject": ROOT / "pyproject.toml",
}


def _replace_in_file(path: Path, pattern: str, repl: str) -> tuple[bool, str, str]:
    text = path.read_text(encoding="utf8")
    new_text = re.sub(pattern, repl, text, flags=re.MULTILINE)
    changed = new_text != text
    if changed:
        path.write_text(new_text, encoding="utf8")
    return changed, text, new_text


def bump_version(version: str, date: str | None = None, do_git: bool = False) -> int:
    changed_files = []

    # Version.py
    p = FILES["version_py"]
    if not p.exists():
        print(f"ERROR: {p} does not exist", file=sys.stderr)
        return 2
    changed, old, new = _replace_in_file(
        p,
        r"(^__version__\s*=\s*)([\"\'])([^\"\']+)([\"\'])",
        lambda m: m.group(1) + m.group(2) + version + m.group(4),
    )
    if changed:
        print(f"Updated {p}: {old.strip()} -> {version}")
        changed_files.append(str(p))

    # package.xml: version and date
    p = FILES["package_xml"]
    if not p.exists():
        print(f"ERROR: {p} does not exist", file=sys.stderr)
        return 2

    changed_v, old_v, new_v = _replace_in_file(
        p,
        r"(<version>\s*)([^<]+?)(\s*</version>)",
        lambda m: m.group(1) + version + m.group(3),
    )
    if date is None:
        date = datetime.date.today().isoformat()
    changed_d, old_d, new_d = _replace_in_file(
        p,
        r"(<date>\s*)([^<]+?)(\s*</date>)",
        lambda m: m.group(1) + date + m.group(3),
    )
    if changed_v or changed_d:
        print(f"Updated {p}:")
        if changed_v:
            print(f"  version: -> {version}")
            changed_files.append(str(p))
        if changed_d:
            print(f"  date: -> {date}")
            if str(p) not in changed_files:
                changed_files.append(str(p))

    # pyproject.toml
    p = FILES["pyproject"]
    if not p.exists():
        print(f"ERROR: {p} does not exist", file=sys.stderr)
        return 2

    # match a line like: version = '0.2.0' or version = "0.2.0"
    changed, old, new = _replace_in_file(
        p,
        r"(^\s*version\s*=\s*)([\"\'])([^\"\']+)([\"\'])",
        lambda m: m.group(1) + m.group(2) + version + m.group(4),
    )
    if changed:
        print(f"Updated {p}: version -> {version}")
        changed_files.append(str(p))

    if do_git and changed_files:
        try:
            subprocess.check_call(["git", "add"] + changed_files)
            subprocess.check_call([
                "git",
                "commit",
                "-m",
                f"Bumped version to {version}",
            ])
            print("Committed version bump to git")
        except subprocess.CalledProcessError as exc:
            print("Git command failed:", exc, file=sys.stderr)
            return 3

    if not changed_files:
        print("No changes made (files already at requested version)")
    else:
        print("Changed files:")
        for f in changed_files:
            print(" -", f)

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bump project version in a few files")
    parser.add_argument("version", help="New version string (e.g. 1.2.3)")
    parser.add_argument("--date", help="Date to place into package.xml (YYYY-MM-DD)")
    parser.add_argument("--git", action="store_true", help="Stage and commit changes with git")
    args = parser.parse_args(argv)
    return bump_version(args.version, args.date, args.git)


if __name__ == "__main__":
    raise SystemExit(main())
