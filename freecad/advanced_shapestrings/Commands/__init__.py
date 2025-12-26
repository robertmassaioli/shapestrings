# SPDX-License-Identifier: LGPL-2.1-only
# SPDX-FileNotice: Part of the ShapeStrings addon.

from .Spaced import registerSpaced
from .Radial import registerRadial

def registerCommands ():
    registerSpaced()
    registerRadial()
