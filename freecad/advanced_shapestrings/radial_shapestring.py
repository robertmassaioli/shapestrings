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

"""Provides the object code for the RadialShapeString object."""

import math

import FreeCAD as App
import Part

from draftgeoutils import faces
from draftutils.messages import _wrn

from draftobjects.base import DraftObject
from .justification import justification_vector

from FreeCAD import Qt

translate = Qt.translate


class RadialShapeString(DraftObject):
    """The RadialShapeString object - renders multiple strings arranged on an arc."""

    def __init__(self, obj):
        super().__init__(obj, "RadialShapeString")
        self.set_properties(obj)

    def set_properties(self, obj):
        """Add properties to the object and set them."""
        properties = obj.PropertiesList

        if "Strings" not in properties:
            _tip = translate(
                "App::Property",
                "List of text strings to render around the center point",
            )
            obj.addProperty("App::PropertyStringList", "Strings", "Draft", _tip)

        if "Radius" not in properties:
            _tip = translate(
                "App::Property",
                "Distance from center to text baseline",
            )
            obj.addProperty("App::PropertyLength", "Radius", "Draft", _tip)
            obj.Radius = 50.0

        if "StartAngle" not in properties:
            _tip = translate(
                "App::Property",
                "Starting angle for the first string (0° = +X axis)",
            )
            obj.addProperty("App::PropertyAngle", "StartAngle", "Draft", _tip)
            obj.StartAngle = 0.0

        if "AngleStep" not in properties:
            _tip = translate(
                "App::Property",
                "Angular increment between successive strings",
            )
            obj.addProperty("App::PropertyAngle", "AngleStep", "Draft", _tip)
            obj.AngleStep = 30.0

        if "Tangential" not in properties:
            _tip = translate(
                "App::Property",
                "Rotate each string so its baseline is tangent to the arc. "
                "Uncheck to keep text baseline parallel to the X axis.",
            )
            obj.addProperty("App::PropertyBool", "Tangential", "Draft", _tip)
            obj.Tangential = True

        if "FontFile" not in properties:
            _tip = translate("App::Property", "Font file name")
            obj.addProperty("App::PropertyFile", "FontFile", "Draft", _tip)

        if "Size" not in properties:
            _tip = translate("App::Property", "Height of text")
            obj.addProperty("App::PropertyLength", "Size", "Draft", _tip)

        if "Justification" not in properties:
            _tip = translate(
                "App::Property",
                "Horizontal and vertical alignment",
            )
            obj.addProperty("App::PropertyEnumeration", "Justification", "Draft", _tip)
            obj.Justification = [
                "Top-Left",
                "Top-Center",
                "Top-Right",
                "Middle-Left",
                "Middle-Center",
                "Middle-Right",
                "Bottom-Left",
                "Bottom-Center",
                "Bottom-Right",
            ]
            obj.Justification = "Middle-Center"

        if "JustificationReference" not in properties:
            _tip = translate(
                "App::Property",
                "Height reference used for justification",
            )
            obj.addProperty(
                "App::PropertyEnumeration",
                "JustificationReference",
                "Draft",
                _tip,
            )
            obj.JustificationReference = ["Cap Height", "Shape Height"]
            obj.JustificationReference = "Cap Height"

        if "KeepLeftMargin" not in properties:
            _tip = translate(
                "App::Property",
                "Keep left margin and leading white space when justification is left",
            )
            obj.addProperty("App::PropertyBool", "KeepLeftMargin", "Draft", _tip)
            obj.KeepLeftMargin = False

        if "ScaleToSize" not in properties:
            _tip = translate(
                "App::Property",
                "Scale to ensure cap height is equal to size",
            )
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
            _tip = translate(
                "App::Property",
                "Fuse faces if faces overlap, usually not required (can be very slow)",
            )
            obj.addProperty("App::PropertyBool", "Fuse", "Draft", _tip)
            obj.Fuse = False

        if "RotationDirection" not in properties:
            _tip = translate(
                "App::Property",
                "Direction to step angles when placing strings",
            )
            obj.addProperty(
                "App::PropertyEnumeration",
                "RotationDirection",
                "Draft",
                _tip,
            )
            obj.RotationDirection = ["CounterClockwise", "Clockwise"]
            obj.RotationDirection = "CounterClockwise"

        if "StringRotation" not in properties:
            _tip = translate(
                "App::Property",
                "Extra rotation angle applied uniformly to every string",
            )
            obj.addProperty("App::PropertyAngle", "StringRotation", "Draft", _tip)
            obj.StringRotation = 0.0

    def onDocumentRestored(self, obj):
        super().onDocumentRestored(obj)
        # Ensure all properties exist after document restoration
        self.set_properties(obj)

    def execute(self, obj):
        """Generate the compound shape from the list of strings, arranged radially."""
        if self.props_changed_placement_only():
            obj.positionBySupport()
            self.props_changed_clear()
            return

        if obj.Strings and obj.FontFile:
            plm = obj.Placement
            all_shapes = []

            # Pre-calculate justification vector parameters once
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
                        fill = (
                            sum([shape.Area for shape in shapes]) > 0.03
                            and math.isclose(
                                Part.Compound(char).BoundBox.DiagonalLength,
                                Part.Compound(shapes).BoundBox.DiagonalLength,
                                rel_tol=1e-7,
                            )
                        )

                # Generate wire representation for this string
                chars = Part.makeWireString(
                    string_text, obj.FontFile, obj.Size, obj.Tracking
                )
                string_shapes = []

                for char in chars:
                    if fill is False:
                        string_shapes.extend(char)
                    elif char:
                        string_shapes.extend(self.make_faces(char))

                if not string_shapes:
                    continue

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
                        wrn = (
                            translate(
                                "draft",
                                "RadialShapeString: oblique angle must be in the "
                                "-80 to +80 degree range",
                            )
                            + "\n"
                        )
                        _wrn(wrn)

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

                # Determine direction sign: +1 = CCW, -1 = CW
                try:
                    if obj.RotationDirection == "Clockwise":
                        direction = -1.0
                    else:
                        direction = 1.0
                except Exception:
                    direction = 1.0

                step = float(obj.AngleStep) * direction

                # Compute radial position for this string
                angle_deg = float(obj.StartAngle) + string_index * step
                angle_rad = math.radians(angle_deg)

                # Radius is an App::PropertyLength, ensure we use value in mm
                radius_val = float(obj.Radius)

                # Base center for this string (relative to object origin)
                cx = radius_val * math.cos(angle_rad)
                cy = radius_val * math.sin(angle_rad)
                offset_vec = App.Vector(cx, cy, 0)

                # Extra per-string rotation
                extra_rot = float(getattr(obj, "StringRotation", 0.0))

                # Apply tangent or horizontal orientation
                if obj.Tangential:
                    # Tangent direction pointing toward the center:
                    # radial angle + 180° is inward; minus 90° for baseline.
                    rot_deg = angle_deg - 90.0
                else:
                    # Baseline kept parallel to global X axis
                    rot_deg = 0.0

                # Apply global string rotation offset
                rot_deg += extra_rot

                # Apply placement: we rotate and translate all shapes
                m = App.Matrix()
                # Rotation around Z
                rot_rad = math.radians(rot_deg)
                m.A11 = math.cos(rot_rad)
                m.A12 = -math.sin(rot_rad)
                m.A21 = math.sin(rot_rad)
                m.A22 = math.cos(rot_rad)
                # Translation
                m.A14 = offset_vec.x
                m.A24 = offset_vec.y
                m.A34 = offset_vec.z

                transformed = []
                for shape in shapes:
                    transformed.append(shape.transformGeometry(m))

                all_shapes.extend(transformed)

            if all_shapes:
                obj.Shape = Part.Compound(all_shapes)
            else:
                _wrn(
                    translate("draft", "RadialShapeString: strings have no wires")
                    + "\n"
                )

            obj.Placement = plm

        obj.positionBySupport()
        self.props_changed_clear()

    def onChanged(self, obj, prop):
        self.props_changed_store(prop)

    # justification_vector moved to shared module `justification.py`

    def make_faces(self, wireChar):
        """Create faces from wire character representation."""
        wrn = (
            translate(
                "draft",
                "RadialShapeString: face creation failed for one character",
            )
            + "\n"
        )

        wirelist = []
        for w in wireChar:
            compEdges = Part.Compound(w.Edges)
            compEdges = compEdges.connectEdgesToWires()
            if compEdges.Wires[0].isClosed():
                wirelist.append(compEdges.Wires[0])

        if not wirelist:
            _wrn(wrn)
            return []

        try:
            faces_list = Part.makeFace(wirelist, "Part::FaceMakerBullseye").Faces
            for face in faces_list:
                face.validate()
        except Part.OCCError:
            try:
                faces_list = Part.makeFace(wirelist, "Part::FaceMakerCheese").Faces
                for face in faces_list:
                    face.validate()
            except Part.OCCError:
                try:
                    faces_list = Part.makeFace(wirelist, "Part::FaceMakerSimple").Faces
                    for face in faces_list:
                        face.validate()
                except Part.OCCError:
                    _wrn(wrn)
                    return []

        for face in faces_list:
            try:
                if face.normalAt(0, 0).z < 0:
                    face.reverse()
            except Exception:
                pass

        return faces_list
