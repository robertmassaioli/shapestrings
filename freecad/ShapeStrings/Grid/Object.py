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

"""Provides the object code for the GridShapeString object."""

import FreeCAD as App
import Part

from draftutils.translate import translate

from draftobjects.base import DraftObject
from ..Misc.StringGeometry import build_string_shape, compute_measured_cap_height


class GridShapeString(DraftObject):
    """The GridShapeString object - renders multiple strings wrapped onto a
    2D grid of rows and columns."""

    def __init__(self, obj):
        super().__init__(obj, "GridShapeString")
        self.set_properties(obj)

    def set_properties(self, obj):
        """Add properties to the object and set them."""
        properties = obj.PropertiesList

        if "Strings" not in properties:
            _tip = translate("App::Property", "List of text strings to render, row-major. A blank entry leaves that grid position empty")
            obj.addProperty("App::PropertyStringList", "Strings", "Draft", _tip)

        if "Columns" not in properties:
            _tip = translate("App::Property", "Number of columns before wrapping to a new row")
            obj.addProperty("App::PropertyInteger", "Columns", "Draft", _tip)
            obj.Columns = 3

        if "ColumnOffset" not in properties:
            _tip = translate("App::Property", "Horizontal spacing between columns")
            obj.addProperty("App::PropertyLength", "ColumnOffset", "Draft", _tip)
            obj.ColumnOffset = 10.0

        if "RowOffset" not in properties:
            _tip = translate("App::Property", "Vertical spacing between rows")
            obj.addProperty("App::PropertyLength", "RowOffset", "Draft", _tip)
            obj.RowOffset = 15.0

        if "UseBoundingBox" not in properties:
            _tip = translate("App::Property", "Use each string's bounding box to size columns/rows, adding the column/row offset as the gap")
            obj.addProperty("App::PropertyBool", "UseBoundingBox", "Draft", _tip)
            obj.UseBoundingBox = False

        if "FontFile" not in properties:
            _tip = translate("App::Property", "Font file name")
            obj.addProperty("App::PropertyFile", "FontFile", "Draft", _tip)

        if "Size" not in properties:
            _tip = translate("App::Property", "Height of text")
            obj.addProperty("App::PropertyLength", "Size", "Draft", _tip)

        if "Justification" not in properties:
            _tip = translate("App::Property", "Horizontal and vertical alignment")
            obj.addProperty("App::PropertyEnumeration", "Justification", "Draft", _tip)
            obj.Justification = ["Top-Left", "Top-Center", "Top-Right",
                                 "Middle-Left", "Middle-Center", "Middle-Right",
                                 "Bottom-Left", "Bottom-Center", "Bottom-Right"]
            obj.Justification = "Bottom-Left"

        if "JustificationReference" not in properties:
            _tip = translate("App::Property", "Height reference used for justification")
            obj.addProperty("App::PropertyEnumeration", "JustificationReference", "Draft", _tip)
            obj.JustificationReference = ["Cap Height", "Shape Height"]
            obj.JustificationReference = "Cap Height"

        if "KeepLeftMargin" not in properties:
            _tip = translate("App::Property", "Keep left margin and leading white space when justification is left")
            obj.addProperty("App::PropertyBool", "KeepLeftMargin", "Draft", _tip)
            obj.KeepLeftMargin = False

        if "ScaleToSize" not in properties:
            _tip = translate("App::Property", "Scale to ensure cap height is equal to size")
            obj.addProperty("App::PropertyBool", "ScaleToSize", "Draft", _tip)
            obj.ScaleToSize = True

        if "Tracking" not in properties:
            _tip = translate("App::Property", "Inter-character spacing")
            obj.addProperty("App::PropertyDistance", "Tracking", "Draft", _tip)

        if "ObliqueAngle" not in properties:
            _tip = translate("App::Property", "Oblique (slant) angle")
            obj.addProperty("App::PropertyAngle", "ObliqueAngle", "Draft", _tip)

        if "MakeFace" not in properties:
            _tip = translate("App::Property", "Fill letters with faces")
            obj.addProperty("App::PropertyBool", "MakeFace", "Draft", _tip)
            obj.MakeFace = True

        if "Fuse" not in properties:
            _tip = translate("App::Property", "Fuse faces if faces overlap, usually not required (can be very slow)")
            obj.addProperty("App::PropertyBool", "Fuse", "Draft", _tip)
            obj.Fuse = False

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        # Ensure all properties exist after document restoration
        self.set_properties(obj)

    def execute(self, obj):
        """Generate the compound shape from the list of strings, wrapped onto a grid."""
        if self.props_changed_placement_only():
            obj.positionBySupport()
            self.props_changed_clear()
            return

        if obj.Strings and obj.FontFile:
            plm = obj.Placement
            columns = max(1, int(obj.Columns))

            measured_cap_height = compute_measured_cap_height(obj.FontFile, obj.Size, obj.Tracking)
            justification_cap_height = obj.Size if obj.ScaleToSize else measured_cap_height

            # Render every string once, remembering which grid cell (row,
            # col) it belongs to. A blank string still consumes a cell -
            # that's what lets a grid have gaps instead of being a flat
            # list of only non-empty entries like SpacedShapeString.
            cells = []
            max_row = -1
            for index, string_text in enumerate(obj.Strings):
                row = index // columns
                col = index % columns
                max_row = max(max_row, row)

                shapes = build_string_shape(
                    string_text,
                    obj.FontFile,
                    obj.Size,
                    obj.Tracking,
                    obj.MakeFace,
                    obj.Fuse,
                    obj.ScaleToSize,
                    measured_cap_height,
                    obj.ObliqueAngle,
                    obj.Justification,
                    obj.JustificationReference,
                    obj.KeepLeftMargin,
                    justification_cap_height,
                )
                if shapes:
                    bbox = Part.Compound(shapes).optimalBoundingBox()
                    cells.append((row, col, shapes, bbox))

            if cells:
                column_offset = float(obj.ColumnOffset)
                row_offset = float(obj.RowOffset)

                if obj.UseBoundingBox:
                    col_width = {}
                    row_height = {}
                    for row, col, _shapes, bbox in cells:
                        col_width[col] = max(col_width.get(col, 0.0), bbox.XLength)
                        row_height[row] = max(row_height.get(row, 0.0), bbox.YLength)

                    col_x = {}
                    cursor = 0.0
                    for col in range(columns):
                        col_x[col] = cursor
                        cursor += col_width.get(col, 0.0) + column_offset

                    row_y = {}
                    cursor = 0.0
                    for row in range(max_row + 1):
                        row_y[row] = cursor
                        cursor -= row_height.get(row, 0.0) + row_offset
                else:
                    col_x = {col: col * column_offset for col in range(columns)}
                    # Row 0 is the first entry in Strings and sits at the
                    # insertion point; later rows step in -Y so the grid
                    # reads top-to-bottom like the Strings list itself.
                    row_y = {row: -row * row_offset for row in range(max_row + 1)}

                all_shapes = []
                for row, col, shapes, _bbox in cells:
                    offset_vec = App.Vector(col_x[col], row_y[row], 0)
                    for shape in shapes:
                        shape.translate(offset_vec)
                    all_shapes.extend(shapes)

                obj.Shape = Part.Compound(all_shapes)
            else:
                App.Console.PrintWarning(translate("draft", "GridShapeString: strings have no wires") + "\n")

            obj.Placement = plm

        obj.positionBySupport()
        self.props_changed_clear()

    def onChanged(self, obj, prop):
        self.props_changed_store(prop)
