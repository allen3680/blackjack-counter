"""
Wong Halves 算牌系統實作
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import yaml

from src.config import WONG_HALVES_CONFIG


class WongHalvesCounter:
    def __init__(
        self, num_decks: int = 8, counting_file: Optional[Union[str, Path]] = None
    ) -> None:
        """初始化計數器，從YAML檔案載入牌值"""
        self.num_decks: int = num_decks
        self.total_cards: int = num_decks * 52
        self.cards_seen: int = 0
        self.running_count: float = 0.0

        # 使用預設路徑或自定義路徑
        if counting_file is None:
            counting_path = WONG_HALVES_CONFIG
        else:
            counting_path = Path(counting_file)

        try:
            with open(counting_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到計數系統檔案：{counting_path}") from None
        except yaml.YAMLError as e:
            raise ValueError(f"計數系統檔案格式錯誤：{e}") from e

        # 檢查是否為空檔案
        if config is None:
            raise ValueError("計數系統檔案是空的")

        # 載入系統資訊
        self.system_info: Dict[str, Any] = config.get("counting_system", {})
        self.system_name: str = self.system_info.get("name", "Wong Halves")

        # 載入牌值對照表並轉換為數值
        raw_card_values: Dict[str, Any] = config.get("card_values", {})
        if not raw_card_values:
            raise ValueError("計數系統檔案缺少牌值對照表")

        # 將字串值轉換為浮點數
        self.card_values: Dict[str, float] = {}
        for card, value in raw_card_values.items():
            try:
                self.card_values[card] = float(value)
            except (ValueError, TypeError):
                raise ValueError(f"牌值 {card} 的數值 {value} 無法轉換為數字") from None

        # 載入系統特性和門檻值
        self.properties: Dict[str, Any] = config.get("properties", {})
        self.betting_thresholds: Dict[str, float] = config.get("betting_thresholds", {})

        # 驗證牌值完整性
        self._validate_card_values()

    def _validate_card_values(self) -> None:
        """驗證牌值對照表的完整性"""
        required_cards = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        for card in required_cards:
            if card not in self.card_values:
                raise ValueError(f"牌值對照表缺少 {card} 的數值")

    def add_card(self, card: str) -> None:
        """新增一張牌到計數中"""
        if card in self.card_values:
            self.running_count += self.card_values[card]
            self.cards_seen += 1

    def get_true_count(self) -> float:
        """計算真實計數（流水計數 ÷ 剩餘牌組數）"""
        cards_remaining = self.total_cards - self.cards_seen
        decks_remaining = cards_remaining / 52.0

        if decks_remaining > 0:
            return round(self.running_count / decks_remaining, 2)
        return 0.0

    def get_decks_remaining(self) -> float:
        """取得剩餘牌組數"""
        cards_remaining = self.total_cards - self.cards_seen
        return round(cards_remaining / 52.0, 2)

    def get_betting_suggestion(self) -> Tuple[str, str]:
        """根據真實計數取得下注建議"""
        true_count = self.get_true_count()

        if true_count >= self.betting_thresholds.get("max_bet", 4.0):
            return "最大下注", f"真實計數 {true_count:.1f} - 強烈玩家優勢"
        elif true_count >= self.betting_thresholds.get("increase_bet", 2.0):
            return "增加下注", f"真實計數 {true_count:.1f} - 玩家優勢"
        elif true_count <= -2:
            return "最小下注", f"真實計數 {true_count:.1f} - 莊家優勢"
        else:
            return "標準下注", f"真實計數 {true_count:.1f} - 中性"

    def should_take_insurance(self) -> bool:
        """判斷是否應該買保險"""
        true_count = self.get_true_count()
        threshold = self.betting_thresholds.get("take_insurance", 3.0)
        return true_count >= threshold

    def reset(self) -> None:
        """重置計數器"""
        self.cards_seen = 0
        self.running_count = 0.0

    def new_shoe(self) -> None:
        """開始新牌靴"""
        self.reset()
