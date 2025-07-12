"""
8副牌21點基本策略決策引擎
假設莊家軟17點停牌
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml

from src.config import STRATEGY_CONFIG


class BasicStrategy:
    def __init__(self, strategy_file: Optional[Union[str, Path]] = None) -> None:
        """初始化策略引擎，從YAML檔案載入策略"""
        # 使用預設路徑或自定義路徑
        if strategy_file is None:
            strategy_path = STRATEGY_CONFIG
        else:
            strategy_path = Path(strategy_file)

        # 載入策略配置
        try:
            with open(strategy_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到策略檔案：{strategy_path}") from None
        except yaml.YAMLError as e:
            raise ValueError(f"策略檔案格式錯誤：{e}") from e

        # 載入策略表
        self.settings: Dict[str, Any] = config.get("settings", {})
        self.action_codes: Dict[str, Dict[str, str]] = config.get("action_codes", {})
        self.dealer_card_index: Dict[str, int] = config.get("dealer_card_index", {})

        # 載入策略表格
        hard_config: Dict[str, Any] = config.get("hard_strategy", {})
        self.hard_strategy: Dict[int, List[str]] = hard_config.get("hands", {})

        soft_config: Dict[str, Any] = config.get("soft_strategy", {})
        self.soft_strategy: Dict[int, List[str]] = soft_config.get("hands", {})

        pair_config: Dict[str, Any] = config.get("pair_strategy", {})
        self.pair_strategy: Dict[str, List[str]] = pair_config.get("pairs", {})

        # 驗證策略表格
        self._validate_strategies()

    def _validate_strategies(self) -> None:
        """驗證策略表格的完整性"""
        # 檢查硬牌策略
        for value in range(5, 22):
            if value not in self.hard_strategy:
                raise ValueError(f"硬牌策略缺少點數 {value} 的策略")

        # 檢查軟牌策略
        for value in range(13, 22):
            if value not in self.soft_strategy:
                raise ValueError(f"軟牌策略缺少點數 {value} 的策略")

        # 檢查對子策略
        expected_pairs = ["A,A", "2,2", "3,3", "4,4", "5,5", "6,6", "7,7", "8,8", "9,9", "10,10"]
        for pair in expected_pairs:
            if pair not in self.pair_strategy:
                raise ValueError(f"對子策略缺少 {pair} 的策略")

    def get_card_value(self, card: str) -> int:
        """取得牌的數值"""
        if card in ["J", "Q", "K"]:
            return 10
        elif card == "A":
            return 11
        else:
            return int(card)

    def calculate_hand_value(self, cards: List[str]) -> Tuple[int, bool]:
        """計算手牌點數，處理A的計算"""
        value = 0
        aces = 0

        for card in cards:
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

        return value, aces > 0 and value <= 21

    def get_decision(self, player_cards: List[str], dealer_card: str) -> Tuple[str, str]:
        """取得基本策略決策"""
        if len(player_cards) == 0:
            return "無手牌", "請加入玩家手牌"

        if dealer_card not in self.dealer_card_index:
            return "無效的莊家牌", "請選擇有效的莊家牌"

        dealer_index = self.dealer_card_index[dealer_card]

        # 檢查是否為對子
        if len(player_cards) == 2 and player_cards[0] == player_cards[1]:
            pair_key = f"{player_cards[0]},{player_cards[1]}"
            if pair_key in self.pair_strategy:
                decision = self.pair_strategy[pair_key][dealer_index]
                if decision == "Y":
                    action_info = self.action_codes.get("Y", {})
                    return action_info.get("action", "分牌"), action_info.get(
                        "description", "分開這對對子"
                    )

        # 計算手牌點數
        hand_value, is_soft = self.calculate_hand_value(player_cards)

        if hand_value > 21:
            return "爆牌", f"手牌點數：{hand_value}"

        # 檢查軟牌
        if is_soft and hand_value in self.soft_strategy:
            decision = self.soft_strategy[hand_value][dealer_index]
        # 檢查硬牌
        elif hand_value in self.hard_strategy:
            decision = self.hard_strategy[hand_value][dealer_index]
        else:
            # 極低點數（< 5）永遠要牌
            decision = "H"

        # 從YAML設定取得決策說明
        if decision in self.action_codes:
            action_info = self.action_codes[decision]
            action = action_info.get("action", "")
            explanation = action_info.get("description", "")
            if action:
                return action, explanation

        # 硬牌備用規則
        if hand_value >= 17:
            return "停牌", "手牌點數17或以上"
        else:
            return "要牌", "手牌點數低於17"
