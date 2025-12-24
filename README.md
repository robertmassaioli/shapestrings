# AdvancedShapestrings (FreeCAD)

## Overview
AdvancedShapestrings adds a new FreeCAD workbench with additional, or improved, Shapestring commands.
## SpacedShapeString — what it is and why use it

![SpacedShapeString icon](./freecad/advanced_shapestrings/resources/icons/Draft_SpacedShapeString.svg)

- The SpacedShapeString object renders each string using a chosen font and arranges strings horizontally with configurable spacing (offset) or with spacing derived from each string's bounding box width.
- Use it when you need text as true geometry (not annotations), so you can extrude, fillet, boolean-subtract, or otherwise operate on the letters as solids or faces.
- Properties of the created object include:
  - `Strings` (list of string lines)
  - `FontFile` (path to .ttf/.otf)
  - `Size` (font size)
  - `Offset` (spacing between strings)
  - `UseBoundingBox` (bool — derive spacing from bounding boxes)
- Resulting shapes are standard FreeCAD objects and can be used in Part/PartDesign workflows.

## Using the tool (GUI)
1. Switch to the Draft workbench.
2. Choose the "Spaced shape from text" tool (icon: Spaced shape from text).
3. In the task panel:
   - Add, edit or remove strings.
   - Select a font file.
   - Set Size and Offset.
   - Optionally set "Use bounding box" to space strings by their width.
4. Pick the placement point in the 3D view.
5. Click OK to create the SpacedShapeString object in the active document.

## Using from Python (inside FreeCAD)
Example (run in the FreeCAD Python console with an open document):

```python
from freecad.advanced_shapestrings.make import make_spacedshapestring
make_spacedshapestring(["Line1", "Line2"], "/path/to/font.ttf", Size=10, Offset=5, UseBoundingBox=False)
```

## Installation
### User install (simple)
Copy the module directory into FreeCAD's Mod folder, then restart FreeCAD.

macOS example:

```bash
mkdir -p ~/Library/Application\ Support/FreeCAD/Mod
cp -R /path/to/advanced-shapestrings/freecad/advanced_shapestrings \
      ~/Library/Application\ Support/FreeCAD/Mod/AdvancedShapestrings
```

Restart FreeCAD. The tool appears in the Draft toolbox.

### Development install (recommended for contributors)
1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the package and dependencies for local testing:

```bash
pip install -e .
pip install "PySide2>=5.15"  # or PySide6 if your environment/FreeCAD expects Qt6
```

Note: FreeCAD ships its own Python/PySide environment; installing PySide into your system/venv is useful for running unit tests and tools outside the FreeCAD app.

## Troubleshooting
- Error: `'PySide2.QtWidgets.QWidget' object has no attribute 'pteStrings'`  
  Cause: the UI loader returned a widget that does not expose the named child. Fixes:
  - Ensure the UI file `TaskSpacedShapeString.ui` in the repo is present and correct.
  - Use `findChild` as a fallback (code change) to locate widgets by object name.
- Error: `module 'FreeCAD' has no attribute 'activeDraftCommand'`  
  Cause: FreeCAD API differences. Guard uses of `App.activeDraftCommand` with `hasattr` or set `App.activeDraftCommand = None` before calling code that expects it.

## Contributing & License
- Contributions are welcome via pull requests and issues on the repository.
- See `LICENSE` for license terms (LGPL).
- For tests and development, follow the development install steps above.
```// filepath: /Users/robertmassaioli/Code/AdvancedShapestrings/README.md
# AdvancedShapestrings (FreeCAD)

## Overview
AdvancedShapestrings adds an improved "spaced shape from text" tool to FreeCAD's Draft workbench. The tool converts one or more text strings into editable 2D shapes (closed edges/faces) that can be extruded into solids and used in boolean operations (e.g., engraving and cutouts).

## SpacedShapeString — what it is and why use it
- The SpacedShapeString object renders each string using a chosen font and arranges strings horizontally with configurable spacing (offset) or with spacing derived from each string's bounding box width.
- Use it when you need text as true geometry (not annotations), so you can extrude, fillet, boolean-subtract, or otherwise operate on the letters as solids or faces.
- Properties of the created object include:
  - `Strings` (list of string lines)
  - `FontFile` (path to .ttf/.otf)
  - `Size` (font size)
  - `Offset` (spacing between strings)
  - `UseBoundingBox` (bool — derive spacing from bounding boxes)
- Resulting shapes are standard FreeCAD objects and can be used in Part/PartDesign workflows.

## Using the tool (GUI)
1. Switch to the Draft workbench.
2. Choose the "Spaced shape from text" tool (icon: Spaced shape from text).
3. In the task panel:
   - Add, edit or remove strings.
   - Select a font file.
   - Set Size and Offset.
   - Optionally set "Use bounding box" to space strings by their width.
4. Pick the placement point in the 3D view.
5. Click OK to create the SpacedShapeString object in the active document.

## Using from Python (inside FreeCAD)
Example (run in the FreeCAD Python console with an open document):

```python
from freecad.advanced_shapestrings.make import make_spacedshapestring
make_spacedshapestring(["Line1", "Line2"], "/path/to/font.ttf", Size=10, Offset=5, UseBoundingBox=False)
```

## Installation
### User install (simple)
Copy the module directory into FreeCAD's Mod folder, then restart FreeCAD.

macOS example:

```bash
mkdir -p ~/Library/Application\ Support/FreeCAD/Mod
cp -R /path/to/advanced-shapestrings/freecad/advanced_shapestrings \
      ~/Library/Application\ Support/FreeCAD/Mod/AdvancedShapestrings
```

Restart FreeCAD. The tool appears in the Draft toolbox.

### Development install (recommended for contributors)
1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the package and dependencies for local testing:

```bash
pip install -e .
pip install "PySide2>=5.15"  # or PySide6 if your environment/FreeCAD expects Qt6
```

Note: FreeCAD ships its own Python/PySide environment; installing