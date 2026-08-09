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

"""Shared single-string rendering helpers, used by GridShapeString.

This factors out the wire -> face -> scale -> oblique -> justify pipeline
that SpacedShapeString and RadialShapeString each carry their own copy of
(see `Spaced/Object.py` and `Radial/Object.py`), so GridShapeString does not
need a third copy.

Spaced/Radial are intentionally left as-is rather than retrofitted onto this
helper: their local copies compute `cap_height` and then overwrite it with
`obj.Size` *before* using it as the scale divisor, which makes `ScaleToSize`
a no-op (scale factor `obj.Size / obj.Size == 1.0`) in both objects. This
helper follows FreeCAD upstream's ordering instead (see
`Draft/draftobjects/shapestring.py`), which scales using the *measured* cap
height and only substitutes `obj.Size` afterwards for the justification
reference. Reusing this helper for Spaced/Radial would therefore change the
rendered geometry of existing saved documents - out of scope for adding a
grid layout tool, so it is left for a separate, deliberate follow-up.
"""

import math

import FreeCAD as App
import Part

from draftgeoutils import faces as draft_faces
from draftutils.translate import translate

from .Justify import justification_vector


def compute_measured_cap_height(font_file, size, tracking):
    """Return the unscaled cap height (Y max) of a rendered 'M' glyph."""
    cap_char = Part.makeWireString("M", font_file, size, tracking)[0]
    return Part.Compound(cap_char).BoundBox.YMax


def make_faces(wire_char):
    """Create faces from a wire character representation.

    Tries FaceMakerBullseye, then Cheese, then Simple - the same fallback
    chain used by Spaced/Radial's own `make_faces()` and by upstream
    `ShapeString.make_faces()`.
    """
    wrn = translate("draft", "GridShapeString: face creation failed for one character") + "\n"

    wirelist = []
    for w in wire_char:
        comp_edges = Part.Compound(w.Edges)
        comp_edges = comp_edges.connectEdgesToWires()
        if comp_edges.Wires[0].isClosed():
            wirelist.append(comp_edges.Wires[0])

    if not wirelist:
        App.Console.PrintWarning(wrn)
        return []

    built_faces = None
    for face_maker in ("Part::FaceMakerBullseye", "Part::FaceMakerCheese", "Part::FaceMakerSimple"):
        try:
            candidate = Part.makeFace(wirelist, face_maker).Faces
            for face in candidate:
                face.validate()
            built_faces = candidate
            break
        except Part.OCCError:
            continue

    if built_faces is None:
        App.Console.PrintWarning(wrn)
        return []

    for face in built_faces:
        try:
            if face.normalAt(0, 0).z < 0:
                face.reverse()
        except Exception:
            pass

    return built_faces


def build_string_shape(
    string_text,
    font_file,
    size,
    tracking,
    make_face,
    fuse,
    scale_to_size,
    measured_cap_height,
    oblique_angle,
    justification,
    justification_reference,
    keep_left_margin,
    justification_cap_height,
):
    """Render a single string into a positioned, justified list of shapes.

    Mirrors the per-string pipeline in SpacedShapeString/RadialShapeString's
    `execute()`: wire generation, optional face fill, scale, oblique shear,
    then justification. Returns a list of `Part` shapes local to the
    string's own origin (not yet translated to a grid position), or an
    empty list if the string produced no usable geometry.
    """
    if not string_text:
        return []

    fill = make_face
    if fill is True:
        # Test a simple letter to know if we have a sticky font or not.
        char = Part.makeWireString("L", font_file, 1, 0)[0]
        probe_shapes = make_faces(char)
        if not probe_shapes:
            fill = False
        else:
            # The area threshold is scaled by glyph size so it behaves
            # consistently across fonts/sizes (FreeCAD issue #21501).
            char_comp = Part.Compound(char)
            factor = 1 / char_comp.BoundBox.YLength
            fill = sum(shape.Area for shape in probe_shapes) > (0.03 / factor**2) and math.isclose(
                char_comp.BoundBox.DiagonalLength,
                Part.Compound(probe_shapes).BoundBox.DiagonalLength,
                rel_tol=1e-7,
            )

    chars = Part.makeWireString(string_text, font_file, size, tracking)
    string_shapes = []
    for char in chars:
        if fill is False:
            string_shapes.extend(char)
        elif char:
            string_shapes.extend(make_faces(char))

    if not string_shapes:
        return []

    if fill and fuse:
        ss_shape = string_shapes[0].fuse(string_shapes[1:])
        ss_shape = draft_faces.concatenate(ss_shape)
        # concatenate() can collapse a single-face compound into a bare
        # Face, but the code below relies on `.SubShapes`.
        if ss_shape.ShapeType == "Face":
            ss_shape = Part.Compound([ss_shape])
    else:
        ss_shape = Part.Compound(string_shapes)

    if scale_to_size:
        ss_shape.scale(size / measured_cap_height)

    if oblique_angle:
        if -80 <= oblique_angle <= 80:
            mtx = App.Matrix()
            mtx.A12 = math.tan(math.radians(oblique_angle))
            ss_shape = ss_shape.transformGeometry(mtx)
        else:
            wrn = translate("draft", "GridShapeString: oblique angle must be in the -80 to +80 degree range") + "\n"
            App.Console.PrintWarning(wrn)

    just_vec = justification_vector(
        ss_shape,
        justification_cap_height,
        justification,
        justification_reference,
        keep_left_margin,
    )
    shapes = ss_shape.SubShapes
    for shape in shapes:
        shape.translate(just_vec)

    return shapes
