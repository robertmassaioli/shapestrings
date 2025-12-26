
from FreeCAD import Gui


class Manipulator:

    def modifyToolBars ( self ):
        return [{
            'toolBar' : 'Draft Annotation' ,
            'append' : 'ShapeStrings_Spaced'
        },{
            'toolBar' : 'Draft Annotation' ,
            'append' : 'ShapeStrings_Radial'
        }]


def extendToolbar ():
    Gui.addWorkbenchManipulator(Manipulator())
