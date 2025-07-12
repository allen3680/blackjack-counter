"""Blackjack Counter - A card counting and basic strategy application."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from src.core.basic_strategy import BasicStrategy
from src.core.card_counter import WongHalvesCounter
from src.core.game_state import GameState

__all__ = ["GameState", "WongHalvesCounter", "BasicStrategy"]
