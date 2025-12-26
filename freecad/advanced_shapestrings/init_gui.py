# SPDX-License-Identifier: LGPL-2.1-only
# SPDX-FileNotice: Part of the ShapeStrings addon.

import FreeCADGui as Gui
import FreeCAD as App
from draftutils.messages import _msg
from .paths import get_icon_path, get_translation_directory
from . import AdvancedShapestringTools

# Fallback-safe translate helpers and toolbox entries (inlined from gui_common)
try:
    import FreeCAD as App

    QT_TRANSLATE_NOOP = App.Qt.QT_TRANSLATE_NOOP

    def translate(context, text):
        return App.Qt.translate(context, text)
except Exception:
    def QT_TRANSLATE_NOOP(context, text):
        return text

    def translate(context, text):
        return text
    
TOOLBOX = [
    "AdvancedShapestrings_SpacedShapeString", 
    "AdvancedShapestrings_RadialShapeString",
]

# Add translations path
Gui.addLanguagePath(get_translation_directory())
Gui.updateLocale()

class AdvancedShapestrings(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """
    MenuText = translate("Workbench", "Shapestrings")
    ToolTip = translate("Workbench", "Many more Shapestring tools")
    Icon = get_icon_path("Workbench.svg")
    toolbox = TOOLBOX

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

        except Exception as exc:
            App.Console.PrintError(exc)
            App.Console.PrintError("Error: Initializing one or more "
                                       "of the Draft modules failed, "
                                       "Draft will not work as expected.\n")

        _msg(translate(
            "Log",
            "Switching to advanced_shapestrings") + "\n")

        # NOTE: Context for this commands must be "Workbench"
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "Shapestring Tools"), self.toolbox)
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "Shapestring Tools"), self.toolbox)

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

# Register the workbench class with FreeCAD
Gui.addWorkbench(AdvancedShapestrings())

_ran_draft_refresh = False
_appended_to_draft = False

def _on_workbench_activated():
    global _ran_draft_refresh, _appended_to_draft

    wb = Gui.activeWorkbench()
    if not hasattr(wb, "__Workbench__"):
        return
    if wb.__class__.__name__ != "DraftWorkbench":
        return

    # First, try to append our toolbar/menu if not done yet
    if not _appended_to_draft:
        try:
            draft_wb = Gui.getWorkbench("DraftWorkbench")
            if draft_wb:
                draft_wb.appendToolbar(
                    QT_TRANSLATE_NOOP("Workbench", "Shapestrings"),
                    TOOLBOX,
                )
                draft_wb.appendMenu(
                    QT_TRANSLATE_NOOP("Workbench", "&Shapestrings"),
                    TOOLBOX,
                )
                _msg("Appended Shapestrings tools to Draft workbench\n")
                _appended_to_draft = True  # Only set when appendMenu completed
        except Exception as exc:
            try:
                App.Console.PrintError(
                    "AdvancedShapestrings: could not append to Draft workbench: {}\n"
                    .format(exc)
                )
            except Exception:
                pass
            # append failed; do NOT try to refresh yet
            return

    # Only do the refresh if:
    #  - appendMenu has succeeded at least once
    #  - and we have not already done the refresh
    if _appended_to_draft and not _ran_draft_refresh:
        _ran_draft_refresh = True
        # Bounce through another workbench to force UI refresh
        Gui.activateWorkbench("PartWorkbench")
        Gui.activateWorkbench("DraftWorkbench")
        # Optionally disconnect so this handler is run only once
        try:
            Gui.getMainWindow().workbenchActivated.disconnect(_on_workbench_activated)
        except Exception:
            pass

# Connect once (e.g. in your InitGui.py)
Gui.getMainWindow().workbenchActivated.connect(_on_workbench_activated)