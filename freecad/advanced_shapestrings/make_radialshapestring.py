# ***************************************************************************
# *   Copyright (c) 2025 Robert Massaioli                                   *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""Provides functions to create RadialShapeString objects."""
## @package make_radialshapestring
# \ingroup draftmake
# \brief Provides functions to create RadialShapeString objects.


## \addtogroup draftmake
# @{
import FreeCAD as App
import draftutils.gui_utils as gui_utils

from .radial_shapestring import RadialShapeString

if App.GuiUp:
    from .view_radialshapestring import ViewProviderRadialShapeString


def make_radialshapestring(Strings,
                           FontFile,
                           Size=100,
                           Radius=50,
                           StartAngle=0,
                           AngleStep=30,
                           Tangential=True):
    """RadialShapeString(Strings, FontFile,
                         [Size], [Radius], [StartAngle], [AngleStep], [Tangential])

    Turns a list of text strings into a single Compound Shape, with each
    string rendered using the given font and placed on an arc of radius
    `Radius` at angles:

        angle_i = StartAngle + i * AngleStep

    If `Tangential` is True, each string’s baseline is rotated to be
    tangent to the arc at its position; otherwise the baseline stays
    parallel to the global X axis.
    """
    App.Console.PrintMessage("Creating RadialShapeString object...\n")

    if not App.ActiveDocument:
        App.Console.PrintError("No active document. Aborting\n")
        return

    obj = App.ActiveDocument.addObject(
        "Part::Part2DObjectPython",
        "RadialShapeString"
    )
    RadialShapeString(obj)

    # Core radial properties
    obj.Strings = list(Strings)
    obj.FontFile = FontFile
    obj.Size = Size
    obj.Radius = Radius
    obj.StartAngle = StartAngle
    obj.AngleStep = AngleStep
    obj.Tangential = bool(Tangential)

    # Print all object properties to the FreeCAD console
    App.Console.PrintMessage("RadialShapeString properties:\n")
    for prop in obj.PropertiesList:
        try:
            val = getattr(obj, prop)
        except Exception as e:
            val = "<unreadable: {}>".format(e)
        App.Console.PrintMessage("  {} = {}\n".format(prop, val))

    if App.GuiUp:
        ViewProviderRadialShapeString(obj.ViewObject)
        gui_utils.format_object(obj)
        obrep = obj.ViewObject
        if "PointSize" in obrep.PropertiesList:
            obrep.PointSize = 1
        gui_utils.select(obj)

    obj.recompute()

    App.Console.PrintMessage("RadialShapeString object created successfully.\n")
    return obj


makeRadialShapeString = make_radialshapestring


## @}
