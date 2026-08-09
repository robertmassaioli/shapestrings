# Changelog

All notable changes to ShapeStrings are documented in this file.

## [0.3.0] — 2026-08-09

### Added

- **Grid ShapeString** — a new `Grid/` tool (`Object.py`, `View.py`,
  `Dialog.py`, `Command.py`, `Generator.py`) that wraps a list of strings
  onto a 2D grid of rows/columns, alongside the existing `Spaced` and
  `Radial` tools. Adds `Strings` (row-major), `Columns`, `ColumnOffset`,
  `RowOffset`, and `UseBoundingBox` properties. A blank entry in `Strings`
  still reserves its grid position, so grids can have gaps (e.g. an
  L-shaped layout). The task panel exposes a genuine 2D table for entering
  strings that reshapes live as `Columns` changes, with Add/Remove Row
  controls. (#14, resolves #9's grid-layout request)
- Expression-editor access on the **Grid** and **Spaced** edit dialogs —
  the numeric spin boxes (position, size, offsets, and for Grid, columns)
  are now bound to their document object properties via
  `Gui.ExpressionBinding`, so the `=` shortcut and "fx" icon open FreeCAD's
  expression editor directly from the task panel in edit mode. Create mode
  is intentionally left unbound (no object exists yet at dialog-open time).
  (#12, resolves #8)
- `Misc/StringGeometry.py` — a shared helper factoring out the per-string
  wire/face/scale/oblique/justify pipeline, used by the new Grid tool.
  `Spaced` and `Radial` are deliberately left on their own existing copies
  rather than retrofitted onto it, since the shared helper fixes an
  ordering bug (`ScaleToSize` being a no-op) that would change already
  saved documents' rendered geometry if applied retroactively.
- `bump_version.py` — a script to keep the version number in sync across
  `Misc/Version.py`, `package.xml`, and `pyproject.toml`.
- `AGENTS.md` — orientation for AI coding agents working in this
  repository, including guidance on referencing the FreeCAD source tree
  alongside this addon.

### Fixed

- Corrected SPDX license identifiers and added missing attributions across
  source files.
- Corrected the overall project license ID.
- Corrected `AGENTS.md`'s guidance on symlinking into FreeCAD's `Mod/`
  directory — the addon's namespace-package loader needs
  `Mod/<Name>/freecad/ShapeStrings/init_gui.py`, so the repository root
  must be linked in, not the inner `freecad/ShapeStrings` folder alone.
  Also notes that FreeCAD can keep a separate `Mod/` per major version, so
  a symlink in the wrong one fails silently with no addon and no error.

### Documentation

- Added a Grid preview screenshot and a "Preview" section to
  `Documentation/Commands/Grid.md`, and added Grid to the README's tool
  showcase table.
- Added `AI-planning/` proposal documents for issues #8 (expression editor
  access) and #9 (grid columns/interline spacing), each verified against
  the FreeCAD source before implementation.
