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


"""Provides the viewprovider code for the RadialShapeString object."""


import FreeCADGui as Gui

from draftviewproviders.view_base import ViewProviderDraft
from ..Dialogs import RadialShapeStringTaskPanelEdit
from ..Misc.Resources import asIcon


class ViewProviderRadialShapeString(ViewProviderDraft):

    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        return asIcon('Radial')

    def updateData(self, obj, prop):
        if (
            prop == "Strings"
            or prop == "FontFile"
            or prop == "Size"
            or prop == "Radius"
            or prop == "StartAngle"
            or prop == "AngleStep"
            or prop == "Tangential"
            or prop == "RotationDirection"
            or prop == "StringRotation"
        ):
            obj.recompute()
        return

    def setEdit(self, vobj, mode):
        if mode != 0:
            return None

        # Using Draft_Edit to detect if the Draft, Arch or BIM WB has been loaded.
        if "Draft_Edit" not in Gui.listCommands():
            self.wb_before_edit = Gui.activeWorkbench()
            Gui.activateWorkbench("DraftWorkbench")

        self.task = RadialShapeStringTaskPanelEdit(vobj)
        Gui.Control.showDialog(self.task)
        return True

    def unsetEdit(self, vobj, mode):
        if mode != 0:
            return None

        self.task.finish()
        if hasattr(self, "wb_before_edit"):
            Gui.activateWorkbench(self.wb_before_edit.name())
            delattr(self, "wb_before_edit")
        return True
