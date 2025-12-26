"""Shared justification helpers for shape string objects.

This module extracts the common justification_vector logic used by
SpacedShapeString and RadialShapeString so it can be maintained in one
place.
"""
import FreeCAD as App


def justification_vector(ss_shape, cap_height, just, just_ref, keep_left_margin):
    """Calculate the justification offset vector.

    Parameters
    - ss_shape: shape (Compound) containing the string's subshapes
    - cap_height: reference cap height (number)
    - just: justification enumeration string containing alignment flags
    - just_ref: either "Cap Height" or "Shape Height"
    - keep_left_margin: boolean indicating whether to preserve left margin

    Returns an App.Vector offset to apply to the string shapes.
    """
    box = ss_shape.optimalBoundingBox()
    if keep_left_margin is True and "Left" in just:
        vec = App.Vector(0, 0, 0)
    else:
        vec = App.Vector(-box.XMin, 0, 0)

    width = box.XLength
    if "Shape" in just_ref:
        vec = vec + App.Vector(0, -box.YMin, 0)
        height = box.YLength
    else:
        height = cap_height

    if "Top" in just:
        vec = vec + App.Vector(0, -height, 0)
    elif "Middle" in just:
        vec = vec + App.Vector(0, -height / 2, 0)

    if "Right" in just:
        vec = vec + App.Vector(-width, 0, 0)
    elif "Center" in just:
        vec = vec + App.Vector(-width / 2, 0, 0)

    return vec
