# ***************************************************************************
# *   Copyright (c) 2025 Robert Massaioli                                   *
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
"""Provides GUI tools to create spaced text shapes with a particular font.

These text shapes are made of various edges and closed faces, and therefore
can be extruded to create solid bodies that can be used in boolean
operations. That is, these text shapes can be used for engraving text
into solid bodies.

They are more complex that simple text annotations, and support multiple
strings with configurable spacing.
"""
## @package gui_spacedshapestrings
# \ingroup draftguitools
# \brief Provides GUI tools to create spaced text shapes with a particular font.


## \addtogroup draftguitools
# @{
from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCAD as App
import FreeCADGui as Gui
import Draft_rc
import DraftVecUtils
import draftutils.utils as utils
import draftguitools.gui_base_original as gui_base_original
import draftguitools.gui_tool_utils as gui_tool_utils
import draftutils.todo as todo

from .paths import get_icon_path
from .task_spacedshapestring import SpacedShapeStringTaskPanelCmd
from draftutils.translate import translate
from draftutils.messages import _toolmsg, _err, _msg

# The module is used to prevent complaints from code checkers (flake8)
True if Draft_rc.__name__ else False


class SpacedShapeString(gui_base_original.Creator):
    """Gui command for the SpacedShapeString tool."""

    def GetResources(self):
        """Set icon, menu, and tooltip."""
        return {
            'Pixmap': get_icon_path("AdvancedShapestrings_SpacedShapeString.svg"),
            'MenuText': QT_TRANSLATE_NOOP(
                "AdvancedShapestrings_SpacedShapeString",
                "Spaced ShapeString"
            ),
            'ToolTip': QT_TRANSLATE_NOOP(
                "AdvancedShapestrings_SpacedShapeString",
                "Creates multiple ShapeStrings from a list of text entries, "
                "arranged in a line with uniform spacing. "
                "Spacing can be fixed by insertion point or adjusted for visible gaps "
                "using each string's bounding box. "
                "Useful for laying out labels, numbers, or sequential text for Part and PartDesign operations."
            ),
        }

    def Activated(self):
        """Execute when the command is called."""
        super().Activated(name="SpacedShapeString")
        if self.ui:
            self.ui = Gui.draftToolBar
            self.sourceCmd = self
            self.task = SpacedShapeStringTaskPanelCmd(self)
            self.call = self.view.addEventCallback("SoEvent", self.task.action)
            _toolmsg(translate("draft", "Pick SpacedShapeString location point"))
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

Gui.addCommand('AdvancedShapestrings_SpacedShapeString', SpacedShapeString())


## @}
