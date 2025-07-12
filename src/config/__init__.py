"""Configuration module for blackjack counter."""

from pathlib import Path
import sys

# Check if running in PyInstaller bundle
if hasattr(sys, '_MEIPASS'):
    # Running in a PyInstaller bundle
    CONFIG_DIR = Path(sys._MEIPASS) / "src" / "config"
else:
    # Running in normal Python environment
    CONFIG_DIR = Path(__file__).parent

STRATEGY_CONFIG = CONFIG_DIR / "strategy.yaml"
WONG_HALVES_CONFIG = CONFIG_DIR / "wong_halves.yaml"
SHORTCUTS_CONFIG = CONFIG_DIR / "shortcuts.yaml"

__all__ = ["CONFIG_DIR", "STRATEGY_CONFIG", "WONG_HALVES_CONFIG", "SHORTCUTS_CONFIG"]
