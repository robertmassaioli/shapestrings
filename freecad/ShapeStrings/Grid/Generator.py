# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2009 Yorik van Havre <yorik@uncreated.net>
# SPDX-FileCopyrightText: 2009 Ken Cline <cline@frii.com>
# SPDX-FileCopyrightText: 2020 FreeCAD Developers
# SPDX-FileCopyrightText: 2025 Robert Massaioli
# SPDX-FileNotice: Part of the ShapeStrings addon.

################################################################################
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

"""Provides functions to create GridShapeString objects."""

import FreeCAD as App
import draftutils.gui_utils as gui_utils

from .Object import GridShapeString

if App.GuiUp:
    from .View import ViewProviderGridShapeString


def make_gridshapestring(Strings, FontFile, Size=100, Columns=3, ColumnOffset=10, RowOffset=15, UseBoundingBox=False):
    """GridShapeString(Strings,FontFile,[Height],[Columns],[ColumnOffset],[RowOffset],[UseBoundingBox])

    Turns a list of text strings into a single Compound Shape, wrapped onto
    a 2D grid after the given number of columns, using the given font and
    separated by the given column/row offsets (optionally using each
    string's bounding box to size columns/rows instead of a fixed pitch).
    """
    App.Console.PrintMessage("Creating GridShapeString object...\n")

    if not App.ActiveDocument:
        App.Console.PrintError("No active document. Aborting\n")
        return

    obj = App.ActiveDocument.addObject(
        "Part::Part2DObjectPython",
        "GridShapeString"
    )
    GridShapeString(obj)
    # Core grid properties
    obj.Strings = list(Strings)
    obj.FontFile = FontFile
    obj.Size = Size
    obj.Columns = int(Columns)
    obj.ColumnOffset = ColumnOffset
    obj.RowOffset = RowOffset
    obj.UseBoundingBox = bool(UseBoundingBox)

    # Print all object properties to the FreeCAD console
    App.Console.PrintMessage("GridShapeString properties:\n")
    for prop in obj.PropertiesList:
        try:
            val = getattr(obj, prop)
        except Exception as e:
            val = "<unreadable: {}>".format(e)
        App.Console.PrintMessage("  {} = {}\n".format(prop, val))


    if App.GuiUp:
        ViewProviderGridShapeString(obj.ViewObject)
        gui_utils.format_object(obj)
        obrep = obj.ViewObject
        if "PointSize" in obrep.PropertiesList:
            obrep.PointSize = 1
        gui_utils.select(obj)

    obj.recompute()

    App.Console.PrintMessage("GridShapeString object created successfully.\n")
    return obj
