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

"""Provides the object code for the SpacedShapeString object."""
## @package spaced_shapestring
# \ingroup draftobjects
# \brief Provides the object code for the SpacedShapeString object.

## \addtogroup draftobjects
# @{
import math
from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCAD as App
import Part

from draftgeoutils import faces
from draftutils.messages import _wrn, _msg, _toolmsg
from draftutils.translate import translate

from draftobjects.base import DraftObject
from .justification import justification_vector


class SpacedShapeString(DraftObject):
    """The SpacedShapeString object - renders multiple strings with x-direction spacing"""

    def __init__(self, obj):
        super().__init__(obj, "SpacedShapeString")
        self.set_properties(obj)

    def set_properties(self, obj):
        """Add properties to the object and set them."""
        properties = obj.PropertiesList

        if "Strings" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "List of text strings to render")
            obj.addProperty("App::PropertyStringList", "Strings", "Draft", _tip)

        if "Offset" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "X-direction offset between each string")
            obj.addProperty("App::PropertyLength", "Offset", "Draft", _tip)
            obj.Offset = 10.0

        if "UseBoundingBox" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Use bounding box width to calculate spacing between strings")
            obj.addProperty("App::PropertyBool", "UseBoundingBox", "Draft", _tip)
            obj.UseBoundingBox = False

        if "FontFile" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Font file name")
            obj.addProperty("App::PropertyFile", "FontFile", "Draft", _tip)

        if "Size" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Height of text")
            obj.addProperty("App::PropertyLength", "Size", "Draft", _tip)

        if "Justification" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Horizontal and vertical alignment")
            obj.addProperty("App::PropertyEnumeration", "Justification", "Draft", _tip)
            obj.Justification = ["Top-Left", "Top-Center", "Top-Right",
                                 "Middle-Left", "Middle-Center", "Middle-Right",
                                 "Bottom-Left", "Bottom-Center", "Bottom-Right"]
            obj.Justification = "Bottom-Left"

        if "JustificationReference" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Height reference used for justification")
            obj.addProperty("App::PropertyEnumeration", "JustificationReference", "Draft", _tip)
            obj.JustificationReference = ["Cap Height", "Shape Height"]
            obj.JustificationReference = "Cap Height"

        if "KeepLeftMargin" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Keep left margin and leading white space when justification is left")
            obj.addProperty("App::PropertyBool", "KeepLeftMargin", "Draft", _tip)
            obj.KeepLeftMargin = False

        if "ScaleToSize" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Scale to ensure cap height is equal to size")
            obj.addProperty("App::PropertyBool", "ScaleToSize", "Draft", _tip)
            obj.ScaleToSize = True

        if "Tracking" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Inter-character spacing")
            obj.addProperty("App::PropertyDistance", "Tracking", "Draft", _tip)

        if "ObliqueAngle" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Oblique (slant) angle")
            obj.addProperty("App::PropertyAngle", "ObliqueAngle", "Draft", _tip)

        if "MakeFace" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Fill letters with faces")
            obj.addProperty("App::PropertyBool", "MakeFace", "Draft", _tip)
            obj.MakeFace = True

        if "Fuse" not in properties:
            _tip = QT_TRANSLATE_NOOP("App::Property", "Fuse faces if faces overlap, usually not required (can be very slow)")
            obj.addProperty("App::PropertyBool", "Fuse", "Draft", _tip)
            obj.Fuse = False

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        # Ensure all properties exist after document restoration
        self.set_properties(obj)

    def execute(self, obj):
        """Generate the compound shape from the list of strings."""
        if self.props_changed_placement_only():
            obj.positionBySupport()
            self.props_changed_clear()
            return

        if obj.Strings and obj.FontFile:
            plm = obj.Placement
            all_shapes = []
            x_offset = App.Units.Quantity(0, App.Units.Length)  # 0 mm

            # Pre-calculate justification vector once (same for all strings)
            # Create a test shape to get justification parameters
            cap_char = Part.makeWireString("M", obj.FontFile, obj.Size, obj.Tracking)[0]
            cap_height = Part.Compound(cap_char).BoundBox.YMax
            if obj.ScaleToSize:
                cap_height = obj.Size

            # Process each string in the list
            for string_index, string_text in enumerate(obj.Strings):
                if not string_text:
                    continue

                fill = obj.MakeFace
                if fill is True:
                    # Test a simple letter to know if we have a sticky font or not
                    char = Part.makeWireString("L", obj.FontFile, 1, 0)[0]
                    shapes = self.make_faces(char)
                    if not shapes:
                        fill = False
                    else:
                        fill = sum([shape.Area for shape in shapes]) > 0.03\
                                and math.isclose(Part.Compound(char).BoundBox.DiagonalLength,
                                                 Part.Compound(shapes).BoundBox.DiagonalLength,
                                                 rel_tol=1e-7)

                # Generate wire representation for this string
                chars = Part.makeWireString(string_text, obj.FontFile, obj.Size, obj.Tracking)
                string_shapes = []

                for char in chars:
                    if fill is False:
                        string_shapes.extend(char)
                    elif char:
                        string_shapes.extend(self.make_faces(char))

                if string_shapes:
                    # Create compound for this string
                    if fill and obj.Fuse:
                        ss_shape = string_shapes[0].fuse(string_shapes[1:])
                        ss_shape = faces.concatenate(ss_shape)
                    else:
                        ss_shape = Part.Compound(string_shapes)

                    # Apply scaling and oblique angle transformations
                    if obj.ScaleToSize:
                        ss_shape.scale(obj.Size / cap_height)

                    if obj.ObliqueAngle:
                        if -80 <= obj.ObliqueAngle <= 80:
                            mtx = App.Matrix()
                            mtx.A12 = math.tan(math.radians(obj.ObliqueAngle))
                            ss_shape = ss_shape.transformGeometry(mtx)
                        else:
                            wrn = translate("draft", "SpacedShapeString: oblique angle must be in the -80 to +80 degree range") + "\n"
                            App.Console.PrintWarning(wrn)

                    # Apply justification
                    just_vec = justification_vector(
                        ss_shape,
                        cap_height,
                        obj.Justification,
                        obj.JustificationReference,
                        obj.KeepLeftMargin,
                    )
                    shapes = ss_shape.SubShapes
                    for shape in shapes:
                        shape.translate(just_vec)

                    # Apply x-direction offset for this string
                    # (first string has no offset applied)
                    if string_index > 0:
                        offset_vec = App.Vector(x_offset, 0, 0)
                        for shape in shapes:
                            shape.translate(offset_vec)

                    # Calculate spacing for next string if UseBoundingBox is enabled
                    _toolmsg("type x_offset: {} repr: {}".format(type(x_offset), repr(x_offset)))
                    _toolmsg("type obj.Offset: {} repr: {}".format(type(obj.Offset), repr(obj.Offset)))

                    # Update x_offset for bounding box width if needed
                    if obj.UseBoundingBox:
                        string_compound = Part.Compound(shapes)
                        bbox = string_compound.optimalBoundingBox()
                        x_offset += App.Units.Quantity(bbox.XLength, App.Units.Length)

                    # Add fixed offset
                    x_offset += obj.Offset

                    all_shapes.extend(shapes)

            if all_shapes:
                obj.Shape = Part.Compound(all_shapes)
            else:
                App.Console.PrintWarning(translate("draft", "SpacedShapeString: strings have no wires") + "\n")

            obj.Placement = plm

        obj.positionBySupport()
        self.props_changed_clear()

    def onChanged(self, obj, prop):
        self.props_changed_store(prop)

    # justification_vector moved to shared module `justification.py`

    def make_faces(self, wireChar):
        """Create faces from wire character representation."""
        wrn = translate("draft", "SpacedShapeString: face creation failed for one character") + "\n"

        wirelist = []
        for w in wireChar:
            compEdges = Part.Compound(w.Edges)
            compEdges = compEdges.connectEdgesToWires()
            if compEdges.Wires[0].isClosed():
                wirelist.append(compEdges.Wires[0])

        if not wirelist:
            App.Console.PrintWarning(wrn)
            return []

        try:
            faces = Part.makeFace(wirelist, "Part::FaceMakerBullseye").Faces
            for face in faces:
                face.validate()
        except Part.OCCError:
            try:
                faces = Part.makeFace(wirelist, "Part::FaceMakerCheese").Faces
                for face in faces:
                    face.validate()
            except Part.OCCError:
                try:
                    faces = Part.makeFace(wirelist, "Part::FaceMakerSimple").Faces
                    for face in faces:
                        face.validate()
                except Part.OCCError:
                    App.Console.PrintWarning(wrn)
                    return []

        for face in faces:
            try:
                if face.normalAt(0, 0).z < 0:
                    face.reverse()
            except Exception:
                pass

        return faces


# Alias for compatibility
_SpacedShapeString = SpacedShapeString

## @}
