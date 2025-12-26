# SPDX-License-Identifier: LGPL-2.1-only
# SPDX-FileNotice: Part of the ShapeStrings addon.

from .gui_spacedshapestring import registerSpaced
from .gui_radialshapestring import registerRadial

def registerCommands ():
    registerSpaced()
    registerRadial()
