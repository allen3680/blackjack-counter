"""
Resource path helper for PyInstaller compatibility.
"""

import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path: Path relative to the project root

    Returns:
        Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        # In development, use the project root
        base_path = Path(__file__).parent.parent.parent

    return Path(base_path) / relative_path


def get_config_path(filename: str) -> Path:
    """
    Get path to configuration file.

    Args:
        filename: Name of the config file (e.g., 'strategy.yaml')

    Returns:
        Absolute path to the config file
    """
    return get_resource_path(f"src/config/{filename}")
