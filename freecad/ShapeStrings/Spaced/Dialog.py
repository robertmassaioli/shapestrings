# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2009 Yorik van Havre <yorik@uncreated.net>
# SPDX-FileCopyrightText: 2020 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de>
# SPDX-FileCopyrightText: 2025 FreeCAD Project Association
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

"""Provides the task panel code for the Draft SpacedShapeString tool."""

import traceback
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

import FreeCAD as App
import FreeCADGui as Gui

import Draft_rc

from draftguitools import gui_tool_utils
from draftutils.messages import _err, _msg
from draftutils.params import get_param
from draftutils.translate import translate
from DraftVecUtils import toString

from ..Misc.Resources import asIcon , asUI


# So the resource file doesn't trigger errors from code checkers (flake8)
True if Draft_rc.__name__ else False

# Parameter groups for preferences
ADV_PARAM_GROUP = "User parameter:BaseApp/Preferences/Mod/ShapeStrings"

class SpacedShapeStringTaskPanel:
    """Base class for spaced task panel."""

    def __init__(self,
                 point=App.Vector(0, 0, 0),
                 size=10,
                 strings=None,
                 offset=10.0,
                 use_bounding_box=False,
                 font=""):

        if strings is None:
            strings = []

        # Load custom UI for spaced shapestring
        self.form = Gui.PySideUic.loadUi(asUI('Spaced'))
        self.form.setObjectName("SpacedShapeStringTaskPanel")
        self.form.setWindowTitle(translate("draft", "SpacedShapeString"))
        self.form.setWindowIcon(QtGui.QIcon(asIcon('Spaced')))

        unit_length = App.Units.Quantity(0.0, App.Units.Length).getUserPreferred()[2]

        self.form.sbX.setProperty("rawValue", point.x)
        self.form.sbX.setProperty("unit", unit_length)
        self.form.sbY.setProperty("rawValue", point.y)
        self.form.sbY.setProperty("unit", unit_length)
        self.form.sbZ.setProperty("rawValue", point.z)
        self.form.sbZ.setProperty("unit", unit_length)

        self.form.sbHeight.setProperty("rawValue", size)
        self.form.sbHeight.setProperty("unit", unit_length)

        # Populate listStrings instead of pteStrings
        list_widget = self.form.listStrings
        list_widget.clear()
        if strings:
            for s in strings:
                item = QtGui.QListWidgetItem(s)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
                list_widget.addItem(item)
        else:
            # Provide a default editable item
            item = QtGui.QListWidgetItem(translate("draft", "Default"))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            list_widget.addItem(item)

        # Offset and UseBoundingBox controls
        self.form.sbOffset.setProperty("rawValue", offset)
        self.form.sbOffset.setProperty("unit", unit_length)
        self.form.cbUseBoundingBox.setChecked(bool(use_bounding_box))

        # Platform dialog setup
        self.platWinDialog("Overwrite")

        # Parameter groups
        self._adv_params = App.ParamGet(ADV_PARAM_GROUP)

        # Font file: Shapestring default → Draft default → explicit arg → empty
        if font:
            self.fileSpec = font
        else:
            adv_font = self._adv_params.GetString("FontFile", "")
            if adv_font:
                self.fileSpec = adv_font
            else:
                # Use existing Draft preference helper as final fallback
                self.fileSpec = get_param("FontFile") or ""

        self.form.fcFontFile.setFileName(self.fileSpec)

        self.point = point
        self.pointPicked = False

        # Default for the "DontUseNativeFontDialog" preference:
        self.font_dialog_pref = False

        # Dummy attribute used by gui_tool_utils.getPoint in action method
        self.node = None

        QtCore.QObject.connect(
            self.form.fcFontFile,
            QtCore.SIGNAL("fileNameSelected(const QString&)"),
            self.fileSelect,
        )

        QtCore.QObject.connect(
            self.form.pbReset,
            QtCore.SIGNAL("clicked()"),
            self.resetPoint,
        )

        # New: connect Add/Remove buttons
        QtCore.QObject.connect(
            self.form.pbAddString,
            QtCore.SIGNAL("clicked()"),
            self.addStringItem,
        )
        QtCore.QObject.connect(
            self.form.pbRemoveString,
            QtCore.SIGNAL("clicked()"),
            self.removeStringItem,
        )

    def fileSelect(self, fn):
        """Assign the selected file and remember it as default for ShapeStrings."""
        self.fileSpec = fn
        # Ensure parameter group exists
        if not hasattr(self, "_adv_params"):
            self._adv_params = App.ParamGet(ADV_PARAM_GROUP)
        # Store last-used font as mod preference
        self._adv_params.SetString("FontFile", str(fn))


    def resetPoint(self):
        """Reset the selected point."""
        self.pointPicked = False
        origin = App.Vector(0.0, 0.0, 0.0)
        self.setPoint(origin)

    def _createEditableItem(self, text):
        """Create an editable QListWidgetItem with the given text."""
        item = QtGui.QListWidgetItem(text)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        return item

    def addStringItem(self):
        """Add a new editable entry to listStrings."""
        list_widget = self.form.listStrings
        # Use a simple translated default label, user can edit after
        item = self._createEditableItem(translate("draft", "New string"))
        list_widget.addItem(item)
        # Optionally start editing the new item immediately
        list_widget.setCurrentItem(item)
        list_widget.editItem(item)
        self.updateRemoveButtonState()

    def removeStringItem(self):
        """Remove the currently selected entry from listStrings if more than one."""
        list_widget = self.form.listStrings
        count = list_widget.count()
        if count <= 1:
            return  # Do not allow removing the last remaining item

        current_row = list_widget.currentRow()
        if current_row < 0:
            # If nothing is selected, remove the last item
            current_row = count - 1
        item = list_widget.takeItem(current_row)
        # Explicitly delete to avoid leaks in long sessions
        del item
        self.updateRemoveButtonState()

    def collectStrings(self):
        """Read strings from the listStrings widget, one row per string."""
        items = []
        list_widget = self.form.listStrings
        for i in range(list_widget.count()):
            text = list_widget.item(i).text().strip()
            if text:
                items.append(text)
        return items

    def updateRemoveButtonState(self):
        """Enable/disable the Remove button depending on the number of items."""
        list_widget = self.form.listStrings
        can_remove = list_widget.count() > 1
        self.form.pbRemoveString.setEnabled(can_remove)

    def action(self, arg):
        """Scene event handler."""
        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.reject()
        elif arg["Type"] == "SoLocation2Event":  # mouse movement detection
            self.point, ctrlPoint, info = gui_tool_utils.getPoint(
                self, arg, noTracker=True
            )
            if not self.pointPicked:
                self.setPoint(self.point)
        elif arg["Type"] == "SoMouseButtonEvent":
            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):
                self.setPoint(self.point)
                self.pointPicked = True

    def setPoint(self, point):
        """Assign the selected point."""
        self.form.sbX.setProperty("rawValue", point.x)
        self.form.sbY.setProperty("rawValue", point.y)
        self.form.sbZ.setProperty("rawValue", point.z)

    def platWinDialog(self, flag):
        """Handle the type of dialog depending on the platform."""
        ParamGroup = App.ParamGet("User parameter:BaseApp/Preferences/Dialog")

        if flag == "Overwrite":
            if "DontUseNativeFontDialog" not in ParamGroup.GetBools():
                # initialize nonexisting one
                ParamGroup.SetBool("DontUseNativeFontDialog", True)
            param = ParamGroup.GetBool("DontUseNativeFontDialog")
            self.font_dialog_pref = ParamGroup.GetBool("DontUseNativeDialog")
            ParamGroup.SetBool("DontUseNativeDialog", param)

        elif flag == "Restore":
            ParamGroup.SetBool("DontUseNativeDialog", self.font_dialog_pref)


class SpacedShapeStringTaskPanelCmd(SpacedShapeStringTaskPanel):
    """Task panel for the spaced command."""

    def __init__(self, sourceCmd):
        super().__init__()
        self.sourceCmd = sourceCmd

    def accept(self):
        """Execute when clicking the OK button."""
        # Persist font used in this operation as AdvancedShapestring default
        if not hasattr(self, "_adv_params"):
            self._adv_params = App.ParamGet(ADV_PARAM_GROUP)
        self._adv_params.SetString("FontFile", str(self.fileSpec))

        self.createObject()
        self.reject()
        return True

    def reject(self):
        """Run when clicking the Cancel button."""
        Gui.ActiveDocument.resetEdit()
        self.sourceCmd.finish()
        self.platWinDialog("Restore")
        return True

    def createObject(self):
        """Create SpacedShapeString object in the current document."""

        # Strings
        strings = self.collectStrings()

        # Escape each for Python string literal usage
        string_list_expr = "[" + ", ".join(
            ['"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"' for s in strings]
        ) + "]"

        # Font file
        FFile = '"' + str(self.fileSpec) + '"'

        # Size and spacing
        Size = str(App.Units.Quantity(self.form.sbHeight.text()).Value)
        Offset = str(App.Units.Quantity(self.form.sbOffset.text()).Value)
        UseBoundingBox = str(bool(self.form.cbUseBoundingBox.isChecked()))

        # Base point
        x = App.Units.Quantity(self.form.sbX.text()).Value
        y = App.Units.Quantity(self.form.sbY.text()).Value
        z = App.Units.Quantity(self.form.sbZ.text()).Value
        ssBase = App.Vector(x, y, z)

        try:
            qr, sup, points, fil = self.sourceCmd.getStrings()
            c = "ShapeStrings"
            Gui.addModule("Draft")
            Gui.addModule(f"{c}")
            commands = [
                (
                    f"ss = {c}.Spaced("
                    f"Strings={string_list_expr}, "
                    f"FontFile={FFile}, Size={Size}, Offset={Offset}, "
                    f"UseBoundingBox={UseBoundingBox})"
                ),
                "plm = FreeCAD.Placement()",
                f"plm.Base = {toString(ssBase)}",
                f"plm.Rotation.Q = {qr}",
                "ss.Placement = plm",
                f"ss.AttachmentSupport = {sup}",
                "Draft.autogroup(ss)", # Requires the "Draft" module
                "FreeCAD.ActiveDocument.recompute()",
            ]
            # Print the commands that will be passed to commit for debugging/logging
            _msg("Spaced ShapeString commit commands:\n" + "\n".join(commands))
            self.sourceCmd.commit(translate("draft", "Create Spaced ShapeString"), commands)
        except Exception:
            _err("Spaced ShapeString : error delaying commit\n")
            # Also print the full Python traceback to the console/log
            traceback.print_exc()


class SpacedShapeStringTaskPanelEdit(SpacedShapeStringTaskPanel):
    """Task panel for Draft SpacedShapeString object in edit mode."""

    def __init__(self, vobj):
        base = vobj.Object.Placement.Base
        size = vobj.Object.Size.Value
        strings = list(vobj.Object.Strings)
        offset = vobj.Object.Offset.Value
        use_bounding_box = bool(getattr(vobj.Object, "UseBoundingBox", False))
        font = vobj.Object.FontFile

        super().__init__(base, size, strings, offset, use_bounding_box, font)

        self.pointPicked = True
        self.vobj = vobj
        self.call = Gui.activeView().addEventCallback("SoEvent", self.action)

    def accept(self):
        x = App.Units.Quantity(self.form.sbX.text()).Value
        y = App.Units.Quantity(self.form.sbY.text()).Value
        z = App.Units.Quantity(self.form.sbZ.text()).Value
        base = App.Vector(x, y, z)

        size = App.Units.Quantity(self.form.sbHeight.text()).Value
        strings = self.collectStrings()
        offset = App.Units.Quantity(self.form.sbOffset.text()).Value
        use_bounding_box = bool(self.form.cbUseBoundingBox.isChecked())
        font_file = self.fileSpec

        o = 'FreeCAD.ActiveDocument.getObject("{}")'.format(self.vobj.Object.Name)
        Gui.doCommand(o + ".Placement.Base=" + toString(base))
        Gui.doCommand(o + ".Size=" + str(size))
        Gui.doCommand(o + ".Strings=" + repr(strings))
        Gui.doCommand(o + ".Offset=" + str(offset))
        Gui.doCommand(o + ".UseBoundingBox=" + str(use_bounding_box))
        Gui.doCommand(o + '.FontFile="' + font_file + '"')
        Gui.doCommand("FreeCAD.ActiveDocument.recompute()")

        # Persist font used in edit as Shapestring default
        if not hasattr(self, "_adv_params"):
            self._adv_params = App.ParamGet(ADV_PARAM_GROUP)
        self._adv_params.SetString("FontFile", str(font_file))

        self.reject()
        return True

    def reject(self):
        self.vobj.Document.resetEdit()
        self.platWinDialog("Restore")
        return True

    def finish(self):
        Gui.activeView().removeEventCallback("SoEvent", self.call)
        Gui.Snapper.off()
        Gui.Control.closeDialog()
        return None
