# ***************************************************************************
# * (c) 2009 Yorik van Havre *
# * (c) 2020 Eliud Cabrera Castillo *
# *
# * This file is part of the FreeCAD CAx development system. *
# *
# * This program is free software; you can redistribute it and/or modify *
# * it under the terms of the GNU Lesser General Public License (LGPL) *
# * as published by the Free Software Foundation; either version 2 of *
# * the License, or (at your option) any later version. *
# * for detail see the LICENCE text file. *
# *
# * FreeCAD is distributed in the hope that it will be useful, *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the *
# * GNU Library General Public License for more details. *
# *
# * You should have received a copy of the GNU Library General Public *
# * License along with FreeCAD; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 *
# * USA *
# *
# ***************************************************************************

"""Provides the task panel code for the Draft SpacedShapeString tool."""

## @package task_spacedshapestring
# \ingroup drafttaskpanels
# \brief Provides the task panel code for the Draft SpacedShapeString tool.
## \addtogroup drafttaskpanels
# @{

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

import FreeCAD as App
import FreeCADGui as Gui

import Draft_rc

from draftguitools import gui_tool_utils
from draftutils.messages import _err
from draftutils.params import get_param
from draftutils.translate import translate
from DraftVecUtils import toString

from .paths import get_icon_path, get_ui_path

# So the resource file doesn't trigger errors from code checkers (flake8)
True if Draft_rc.__name__ else False


class SpacedShapeStringTaskPanel:
    """Base class for Draft_SpacedShapeString task panel."""

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
        self.form = Gui.PySideUic.loadUi(get_ui_path("TaskSpacedShapeString.ui"))
        self.form.setObjectName("SpacedShapeStringTaskPanel")
        self.form.setWindowTitle(translate("draft", "SpacedShapeString"))
        self.form.setWindowIcon(QtGui.QIcon(get_icon_path("Draft_SpacedShapeString.svg")))

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

        self.platWinDialog("Overwrite")

        self.fileSpec = font if font else get_param("FontFile")
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

    def fileSelect(self, fn):
        """Assign the selected file."""
        self.fileSpec = fn

    def resetPoint(self):
        """Reset the selected point."""
        self.pointPicked = False
        origin = App.Vector(0.0, 0.0, 0.0)
        self.setPoint(origin)

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
    """Task panel for Draft_SpacedShapeString."""

    def __init__(self, sourceCmd):
        super().__init__()
        self.sourceCmd = sourceCmd

    def accept(self):
        """Execute when clicking the OK button."""
        self.createObject()
        self.reject()
        return True

    def reject(self):
        """Run when clicking the Cancel button."""
        Gui.ActiveDocument.resetEdit()
        self.sourceCmd.finish()
        self.platWinDialog("Restore")
        return True

    def _collectStrings(self):
        """Read strings from the listStrings widget, one row per string."""
        items = []
        list_widget = self.form.listStrings
        for i in range(list_widget.count()):
            text = list_widget.item(i).text().strip()
            if text:
                items.append(text)
        return items

    def createObject(self):
        """Create SpacedShapeString object in the current document."""

        # Strings
        strings = self._collectStrings()

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
            Gui.addModule("Draft")
            # You must implement Draft.make_spacedshapestring in draftmake.py
            self.sourceCmd.commit(
                translate("draft", "Create SpacedShapeString"),
                [
                    "ss = Draft.make_spacedshapestring(Strings={strings}, "
                    "FontFile={font}, Size={size}, Offset={offset}, "
                    "UseBoundingBox={use_bbox})".format(
                        strings=string_list_expr,
                        font=FFile,
                        size=Size,
                        offset=Offset,
                        use_bbox=UseBoundingBox,
                    ),
                    "plm = FreeCAD.Placement()",
                    "plm.Base = " + toString(ssBase),
                    "plm.Rotation.Q = " + qr,
                    "ss.Placement = plm",
                    "ss.AttachmentSupport = " + sup,
                    "Draft.autogroup(ss)",
                    "FreeCAD.ActiveDocument.recompute()",
                ],
            )
        except Exception:
            _err("Draft_SpacedShapeString: error delaying commit\n")


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
        strings = self._collectStrings()
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

## @}
