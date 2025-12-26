# SPDX-License-Identifier: LGPL-2.1-only
# SPDX-FileNotice: Part of the ShapeStrings addon.

import FreeCADGui as Gui
import FreeCAD as App
from draftutils.messages import _msg
from .paths import get_icon_path, get_translation_directory
from .AdvancedShapestringTools import registerCommands

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
        QT_TRANSLATE_NOOP("Workbench", "Shapestrings"),
        TOOLBOX,
    )
    workbench.appendMenu(
        QT_TRANSLATE_NOOP("Workbench", "&Shapestrings"),
        TOOLBOX,
    )
    _msg("Appended Shapestrings tools to Draft workbench\n")

    _appended_to_draft = True


# Connect once (e.g. in your InitGui.py)
Gui.getMainWindow().workbenchActivated.connect(_on_workbench_activated)