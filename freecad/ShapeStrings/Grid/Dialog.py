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

"""Provides the task panel code for the Draft GridShapeString tool."""

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

class GridShapeStringTaskPanel:
    """Base class for grid task panel."""

    def __init__(self,
                 point=App.Vector(0, 0, 0),
                 size=10,
                 strings=None,
                 columns=3,
                 column_offset=10.0,
                 row_offset=15.0,
                 use_bounding_box=False,
                 font=""):

        columns = max(1, int(columns))

        if not strings:
            # Provide a single default editable cell, same spirit as
            # SpacedShapeString's default list entry.
            strings = [translate("draft", "Default")]

        # Load custom UI for grid shapestring
        self.form = Gui.PySideUic.loadUi(asUI('Grid'))
        self.form.setObjectName("GridShapeStringTaskPanel")
        self.form.setWindowTitle(translate("draft", "GridShapeString"))
        self.form.setWindowIcon(QtGui.QIcon(asIcon('Grid')))

        unit_length = App.Units.Quantity(0.0, App.Units.Length).getUserPreferred()[2]

        self.form.sbX.setProperty("rawValue", point.x)
        self.form.sbX.setProperty("unit", unit_length)
        self.form.sbY.setProperty("rawValue", point.y)
        self.form.sbY.setProperty("unit", unit_length)
        self.form.sbZ.setProperty("rawValue", point.z)
        self.form.sbZ.setProperty("unit", unit_length)

        self.form.sbHeight.setProperty("rawValue", size)
        self.form.sbHeight.setProperty("unit", unit_length)

        # Columns and the 2D strings table
        self.form.sbColumns.setValue(columns)
        self._populateTable(strings, columns)

        # ColumnOffset, RowOffset and UseBoundingBox controls
        self.form.sbColumnOffset.setProperty("rawValue", column_offset)
        self.form.sbColumnOffset.setProperty("unit", unit_length)
        self.form.sbRowOffset.setProperty("rawValue", row_offset)
        self.form.sbRowOffset.setProperty("unit", unit_length)
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

        QtCore.QObject.connect(
            self.form.pbAddRow,
            QtCore.SIGNAL("clicked()"),
            self.addRow,
        )
        QtCore.QObject.connect(
            self.form.pbRemoveRow,
            QtCore.SIGNAL("clicked()"),
            self.removeRow,
        )
        QtCore.QObject.connect(
            self.form.sbColumns,
            QtCore.SIGNAL("valueChanged(int)"),
            self.columnsChanged,
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

    def _populateTable(self, texts, columns):
        """(Re)build tableStrings as a `columns`-wide grid holding `texts`
        row-major, padding any remaining cells with empty, editable items."""
        table = self.form.tableStrings
        table.blockSignals(True)
        table.clear()
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.setColumnCount(columns)
        row_count = max(1, -(-len(texts) // columns)) if texts else 1
        table.setRowCount(row_count)

        for index, text in enumerate(texts):
            row, col = index // columns, index % columns
            table.setItem(row, col, QtGui.QTableWidgetItem(text))

        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                if table.item(row, col) is None:
                    table.setItem(row, col, QtGui.QTableWidgetItem(""))

        table.blockSignals(False)

    def columnsChanged(self, new_columns):
        """Reshape the table when the Columns spin box changes."""
        new_columns = max(1, int(new_columns))
        texts = self._collectTableTexts()
        self._populateTable(texts, new_columns)

    def _collectTableTexts(self):
        """Flatten tableStrings row-major, one entry per cell (blanks kept)."""
        table = self.form.tableStrings
        texts = []
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                texts.append(item.text().strip() if item else "")
        return texts

    def addRow(self):
        """Append a new blank row of cells to tableStrings."""
        table = self.form.tableStrings
        row = table.rowCount()
        table.insertRow(row)
        for col in range(table.columnCount()):
            table.setItem(row, col, QtGui.QTableWidgetItem(""))
        self.updateRemoveRowButtonState()

    def removeRow(self):
        """Remove the currently selected row from tableStrings, if more than one remains."""
        table = self.form.tableStrings
        if table.rowCount() <= 1:
            return  # Do not allow removing the last remaining row

        row = table.currentRow()
        if row < 0:
            row = table.rowCount() - 1
        table.removeRow(row)
        self.updateRemoveRowButtonState()

    def updateRemoveRowButtonState(self):
        """Enable/disable the Remove Row button depending on the number of rows."""
        table = self.form.tableStrings
        self.form.pbRemoveRow.setEnabled(table.rowCount() > 1)

    def collectStrings(self):
        """Read strings from tableStrings, row-major. Interior blank cells
        are kept (they mark an empty grid position); only a trailing run
        of blanks is trimmed off the end of the list."""
        texts = self._collectTableTexts()
        while texts and not texts[-1]:
            texts.pop()
        return texts

    def collectColumns(self):
        """Read the configured column count."""
        return max(1, int(self.form.sbColumns.value()))

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


class GridShapeStringTaskPanelCmd(GridShapeStringTaskPanel):
    """Task panel for the grid command."""

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
        """Create GridShapeString object in the current document."""

        # Strings and grid layout
        strings = self.collectStrings()
        columns = self.collectColumns()

        # Escape each for Python string literal usage
        string_list_expr = "[" + ", ".join(
            ['"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"' for s in strings]
        ) + "]"

        # Font file
        FFile = '"' + str(self.fileSpec) + '"'

        # Size and spacing
        Size = str(App.Units.Quantity(self.form.sbHeight.text()).Value)
        ColumnOffset = str(App.Units.Quantity(self.form.sbColumnOffset.text()).Value)
        RowOffset = str(App.Units.Quantity(self.form.sbRowOffset.text()).Value)
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
                    f"ss = {c}.Grid("
                    f"Strings={string_list_expr}, "
                    f"FontFile={FFile}, Size={Size}, Columns={columns}, "
                    f"ColumnOffset={ColumnOffset}, RowOffset={RowOffset}, "
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
            _msg("Grid ShapeString commit commands:\n" + "\n".join(commands))
            self.sourceCmd.commit(translate("draft", "Create Grid ShapeString"), commands)
        except Exception:
            _err("Grid ShapeString : error delaying commit\n")
            # Also print the full Python traceback to the console/log
            traceback.print_exc()


class GridShapeStringTaskPanelEdit(GridShapeStringTaskPanel):
    """Task panel for Draft GridShapeString object in edit mode."""

    def __init__(self, vobj):
        base = vobj.Object.Placement.Base
        size = vobj.Object.Size.Value
        columns = vobj.Object.Columns
        strings = list(vobj.Object.Strings)
        column_offset = vobj.Object.ColumnOffset.Value
        row_offset = vobj.Object.RowOffset.Value
        use_bounding_box = bool(getattr(vobj.Object, "UseBoundingBox", False))
        font = vobj.Object.FontFile

        super().__init__(base, size, strings, columns, column_offset, row_offset, use_bounding_box, font)

        self.pointPicked = True
        self.vobj = vobj
        self.call = Gui.activeView().addEventCallback("SoEvent", self.action)

        # Bind the numeric fields to their document object properties so the
        # "=" shortcut and "fx" icon open FreeCAD's expression editor.
        Gui.ExpressionBinding(self.form.sbX).bind(vobj.Object, "Placement.Base.x")
        Gui.ExpressionBinding(self.form.sbY).bind(vobj.Object, "Placement.Base.y")
        Gui.ExpressionBinding(self.form.sbZ).bind(vobj.Object, "Placement.Base.z")
        Gui.ExpressionBinding(self.form.sbHeight).bind(vobj.Object, "Size")
        Gui.ExpressionBinding(self.form.sbColumns).bind(vobj.Object, "Columns")
        Gui.ExpressionBinding(self.form.sbColumnOffset).bind(vobj.Object, "ColumnOffset")
        Gui.ExpressionBinding(self.form.sbRowOffset).bind(vobj.Object, "RowOffset")

    def accept(self):
        x = App.Units.Quantity(self.form.sbX.text()).Value
        y = App.Units.Quantity(self.form.sbY.text()).Value
        z = App.Units.Quantity(self.form.sbZ.text()).Value
        base = App.Vector(x, y, z)

        size = App.Units.Quantity(self.form.sbHeight.text()).Value
        strings = self.collectStrings()
        columns = self.collectColumns()
        column_offset = App.Units.Quantity(self.form.sbColumnOffset.text()).Value
        row_offset = App.Units.Quantity(self.form.sbRowOffset.text()).Value
        use_bounding_box = bool(self.form.cbUseBoundingBox.isChecked())
        font_file = self.fileSpec

        o = 'FreeCAD.ActiveDocument.getObject("{}")'.format(self.vobj.Object.Name)
        Gui.doCommand(o + ".Placement.Base=" + toString(base))
        Gui.doCommand(o + ".Size=" + str(size))
        Gui.doCommand(o + ".Strings=" + repr(strings))
        Gui.doCommand(o + ".Columns=" + str(columns))
        Gui.doCommand(o + ".ColumnOffset=" + str(column_offset))
        Gui.doCommand(o + ".RowOffset=" + str(row_offset))
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
