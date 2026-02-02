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

"""Provides functions to create RadialShapeString objects."""

import FreeCAD as App
import draftutils.gui_utils as gui_utils

from .Object import RadialShapeString

if App.GuiUp:
    from .View import ViewProviderRadialShapeString


def make_radialshapestring(Strings,
                           FontFile,
                           Size=100,
                           Radius=50,
                           StartAngle=0,
                           AngleStep=30,
                           Tangential=True,
                           RotationDirection="CounterClockwise",
                           StringRotation=0):
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
    obj.RotationDirection = str(RotationDirection)
    obj.StringRotation = StringRotation

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

