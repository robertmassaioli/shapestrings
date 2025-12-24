# AdvancedShapestrings (FreeCAD)

## Overview
AdvancedShapestrings adds a new FreeCAD workbench with additional, or improved, Shapestring commands.
## SpacedShapeString — what it is and why use it

Icon: 

![SpacedShapeString icon](./freecad/advanced_shapestrings/resources/icons/Draft_SpacedShapeString.svg)

### What the command does

A way to ensure that different strings are relatively offset from eachother.

The SpacedShapeString object renders one or more strings using a chosen font and arranges strings horizontally with configurable spacing (offset) or with spacing derived from each string's bounding box width.

Resulting shapes are standard FreeCAD objects and can be used in Part/PartDesign workflows.

### Properties

  - `Strings` (list of string lines)
  - `FontFile` (path to .ttf/.otf)
  - `Size` (font size)
  - `Offset` (spacing between strings)
  - `UseBoundingBox` 
    - False => Each String starts at a consistent offset from the last string
    - True = The gap between strings is always a constant `Offset`, instead of  the distance between the strings themselves.

## Using the tool (GUI)
1. Switch to the Advanced Shapestrings workbench.
2. Choose the "Spaced shape from text" tool.
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

make_spacedshapestring(["String1", "String2"], "/path/to/font.ttf", Size=10, Offset=5, UseBoundingBox=False)
```

## Installation

### Via the Addon Manager

TODO

### User install (for development)
Copy the module directory into FreeCAD's Mod folder, then restart FreeCAD.

macOS example:

```bash
cd ~/Library/Application\ Support/FreeCAD/Mod
ln -s /path/to/this/repo AdvancedShapestrings
```

Restart FreeCAD. The tool appears in the Draft toolbox.