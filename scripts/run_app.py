#!/usr/bin/env python3
"""
Entry point script for Blackjack Counter application.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from blackjack_counter.gui.app import main

if __name__ == "__main__":
    main()