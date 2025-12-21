# ***************************************************************************
# *   Copyright (c) 2009, 2010 Yorik van Havre <yorik@uncreated.net>        *
# *   Copyright (c) 2009, 2010 Ken Cline <cline@frii.com>                   *
# *   Copyright (c) 2020 FreeCAD Developers                                 *
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
"""Provides functions to create SpacedShapeString objects."""
## @package make_shapestring
# \ingroup draftmake
# \brief Provides functions to create SpacedShapeString objects.


## \addtogroup draftmake
# @{
import FreeCAD as App
import draftutils.gui_utils as gui_utils

from freecad.advanced_shapestrings.spaced_shapestring import SpacedShapeString

if App.GuiUp:
    from draftviewproviders.view_shapestring import ViewProviderShapeString


def make_spacedshapestring(Strings, FontFile, Size=100, Offset=10, UseBoundingBox=False):
    """SpacedShapeString(Strings,FontFile,[Height],[Offset],[UseBoundingBox])

    Turns a list of text strings into a single Compound Shape, with each
    string rendered using the given font and separated in the x-direction
    by the specified offset (and optionally using each string's bounding
    box width to compute spacing).
    """
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

    if App.GuiUp:
        ViewProviderShapeString(obj.ViewObject)
        gui_utils.format_object(obj)
        obrep = obj.ViewObject
        if "PointSize" in obrep.PropertiesList:
            obrep.PointSize = 1
        gui_utils.select(obj)
    obj.recompute()
    return obj


makeSpacedShapeString = make_spacedshapestring


## @}
