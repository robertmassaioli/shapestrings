# SPDX-License-Identifier: LGPL-2.1-only
# SPDX-FileNotice: Part of the ShapeStrings addon.

from .AdvancedShapestringTools import registerCommands
from .paths import get_translation_directory

from draftutils.messages import _msg
from FreeCAD import Gui , Qt

translate = Qt.translate


TOOLBOX = [
    "ShapeStrings_Spaced",
    "ShapeStrings_Radial",
]

# Add translations path
Gui.addLanguagePath(get_translation_directory())
Gui.updateLocale()
registerCommands()


_ran_draft_refresh = False
_appended_to_draft = False

def _on_workbench_activated():

    global _ran_draft_refresh, _appended_to_draft

    workbench = Gui.activeWorkbench()

    if not hasattr(workbench, "__Workbench__"):
        return

    if workbench.__class__.__name__ != "DraftWorkbench":
        return

    # First, try to append our toolbar/menu if not done yet
    if _appended_to_draft:
        return

    workbench.appendToolbar(
        translate("Workbench", "ShapeStrings"),
        TOOLBOX,
    )
    workbench.appendMenu(
        translate("Workbench", "&ShapeStrings"),
        TOOLBOX,
    )
    _msg("Appended Shapestrings tools to Draft workbench\n")

    _appended_to_draft = True


# Connect once (e.g. in your InitGui.py)
Gui.getMainWindow().workbenchActivated.connect(_on_workbench_activated)