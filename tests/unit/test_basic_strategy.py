"""Unit tests for BasicStrategy class."""

from unittest.mock import mock_open, patch

import pytest
import yaml

from src.core.basic_strategy import BasicStrategy


class TestBasicStrategy:
    """Test cases for BasicStrategy class."""

    def test_initialization_default(self, mock_basic_strategy_config):
        """Test BasicStrategy initialization with default config file."""
        mock_yaml = yaml.dump(mock_basic_strategy_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            strategy = BasicStrategy()

        assert strategy.hard_strategy == mock_basic_strategy_config["hard_strategy"]["hands"]
        assert strategy.soft_strategy == mock_basic_strategy_config["soft_strategy"]["hands"]
        assert strategy.pair_strategy == mock_basic_strategy_config["pair_strategy"]["pairs"]

    def test_initialization_custom_config(self, mock_basic_strategy_config, tmp_path):
        """Test BasicStrategy initialization with custom config file."""
        config_file = tmp_path / "custom_strategy.yaml"
        with open(config_file, "w") as f:
            yaml.dump(mock_basic_strategy_config, f)

        strategy = BasicStrategy(str(config_file))
        assert strategy.hard_strategy == mock_basic_strategy_config["hard_strategy"]["hands"]
        assert strategy.soft_strategy == mock_basic_strategy_config["soft_strategy"]["hands"]
        assert strategy.pair_strategy == mock_basic_strategy_config["pair_strategy"]["pairs"]

    def test_initialization_missing_file(self):
        """Test initialization with missing config file."""
        with pytest.raises(FileNotFoundError):
            BasicStrategy("nonexistent.yaml")

    @pytest.mark.parametrize(
        "card,expected_value",
        [
            ("2", 2),
            ("3", 3),
            ("4", 4),
            ("5", 5),
            ("6", 6),
            ("7", 7),
            ("8", 8),
            ("9", 9),
            ("10", 10),
            ("J", 10),
            ("Q", 10),
            ("K", 10),
            ("A", 11),
        ],
    )
    def test_get_card_value(self, card, expected_value, mock_basic_strategy_config):
        """Test card value calculation."""
        mock_yaml = yaml.dump(mock_basic_strategy_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            strategy = BasicStrategy()

        assert strategy.get_card_value(card) == expected_value

    def test_get_card_value_invalid(self, mock_basic_strategy_config):
        """Test invalid card returns int value if possible."""
        mock_yaml = yaml.dump(mock_basic_strategy_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            strategy = BasicStrategy()

        # Non-numeric invalid card should raise ValueError
        with pytest.raises(ValueError):
            strategy.get_card_value("X")

    @pytest.mark.parametrize(
        "cards,expected_value,expected_soft",
        [
            (["2", "3"], 5, False),  # Hard 5
            (["10", "7"], 17, False),  # Hard 17
            (["K", "Q"], 20, False),  # Hard 20
            (["A", "6"], 17, True),  # Soft 17
            (["A", "K"], 21, True),  # Blackjack (still soft)
            (["A", "A"], 12, True),  # Soft 12
            (["A", "A", "9"], 21, True),  # 1+11+9 = 21, one ace still as 11
            (["10", "9", "5"], 24, False),  # Bust
            ([], 0, False),  # No cards
            (["A"], 11, True),  # Single ace
            (["A", "3", "3"], 17, True),  # Soft 17 (A+3+3)
            (["A", "5", "5"], 21, True),  # Soft 21 (A still as 11)
            (["A", "A", "A", "8"], 21, True),  # Multiple aces (1+1+11+8, one ace still as 11)
        ],
    )
    def test_calculate_hand_value(
        self, cards, expected_value, expected_soft, mock_basic_strategy_config
    ):
        """Test hand value calculation with various card combinations."""
        mock_yaml = yaml.dump(mock_basic_strategy_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            strategy = BasicStrategy()

        value, is_soft = strategy.calculate_hand_value(cards)
        assert value == expected_value
        assert is_soft == expected_soft

    def test_get_decision_hard_hands(self, mock_basic_strategy_config):
        """Test decision making for hard hands."""
        mock_yaml = yaml.dump(mock_basic_strategy_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            strategy = BasicStrategy()

        # Hard 8 vs 6 should hit
        action, desc = strategy.get_decision(["5", "3"], "6")
        assert action == "要牌"

        # Hard 11 vs 6 should double
        action, desc = strategy.get_decision(["7", "4"], "6")
        assert action == "加倍"

        # Hard 17 vs 6 should stand
        action, desc = strategy.get_decision(["10", "7"], "6")
        assert action == "停牌"

        # Hard 12 vs 4 should stand
        action, desc = strategy.get_decision(["10", "2"], "4")
        assert action == "停牌"

    def test_get_decision_soft_hands(self, mock_basic_strategy_config):
        """Test decision making for soft hands."""
        mock_yaml = yaml.dump(mock_basic_strategy_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            strategy = BasicStrategy()

        # Soft 13 (A,2) vs 5 should double
        action, desc = strategy.get_decision(["A", "2"], "5")
        assert action == "加倍"

        # Soft 18 (A,7) vs 3 should double
        action, desc = strategy.get_decision(["A", "7"], "3")
        assert action == "加倍"

        # Soft 19 (A,8) vs any should stand
        action, desc = strategy.get_decision(["A", "8"], "10")
        assert action == "停牌"

        # Soft 17 (A,6) vs 2 should hit
        action, desc = strategy.get_decision(["A", "6"], "2")
        assert action == "要牌"

    def test_get_decision_pairs(self, mock_basic_strategy_config):
        """Test decision making for pairs."""
        mock_yaml = yaml.dump(mock_basic_strategy_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            strategy = BasicStrategy()

        # Aces should always split
        action, desc = strategy.get_decision(["A", "A"], "10")
        assert action == "分牌"

        # 8s should always split
        action, desc = strategy.get_decision(["8", "8"], "A")
        assert action == "分牌"

        # 10s should never split
        action, desc = strategy.get_decision(["10", "10"], "6")
        assert action == "停牌"

        # 2s vs 7 should split (according to basic strategy)
        action, desc = strategy.get_decision(["2", "2"], "7")
        assert action == "分牌"

        # 9s vs 7 should stand
        action, desc = strategy.get_decision(["9", "9"], "7")
        assert action == "停牌"

    def test_get_decision_edge_cases(self, mock_basic_strategy_config):
        """Test edge cases in decision making."""
        mock_yaml = yaml.dump(mock_basic_strategy_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            strategy = BasicStrategy()

        # No cards
        action, desc = strategy.get_decision([], "6")
        assert action == "無手牌"

        # Invalid dealer card
        action, desc = strategy.get_decision(["10", "7"], "X")
        assert action == "無效的莊家牌"

        # Bust hand
        action, desc = strategy.get_decision(["10", "9", "5"], "6")
        assert action == "爆牌"

        # Blackjack
        action, desc = strategy.get_decision(["A", "K"], "6")
        assert action == "停牌"

    def test_get_decision_multi_card_hands(self, mock_basic_strategy_config):
        """Test decision making with multiple cards."""
        mock_yaml = yaml.dump(mock_basic_strategy_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            strategy = BasicStrategy()

        # 3-card hard 17
        action, desc = strategy.get_decision(["5", "7", "5"], "6")
        assert action == "停牌"

        # 4-card soft 18
        action, desc = strategy.get_decision(["A", "2", "2", "3"], "6")
        assert action == "加倍"

        # Multi-card hard 12
        action, desc = strategy.get_decision(["2", "3", "3", "4"], "3")
        assert action == "要牌"

    def test_get_decision_missing_strategy_entries(self):
        """Test behavior when strategy entries are missing."""
        incomplete_config = {
            "hard_hands": {"17": {"2": "S", "3": "S"}},  # Missing many entries
            "soft_hands": {},
            "pairs": {},
        }

        mock_yaml = yaml.dump(incomplete_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            with pytest.raises(ValueError):
                BasicStrategy()

    def test_get_decision_all_dealer_cards(self, mock_basic_strategy_config):
        """Test decisions against all possible dealer cards."""
        mock_yaml = yaml.dump(mock_basic_strategy_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            strategy = BasicStrategy()

        dealer_cards = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "A"]

        # Test a few hands against all dealer cards
        for dealer_card in dealer_cards:
            # Hard 11 should mostly double
            action, desc = strategy.get_decision(["6", "5"], dealer_card)
            assert action in ["加倍", "要牌", "停牌"]

            # Hard 20 should always stand
            action, desc = strategy.get_decision(["10", "10"], dealer_card)
            assert action == "停牌"

            # Soft 19 should always stand
            action, desc = strategy.get_decision(["A", "8"], dealer_card)
            assert action == "停牌"

    @pytest.mark.parametrize(
        "player_cards,dealer_card,expected",
        [
            # Classic scenarios
            (["10", "6"], "9", "R"),  # Hard 16 vs 9 - surrender
            (["10", "6"], "6", "S"),  # Hard 16 vs 6 - stand
            (["A", "7"], "9", "H"),  # Soft 18 vs 9 - hit
            (["A", "7"], "6", "D"),  # Soft 18 vs 6 - double
            (["8", "8"], "10", "Y"),  # 8,8 vs 10 - split
            (["5", "5"], "10", "H"),  # 5,5 vs 10 - hit (treated as 10)
        ],
    )
    def test_specific_strategy_decisions(
        self, player_cards, dealer_card, expected, mock_basic_strategy_config
    ):
        """Test specific known strategy decisions."""
        mock_yaml = yaml.dump(mock_basic_strategy_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            strategy = BasicStrategy()

        action, desc = strategy.get_decision(player_cards, dealer_card)
        expected_action = {"H": "要牌", "S": "停牌", "D": "加倍", "R": "投降", "Y": "分牌"}
        assert action == expected_action[expected]
