"""Shared pytest fixtures and configuration."""

from typing import Any, Dict

import pytest
import yaml


@pytest.fixture
def mock_wong_halves_config() -> Dict[str, Any]:
    """Mock Wong Halves configuration."""
    return {
        "counting_system": {
            "name": "Wong Halves",
            "description": "專業等級的平衡計數系統，由 Stanford Wong 開發",
        },
        "card_values": {
            "2": 0.5,
            "3": 1.0,
            "4": 1.0,
            "5": 1.5,
            "6": 1.0,
            "7": 0.5,
            "8": 0.0,
            "9": -0.5,
            "10": -1.0,
            "J": -1.0,
            "Q": -1.0,
            "K": -1.0,
            "A": -1.0,
        },
        "properties": {
            "balanced": True,
            "level": 3,
            "insurance_correlation": 0.99,
            "betting_correlation": 0.99,
            "playing_efficiency": 0.57,
        },
        "betting_thresholds": {"increase_bet": 2.0, "max_bet": 4.0, "take_insurance": 3.0},
        "advantages": [
            "高度準確的下注相關性（0.99）",
            "適合多副牌遊戲",
            "提供精確的玩牌決策調整",
            "專業玩家廣泛使用",
        ],
    }


@pytest.fixture
def mock_basic_strategy_config() -> Dict[str, Any]:
    """Mock basic strategy configuration."""
    return {
        "settings": {"decks": 8, "dealer_stands_soft_17": True},
        "action_codes": {
            "H": {"action": "要牌", "description": "再拿一張牌"},
            "S": {"action": "停牌", "description": "保持現有手牌"},
            "D": {"action": "加倍", "description": "如允許則加倍下注，否則要牌"},
            "R": {"action": "投降", "description": "如允許則投降，否則要牌"},
            "Y": {"action": "分牌", "description": "分開這對對子"},
            "N": {"action": "", "description": ""},
        },
        "dealer_card_index": {
            "2": 0,
            "3": 1,
            "4": 2,
            "5": 3,
            "6": 4,
            "7": 5,
            "8": 6,
            "9": 7,
            "10": 8,
            "J": 8,
            "Q": 8,
            "K": 8,
            "A": 9,
        },
        "hard_strategy": {
            "hands": {
                5: ["H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
                6: ["H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
                7: ["H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
                8: ["H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
                9: ["H", "D", "D", "D", "D", "H", "H", "H", "H", "H"],
                10: ["D", "D", "D", "D", "D", "D", "D", "D", "H", "H"],
                11: ["D", "D", "D", "D", "D", "D", "D", "D", "D", "H"],
                12: ["H", "H", "S", "S", "S", "H", "H", "H", "H", "H"],
                13: ["S", "S", "S", "S", "S", "H", "H", "H", "H", "H"],
                14: ["S", "S", "S", "S", "S", "H", "H", "H", "H", "H"],
                15: ["S", "S", "S", "S", "S", "H", "H", "H", "R", "R"],
                16: ["S", "S", "S", "S", "S", "H", "H", "R", "R", "R"],
                17: ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
                18: ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
                19: ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
                20: ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
                21: ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
            }
        },
        "soft_strategy": {
            "hands": {
                13: ["H", "H", "H", "D", "D", "H", "H", "H", "H", "H"],
                14: ["H", "H", "H", "D", "D", "H", "H", "H", "H", "H"],
                15: ["H", "H", "D", "D", "D", "H", "H", "H", "H", "H"],
                16: ["H", "H", "D", "D", "D", "H", "H", "H", "H", "H"],
                17: ["H", "D", "D", "D", "D", "H", "H", "H", "H", "H"],
                18: ["S", "D", "D", "D", "D", "S", "S", "H", "H", "H"],
                19: ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
                20: ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
                21: ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
            }
        },
        "pair_strategy": {
            "pairs": {
                "A,A": ["Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y"],
                "2,2": ["Y", "Y", "Y", "Y", "Y", "Y", "N", "N", "N", "N"],
                "3,3": ["Y", "Y", "Y", "Y", "Y", "Y", "N", "N", "N", "N"],
                "4,4": ["N", "N", "N", "Y", "Y", "N", "N", "N", "N", "N"],
                "5,5": ["N", "N", "N", "N", "N", "N", "N", "N", "N", "N"],
                "6,6": ["Y", "Y", "Y", "Y", "Y", "N", "N", "N", "N", "N"],
                "7,7": ["Y", "Y", "Y", "Y", "Y", "Y", "N", "N", "N", "N"],
                "8,8": ["Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y"],
                "9,9": ["Y", "Y", "Y", "Y", "Y", "N", "Y", "Y", "N", "N"],
                "10,10": ["N", "N", "N", "N", "N", "N", "N", "N", "N", "N"],
            }
        },
    }


@pytest.fixture
def temp_yaml_file(tmp_path, request):
    """Create a temporary YAML file with given content."""
    content = request.param
    yaml_file = tmp_path / "test_config.yaml"
    with open(yaml_file, "w") as f:
        yaml.dump(content, f)
    return yaml_file


@pytest.fixture
def sample_cards():
    """Common card combinations for testing."""
    return {
        "blackjack": ["A", "K"],
        "hard_16": ["10", "6"],
        "soft_17": ["A", "6"],
        "pair_8s": ["8", "8"],
        "bust": ["10", "9", "5"],
    }
