# SPDX-License-Identifier: LGPL-2.1-only
# SPDX-FileNotice: Part of the ShapeStrings addon.

import freecad.ShapeStrings as module
from importlib import resources
from os.path import dirname , join
from typing import TypedDict


icons = resources.files(module) / 'Resources/Icons'
uis = resources.files(module) / 'Resources/Interfaces'


class Paths ( TypedDict ):
    translations : str

paths : Paths = {
    'translations' : join(dirname(__file__),'..','Resources','Translations')
}


def asIcon ( name : str ):

    file = name + '.svg'

    icon = icons / file

    with resources.as_file(icon) as path:
        return str( path )


def asUI ( name : str ):

    file = name + '.ui'

    ui = uis / file

    with resources.as_file(ui) as path:
        return str( path )