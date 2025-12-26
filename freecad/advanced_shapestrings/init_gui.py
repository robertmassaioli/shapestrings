# SPDX-License-Identifier: LGPL-2.1-only
# SPDX-FileNotice: Part of the ShapeStrings addon.

from .Misc.Resources import paths
from .Commands import registerCommands
from .Toolbar import extendToolbar

from FreeCAD import Gui


Gui.addLanguagePath(paths['translations'])
Gui.updateLocale()

registerCommands()
extendToolbar()
