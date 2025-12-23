import os
import FreeCADGui as Gui
import FreeCAD as App
from . import my_numpy_function
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
    MenuText = translate("Workbench", "AdvancedShapestrings")
    ToolTip = translate("Workbench", "a simple AdvancedShapestrings")
    Icon = get_icon_path("cool.svg")
    toolbox = [
        "Draft_SpacedShapeString",  # SpacedShapeString
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

        App.Console.PrintMessage(translate(
            "Log",
            "Switching to advanced_shapestrings") + "\n")
        App.Console.PrintMessage(translate(
            "Log",
            "Run a numpy function:") + "sqrt(100) = {}\n".format(my_numpy_function.my_foo(100)))

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
        App.Console.PrintMessage(translate(
            "Log",
            "Workbench advanced_shapestrings de-activated.") + "\n")


Gui.addWorkbench(AdvancedShapestrings())
