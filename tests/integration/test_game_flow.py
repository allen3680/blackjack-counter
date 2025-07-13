"""Integration tests for complete game flow."""

from unittest.mock import mock_open, patch

import yaml

from src.core.basic_strategy import BasicStrategy
from src.core.card_counter import WongHalvesCounter
from src.core.game_state import GameState


class TestGameFlow:
    """Test complete game flow scenarios."""

    def setup_method(self):
        """Set up test dependencies."""
        self.wong_config = {
            "counting_system": {"name": "Wong Halves", "description": "專業等級的平衡計數系統"},
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
            "properties": {"balanced": True, "level": 3},
            "betting_thresholds": {"increase_bet": 2.0, "max_bet": 4.0, "take_insurance": 3.0},
        }

        self.strategy_config = {
            "settings": {"decks": 8, "dealer_stands_soft_17": True},
            "action_codes": {
                "H": {"action": "要牌", "description": "再拿一張牌"},
                "S": {"action": "停牌", "description": "保持現有手牌"},
                "D": {"action": "加倍", "description": "如允許則加倍下注，否則要牌"},
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
                    15: ["S", "S", "S", "S", "S", "H", "H", "H", "H", "H"],
                    16: ["S", "S", "S", "S", "S", "H", "H", "H", "H", "H"],
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

    def test_complete_hand_scenario(self):
        """Test a complete hand from deal to decision."""
        wong_yaml = yaml.dump(self.wong_config)
        strategy_yaml = yaml.dump(self.strategy_config)

        with patch("builtins.open") as mock_file:
            # Configure mock to return different content based on filename
            def mock_open_side_effect(filename, *args, **kwargs):
                filename_str = str(filename)  # Convert Path to string
                if "wong" in filename_str:
                    return mock_open(read_data=wong_yaml)()
                else:
                    return mock_open(read_data=strategy_yaml)()

            mock_file.side_effect = mock_open_side_effect

            # Initialize components
            game_state = GameState()
            counter = WongHalvesCounter()
            strategy = BasicStrategy()

        # Deal initial hand
        game_state.add_player_card("10")
        game_state.add_player_card("6")
        game_state.set_dealer_card("9")

        # Update counter
        counter.add_card("10")  # -1.0
        counter.add_card("6")  # +1.0
        counter.add_card("9")  # -0.5

        # Get decision
        decision = strategy.get_decision(game_state.player_cards, game_state.dealer_card)

        # Verify
        assert game_state.get_player_hand_string() == "10, 6"
        assert game_state.get_dealer_card_string() == "9"
        assert counter.running_count == -0.5
        action, desc = decision
        assert action == "要牌"  # Hard 16 vs 9 should hit

    def test_blackjack_scenario(self):
        """Test blackjack hand."""
        wong_yaml = yaml.dump(self.wong_config)
        strategy_yaml = yaml.dump(self.strategy_config)

        with patch("builtins.open") as mock_file:

            def mock_open_side_effect(filename, *args, **kwargs):
                filename_str = str(filename)  # Convert Path to string
                if "wong" in filename_str:
                    return mock_open(read_data=wong_yaml)()
                else:
                    return mock_open(read_data=strategy_yaml)()

            mock_file.side_effect = mock_open_side_effect

            game_state = GameState()
            counter = WongHalvesCounter()
            strategy = BasicStrategy()

        # Deal blackjack
        game_state.add_player_card("A")
        game_state.add_player_card("K")
        game_state.set_dealer_card("6")

        # Update counter
        counter.add_card("A")  # -1.0
        counter.add_card("K")  # -1.0
        counter.add_card("6")  # +1.0

        # Calculate hand value
        value, is_soft = strategy.calculate_hand_value(game_state.player_cards)

        # Get decision (should stand on blackjack)
        decision = strategy.get_decision(game_state.player_cards, game_state.dealer_card)

        assert value == 21
        assert is_soft  # A+K is soft 21 (Ace still counts as 11)
        assert counter.running_count == -1.0
        action, desc = decision
        assert action == "停牌"

    def test_split_scenario(self):
        """Test pair splitting scenario."""
        wong_yaml = yaml.dump(self.wong_config)
        strategy_yaml = yaml.dump(self.strategy_config)

        with patch("builtins.open") as mock_file:

            def mock_open_side_effect(filename, *args, **kwargs):
                filename_str = str(filename)  # Convert Path to string
                if "wong" in filename_str:
                    return mock_open(read_data=wong_yaml)()
                else:
                    return mock_open(read_data=strategy_yaml)()

            mock_file.side_effect = mock_open_side_effect

            game_state = GameState()
            counter = WongHalvesCounter()
            strategy = BasicStrategy()

        # Deal pair of 8s
        game_state.add_player_card("8")
        game_state.add_player_card("8")
        game_state.set_dealer_card("10")

        # Update counter
        counter.add_card("8")  # 0.0
        counter.add_card("8")  # 0.0
        counter.add_card("10")  # -1.0

        # Get decision
        decision = strategy.get_decision(game_state.player_cards, game_state.dealer_card)

        action, desc = decision
        assert action == "分牌"  # Should split 8s vs 10
        assert counter.running_count == -1.0

    def test_multiple_hands_with_counting(self):
        """Test multiple hands affecting the count."""
        wong_yaml = yaml.dump(self.wong_config)
        strategy_yaml = yaml.dump(self.strategy_config)

        with patch("builtins.open") as mock_file:

            def mock_open_side_effect(filename, *args, **kwargs):
                filename_str = str(filename)  # Convert Path to string
                if "wong" in filename_str:
                    return mock_open(read_data=wong_yaml)()
                else:
                    return mock_open(read_data=strategy_yaml)()

            mock_file.side_effect = mock_open_side_effect

            game_state = GameState()
            counter = WongHalvesCounter()
            strategy = BasicStrategy()

        # Hand 1: Player 20 vs Dealer 6
        game_state.add_player_card("K")
        game_state.add_player_card("Q")
        game_state.set_dealer_card("6")

        counter.add_card("K")  # -1.0
        counter.add_card("Q")  # -1.0
        counter.add_card("6")  # +1.0

        decision1 = strategy.get_decision(game_state.player_cards, game_state.dealer_card)
        count1 = counter.get_true_count()

        # Clear for next hand
        game_state.clear_hand()

        # Hand 2: After some low cards
        # Simulate dealer busting with low cards
        counter.add_card("5")  # +1.5
        counter.add_card("6")  # +1.0
        counter.add_card("4")  # +1.0

        # New hand
        game_state.add_player_card("A")
        game_state.add_player_card("7")
        game_state.set_dealer_card("3")

        counter.add_card("A")  # -1.0
        counter.add_card("7")  # +0.5
        counter.add_card("3")  # +1.0

        decision2 = strategy.get_decision(game_state.player_cards, game_state.dealer_card)
        count2 = counter.get_true_count()
        betting_suggestion = counter.get_betting_suggestion()

        # Verify
        action1, desc1 = decision1
        assert action1 == "停牌"  # Stand on 20
        action2, desc2 = decision2
        assert action2 == "加倍"  # Double soft 18 vs 3
        assert count2 > count1  # Count increased after low cards
        assert counter.running_count == 3.0  # -1-1+1+1.5+1+1-1+0.5+1
        bet_action, bet_desc = betting_suggestion
        assert bet_action in ["標準下注", "增加下注"]  # Positive count

    def test_insurance_decision_flow(self):
        """Test insurance decision based on count."""
        wong_yaml = yaml.dump(self.wong_config)
        strategy_yaml = yaml.dump(self.strategy_config)

        with patch("builtins.open") as mock_file:

            def mock_open_side_effect(filename, *args, **kwargs):
                filename_str = str(filename)  # Convert Path to string
                if "wong" in filename_str:
                    return mock_open(read_data=wong_yaml)()
                else:
                    return mock_open(read_data=strategy_yaml)()

            mock_file.side_effect = mock_open_side_effect

            counter = WongHalvesCounter()

        # Simulate high count scenario
        # Add many low cards to increase count
        for _ in range(20):
            counter.add_card("5")  # +1.5 each

        # Dealer shows Ace
        counter.add_card("A")  # -1.0

        # Check insurance decision
        should_insure = counter.should_take_insurance()
        true_count = counter.get_true_count()

        assert should_insure is True
        assert true_count > 3.0  # Above insurance threshold

    def test_shoe_progression(self):
        """Test game flow through multiple shoes."""
        wong_yaml = yaml.dump(self.wong_config)
        strategy_yaml = yaml.dump(self.strategy_config)

        with patch("builtins.open") as mock_file:

            def mock_open_side_effect(filename, *args, **kwargs):
                filename_str = str(filename)  # Convert Path to string
                if "wong" in filename_str:
                    return mock_open(read_data=wong_yaml)()
                else:
                    return mock_open(read_data=strategy_yaml)()

            mock_file.side_effect = mock_open_side_effect

            GameState()
            counter = WongHalvesCounter()

        # Play through part of a shoe
        cards_played = ["10", "J", "Q", "K", "A", "2", "3", "4", "5", "6"]
        for card in cards_played:
            counter.add_card(card)

        initial_count = counter.running_count
        initial_cards_seen = counter.cards_seen

        # Calculate expected count
        # 10,J,Q,K,A = -1 each = -5
        # 2 = +0.5
        # 3,4,6 = +1 each = +3
        # 5 = +1.5
        # Total = -5 + 0.5 + 3 + 1.5 = 0
        expected_count = 0.0

        # New shoe
        counter.new_shoe()

        # Verify reset
        assert counter.running_count == 0
        assert counter.cards_seen == 0
        assert initial_count == expected_count  # Should be 0
        assert initial_cards_seen == 10

    def test_edge_case_soft_hand_becomes_hard(self):
        """Test soft hand that becomes hard after hitting."""
        wong_yaml = yaml.dump(self.wong_config)
        strategy_yaml = yaml.dump(self.strategy_config)

        with patch("builtins.open") as mock_file:

            def mock_open_side_effect(filename, *args, **kwargs):
                filename_str = str(filename)  # Convert Path to string
                if "wong" in filename_str:
                    return mock_open(read_data=wong_yaml)()
                else:
                    return mock_open(read_data=strategy_yaml)()

            mock_file.side_effect = mock_open_side_effect

            game_state = GameState()
            strategy = BasicStrategy()

        # Start with soft 17
        game_state.add_player_card("A")
        game_state.add_player_card("6")
        game_state.set_dealer_card("2")

        # Get initial decision
        decision1 = strategy.get_decision(game_state.player_cards, game_state.dealer_card)
        value1, is_soft1 = strategy.calculate_hand_value(game_state.player_cards)

        # Hit and get 10 (becomes hard 17)
        game_state.add_player_card("10")

        # Get new decision
        decision2 = strategy.get_decision(game_state.player_cards, game_state.dealer_card)
        value2, is_soft2 = strategy.calculate_hand_value(game_state.player_cards)

        assert value1 == 17 and is_soft1 is True
        action1, desc1 = decision1
        assert action1 == "要牌"  # Soft 17 vs 2 should hit
        assert value2 == 17 and is_soft2 is False
        action2, desc2 = decision2
        assert action2 == "停牌"  # Hard 17 vs 2 should stand
