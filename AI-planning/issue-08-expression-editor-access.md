# Issue #8: Missing access to expression editor from SpacedShapeString dialog

**Link:** https://github.com/robertmassaioli/shapestrings/issues/8

## Problem statement

The `SpacedShapeString` task panel (`freecad/ShapeStrings/Spaced/Dialog.py`)
does not let the user open FreeCAD's expression editor for its numeric
fields — not even by typing `=`, which normally triggers it automatically on
a bound `Gui::QuantitySpinBox`. The only way to attach an expression today is
to close the dialog and edit the property directly in the Property Editor.

## Current behavior (for reference)

`Spaced.ui` (`freecad/ShapeStrings/Resources/Interfaces/Spaced.ui`) uses
`Gui::QuantitySpinBox` for `sbX`, `sbY`, `sbZ`, `sbHeight`, and `sbOffset` —
the same widget class FreeCAD's native property editor uses, which *does*
support inline expression editing, but only once it is explicitly bound to a
document object's property via `.bind(obj, "PropertyPath")`. A repo-wide
search confirms none of these widgets are ever bound
(`Dialog.py` has no calls to `.bind(`) — the fields are populated with plain
`rawValue`s and read back with `App.Units.Quantity(...).Value` in
`createObject()` (create mode, `Dialog.py:284-336`) and `accept()` (edit mode,
`Dialog.py:355-382`). That absence of binding is why the `=` shortcut and
"fx" icon never appear.

Note the dialog is shared by two panels with different constraints:
`SpacedShapeStringTaskPanelCmd` (creation — no object exists yet) and
`SpacedShapeStringTaskPanelEdit` (editing — `vobj.Object` already exists).

## Option A — Bind the QuantitySpinBoxes to the object in Edit mode

In `SpacedShapeStringTaskPanelEdit.__init__` (`Dialog.py:341-353`), after the
base `SpacedShapeStringTaskPanel.__init__` call, bind each spin box to its
corresponding property on `vobj.Object`, e.g.
`self.form.sbHeight.bind(vobj.Object, "Size")`,
`self.form.sbOffset.bind(vobj.Object, "Offset")`, and the `sbX`/`sbY`/`sbZ`
boxes to `Placement.Base.x/y/z`. This is the same mechanism FreeCAD's own
Property Editor and several stock task panels use, so it lights up the "fx"
icon and the `=` shortcut with no new UI.

Create mode (`SpacedShapeStringTaskPanelCmd`) has no object yet at dialog-open
time, so binding isn't directly possible there — this option leaves creation
unbound, matching the behavior of many other Draft creation dialogs (e.g.
Line, Wire), and only fixes the *edit* path the screenshots in the issue
focus on.

**Pros**
- Matches the exact idiom FreeCAD itself uses elsewhere — least surprising
  fix, smallest diff, no new dialog widgets or `.ui` changes.
- Confined to `Dialog.py`; no changes to `Object.py` or `Spaced.ui` needed.

**Cons**
- Only fixes the Edit-mode dialog, not the Create-mode dialog the reporter's
  first screenshot may also apply to — worth confirming with the reporter
  which flow they hit.
- The exact `.bind()` call signature/behavior for sub-properties like
  `Placement.Base.x` has shifted slightly across FreeCAD versions, so it
  needs verifying against the FreeCAD version(s) this addon targets.

## Option B — Add an explicit expression-editor affordance that also works at creation time

Give every numeric field a visible trigger (icon/button) that opens
`Gui::Dialog::DlgExpressionInput` directly from `Dialog.py`, independent of
FreeCAD's implicit "type `=`" binding gesture. To make this work in Create
mode too (where no object exists yet), create a hidden scratch
`App::FeaturePython` object when the dialog opens purely to host the
expression bindings, and discard it on cancel or fold its expressions into
the real object's properties on accept.

**Pros**
- Works uniformly in both Create and Edit dialogs, fully closing the gap the
  reporter describes rather than only half of it.
- An explicit icon is more discoverable than the "hit `=`" convention, which
  not all users know about.

**Cons**
- Substantially more work and risk: the scratch object must be reliably
  cleaned up on every exit path (accept, cancel, ESC, dialog crash) or it
  leaks into the document/undo stack.
- Larger surface area for bugs relative to the size of the original request.

## Option C — Fix Edit mode only (Option A) and document the Create-mode limitation

Apply Option A's `.bind()` fix for the Edit dialog since it's low-risk and
the object already exists there, and explicitly treat Create-mode as
out-of-scope — add a short tooltip or status-bar hint in the create dialog
("Expressions can be set after creation via the Property Editor") instead of
building new infrastructure for it. This mirrors how several native FreeCAD
creation tools behave: values are typed at creation, expressions are added
afterward once the object is in the tree.

**Pros**
- Fastest to ship, lowest risk, no scratch-object lifecycle to manage.
- Consistent with existing FreeCAD precedent for creation-time dialogs.

**Cons**
- Doesn't fully resolve the reporter's stated preference (they explicitly
  didn't want to have to leave the dialog); still requires closing the
  dialog once for parametric values set at creation time, though never again
  afterward since Edit mode would then support expressions directly.

## Recommendation

Option A is the pragmatic first step — it directly fixes the Edit-mode case
shown in the issue's screenshots with minimal risk. Option C packages that
same fix with a small doc/UX note about the Create-mode gap. Option B is only
worth the added complexity if users frequently need expressions bound at
creation time rather than being willing to set them once the object exists.
