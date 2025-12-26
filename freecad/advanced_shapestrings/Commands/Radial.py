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

"""Provides GUI tools to create radial text shapes with a particular font.


These text shapes are made of various edges and closed faces, and therefore
can be extruded to create solid bodies that can be used in boolean
operations. That is, these text shapes can be used for engraving text
into solid bodies arranged around circular features such as dials, flanges,
or bolt circles.


They are more complex than simple text annotations, and support multiple
strings positioned on an arc with configurable radius, starting angle,
angular step, and optional tangential alignment to the circle.
"""

import FreeCADGui as Gui
import Draft_rc
import draftguitools.gui_base_original as gui_base_original
import draftutils.todo as todo

from ..paths import get_icon_path
from ..Dialogs import RadialShapeStringTaskPanelCmd
from draftutils.messages import _toolmsg


# The module is used to prevent complaints from code checkers (flake8)
True if Draft_rc.__name__ else False


from FreeCAD import Qt

translate = Qt.translate

class RadialShapeString(gui_base_original.Creator):
    """Gui command for the RadialShapeString tool."""

    def GetResources(self):
        """Set icon, menu, and tooltip."""
        return {
            'Pixmap': get_icon_path("AdvancedShapestrings_RadialShapeString.svg"),
            'MenuText': translate(
                "ShapeStrings-Radial",
                "Radial ShapeString"
            ),
            'ToolTip': translate(
                "ShapeStrings-Radial",
                "Creates multiple ShapeStrings from a list of text entries, "
                "arranged around a center point on a circular arc with a given radius. "
                "Positions are controlled by a starting angle and an angular step, and each "
                "string can be oriented tangentially to the arc or kept horizontal. "
                "Useful for labeling dials, gauges, bolt circles, and other circular Part "
                "and PartDesign geometry."
            ),
        }

    def Activated(self):
        """Execute when the command is called."""
        super().Activated(name="RadialShapeString")
        if self.ui:
            self.ui = Gui.draftToolBar
            self.sourceCmd = self
            self.task = RadialShapeStringTaskPanelCmd(self)
            self.call = self.view.addEventCallback("SoEvent", self.task.action)
            _toolmsg(translate("draft", "Pick RadialShapeString center point"))
            todo.ToDo.delay(Gui.Control.showDialog, self.task)

    def finish(self):
        """Finalize the command and remove callbacks."""
        if not hasattr(self, 'planetrack'):
            self.planetrack = None
        if hasattr(self, 'call'):
            self.end_callbacks(self.call)
        if not hasattr(self, 'ui'):
            self.ui = Gui.draftToolBar
        super().finish()


def registerRadial():
    Gui.addCommand('ShapeStrings_Radial', RadialShapeString())
