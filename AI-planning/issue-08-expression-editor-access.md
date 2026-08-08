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
document object's property via `Gui.ExpressionBinding(widget).bind(obj,
"PropertyPath")` (confirmed against `src/Gui/ExpressionBindingPy.cpp` and
`src/Gui/SpinBox.cpp` in the FreeCAD source). A repo-wide search confirms
none of these widgets are ever bound (`Dialog.py` has no calls to `.bind(`)
— the fields are populated with plain
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
corresponding property on `vobj.Object` via the `Gui.ExpressionBinding`
wrapper, e.g. `Gui.ExpressionBinding(self.form.sbHeight).bind(vobj.Object,
"Size")`, `Gui.ExpressionBinding(self.form.sbOffset).bind(vobj.Object,
"Offset")`, and the `sbX`/`sbY`/`sbZ` boxes to `Placement.Base.x/y/z`.

Note: `QuantitySpinBox.bind(...)` is *not* itself callable from Python —
binding must go through the `Gui.ExpressionBinding(widget).bind(obj, "Path")`
wrapper (`src/Gui/ExpressionBindingPy.cpp`). This is confirmed, working
precedent used throughout FreeCAD's own task panels, e.g.
`Part/BasicShapes/ViewProviderShapes.py`
(`Gui.ExpressionBinding(self.form.tubeOuterRadius).bind(object,
"OuterRadius")`), `Part/AttachmentEditor/TaskAttachmentEditor.py`, and
`Assembly/JointObject.py`. The latter two also confirm dotted sub-property
paths like `Placement.Base.x` / `AttachmentOffset.Base.x` resolve correctly
through this wrapper, so the `sbX`/`sbY`/`sbZ` binding is real, precedented
syntax and not speculative.

This is the same mechanism FreeCAD's own Property Editor and several stock
task panels use, so it lights up the "fx" icon and the `=` shortcut with no
new UI. It's worth a quick in-FreeCAD smoke test that a bound expression
survives `accept()` — `Dialog.py`'s edit-mode `accept()` writes a literal
value via `Gui.doCommand` before calling `recompute()` at the end
(`Dialog.py:374`), and FreeCAD re-applies `ExpressionEngine` bindings on every
recompute (`Document.cpp`), so the literal write should be immediately
superseded by the live expression — but this interaction is worth confirming
empirically rather than assumed from source alone.

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
- Must use the `Gui.ExpressionBinding(widget).bind(...)` wrapper rather than
  calling `.bind()` directly on the spin box (see note above) — a small but
  easy-to-get-wrong detail when implementing.

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
- Substantially more work relative to the size of the original request: a
  new dialog affordance plus scratch-object lifecycle management.
- The cleanup risk is real but not novel — `Assembly/JointObject.py` already
  implements essentially this pattern in FreeCAD core: it creates a real
  object under `App.setActiveTransaction(...)` at dialog-open time, binds
  spin boxes to it immediately, and on `reject()` aborts the transaction to
  clean up on cancel/ESC/crash paths too (`JointObject.py:1558-1639`). That
  precedent could be followed directly instead of inventing new lifecycle
  handling, which lowers the risk below what's implied above — though it's
  still more moving parts than Option A.

## Option C — Fix Edit mode only (Option A) and document the Create-mode limitation

Apply Option A's binding fix for the Edit dialog since it's low-risk and
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
