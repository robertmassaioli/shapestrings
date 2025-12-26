# ShapeStrings (FreeCAD)

## Overview

ShapeStrings adds a new FreeCAD workbench with additional, or improved, Shapestring commands.

## Compatability

This Workbench was developed against FreeCad version 1.0.2 and is designed to work with that version and all subsequent versions.

## SpacedShapeString — what it is and why use it

Icon: 

![SpacedShapeString icon](./freecad/ShapeStrings/resources/icons/AdvancedShapestrings_SpacedShapeString.svg)

### Screenshot

![Spaced Shape String Screenshot](./docs/screenshots/spaced-shapestring-example.png)

### What the Command Does

The **SpacedShapeString** command lets you create several text strings—like numbers or labels—and place them in a line with even spacing between each one. The offset you choose always applies, either setting where each string starts relative to the last, or keeping the visible gap between strings constant.

For example, if you want to display numbers 1 through 11 across a face for a Pad, you’d usually need to create and position each number separately with the **Draft ShapeString** command. With **SpacedShapeString**, that same pattern can be done in one easy step.

The resulting shapes are standard FreeCAD objects that work seamlessly with both **Part** and **PartDesign** tools.

### Properties

- **Strings**  
  List of text entries to render, in order, as separate strings.

- **FontFile**  
  Path to the font file to use (for example, a `.ttf` or `.otf` file).

- **Size**  
  Height of the rendered text, in model units (the same meaning as the Size property of a standard Draft ShapeString).

- **Offset**  
  Horizontal spacing value applied between strings. This value is always used when positioning each subsequent string.

- **UseBoundingBox**  
  Controls how the offset is interpreted when laying out the strings:
  - **False**: Each string’s insertion point is placed at a fixed offset from the previous string’s insertion point, regardless of character widths.  
  - **True**: The visible gap between the end of one string and the start of the next is kept equal to the offset, using each string’s bounding box to measure its width.

### SpacedShapeString – example use cases

- **Slot numbering**  
  Numbering individual slots, pockets, or cavities along a plate or rail so each feature has a clear index for assembly or inspection.  

- **Serial ID rows**  
  Creating a row of serial numbers or IDs on a nameplate, tag strip, or terminal block that will be engraved or embossed.  

- **Connector edge labels**  
  Laying out repeated text labels (e.g. “IN”, “OUT”, “GND”, “+5V”) along the edge of a PCB or electronics enclosure.  

- **Process step markers**  
  Generating dimension or step labels (“Step 1”, “Step 2”, …) along a process panel or jig to guide an operator.  

- **Linear scale text**  
  Producing evenly spaced text for ruler‑like scales, linear indicators, or calibration bars on a straight edge.  

- **Decorative text bands**  
  Creating decorative repeated words or phrases along a straight band that will later be wrapped or mapped onto a surface.  

## RadialShapeString — what it is and why use it

Icon: 

![RadialShapeString icon](./freecad/ShapeStrings/resources/icons/AdvancedShapestrings_RadialShapeString.svg)

### Screenshot

![Radial Shape String Screenshot](./docs/screenshots/radial-shapestring-example.png)

### What the Command Does

The **RadialShapeString** command lets you create several text strings—such as numbers for a dial or labels around a bolt circle—and place them on a circular arc around a common center point. You control the radius, starting angle, and angular step, so each string lands at a predictable polar position.

Strings can be oriented tangentially to the circle (ideal for gauges and knobs) or kept horizontal for documentation‑style layouts. As with SpacedShapeString, the result is a regular FreeCAD shape object that works with **Part** and **PartDesign** operations for engraving or embossing.

### Properties

- **Strings**  
  List of text entries to render, each placed at a different angle around the center.

- **FontFile**  
  Path to the font file to use (for example, a `.ttf` or `.otf` file).

- **Size**  
  Height of the rendered text, in model units.

- **Radius**  
  Distance from the center point to the text baseline.

- **StartAngle**  
  Angle (in degrees) for the first string. By convention, `0°` lies along the +X axis.

- **AngleStep**  
  Angular increment (in degrees) between successive strings.

- **Tangential**  
  When **True**, each string is rotated so its baseline is tangent to the circle; when **False**, all text remains parallel to the global X axis.

- **RotationDirection**  
  Direction in which angles advance when laying out strings: **CounterClockwise** or **Clockwise**.

- **StringRotation**  
  Extra rotation angle (in degrees) applied uniformly to every string, after tangential or horizontal alignment.

### RadialShapeString – example use cases

- **Dial face labels**  
  Labeling gauge or dial faces (e.g. “0, 10, 20, …” or “LOW, NORM, HIGH”) around a circular pointer indicator.  

- **Bolt‑circle notes**  
  Adding bolt‑circle annotations (e.g. “8x M8”, “Ø10 THRU”) equally spaced around a flange or hub.  

- **Compass / direction marks**  
  Creating compass roses or directional markers (“N, NE, E, …”) on navigation instruments or panel graphics.  

- **Rotary index positions**  
  Marking positions around a rotary switch, indexing plate, or turret (e.g. “1–12”) for repeatable angle settings.  

- **Knob legends**  
  Designing radial legends around knobs, volume controls, or selector dials on audio and industrial equipment.  

- **Circular badge text**  
  Generating circular text for badges, coins, medallions, or ornamental rings where wording must follow a circle.

## Using the tools (GUI)

### SpacedShapeString
1. Switch to the Shapestrings workbench.  
2. Choose the "Spaced shape from text" tool.  
3. In the task panel:
   - Add, edit or remove strings.
   - Select a font file.
   - Set Size and Offset.
   - Optionally set "Use bounding box" to space strings by their width.
4. Pick the placement point in the 3D view.  
5. Click OK to create the SpacedShapeString object in the active document.

### RadialShapeString
1. Switch to the Shapestrings workbench.  
2. Choose the "Radial shape from text" tool.  
3. In the task panel:
   - Add, edit or remove strings.
   - Select a font file.
   - Set Size and Radius.
   - Adjust Start angle and Angle step.
   - Choose Tangential on/off, Rotation direction, and optional String rotation.
4. Pick the center point in the 3D view.  
5. Click OK to create the RadialShapeString object in the active document.

## Using from Python (inside FreeCAD)
Example (run the following examples in the FreeCAD Python console with an open document).

### Linear Spaced text

```python
from freecad.ShapeStrings.make_spacedshapestring import make_spacedshapestring

make_spacedshapestring(["String1", "String2"], "/path/to/font.ttf", Size=10, Offset=5, UseBoundingBox=False)
```

### Radial Spaced text

```python
from freecad.ShapeStrings.make_radialshapestring import make_radialshapestring

make_radialshapestring(
    ["1", "2", "3", "4", "5"],
    "/path/to/font.ttf",
    Size=4,
    Radius=50,
    StartAngle=0,
    AngleStep=30,
    Tangential=True,
    RotationDirection="CounterClockwise",
    StringRotation=0,
)
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