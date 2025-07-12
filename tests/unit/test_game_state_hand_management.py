"""
測試 GameState 手牌管理功能
"""

import pytest
from src.core.game_state import GameState
from src.core.hand import Hand, HandStatus


class TestGameStateHandManagement:
    """測試 GameState 的手牌管理功能"""

    def test_set_current_hand_index_valid(self):
        """測試設定有效的手牌索引"""
        game_state = GameState()
        
        # 添加多個手牌
        game_state.player_hands.append(Hand())
        game_state.player_hands.append(Hand())
        
        # 測試設定有效索引
        assert game_state.set_current_hand_index(1) is True
        assert game_state.current_hand_index == 1
        
        assert game_state.set_current_hand_index(2) is True
        assert game_state.current_hand_index == 2
        
        assert game_state.set_current_hand_index(0) is True
        assert game_state.current_hand_index == 0

    def test_set_current_hand_index_invalid(self):
        """測試設定無效的手牌索引"""
        game_state = GameState()
        
        # 只有一個手牌，索引 0
        assert game_state.set_current_hand_index(-1) is False
        assert game_state.current_hand_index == 0  # 應該保持不變
        
        assert game_state.set_current_hand_index(1) is False
        assert game_state.current_hand_index == 0  # 應該保持不變
        
        assert game_state.set_current_hand_index(10) is False
        assert game_state.current_hand_index == 0  # 應該保持不變

    def test_validate_current_hand_index(self):
        """測試驗證當前手牌索引"""
        game_state = GameState()
        
        # 設定一個無效的索引（模擬內部錯誤）
        game_state.current_hand_index = 5
        game_state.validate_current_hand_index()
        assert game_state.current_hand_index == 0
        
        # 設定負數索引
        game_state.current_hand_index = -1
        game_state.validate_current_hand_index()
        assert game_state.current_hand_index == 0
        
        # 添加更多手牌，測試有效索引
        game_state.player_hands.append(Hand())
        game_state.current_hand_index = 1
        game_state.validate_current_hand_index()
        assert game_state.current_hand_index == 1  # 應該保持不變

    def test_get_hand_by_index(self):
        """測試根據索引獲取手牌"""
        game_state = GameState()
        
        # 獲取第一個手牌
        hand0 = game_state.get_hand_by_index(0)
        assert hand0 is not None
        assert hand0 == game_state.player_hands[0]
        
        # 添加更多手牌
        hand1 = Hand(["A", "K"])
        hand2 = Hand(["5", "5"])
        game_state.player_hands.append(hand1)
        game_state.player_hands.append(hand2)
        
        # 測試獲取各個手牌
        assert game_state.get_hand_by_index(1) == hand1
        assert game_state.get_hand_by_index(2) == hand2
        
        # 測試無效索引
        assert game_state.get_hand_by_index(-1) is None
        assert game_state.get_hand_by_index(3) is None
        assert game_state.get_hand_by_index(100) is None

    def test_split_with_validation(self):
        """測試分牌後的索引驗證"""
        game_state = GameState()
        
        # 設定可以分牌的手牌
        game_state.player_hands[0].cards = ["5", "5"]
        
        # 執行分牌
        assert game_state.split_current_hand() is True
        
        # 確認有兩個手牌
        assert len(game_state.player_hands) == 2
        
        # 確認當前索引仍然有效
        assert 0 <= game_state.current_hand_index < len(game_state.player_hands)

    def test_manual_hand_switching_scenario(self):
        """測試手動切換手牌的場景"""
        game_state = GameState()
        
        # 創建多個手牌的情況（模擬分牌後）
        game_state.player_hands[0].cards = ["5", "3"]
        game_state.player_hands.append(Hand(["5", "2"]))
        game_state.player_hands.append(Hand(["A", "4"]))
        
        # 玩家想要先處理第三個手牌
        assert game_state.set_current_hand_index(2) is True
        assert game_state.current_hand.cards == ["A", "4"]
        
        # 然後切換回第一個手牌
        assert game_state.set_current_hand_index(0) is True
        assert game_state.current_hand.cards == ["5", "3"]
        
        # 最後處理第二個手牌
        assert game_state.set_current_hand_index(1) is True
        assert game_state.current_hand.cards == ["5", "2"]