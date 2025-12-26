# SPDX-License-Identifier: LGPL-2.1-only
# SPDX-FileNotice: Part of the ShapeStrings addon.

from sys import modules
from . import Module


def initializeAPI ():
    modules[ 'ShapeStrings' ] = Module