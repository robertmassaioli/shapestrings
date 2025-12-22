# resources.py
import os

_base_dir = os.path.dirname(__file__)

_ICONSDIRECTORY = os.path.join(_base_dir, "resources", "icons")
_TRANSLATIONSDIRECTORY = os.path.join(_base_dir, "resources", "translations")
_UIDIRECTORY = os.path.join(_base_dir, "resources", "ui")


def get_icon_path(name: str) -> str:
    """Return full path to an icon file in the icons directory."""
    return os.path.join(_ICONSDIRECTORY, name)


def get_translation_directory() -> str:
    """Return full path to a translation file in the translations directory."""
    return _TRANSLATIONSDIRECTORY


def get_ui_path(name: str) -> str:
    """Return full path to a UI file in the ui directory."""
    return os.path.join(_UIDIRECTORY, name)
