# SPDX-License-Identifier: LGPL-2.1-only
# SPDX-FileNotice: Part of the ShapeStrings addon.

from .Misc.Resources import paths
from .Misc.Toolbar import extendToolbar
from .Spaced import registerSpaced
from .Radial import registerRadial
from .API import initializeAPI

from FreeCAD import Gui

Gui.addLanguagePath(paths['translations'])
Gui.updateLocale()

initializeAPI()

registerRadial()
registerSpaced()

extendToolbar()
