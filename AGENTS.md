# AGENTS.md

Guidance for AI coding agents working in this repository.

## What this is

ShapeStrings is a **FreeCAD addon/workbench** that adds two Draft-workbench
tools for laying out multiple text strings as shapes:

- **Spaced** — strings placed side-by-side with a configurable X offset.
- **Radial** — strings arranged around a circle.

It is not a standalone application — it only runs inside FreeCAD (>= 1.0.2),
loaded from FreeCAD's `Mod/` addon directory. There is no server, build step,
or web UI here.

## Layout

```
freecad/ShapeStrings/       The addon itself (this is what gets symlinked into FreeCAD's Mod/ dir)
  init_gui.py                Entry point: registers commands, toolbar, translations
  API/                       Public API surface, re-exported as the `ShapeStrings` module
  Misc/                      Shared helpers (Justify, Resources/paths, Toolbar, Version)
  Spaced/                    Command.py, Dialog.py, Generator.py, Object.py, View.py
  Radial/                    Same five-file shape as Spaced/
  Resources/
    Icons/                   SVG icons
    Interfaces/              Qt .ui files loaded via PySide6
    Translations/            .ts translation files
Documentation/               User-facing docs (API.md + Commands/*.md)
bump_version.py              Keeps version in sync across three files
package.xml                  FreeCAD addon manager metadata
pyproject.toml               Python project metadata (uv-managed)
```

Each tool (`Spaced/`, `Radial/`) follows the same internal split — use the
other one as a template when adding a third tool:

- `Object.py` — the FreeCAD document object: `set_properties()` adds
  properties guarded by `if "Name" not in obj.PropertiesList`, plus
  `execute()`, `onChanged()`, `onDocumentRestored()`.
- `View.py` — the view provider.
- `Dialog.py` — the PySide6 task panel wired to the `.ui` file.
- `Command.py` — the FreeCAD `Gui.Command`, registered via `registerX()`.
- `Generator.py` — the plain-Python factory function re-exported through
  `API/Module.py` as the public `ShapeStrings.Spaced` / `ShapeStrings.Radial`
  API.

The internal `freecad.ShapeStrings` package is not the public API. External
callers (and docs) should only use `from ShapeStrings import Spaced, Radial`,
which is wired up by `API/__init__.py:initializeAPI()` at GUI init time.

## Environment

Dependency management is via [uv](https://docs.astral.sh/uv/):

```sh
uv sync
```

Then symlink the repository root into your FreeCAD `Mod/` directory to test
changes inside FreeCAD itself, e.g. `Mod/ShapeStrings-dev -> /path/to/this/repo`.
FreeCAD discovers the addon via the `freecad.*` namespace package, looking
for `freecad/ShapeStrings/init_gui.py` — so it's the whole repo root that
needs linking in, not just the inner `freecad/ShapeStrings` folder (that
alone won't be found by either FreeCAD's namespace-package addon loader or
its legacy `InitGui.py` loader).

**FreeCAD keeps a separate `Mod/` per major version, and picking the wrong
one fails silently.** On macOS, compare
`~/Library/Application Support/FreeCAD/Mod/` against a version-suffixed
sibling like `~/Library/Application Support/FreeCAD/v1-1/Mod/` — an install
may read only one of them. A symlink placed in the directory the running
FreeCAD doesn't use produces no error at startup; the addon just never
appears. Before trusting a symlink, confirm which `Mod/` the target install
actually reads — e.g. check where an already-working addon's symlink lives,
or look for version-suffixed subfolders under
`~/Library/Application Support/FreeCAD/`.

There is no headless test runner. `python -c
"import ast; ast.parse(...)"` or `python -m py_compile` on changed files is a
reasonable sanity check when FreeCAD isn't available, but it does not
substitute for running the workbench.

There is no linter/formatter config (no ruff/black config in the repo) —
match the surrounding style in the file you're editing rather than
introducing a new one.

### Reference the FreeCAD source alongside this repo

Several files here (e.g. `Spaced/Object.py`) are adapted from FreeCAD's own
Draft workbench (`Draft/objects/shapestring.py`,
`Draft/viewproviders/view_shapestring.py`, `draftobjects/base.py`,
`draftutils/`, `draftgeoutils/`), and this addon depends on FreeCAD internals
(`Part.makeWireString`, `App.Units`, `Gui.Command`, etc.) that aren't
documented outside the FreeCAD source itself. Before modifying or extending
code like this, check out the FreeCAD source next to this repo and point
your AI tool at both directories at once, so it can read the upstream
implementation directly instead of guessing at behavior:

```sh
git clone https://github.com/FreeCAD/FreeCAD.git ../FreeCAD
claude --add-dir ../FreeCAD
```

Useful upstream locations when doing this:

- `src/Mod/Draft/draftobjects/shapestring.py` — the original ShapeString
  object this addon's `Object.py` files are derived from.
- `src/Mod/Draft/draftobjects/base.py` — `DraftObject`, the base class used
  by `Spaced/Object.py` and `Radial/Object.py`.
- `src/Mod/Draft/draftutils/` and `draftgeoutils/` — helper modules imported
  throughout (`messages`, `faces`, etc.).
- `src/App/` / `src/Mod/Part/App/` — for the underlying `App`/`Part` API
  surface used via `freecad-stubs`.

## Conventions

- **SPDX headers on new files.** Every source file starts with
  `SPDX-License-Identifier` (`LGPL-2.1-or-later` for files derived from
  FreeCAD's Draft workbench, `LGPL-2.1-only` for original ShapeStrings files
  — follow whichever an existing neighboring file uses) plus
  `SPDX-FileNotice: Part of the ShapeStrings addon.`. When code is adapted
  from FreeCAD core (e.g. Draft's ShapeString), keep/add the original
  `SPDX-FileCopyrightText` lines — see `Spaced/Object.py` for the pattern.
- **Formatting**: 4-space indentation, LF line endings, UTF-8, trailing
  whitespace trimmed in `.py`/`.toml`/`.xml` but *not* in `.md` (see
  `.editorconfig`).
- **Property idiom**: always guard `addProperty` calls with a
  `PropertiesList` check inside `set_properties()`, and call
  `set_properties()` again from `onDocumentRestored()` so old documents pick
  up new properties on load.
- **User-facing docs**: if you add/rename/remove a property on a command,
  update the matching file under `Documentation/Commands/` and
  `Documentation/API.md`.

## Versioning

Version numbers live in three places and must stay in sync:
`freecad/ShapeStrings/Misc/Version.py`, `package.xml`, `pyproject.toml`.
Don't hand-edit them — use the script:

```sh
./bump_version.py 1.2.3 --date "$(date +%F)"     # updates the three files
./bump_version.py 1.2.3 --date "$(date +%F)" --git  # also stages + commits
```

## Releasing

There is no CI automation for releases (no `.github/workflows/`) — the whole
process is manual, done from a branch and a PR like any other change:

1. **Update `CHANGELOG.md`.** Move the entries accumulated under
   `[Unreleased]` (or write them fresh if none exist yet) under a new
   `## [X.Y.Z] — YYYY-MM-DD` heading, grouped as `Added` / `Changed` /
   `Fixed` / `Documentation` as needed. Reference PR/issue numbers where it
   helps.
2. **Bump the version.** From the repo root:

   ```sh
   python3 bump_version.py X.Y.Z --date "$(date +%F)"
   ```

   This updates `freecad/ShapeStrings/Misc/Version.py`, `package.xml`
   (version + date), and `pyproject.toml`. Commit this as its own commit —
   the existing convention is the exact message `Bumped version to X.Y.Z`
   (see `git log --grep "Bumped version"`) — separate from the changelog
   commit, so each is easy to `git revert` independently if needed.

   Note the script's `--git` flag stages+commits automatically but only
   handles the version-bump commit; the changelog edit still needs its own
   commit either way.
3. **Open a PR** with the version-bump and changelog commits (same workflow
   as any other change — see `.github/CONTRIBUTING.md`). Do not push
   directly to `main`.
4. **After the PR is merged**, tag the merge commit on `main` and push the
   tag. Tags in this repo are `v`-prefixed even though the version strings
   inside the three files are not (compare `git tag -l` — `v0.1.0`,
   `v0.2.0` — against `pyproject.toml`'s `version = '0.2.0'`):

   ```sh
   git checkout main && git pull
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin vX.Y.Z
   ```

   Pushing a tag is outward-facing and irreversible for anyone who fetches
   it — confirm with the user before running the `git push origin vX.Y.Z`
   step, same as any other push.

## Git

Standard PR-based workflow (see `.github/CONTRIBUTING.md`). This repo
follows the user's global git-safety rules: no history rewriting on anything
that might be published, no force-push/reset/clean without explicit
confirmation, prefer `git revert` for undoing.
