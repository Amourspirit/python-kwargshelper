from pathlib import Path
import os

def _get_script_file() -> Path:
    root_path = Path(os.path.dirname(__file__))
    return root_path


def get_project_root_dir() -> Path:
    """
    Gets the Root path of Project

    Returns:
        Path: of Root project
    """
    root_path = _get_script_file()
    return root_path.parent
