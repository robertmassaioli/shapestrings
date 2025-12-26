# SPDX-License-Identifier: LGPL-2.1-only
# SPDX-FileNotice: Part of the ShapeStrings addon.

################################################################################
#                                                                              #
#   Copyright (c) 2025 Robert Massaioli                                        #
#                                                                              #
#   This library is free software; you can redistribute it and/or modify it    #
#   under the terms of the GNU Lesser General Public License as published      #
#   by the Free Software Foundation; either version 2.1 of the License, or     #
#   (at your option) any later version.                                        #
#                                                                              #
#   This library is distributed in the hope that it will be useful,            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                       #
#                                                                              #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public License   #
#   along with this library; if not, write to the Free Software Foundation,    #
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA           #
#                                                                              #
################################################################################

"""Provides functions to create SpacedShapeString objects."""

import FreeCAD as App
import draftutils.gui_utils as gui_utils

from .Object import SpacedShapeString

if App.GuiUp:
    from .View import ViewProviderSpacedShapeString


def make_spacedshapestring(Strings, FontFile, Size=100, Offset=10, UseBoundingBox=False):
    """SpacedShapeString(Strings,FontFile,[Height],[Offset],[UseBoundingBox])

    Turns a list of text strings into a single Compound Shape, with each
    string rendered using the given font and separated in the x-direction
    by the specified offset (and optionally using each string's bounding
    box width to compute spacing).
    """
    App.Console.PrintMessage("Creating SpacedShapeString object...\n")

    if not App.ActiveDocument:
        App.Console.PrintError("No active document. Aborting\n")
        return

    obj = App.ActiveDocument.addObject(
        "Part::Part2DObjectPython",
        "SpacedShapeString"
    )
    SpacedShapeString(obj)
    # Core spaced properties
    obj.Strings = list(Strings)
    obj.FontFile = FontFile
    obj.Size = Size
    obj.Offset = Offset
    obj.UseBoundingBox = bool(UseBoundingBox)

    # Print all object properties to the FreeCAD console
    App.Console.PrintMessage("SpacedShapeString properties:\n")
    for prop in obj.PropertiesList:
        try:
            val = getattr(obj, prop)
        except Exception as e:
            val = "<unreadable: {}>".format(e)
        App.Console.PrintMessage("  {} = {}\n".format(prop, val))


    if App.GuiUp:
        ViewProviderSpacedShapeString(obj.ViewObject)
        gui_utils.format_object(obj)
        obrep = obj.ViewObject
        if "PointSize" in obrep.PropertiesList:
            obrep.PointSize = 1
        gui_utils.select(obj)

    obj.recompute()

    App.Console.PrintMessage("SpacedShapeString object created successfully.\n")
    return obj

