
from FreeCAD import Gui


class Manipulator:
    def modifyToolBars ( self ):
        draft_creation_1_0 = 'Draft Creation'
        draft_creation_1_1 = 'Draft creation tools'
        
        return [{
            'toolBar' : draft_creation_1_0,
            'append' : 'ShapeStrings_Spaced'
        },{
            'toolBar' : draft_creation_1_0,
            'append' : 'ShapeStrings_Radial'
        },{
            'toolBar' : draft_creation_1_1,
            'append' : 'ShapeStrings_Spaced'
        },{
            'toolBar' : draft_creation_1_1,
            'append' : 'ShapeStrings_Radial'
        }]


def extendToolbar ():
    Gui.addWorkbenchManipulator(Manipulator())
