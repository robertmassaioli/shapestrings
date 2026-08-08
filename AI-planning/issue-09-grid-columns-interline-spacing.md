# Issue #9: Add columns field and inter-line field to SpacedShapeString

**Link:** https://github.com/robertmassaioli/shapestrings/issues/9

## Problem statement

`SpacedShapeString` currently lays its `Strings` list out along a single row,
offset only in the X direction (`freecad/ShapeStrings/Spaced/Object.py:205-223`).
To arrange strings on a 2D grid (e.g. a plaque of labelled tiles) today, a user
has to either create one `SpacedShapeString` per row, or wrap several of them
in an array and manually reposition each row — which is fragile if the array
size changes parametrically.

The reporter wants two new fields so a single object can describe a full grid:

- A **column count**, after which the layout wraps to a new row.
- An **interline (row) spacing** value, independent from the existing
  horizontal `Offset`.

## Current behavior (for reference)

- `Strings`: `App::PropertyStringList` — flat, ordered list of strings.
- `Offset`: `App::PropertyLength` — fixed X spacing applied between
  consecutive strings, or (if `UseBoundingBox` is true) added on top of each
  string's measured bounding-box width.
- Layout logic lives entirely in `SpacedShapeString.execute()`, which loops
  over `obj.Strings`, builds each string's shape, justifies it, then
  translates it by an accumulating `x_offset`.

## Option A — Extend `SpacedShapeString` in place with `Columns` + `RowSpacing`

Add two properties directly to the existing object in
`Object.py:set_properties()`:

- `Columns` (`App::PropertyInteger`, default `0`, meaning "single row /
  unlimited" — preserves current behavior for existing files).
- `RowSpacing` (`App::PropertyLength`), mirroring `Offset` but applied in Y
  between rows, with an optional reuse of `UseBoundingBox` (or a new
  `UseBoundingBoxRows` bool) to measure row height from each row's tallest
  string instead of a fixed value.

Modify `execute()` (`Object.py:144-225`) to track `row_index = string_index //
Columns` and `col_index = string_index % Columns` when `Columns > 0`, resetting
`x_offset` and accumulating a `y_offset` at each row boundary. Update
`Spaced.ui` and `Dialog.py` to add `sbColumns` (a plain `QSpinBox`) and
`sbRowSpacing` (`Gui::QuantitySpinBox`) alongside the existing `sbOffset`
control, and thread the two new values through `createObject()` /
`SpacedShapeStringTaskPanelEdit.accept()`.

**Pros**
- Single object, fully parametric, matches the reporter's exact ask with the
  smallest surface area.
- `Columns = 0` is backward compatible — existing saved documents and macros
  keep working unchanged.
- No new command, icon, or documentation page needed; `Documentation/Commands/Spaced.md`
  just gains two new property entries.

**Cons**
- `execute()` is already a fairly dense method (justification, bounding-box
  offset accumulation, oblique/scale transforms); adding row-wrapping logic
  makes one method do noticeably more.
- The `Strings` list stays a flat 1D list in the UI (`listStrings` in
  `Spaced.ui`), so users must count entries mentally to know which row a
  given string lands in — no visual grouping unless the dialog is also
  reworked (e.g. inserting row separators or a table widget).
- Conceptually stretches "SpacedShapeString" (a row layout tool) into also
  being a grid tool, which may need clearer property tooltips/docs to avoid
  confusion.

## Option B — New dedicated `GridShapeString` object/command

Follow the existing repo convention of one folder per variant (`Spaced/`,
`Radial/`) and add a `Grid/` module (`Object.py`, `View.py`, `Command.py`,
`Dialog.py`, `Generator.py`) with its own `GridShapeString` object exposing
`Strings`, `Columns`, `ColumnOffset`, `RowOffset`, and `UseBoundingBox`. The
row/column layout math would be extracted from `SpacedShapeString.execute()`
into a small shared helper (e.g. in `Misc/`) so both objects reuse the same
string-rendering/justification code instead of duplicating it outright.

**Pros**
- Leaves the existing `SpacedShapeString` object's behavior and scope
  completely untouched — zero regression risk for current users' saved
  files or workflows.
- A dedicated dialog can be purpose-built for grid input (e.g. a genuine 2D
  table widget instead of a flat list), which is a better editing experience
  than counting into a flat list.
- Matches the project's existing pattern of one focused tool per layout
  style (`Radial` vs `Spaced`), keeping each object's responsibility narrow.

**Cons**
- More upfront work: a new command, icon, `.ui` file, `init_gui.py`
  registration, and documentation page, plus the refactor to share rendering
  code between `Spaced` and `Grid` without duplicating `make_faces()` /
  justification logic.
- Adds a third top-level tool to the workbench's toolbar/menu, increasing the
  surface users need to learn (two ways to lay out multiple strings —
  `Spaced` for one row, `Grid` for many).
- Slower to ship than Option A for what is fundamentally an incremental
  layout capability.

## Option C — Lean on FreeCAD's native `Draft Array` for repetition

Rather than teaching ShapeStrings its own grid math, add a small convenience
command that creates a `Draft` orthogonal array object referencing an
existing `SpacedShapeString`/`ShapeString`, pre-filled with columns/rows and
spacing the user enters once in a lightweight dialog — reusing FreeCAD's
already-parametric, expression-friendly `Draft Array` implementation instead
of re-implementing interval/offset math.

**Pros**
- Minimal new object code in this repo; delegates to a mature, well-tested
  core FreeCAD tool that already supports expressions, fuse options, and
  live interval editing in the Property Editor.
- Much smaller maintenance surface than Options A or B.

**Cons**
- **Does not actually solve the reporter's core request.** `Draft Array`
  clones an *identical* copy of the same shape into each grid cell — it
  cannot vary the text content per cell. The reporter's use case (tiles with
  different labels arranged on a plaque) needs distinct strings per position,
  which `Draft Array` alone cannot express.
- Only useful as a complement to Option A or B (e.g. repeating one already-
  gridded block), not as a standalone fix — worth listing for completeness,
  but it should not be treated as satisfying the issue on its own.

## Recommendation

Option A is the closest match to what was asked (a single, fully parametric
object) and the least code to review; Option B is worth revisiting later only
if the flat-list editing experience in Option A proves too awkward in
practice for large grids.
