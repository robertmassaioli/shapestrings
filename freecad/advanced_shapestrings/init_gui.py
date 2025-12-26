# SPDX-License-Identifier: LGPL-2.1-only

import FreeCADGui as Gui
import FreeCAD as App
from draftutils.messages import _msg
from .paths import get_icon_path, get_translation_directory

translate=App.Qt.translate
QT_TRANSLATE_NOOP=App.Qt.QT_TRANSLATE_NOOP

# Add translations path
Gui.addLanguagePath(get_translation_directory())
Gui.updateLocale()

class AdvancedShapestrings(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """
    MenuText = translate("Workbench", "Advanced Shapestrings")
    ToolTip = translate("Workbench", "More advanced shapestring tools")
    Icon = get_icon_path("Workbench.svg")
    toolbox = [
        "AdvancedShapestrings_SpacedShapeString",  # SpacedShapeString
        "AdvancedShapestrings_RadialShapeString",  # RadialShapeString
    ]

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """

        try:
            ## Init so that we can use the draft tools
            import DraftGui
            import draftguitools.gui_snapper
            if not hasattr(Gui,"draftToolBar"):
                Gui.draftToolBar = DraftGui.DraftToolBar()    
            if not hasattr(Gui,"Snapper"):
                Gui.Snapper = draftguitools.gui_snapper.Snapper()
            App.activeDraftCommand = None

            from . import AdvancedShapestringTools
        except Exception as exc:
            App.Console.PrintError(exc)
            App.Console.PrintError("Error: Initializing one or more "
                                       "of the Draft modules failed, "
                                       "Draft will not work as expected.\n")

        _msg(translate(
            "Log",
            "Switching to advanced_shapestrings") + "\n")

        # NOTE: Context for this commands must be "Workbench"
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "Tools"), self.toolbox)
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "Tools"), self.toolbox)

    def Activated(self):
        '''
        code which should be computed when a user switch to this workbench
        '''
        App.Console.PrintMessage(translate(
            "Log",
            "Workbench advanced_shapestrings activated.") + "\n")

    def Deactivated(self):
        '''
        code which should be computed when this workbench is deactivated
        '''
        if hasattr(Gui, "draftToolBar"):
            Gui.draftToolBar.Deactivated()
        if hasattr(Gui, "Snapper"):
            Gui.Snapper.hide()
        
        App.Console.PrintMessage(translate(
            "Log",
            "Workbench advanced_shapestrings de-activated.") + "\n")


Gui.addWorkbench(AdvancedShapestrings())
