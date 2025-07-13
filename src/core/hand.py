"""
手牌類別 - 表示單一手牌的狀態和操作
"""

from enum import Enum
from typing import List, Optional, Tuple


class HandStatus(Enum):
    """手牌狀態"""

    ACTIVE = "active"  # 活動中，等待玩家決策
    STANDING = "standing"  # 已停牌
    BUSTED = "busted"  # 已爆牌
    BLACKJACK = "blackjack"  # 21點
    DOUBLED = "doubled"  # 已加倍


class Hand:
    """表示一個21點手牌"""

    def __init__(self, initial_cards: Optional[List[str]] = None) -> None:
        """
        初始化手牌

        Args:
            initial_cards: 初始牌張列表
        """
        self.cards: List[str] = initial_cards or []
        self.status: HandStatus = HandStatus.ACTIVE
        self.bet_multiplier: float = 1.0  # 用於追蹤加倍等情況
        self.is_split_hand: bool = False  # 標記是否為分牌後的手牌
        self.split_aces: bool = False  # 標記是否為分A的手牌

    def add_card(self, card: str) -> None:
        """新增一張牌到手牌"""
        self.cards.append(card)

        # 檢查是否爆牌
        value, _ = self.calculate_value()
        if value > 21:
            self.status = HandStatus.BUSTED
        elif value == 21 and len(self.cards) == 2 and not self.is_split_hand:
            # 只有非分牌手才能算作blackjack
            self.status = HandStatus.BLACKJACK

    def calculate_value(self) -> Tuple[int, bool]:
        """
        計算手牌點數

        Returns:
            (點數, 是否為軟牌)
        """
        value = 0
        aces = 0

        for card in self.cards:
            if card == "A":
                value += 11
                aces += 1
            elif card in ["J", "Q", "K"]:
                value += 10
            else:
                value += int(card)

        # 調整A的點數
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        is_soft = aces > 0 and value <= 21
        return value, is_soft

    def can_double_down(self) -> bool:
        """檢查是否可以加倍"""
        return len(self.cards) == 2 and self.status == HandStatus.ACTIVE

    def can_be_split(self) -> bool:
        """檢查是否可以分牌"""
        if not (
            len(self.cards) == 2
            and self.cards[0] == self.cards[1]
            and self.status == HandStatus.ACTIVE
        ):
            return False

        return True

    def double_down(self) -> None:
        """執行加倍動作"""
        if self.can_double_down():
            self.bet_multiplier = 2.0
            self.status = HandStatus.DOUBLED

    def stand(self) -> None:
        """停牌"""
        if self.status == HandStatus.ACTIVE:
            self.status = HandStatus.STANDING

    def remove_last_card(self) -> Optional[str]:
        """
        移除最後一張牌

        Returns:
            被移除的牌，如果沒有牌則返回 None
        """
        if not self.cards:
            return None

        removed_card = self.cards.pop()

        # 重新計算狀態
        if self.cards:
            value, _ = self.calculate_value()
            # 如果之前是爆牌或21點，可能需要恢復為活動狀態
            if self.status in [HandStatus.BUSTED, HandStatus.BLACKJACK]:
                if value <= 21:
                    self.status = HandStatus.ACTIVE
        else:
            # 如果沒有牌了，重置為活動狀態
            self.status = HandStatus.ACTIVE

        return removed_card

    def get_display_string(self) -> str:
        """取得格式化的手牌顯示字串"""
        if not self.cards:
            return "無手牌"

        cards_str = ", ".join(self.cards)
        return cards_str

    def is_complete(self) -> bool:
        """檢查手牌是否已完成（不需要更多決策）"""
        return self.status != HandStatus.ACTIVE

    def clone(self) -> "Hand":
        """複製手牌（用於分牌）"""
        new_hand = Hand()
        new_hand.cards = self.cards.copy()
        new_hand.status = self.status
        new_hand.bet_multiplier = self.bet_multiplier
        new_hand.is_split_hand = self.is_split_hand
        new_hand.split_aces = self.split_aces
        return new_hand
