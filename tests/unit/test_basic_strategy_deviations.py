"""Unit tests for basic strategy deviations based on true count."""

from src.config import STRATEGY_CONFIG
from src.core.basic_strategy import BasicStrategy


class TestBasicStrategyDeviations:
    """Test basic strategy with count-based deviations."""

    def test_hard_hand_deviation_stand(self):
        """Test hard hand deviation from hit to stand."""
        # 使用真實的配置檔案
        strategy = BasicStrategy(allow_surrender=False)

        # 16 vs 10 - 基本策略要牌
        action, desc = strategy.get_decision(["10", "6"], "10")
        assert action == "要牌"

        # 16 vs 10 計數 >= 0 時停牌
        action, desc = strategy.get_decision(["10", "6"], "10", true_count=0.5)
        assert action == "停牌"
        assert "(計數偏移)" in desc

        # 16 vs 10 計數 < 0 時仍要牌
        action, desc = strategy.get_decision(["10", "6"], "10", true_count=-0.5)
        assert action == "要牌"

    def test_hard_hand_deviation_hit(self):
        """Test hard hand deviation from stand to hit."""
        strategy = BasicStrategy(allow_surrender=False)

        # 13 vs 2 - 基本策略停牌
        action, desc = strategy.get_decision(["10", "3"], "2")
        assert action == "停牌"

        # 13 vs 2 計數 <= -1 時要牌
        action, desc = strategy.get_decision(["10", "3"], "2", true_count=-1.5)
        assert action == "要牌"
        assert "(計數偏移)" in desc

        # 13 vs 2 計數 > -1 時仍停牌
        action, desc = strategy.get_decision(["10", "3"], "2", true_count=-0.5)
        assert action == "停牌"

    def test_hard_hand_deviation_double(self):
        """Test hard hand deviation to double."""
        strategy = BasicStrategy(allow_surrender=False)

        # 11 vs A - 基本策略要牌
        action, desc = strategy.get_decision(["6", "5"], "A")
        assert action == "要牌"

        # 11 vs A 計數 >= 1 時加倍
        action, desc = strategy.get_decision(["6", "5"], "A", true_count=1.5)
        assert action == "加倍"
        assert "(計數偏移)" in desc

        # 11 vs A 計數 < 1 時仍要牌
        action, desc = strategy.get_decision(["6", "5"], "A", true_count=0.5)
        assert action == "要牌"

    def test_pair_deviation(self):
        """Test pair splitting deviation."""
        strategy = BasicStrategy(allow_surrender=False)

        # 10,10 vs 5 - 基本策略不分牌（停牌）
        action, desc = strategy.get_decision(["10", "10"], "5")
        assert action == "停牌"

        # 10,10 vs 5 計數 >= 5 時分牌
        action, desc = strategy.get_decision(["10", "10"], "5", true_count=5.5)
        assert action == "分牌"
        assert "(計數偏移)" in desc

        # 10,10 vs 5 計數 < 5 時仍不分牌
        action, desc = strategy.get_decision(["10", "10"], "5", true_count=4.5)
        assert action == "停牌"

    def test_double_with_multiple_cards(self):
        """Test double deviation with multiple cards (should hit instead)."""
        strategy = BasicStrategy(allow_surrender=False)

        # 11點3張牌 vs A 計數 >= 1 時應該要牌（不能加倍）
        action, desc = strategy.get_decision(["2", "3", "6"], "A", true_count=2.0)
        assert action == "要牌"
        assert "(計數偏移)" in desc

    def test_insurance_decision(self):
        """Test insurance decision based on count."""
        strategy = BasicStrategy(allow_surrender=False)

        # 計數 < 3 不買保險
        assert not strategy.should_take_insurance(2.5)

        # 計數 >= 3 買保險
        assert strategy.should_take_insurance(3.0)
        assert strategy.should_take_insurance(3.5)

    def test_soft_hand_deviations(self):
        """Test soft hand deviations."""
        strategy = BasicStrategy(allow_surrender=False)

        # A,8 vs 4 - 基本策略停牌，計數 >= 3 時加倍
        action, desc = strategy.get_decision(["A", "8"], "4")
        assert action == "停牌"

        action, desc = strategy.get_decision(["A", "8"], "4", true_count=3.5)
        assert action == "加倍"
        assert "(計數偏移)" in desc

        # A,8 vs 5 - 基本策略停牌，計數 >= 1 時加倍
        action, desc = strategy.get_decision(["A", "8"], "5", true_count=0.5)
        assert action == "停牌"

        action, desc = strategy.get_decision(["A", "8"], "5", true_count=1.5)
        assert action == "加倍"
        assert "(計數偏移)" in desc

        # A,7 vs 2 - 基本策略Ds (加倍否則停牌)
        action, desc = strategy.get_decision(["A", "7"], "2")
        assert action in ["停牌", "加倍"]  # Ds

        # 這不是偏移，只是基本策略的Ds
        action, desc = strategy.get_decision(["A", "7"], "2", true_count=1.5)
        assert action == "加倍"
        # 不應該有 "(計數偏移)" 因為這是基本策略

        # 測試多張牌無法加倍的情況 - A,3,5 = 軟19
        action, desc = strategy.get_decision(["A", "3", "5"], "5", true_count=1.5)
        assert action == "停牌"
        assert "無法加倍" in desc

    def test_no_true_count_uses_basic_strategy(self):
        """Test that basic strategy is used when no true count is provided."""
        strategy = BasicStrategy(allow_surrender=False)

        # 沒有提供計數時使用基本策略
        action, desc = strategy.get_decision(["10", "6"], "10", true_count=None)
        assert action == "要牌"
        assert "(計數偏移)" not in desc

    def test_missing_deviations_file(self, tmp_path):
        """Test that strategy works without deviations file."""
        # 沒有偏移檔案時應該正常運作
        strategy = BasicStrategy(
            STRATEGY_CONFIG, tmp_path / "nonexistent.yaml", allow_surrender=False
        )

        # 使用基本策略
        action, desc = strategy.get_decision(["10", "6"], "10", true_count=2.0)
        assert action == "要牌"
        assert "(計數偏移)" not in desc
