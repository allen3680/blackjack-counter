"""Unit tests for GameState class."""

import pytest

from src.core.game_state import GameState


class TestGameState:
    """Test cases for GameState class."""

    def test_initialization(self):
        """Test GameState initialization."""
        game_state = GameState()
        assert game_state.player_cards == []
        assert game_state.dealer_card is None

    def test_add_player_card(self):
        """Test adding cards to player's hand."""
        game_state = GameState()

        # Add single card
        game_state.add_player_card("A")
        assert game_state.player_cards == ["A"]

        # Add another card
        game_state.add_player_card("K")
        assert game_state.player_cards == ["A", "K"]

        # Add numeric card
        game_state.add_player_card("5")
        assert game_state.player_cards == ["A", "K", "5"]

    def test_set_dealer_card(self):
        """Test setting dealer's up card."""
        game_state = GameState()

        # Set dealer card
        game_state.set_dealer_card("10")
        assert game_state.dealer_card == "10"

        # Change dealer card
        game_state.set_dealer_card("A")
        assert game_state.dealer_card == "A"

    def test_clear_hand(self):
        """Test clearing hands."""
        game_state = GameState()

        # Add some cards
        game_state.add_player_card("K")
        game_state.add_player_card("Q")
        game_state.set_dealer_card("A")

        # Clear hands
        game_state.clear_hand()

        # Verify cleared
        assert game_state.player_cards == []
        assert game_state.dealer_card is None

    def test_get_player_hand_string_empty(self):
        """Test player hand string when empty."""
        game_state = GameState()
        assert game_state.get_player_hand_string() == "無手牌"

    def test_get_player_hand_string_single_card(self):
        """Test player hand string with single card."""
        game_state = GameState()
        game_state.add_player_card("A")
        assert game_state.get_player_hand_string() == "A [軟11]"

    def test_get_player_hand_string_multiple_cards(self):
        """Test player hand string with multiple cards."""
        game_state = GameState()
        game_state.add_player_card("A")
        game_state.add_player_card("K")
        # Note: Adding third card triggers blackjack status on first two cards
        assert game_state.get_player_hand_string() == "A, K [21] (21點!)"

    def test_get_dealer_card_string_none(self):
        """Test dealer card string when no card is set."""
        game_state = GameState()
        assert game_state.get_dealer_card_string() == "無牌"

    def test_get_dealer_card_string_with_card(self):
        """Test dealer card string when card is set."""
        game_state = GameState()
        game_state.set_dealer_card("K")
        assert game_state.get_dealer_card_string() == "K"

    def test_complex_game_scenario(self):
        """Test a complex game scenario."""
        game_state = GameState()

        # First hand
        game_state.add_player_card("10")
        game_state.add_player_card("7")
        game_state.set_dealer_card("9")

        assert game_state.get_player_hand_string() == "10, 7 [17]"
        assert game_state.get_dealer_card_string() == "9"

        # Clear and new hand
        game_state.clear_hand()
        assert game_state.get_player_hand_string() == "無手牌"
        assert game_state.get_dealer_card_string() == "無牌"

        # Second hand
        game_state.add_player_card("A")
        game_state.add_player_card("A")
        game_state.set_dealer_card("6")

        assert game_state.get_player_hand_string() == "A, A [軟12]"
        assert game_state.get_dealer_card_string() == "6"

    @pytest.mark.parametrize(
        "cards,expected",
        [
            ([], "無手牌"),
            (["A"], "A [軟11]"),
            (["2", "3"], "2, 3 [5]"),
            (["J", "Q", "K"], "J, Q, K [30] (爆牌)"),
            (["A", "2", "3", "4", "5"], "A, 2, 3, 4, 5 [15]"),
        ],
    )
    def test_get_player_hand_string_parametrized(self, cards, expected):
        """Test player hand string with various card combinations."""
        game_state = GameState()
        for card in cards:
            game_state.add_player_card(card)
        assert game_state.get_player_hand_string() == expected
