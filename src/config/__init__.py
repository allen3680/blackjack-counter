"""Configuration module for blackjack counter."""

from pathlib import Path

CONFIG_DIR = Path(__file__).parent
STRATEGY_CONFIG = CONFIG_DIR / "strategy.yaml"
WONG_HALVES_CONFIG = CONFIG_DIR / "wong_halves.yaml"

__all__ = ["CONFIG_DIR", "STRATEGY_CONFIG", "WONG_HALVES_CONFIG"]
