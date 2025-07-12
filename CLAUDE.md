# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Blackjack card counting desktop application using the Wong Halves system and basic strategy for 8-deck games. It's built with Python and Tkinter for the GUI.

## Development Commands

### Running the Application
```bash
# Direct run
python3 main.py

# Or after installation
pip install -e .
blackjack-counter
```

### Code Quality Tools
```bash
# Format code with Black
black *.py

# Lint with Ruff
ruff check *.py

# Type check with MyPy
mypy *.py

# Install development dependencies
pip install -e ".[dev]"
```

### Testing
Currently no tests exist. When adding tests, use pytest:
```bash
pytest
```

## Architecture

The application follows a simple MVC pattern:

- **Model Layer**:
  - `game_state.py`: Manages player/dealer hands and game state
  - `card_counter.py`: Implements Wong Halves counting system
  - `basic_strategy.py`: Decision engine for optimal play

- **View/Controller**:
  - `main.py`: Tkinter GUI application (`BlackjackCounterApp` class)

- **Configuration**:
  - `strategy.yaml`: Basic strategy tables for 8-deck games
  - `wong_halves.yaml`: Card counting system configuration

## Key Implementation Details

### Card Counting System
The Wong Halves system uses fractional values:
- Cards 2,7: +0.5
- Cards 3,4,6: +1.0
- Card 5: +1.5
- Card 8: 0
- Card 9: -0.5
- Cards 10,J,Q,K,A: -1.0

True count = Running count ÷ Remaining decks

### Basic Strategy
Strategy decisions are loaded from `strategy.yaml` and cover:
- Hard hands (no Ace or Ace as 1)
- Soft hands (Ace as 11)
- Pair splitting
- Assumes: 8 decks, dealer stands on soft 17

### GUI Color Coding
- **Count colors**: Green (player advantage) to Red (dealer advantage)
- **Action colors**: Blue (Hit), Green (Stand), Orange (Double), Purple (Split), Red (Surrender)

## Development Guidelines

### Type Hints
The codebase uses type hints. Maintain type annotations for all new code and ensure `mypy` passes in strict mode.

### Code Style
- Black formatter with 100-character line length
- Follow existing patterns for Tkinter widget organization
- YAML files use lowercase with underscores

### Adding Features
When modifying strategy or counting systems:
1. Update the corresponding YAML configuration file
2. Ensure the loading logic in `BasicStrategy` or `WongHalvesCounter` handles new data
3. Update GUI if new actions or displays are needed