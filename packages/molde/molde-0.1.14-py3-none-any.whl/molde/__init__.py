from pathlib import Path
from qtpy.uic import loadUi
from .colors import Color

MOLDE_DIR = Path(__file__).parent
UI_DIR = MOLDE_DIR / "ui_files/"

def load_ui(uifile: str | Path, baseinstance, working_directory: str| Path = None):
    from PySide6.QtCore import QDir
    if working_directory is not None:
        working_directory = QDir(working_directory)
    return loadUi(uifile, baseinstance, working_directory)
