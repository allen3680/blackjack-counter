"""Integration tests for configuration file loading."""

from pathlib import Path

import pytest
import yaml

from src.core.basic_strategy import BasicStrategy
from src.core.card_counter import WongHalvesCounter


class TestConfigLoading:
    """Test loading and validation of configuration files."""

    def test_load_actual_wong_halves_config(self):
        """Test loading the actual wong_halves.yaml file."""
        # Assuming the file exists in the project root
        config_path = Path(__file__).parent.parent.parent / "wong_halves.yaml"
        if config_path.exists():
            counter = WongHalvesCounter(counting_file=str(config_path))

            # Verify essential properties
            assert hasattr(counter, "card_values")
            assert hasattr(counter, "num_decks")
            assert hasattr(counter, "betting_thresholds")
            assert hasattr(counter, "system_info")

            # Verify card values are loaded
            assert len(counter.card_values) == 13
            assert all(
                card in counter.card_values
                for card in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
            )

            # Verify num_decks is reasonable
            assert 1 <= counter.num_decks <= 8

            # Verify betting thresholds
            assert "increase_bet" in counter.betting_thresholds
            assert "max_bet" in counter.betting_thresholds
            assert "take_insurance" in counter.betting_thresholds

    def test_load_actual_strategy_config(self):
        """Test loading the actual strategy.yaml file."""
        config_path = Path(__file__).parent.parent.parent / "strategy.yaml"
        if config_path.exists():
            strategy = BasicStrategy(str(config_path))

            # Verify strategy properties loaded
            assert hasattr(strategy, "hard_strategy")
            assert hasattr(strategy, "soft_strategy")
            assert hasattr(strategy, "pair_strategy")

            # Verify some hard hands exist
            assert len(strategy.hard_strategy) > 0

            # Verify decision format
            for _, decisions in strategy.hard_strategy.items():
                assert isinstance(decisions, list)
                assert len(decisions) == 10  # 10 dealer cards
                for decision in decisions:
                    assert decision in ["H", "S", "D", "R", "Y", "N"]

    def test_wong_halves_config_validation(self, tmp_path):
        """Test validation of wong_halves configuration."""
        # Test missing required fields - this should pass validation
        # since WongHalvesCounter now validates properly
        config = {
            "counting_system": {"name": "Test"},
            "properties": {},
            "betting_thresholds": {},
            # Missing card_values - should trigger ValueError
        }

        config_file = tmp_path / "invalid_wong.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        with pytest.raises(ValueError, match="計數系統檔案缺少牌值對照表"):
            WongHalvesCounter(counting_file=str(config_file))

    def test_strategy_config_validation(self, tmp_path):
        """Test validation of strategy configuration."""
        # Test incomplete hard strategy (missing required values)
        invalid_config = {
            "settings": {"decks": 8},
            "action_codes": {"H": {"action": "要牌"}},
            "dealer_card_index": {"2": 0},
            "hard_strategy": {
                "hands": {
                    # Missing many required values like 5, 6, 7, etc.
                    17: ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"]
                }
            },
            "soft_strategy": {"hands": {}},
            "pair_strategy": {"pairs": {}},
        }

        config_file = tmp_path / "invalid_strategy.yaml"
        with open(config_file, "w") as f:
            yaml.dump(invalid_config, f)

        with pytest.raises(ValueError, match="硬牌策略缺少點數 5 的策略"):
            BasicStrategy(str(config_file))

    def test_valid_custom_wong_config(self, tmp_path):
        """Test loading a valid custom wong halves configuration."""
        custom_config = {
            "counting_system": {"name": "Custom System", "description": "Test system"},
            "card_values": {
                "2": 1.0,
                "3": 1.0,
                "4": 1.0,
                "5": 1.0,
                "6": 1.0,
                "7": 0.0,
                "8": 0.0,
                "9": 0.0,
                "10": -1.0,
                "J": -1.0,
                "Q": -1.0,
                "K": -1.0,
                "A": -1.0,
            },
            "properties": {"balanced": True, "level": 1},
            "betting_thresholds": {"increase_bet": 2.0, "max_bet": 4.0, "take_insurance": 2.5},
        }

        config_file = tmp_path / "custom_wong.yaml"
        with open(config_file, "w") as f:
            yaml.dump(custom_config, f)

        counter = WongHalvesCounter(num_decks=6, counting_file=str(config_file))

        assert counter.num_decks == 6
        assert counter.betting_thresholds["take_insurance"] == 2.5
        assert counter.card_values["2"] == 1.0
        assert "increase_bet" in counter.betting_thresholds

    def test_valid_custom_strategy_config(self, tmp_path):
        """Test loading a valid custom strategy configuration."""
        # Create a minimal valid strategy config
        custom_config = {
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
                "A": 9,
            },
            "hard_strategy": {
                "hands": {
                    # Complete hard strategy required
                    5: ["S"] * 10,
                    6: ["S"] * 10,
                    7: ["S"] * 10,
                    8: ["S"] * 10,
                    9: ["S"] * 10,
                    10: ["S"] * 10,
                    11: ["S"] * 10,
                    12: ["S"] * 10,
                    13: ["S"] * 10,
                    14: ["S"] * 10,
                    15: ["S"] * 10,
                    16: ["S"] * 10,
                    17: ["S"] * 10,
                    18: ["S"] * 10,
                    19: ["S"] * 10,
                    20: ["S"] * 10,
                    21: ["S"] * 10,
                }
            },
            "soft_strategy": {
                "hands": {
                    # Complete soft strategy required
                    13: ["S"] * 10,
                    14: ["S"] * 10,
                    15: ["S"] * 10,
                    16: ["S"] * 10,
                    17: ["S"] * 10,
                    18: ["S"] * 10,
                    19: ["S"] * 10,
                    20: ["S"] * 10,
                    21: ["S"] * 10,
                }
            },
            "pair_strategy": {
                "pairs": {
                    "A,A": ["S"] * 10,
                    "2,2": ["S"] * 10,
                    "3,3": ["S"] * 10,
                    "4,4": ["S"] * 10,
                    "5,5": ["S"] * 10,
                    "6,6": ["S"] * 10,
                    "7,7": ["S"] * 10,
                    "8,8": ["S"] * 10,
                    "9,9": ["S"] * 10,
                    "10,10": ["S"] * 10,
                }
            },
        }

        config_file = tmp_path / "custom_strategy.yaml"
        with open(config_file, "w") as f:
            yaml.dump(custom_config, f)

        strategy = BasicStrategy(str(config_file))

        # Test loaded correctly
        action, desc = strategy.get_decision(["10", "7"], "5")
        assert action == "停牌"
        action, desc = strategy.get_decision(["A", "8"], "10")
        assert action == "停牌"
        action, desc = strategy.get_decision(["10", "10"], "A")
        assert action == "停牌"

    def test_yaml_parsing_errors(self, tmp_path):
        """Test handling of YAML parsing errors."""
        # Invalid YAML syntax
        invalid_yaml = """
        card_values:
          - this is not valid yaml syntax
          { mixed: formats
        """

        config_file = tmp_path / "invalid_syntax.yaml"
        with open(config_file, "w") as f:
            f.write(invalid_yaml)

        with pytest.raises((yaml.YAMLError, ValueError)):
            WongHalvesCounter(counting_file=str(config_file))

    def test_empty_config_file(self, tmp_path):
        """Test handling of empty configuration files."""
        empty_file = tmp_path / "empty.yaml"
        empty_file.touch()

        with pytest.raises((ValueError, TypeError)):
            WongHalvesCounter(counting_file=str(empty_file))

        with pytest.raises((KeyError, TypeError, AttributeError)):
            BasicStrategy(str(empty_file))

    def test_config_with_extra_fields(self, tmp_path):
        """Test that extra fields in config don't break loading."""
        config_with_extras = {
            "counting_system": {"name": "Test"},
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
            "properties": {},
            "betting_thresholds": {},
            "betting_suggestions": {"low": {"count": -1, "suggestion": "Minimum bet"}},
            "insurance_threshold": 3.0,
            "extra_field": "This should be ignored",
            "another_extra": {"nested": "data"},
        }

        config_file = tmp_path / "config_with_extras.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_with_extras, f)

        # Should load without error
        counter = WongHalvesCounter(counting_file=str(config_file))
        assert counter.num_decks == 8

    def test_config_type_conversions(self, tmp_path):
        """Test that configs handle type conversions properly."""
        config = {
            "counting_system": {"name": "Test"},
            "card_values": {
                "2": "0.5",  # String that should convert to float
                "3": 1,  # Int that should work as float
                "4": 1.0,  # Already float
                "5": "1.5",
                "6": 1,
                "7": "0.5",
                "8": 0,
                "9": "-0.5",
                "10": -1,
                "J": "-1.0",
                "Q": -1.0,
                "K": -1.0,
                "A": -1.0,
            },
            "properties": {},
            "betting_thresholds": {"take_insurance": "3.0"},  # String that should convert to float
        }

        config_file = tmp_path / "config_conversions.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        counter = WongHalvesCounter(counting_file=str(config_file))

        # Verify conversions worked
        assert isinstance(counter.card_values["2"], (int, float))
        assert isinstance(counter.num_decks, int)
        assert counter.card_values["2"] == 0.5
        assert counter.num_decks == 8
