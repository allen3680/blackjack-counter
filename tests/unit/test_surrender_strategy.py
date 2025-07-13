"""Unit tests for surrender strategy functionality."""

from src.core.basic_strategy import BasicStrategy


class TestSurrenderStrategy:
    """Test surrender strategy functionality."""

    def test_surrender_enabled_by_default(self):
        """Test that surrender is enabled by default."""
        strategy = BasicStrategy()
        assert strategy.allow_surrender is True

    def test_surrender_disabled_option(self):
        """Test that surrender can be disabled."""
        strategy = BasicStrategy(allow_surrender=False)
        assert strategy.allow_surrender is False

    def test_hard_15_vs_10_surrender(self):
        """Test hard 15 vs dealer 10 should surrender when allowed."""
        # With surrender enabled
        strategy = BasicStrategy(allow_surrender=True)
        action, desc = strategy.get_decision(["10", "5"], "10")
        assert action == "投降"
        assert "如允許則投降" in desc

        # With surrender disabled
        strategy = BasicStrategy(allow_surrender=False)
        action, desc = strategy.get_decision(["10", "5"], "10")
        assert action == "要牌"

    def test_hard_16_vs_9_10_A_surrender(self):
        """Test hard 16 vs dealer 9, 10, A should surrender when allowed."""
        strategy_enabled = BasicStrategy(allow_surrender=True)
        strategy_disabled = BasicStrategy(allow_surrender=False)

        # Test vs 9
        action, _ = strategy_enabled.get_decision(["10", "6"], "9")
        assert action == "投降"
        action, _ = strategy_disabled.get_decision(["10", "6"], "9")
        assert action == "要牌"

        # Test vs 10
        action, _ = strategy_enabled.get_decision(["10", "6"], "10")
        assert action == "投降"
        action, _ = strategy_disabled.get_decision(["10", "6"], "10")
        assert action == "要牌"

        # Test vs A
        action, _ = strategy_enabled.get_decision(["10", "6"], "A")
        assert action == "投降"
        action, _ = strategy_disabled.get_decision(["10", "6"], "A")
        assert action == "要牌"

    def test_pair_8_8_should_not_surrender(self):
        """Test that pair 8,8 should split, not surrender."""
        strategy = BasicStrategy(allow_surrender=True)

        # 8,8 vs 10 should split, not surrender
        action, _ = strategy.get_decision(["8", "8"], "10")
        assert action == "分牌"

        # 8,8 vs A should split, not surrender
        action, _ = strategy.get_decision(["8", "8"], "A")
        assert action == "分牌"

    def test_no_surrender_on_soft_hands(self):
        """Test that soft hands never surrender."""
        strategy = BasicStrategy(allow_surrender=True)

        # Soft 16 (A,5) vs 10 should not surrender
        action, _ = strategy.get_decision(["A", "5"], "10")
        assert action != "投降"

        # Soft 15 (A,4) vs 10 should not surrender
        action, _ = strategy.get_decision(["A", "4"], "10")
        assert action != "投降"

    def test_no_surrender_after_hitting(self):
        """Test that surrender is only available on first two cards."""
        strategy = BasicStrategy(allow_surrender=True)

        # Three cards totaling 16 should not surrender
        action, _ = strategy.get_decision(["5", "5", "6"], "10")
        assert action == "要牌"  # Not surrender

    def test_toggle_surrender_setting(self):
        """Test toggling surrender setting."""
        strategy = BasicStrategy()

        # Initially enabled
        assert strategy.allow_surrender is True
        action, _ = strategy.get_decision(["10", "6"], "10")
        assert action == "投降"

        # Disable surrender
        strategy.set_allow_surrender(False)
        assert strategy.allow_surrender is False
        action, _ = strategy.get_decision(["10", "6"], "10")
        assert action == "要牌"

        # Re-enable surrender
        strategy.set_allow_surrender(True)
        assert strategy.allow_surrender is True
        action, _ = strategy.get_decision(["10", "6"], "10")
        assert action == "投降"

    def test_surrender_with_count_deviations(self):
        """Test that surrender takes precedence over count deviations."""
        strategy = BasicStrategy(allow_surrender=True)

        # 16 vs 10 with positive count - should still surrender (not stand)
        action, desc = strategy.get_decision(["10", "6"], "10", true_count=1.0)
        assert action == "投降"
        # Count deviation might try to make it stand, but surrender takes precedence

    def test_surrender_deviations_when_enabled(self):
        """Test surrender deviations work when surrender is allowed."""
        strategy = BasicStrategy(allow_surrender=True)

        # 16 vs 8 - 基本策略不投降，但計數 >= 4 時投降
        action, desc = strategy.get_decision(["10", "6"], "8", true_count=3.5)
        assert action == "要牌"  # 計數不夠高

        action, desc = strategy.get_decision(["10", "6"], "8", true_count=4.5)
        assert action == "投降"
        assert "(計數偏移)" in desc

        # 15 vs 9 - 基本策略不投降，計數 >= 2 時投降
        action, desc = strategy.get_decision(["10", "5"], "9", true_count=1.5)
        assert action == "要牌"

        action, desc = strategy.get_decision(["10", "5"], "9", true_count=2.5)
        assert action == "投降"
        assert "(計數偏移)" in desc

    def test_no_surrender_deviations_when_disabled(self):
        """Test surrender deviations don't apply when surrender is disabled."""
        strategy = BasicStrategy(allow_surrender=False)

        # 16 vs 8 with high count - should not surrender when surrender is disabled
        action, desc = strategy.get_decision(["10", "6"], "8", true_count=5.0)
        assert action == "要牌"
        assert "(計數偏移)" not in desc or "投降" not in desc

    def test_16_vs_9_all_count_scenarios(self):
        """Test 16 vs 9 with various true counts to verify deviation priorities."""
        strategy = BasicStrategy(allow_surrender=True)

        # 16 vs 9 基本策略：投降
        # 投降偏移：計數 <= -1 時不投降
        # 硬牌偏移：計數 >= 4 時停牌

        # 測試基本策略（無計數）
        action, desc = strategy.get_decision(["10", "6"], "9")
        assert action == "投降", f"Expected 投降 but got {action}"

        # 測試計數 = 0（投降偏移未生效，應該投降）
        action, desc = strategy.get_decision(["10", "6"], "9", true_count=0)
        assert action == "投降", f"Expected 投降 at count 0 but got {action}"

        # 測試計數 = -0.5（投降偏移未生效，應該投降）
        action, desc = strategy.get_decision(["10", "6"], "9", true_count=-0.5)
        assert action == "投降", f"Expected 投降 at count -0.5 but got {action}"

        # 測試計數 = -1.0（投降偏移生效，應該要牌）
        action, desc = strategy.get_decision(["10", "6"], "9", true_count=-1.0)
        assert action == "要牌", f"Expected 要牌 at count -1.0 but got {action}"
        assert "(計數偏移)" not in desc or "投降" not in desc

        # 測試計數 = -1.5（投降偏移生效，應該要牌）
        action, desc = strategy.get_decision(["10", "6"], "9", true_count=-1.5)
        assert action == "要牌", f"Expected 要牌 at count -1.5 but got {action}"

        # 測試計數 = 3.5（硬牌偏移未生效，應該投降）
        action, desc = strategy.get_decision(["10", "6"], "9", true_count=3.5)
        assert action == "投降", f"Expected 投降 at count 3.5 but got {action}"

        # 測試計數 = 4.0（基本投降優先於硬牌偏移，應該投降）
        action, desc = strategy.get_decision(["10", "6"], "9", true_count=4.0)
        assert action == "投降", f"Expected 投降 at count 4.0 but got {action}"

        # 測試計數 = 4.5（基本投降優先於硬牌偏移，應該投降）
        action, desc = strategy.get_decision(["10", "6"], "9", true_count=4.5)
        assert action == "投降", f"Expected 投降 at count 4.5 but got {action}"

    def test_16_vs_9_no_surrender_allowed(self):
        """Test 16 vs 9 when surrender is not allowed - hard deviations should work."""
        strategy = BasicStrategy(allow_surrender=False)

        # 16 vs 9 基本策略（無投降）：要牌
        # 硬牌偏移：計數 >= 4 時停牌

        # 測試基本策略（無計數）
        action, desc = strategy.get_decision(["10", "6"], "9")
        assert action == "要牌", f"Expected 要牌 but got {action}"

        # 測試計數 = 3.5（硬牌偏移未生效，應該要牌）
        action, desc = strategy.get_decision(["10", "6"], "9", true_count=3.5)
        assert action == "要牌", f"Expected 要牌 at count 3.5 but got {action}"

        # 測試計數 = 4.0（硬牌偏移生效，應該停牌）
        action, desc = strategy.get_decision(["10", "6"], "9", true_count=4.0)
        assert action == "停牌", f"Expected 停牌 at count 4.0 but got {action}"
        assert "(計數偏移)" in desc

        # 測試計數 = 4.5（硬牌偏移生效，應該停牌）
        action, desc = strategy.get_decision(["10", "6"], "9", true_count=4.5)
        assert action == "停牌", f"Expected 停牌 at count 4.5 but got {action}"
        assert "(計數偏移)" in desc
