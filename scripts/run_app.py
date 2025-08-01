#!/usr/bin/env python3
"""
Entry point script for Blackjack Counter application.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.gui.app_modern_qt import main

if __name__ == "__main__":
    main()