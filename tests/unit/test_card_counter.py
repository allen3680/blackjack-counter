"""Unit tests for WongHalvesCounter class."""

from unittest.mock import mock_open, patch

import pytest
import yaml

from src.core.card_counter import WongHalvesCounter


class TestWongHalvesCounter:
    """Test cases for WongHalvesCounter class."""

    def test_initialization_default(self, mock_wong_halves_config):
        """Test WongHalvesCounter initialization with default config file."""
        mock_yaml = yaml.dump(mock_wong_halves_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            counter = WongHalvesCounter()

        assert counter.running_count == 0
        assert counter.cards_seen == 0
        assert counter.num_decks == 8
        assert counter.card_values == mock_wong_halves_config["card_values"]

    def test_initialization_custom_config(self, mock_wong_halves_config, tmp_path):
        """Test WongHalvesCounter initialization with custom config file."""
        config_file = tmp_path / "custom_wong.yaml"
        with open(config_file, "w") as f:
            yaml.dump(mock_wong_halves_config, f)

        counter = WongHalvesCounter(counting_file=str(config_file))

        assert counter.running_count == 0
        assert counter.cards_seen == 0
        assert counter.num_decks == 8

    def test_initialization_missing_file(self):
        """Test initialization with missing config file."""
        with pytest.raises(FileNotFoundError):
            WongHalvesCounter(counting_file="nonexistent.yaml")

    def test_add_card_valid_cards(self, mock_wong_halves_config):
        """Test adding valid cards updates counts correctly."""
        mock_yaml = yaml.dump(mock_wong_halves_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            counter = WongHalvesCounter()

        # Test positive value card
        counter.add_card("3")  # Value: +1.0
        assert counter.running_count == 1.0
        assert counter.cards_seen == 1

        # Test negative value card
        counter.add_card("K")  # Value: -1.0
        assert counter.running_count == 0.0
        assert counter.cards_seen == 2

        # Test fractional value card
        counter.add_card("2")  # Value: +0.5
        assert counter.running_count == 0.5
        assert counter.cards_seen == 3

        # Test zero value card
        counter.add_card("8")  # Value: 0.0
        assert counter.running_count == 0.5
        assert counter.cards_seen == 4

    def test_add_card_invalid_card(self, mock_wong_halves_config):
        """Test adding invalid card does not affect count."""
        mock_yaml = yaml.dump(mock_wong_halves_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            counter = WongHalvesCounter()

        # Invalid card should not change count
        counter.add_card("X")
        assert counter.running_count == 0
        assert counter.cards_seen == 0

    def test_get_true_count(self, mock_wong_halves_config):
        """Test true count calculation."""
        mock_yaml = yaml.dump(mock_wong_halves_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            counter = WongHalvesCounter()

        # Initial true count should be 0
        assert counter.get_true_count() == 0.0

        # Add cards to get running count of 8
        for _ in range(8):
            counter.add_card("3")  # +1.0 each

        # With 8 cards seen from 8 decks, remaining decks ≈ 7.85
        # True count = 8 / 7.85 ≈ 1.02
        assert 1.0 <= counter.get_true_count() <= 1.1

        # Add more cards
        for _ in range(44):  # Total 52 cards = 1 deck
            counter.add_card("8")  # 0 value, doesn't change count

        # True count = 8 / 7 ≈ 1.14
        assert 1.1 <= counter.get_true_count() <= 1.2

    def test_get_decks_remaining(self, mock_wong_halves_config):
        """Test decks remaining calculation."""
        mock_yaml = yaml.dump(mock_wong_halves_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            counter = WongHalvesCounter()

        # Initially should have 8 decks
        assert counter.get_decks_remaining() == 8.0

        # After 52 cards (1 deck), should have 7 decks
        for _ in range(52):
            counter.add_card("8")  # Using 8 for neutral count
        assert counter.get_decks_remaining() == 7.0

        # After 104 cards (2 decks), should have 6 decks
        for _ in range(52):
            counter.add_card("8")
        assert counter.get_decks_remaining() == 6.0

    def test_get_betting_suggestion(self, mock_wong_halves_config):
        """Test betting suggestions based on true count."""
        mock_yaml = yaml.dump(mock_wong_halves_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            counter = WongHalvesCounter()

        # Test low count
        counter.running_count = -20
        suggestion, desc = counter.get_betting_suggestion()
        assert suggestion == "最小下注"

        # Test medium count (true count between -2 and 2)
        counter.running_count = 8  # True count ~1
        suggestion, desc = counter.get_betting_suggestion()
        assert suggestion == "標準下注"

        # Test high count (true count >= 2)
        counter.running_count = 17  # True count ~2.1
        suggestion, desc = counter.get_betting_suggestion()
        assert suggestion == "增加下注"

        # Test very high count (true count >= 4)
        counter.running_count = 33  # True count ~4.1
        suggestion, desc = counter.get_betting_suggestion()
        assert suggestion == "最大下注"

    def test_should_take_insurance(self, mock_wong_halves_config):
        """Test insurance decision based on true count."""
        mock_yaml = yaml.dump(mock_wong_halves_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            counter = WongHalvesCounter()

        # Low count - no insurance
        counter.running_count = 16  # True count ~2
        assert counter.should_take_insurance() is False

        # High count - take insurance
        counter.running_count = 24  # True count ~3
        assert counter.should_take_insurance() is True

        # Very high count - definitely take insurance
        counter.running_count = 40  # True count ~5
        assert counter.should_take_insurance() is True

    def test_reset(self, mock_wong_halves_config):
        """Test resetting the counter."""
        mock_yaml = yaml.dump(mock_wong_halves_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            counter = WongHalvesCounter()

        # Add some cards
        counter.add_card("A")
        counter.add_card("K")
        counter.add_card("5")

        # Reset
        counter.reset()

        # Verify reset
        assert counter.running_count == 0
        assert counter.cards_seen == 0

    def test_new_shoe(self, mock_wong_halves_config):
        """Test starting a new shoe."""
        mock_yaml = yaml.dump(mock_wong_halves_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            counter = WongHalvesCounter()

        # Add some cards
        counter.add_card("A")
        counter.add_card("K")
        counter.add_card("5")

        # New shoe (should be same as reset)
        counter.new_shoe()

        # Verify reset
        assert counter.running_count == 0
        assert counter.cards_seen == 0

    @pytest.mark.parametrize(
        "cards,expected_count",
        [
            (["2", "7"], 1.0),  # 0.5 + 0.5
            (["3", "4", "6"], 3.0),  # 1.0 + 1.0 + 1.0
            (["5"], 1.5),  # 1.5
            (["8"], 0.0),  # 0.0
            (["9"], -0.5),  # -0.5
            (["10", "J", "Q", "K", "A"], -5.0),  # -1.0 each
            (["A", "5", "9", "3"], 1.0),  # -1.0 + 1.5 + -0.5 + 1.0
        ],
    )
    def test_running_count_combinations(self, cards, expected_count, mock_wong_halves_config):
        """Test running count with various card combinations."""
        mock_yaml = yaml.dump(mock_wong_halves_config)

        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            counter = WongHalvesCounter()

        for card in cards:
            counter.add_card(card)

        assert counter.running_count == expected_count
        assert counter.cards_seen == len(cards)

    def test_config_validation(self):
        """Test config validation for missing required fields."""
        # Missing card_values
        bad_config = {
            "counting_system": {"name": "Test"},
            "properties": {},
            "betting_thresholds": {},
        }

        mock_yaml = yaml.dump(bad_config)
        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            with pytest.raises(ValueError, match="計數系統檔案缺少牌值對照表"):
                WongHalvesCounter()
