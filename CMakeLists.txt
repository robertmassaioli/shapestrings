cmake_minimum_required(VERSION 4.1)

set(Namespace_SRCS
        freecad/advanced_shapestrings/init_gui.py
        freecad/advanced_shapestrings/__init__.py
        freecad/advanced_shapestrings/version.py
        freecad/advanced_shapestrings/resources/Workbench.svg
        freecad/advanced_shapestrings/resources/translations/advanced_shapestrings_es-ES.qm
        freecad/advanced_shapestrings/resources/translations/advanced_shapestrings_es-ES.ts
)

SOURCE_GROUP("" FILES ${Namespace_SRCS})

ADD_CUSTOM_TARGET(SEARCHBAR ALL
        SOURCES ${Namespace_SRCS}
)

fc_copy_sources(SEARCHBAR "${CMAKE_BINARY_DIR}/Mod/AdvancedShapestrings" ${Namespace_SRCS})

INSTALL(
    FILES
        ${Namespace_SRCS}
    DESTINATION
        Mod/SearchBar
)
