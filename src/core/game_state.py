"""
21點計牌器的遊戲狀態管理
"""

from typing import List, Optional
from .hand import Hand, HandStatus


class GameState:
    def __init__(self) -> None:
        self.player_hands: List[Hand] = [Hand()]  # 初始化一個手牌
        self.current_hand_index: int = 0  # 當前活動手牌索引
        self.dealer_cards: List[str] = []  # 莊家所有牌
        self.is_new_hand: bool = True
        self.max_hands: int = 32  # 最多允許32個分牌手（8副牌理論最大值）

    @property
    def current_hand(self) -> Hand:
        """取得當前活動手牌"""
        if 0 <= self.current_hand_index < len(self.player_hands):
            return self.player_hands[self.current_hand_index]
        # 如果索引無效，返回第一個手牌
        return self.player_hands[0]

    @property
    def player_cards(self) -> List[str]:
        """向後相容：取得當前手牌的牌張"""
        return self.current_hand.cards
    
    @property
    def dealer_card(self) -> Optional[str]:
        """向後相容：取得莊家明牌（第一張牌）"""
        return self.dealer_cards[0] if self.dealer_cards else None

    def add_player_card(self, card: str) -> None:
        """新增一張牌到當前玩家手牌"""
        self.current_hand.add_card(card)
        self.is_new_hand = False

        # 如果當前手牌已完成，自動切換到下一個活動手牌
        if self.current_hand.is_complete():
            self.move_to_next_active_hand()

    def set_dealer_card(self, card: str) -> None:
        """設定莊家的明牌（向後相容）"""
        self.dealer_cards = [card]
        self.is_new_hand = False
    
    def add_dealer_card(self, card: str) -> None:
        """新增一張牌到莊家手牌"""
        self.dealer_cards.append(card)
        self.is_new_hand = False
    
    def remove_last_dealer_card(self) -> Optional[str]:
        """移除莊家最後一張牌"""
        if self.dealer_cards:
            return self.dealer_cards.pop()
        return None
    
    def get_dealer_upcard(self) -> Optional[str]:
        """取得莊家明牌（第一張牌）"""
        return self.dealer_cards[0] if self.dealer_cards else None

    def clear_hand(self) -> None:
        """清除所有手牌"""
        self.player_hands = [Hand()]
        self.current_hand_index = 0
        self.dealer_cards = []
        self.is_new_hand = True

    def get_player_hand_string(self) -> str:
        """取得格式化的當前玩家手牌（向後相容）"""
        return self.current_hand.get_display_string()

    def get_dealer_card_string(self) -> str:
        """取得格式化的莊家牌"""
        if not self.dealer_cards:
            return "無牌"
        return ", ".join(self.dealer_cards)

    def can_split_current_hand(self) -> bool:
        """檢查當前手牌是否可以分牌"""
        return self.current_hand.can_be_split() and len(self.player_hands) < self.max_hands

    def split_current_hand(self) -> bool:
        """
        分割當前手牌

        Returns:
            是否成功分牌
        """
        if not self.can_split_current_hand():
            return False

        current = self.current_hand
        if len(current.cards) != 2 or current.cards[0] != current.cards[1]:
            return False

        # 建立兩個新手牌，各持有一張原始牌
        first_card = current.cards[0]
        is_ace = first_card == "A"

        # 更新當前手牌
        current.cards = [first_card]
        current.is_split_hand = True
        if is_ace:
            current.split_aces = True

        # 建立新手牌
        new_hand = Hand([first_card])
        new_hand.is_split_hand = True
        if is_ace:
            new_hand.split_aces = True

        # 插入新手牌到當前手牌後面
        self.player_hands.insert(self.current_hand_index + 1, new_hand)
        
        # 確保索引仍然有效
        self.validate_current_hand_index()

        return True

    def move_to_next_active_hand(self) -> bool:
        """
        移動到下一個需要決策的手牌

        Returns:
            是否找到活動手牌
        """
        # 從當前位置開始尋找下一個活動手牌
        for i in range(self.current_hand_index + 1, len(self.player_hands)):
            if self.player_hands[i].status == HandStatus.ACTIVE:
                self.current_hand_index = i
                return True

        # 如果後面沒有活動手牌，從頭開始找
        for i in range(0, self.current_hand_index):
            if self.player_hands[i].status == HandStatus.ACTIVE:
                self.current_hand_index = i
                return True

        # 檢查當前手牌
        if self.current_hand.status == HandStatus.ACTIVE:
            return True

        return False

    def all_hands_complete(self) -> bool:
        """檢查是否所有手牌都已完成"""
        return all(hand.is_complete() for hand in self.player_hands)

    def get_active_hand_count(self) -> int:
        """取得仍在活動中的手牌數量"""
        return sum(1 for hand in self.player_hands if hand.status == HandStatus.ACTIVE)

    def stand_current_hand(self) -> None:
        """當前手牌停牌"""
        self.current_hand.stand()
        self.move_to_next_active_hand()

    def double_down_current_hand(self) -> None:
        """當前手牌加倍"""
        self.current_hand.double_down()

    def set_current_hand_index(self, index: int) -> bool:
        """
        手動設定當前手牌索引
        
        Args:
            index: 要設定的手牌索引
            
        Returns:
            是否成功設定
        """
        if 0 <= index < len(self.player_hands):
            self.current_hand_index = index
            return True
        return False

    def validate_current_hand_index(self) -> None:
        """確保當前手牌索引在有效範圍內"""
        if self.current_hand_index >= len(self.player_hands):
            self.current_hand_index = 0
        elif self.current_hand_index < 0:
            self.current_hand_index = 0
    
    def remove_last_card_from_current_hand(self) -> Optional[str]:
        """
        從當前手牌移除最後一張牌
        
        Returns:
            被移除的牌，如果沒有牌則返回 None
        """
        return self.current_hand.remove_last_card()

    def get_hand_by_index(self, index: int) -> Optional[Hand]:
        """
        根據索引取得特定手牌
        
        Args:
            index: 手牌索引
            
        Returns:
            指定的手牌，如果索引無效則返回 None
        """
        if 0 <= index < len(self.player_hands):
            return self.player_hands[index]
        return None
