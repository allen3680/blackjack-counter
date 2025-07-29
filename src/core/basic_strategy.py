"""
8副牌21點基本策略決策引擎
假設莊家軟17點停牌
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml

from src.config import DEVIATIONS_CONFIG, STRATEGY_CONFIG


class BasicStrategy:
    def __init__(
        self,
        strategy_file: Optional[Union[str, Path]] = None,
        deviations_file: Optional[Union[str, Path]] = None,
        allow_surrender: bool = True,
    ) -> None:
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

        # 載入投降策略表格
        surrender_config: Dict[str, Any] = config.get("surrender_strategy", {})
        self.surrender_strategy: Dict[int, List[str]] = surrender_config.get("hands", {})
        self.allow_surrender = allow_surrender

        # 載入偏移策略
        if deviations_file is None:
            deviations_path = DEVIATIONS_CONFIG
        else:
            deviations_path = Path(deviations_file)

        try:
            with open(deviations_path, "r", encoding="utf-8") as f:
                deviations_config = yaml.safe_load(f)
            self.deviations = deviations_config.get("deviations", {})
            self.insurance_threshold = self.deviations.get("insurance", {}).get(
                "true_count_threshold", 3.0
            )
            self.hard_deviations = self.deviations.get("hard_hands", {})
            self.soft_deviations = self.deviations.get("soft_hands", {})
            self.pair_deviations = self.deviations.get("pairs", {})
            self.surrender_deviations = self.deviations.get("surrender", {})
        except FileNotFoundError:
            # 如果沒有偏移檔案，使用空的偏移設定
            self.deviations = {}
            self.insurance_threshold = 3.0
            self.hard_deviations = {}
            self.soft_deviations = {}
            self.pair_deviations = {}
            self.surrender_deviations = {}
        except yaml.YAMLError:
            # 偏移檔案格式錯誤，使用空的偏移設定
            self.deviations = {}
            self.insurance_threshold = 3.0
            self.hard_deviations = {}
            self.soft_deviations = {}
            self.pair_deviations = {}
            self.surrender_deviations = {}

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

        # 檢查投降策略（如果存在）
        if self.surrender_strategy:
            for value in range(5, 22):
                if value not in self.surrender_strategy:
                    raise ValueError(f"投降策略缺少點數 {value} 的策略")

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

    def _check_surrender_deviation(
        self, hand_value: int, dealer_card: str, true_count: Optional[float]
    ) -> Optional[Tuple[str, str]]:
        """檢查投降偏移（優先級最高）"""
        if true_count is None or not self.allow_surrender:
            return None

        surrender_key = f"{hand_value}-{dealer_card}"
        if surrender_key in self.surrender_deviations:
            deviation = self.surrender_deviations[surrender_key]
            threshold = deviation["true_count_threshold"]
            comparison_op = deviation.get("comparison_operator", ">=")

            # 根據比較運算子判斷是否應用偏移
            apply_deviation = False
            if comparison_op == ">=":
                apply_deviation = true_count >= threshold
            elif comparison_op == "<=":
                apply_deviation = true_count <= threshold

            if apply_deviation:
                if deviation["deviation_action"] == "R":
                    # 偏移動作是投降
                    action_info = self.action_codes.get("R", {})
                    description = deviation.get("description", action_info.get("description", ""))
                    return action_info.get("action", "投降"), f"{description} (計數偏移)"
                else:
                    # 偏移動作不是投降（如要牌），設定標記跳過基本策略的投降檢查
                    return ("SKIP_SURRENDER", deviation["deviation_action"])

        return None

    def _check_other_deviations(
        self,
        hand_value: int,
        dealer_card: str,
        is_pair: bool,
        true_count: Optional[float],
        num_cards: int,
        player_cards: List[str],
    ) -> Optional[Tuple[str, str]]:
        """檢查硬牌、軟牌和分牌偏移"""
        if true_count is None:
            return None

        # 檢查對子偏移
        if is_pair:
            # 對於對子，使用特殊格式 如 "10,10-5"
            card_value = str(hand_value // 2)
            pair_key = f"{card_value},{card_value}-{dealer_card}"
            if pair_key in self.pair_deviations:
                deviation = self.pair_deviations[pair_key]
                threshold = deviation["true_count_threshold"]
                basic_action = deviation["basic_action"]
                deviation_action = deviation["deviation_action"]

                comparison_op = deviation.get("comparison_operator", ">=")

                # 根據比較運算子判斷是否應用偏移
                apply_deviation = False
                if comparison_op == ">=":
                    apply_deviation = true_count >= threshold
                elif comparison_op == "<=":
                    apply_deviation = true_count <= threshold

                if deviation_action == "Y" and apply_deviation:
                    action_info = self.action_codes.get("Y", {})
                    description = deviation.get("description", action_info.get("description", ""))
                    return action_info.get("action", "分牌"), f"{description} (計數偏移)"
                elif deviation_action == "N" and not apply_deviation:
                    # 不分牌，繼續檢查其他選項
                    pass

        # 檢查軟牌偏移（如果是軟牌）
        hand_value_calc, is_soft_calc = self.calculate_hand_value(player_cards)
        if is_soft_calc:
            soft_key = f"{hand_value}-{dealer_card}"
            if soft_key in self.soft_deviations:
                deviation = self.soft_deviations[soft_key]
                threshold = deviation["true_count_threshold"]
                basic_action = deviation["basic_action"]
                deviation_action = deviation["deviation_action"]

                comparison_op = deviation.get("comparison_operator", ">=")

                # 根據比較運算子判斷是否應用偏移
                apply_deviation = False
                if comparison_op == ">=":
                    apply_deviation = true_count >= threshold
                elif comparison_op == "<=":
                    apply_deviation = true_count <= threshold

                if apply_deviation:
                    # 處理 Ds 偏移（加倍否則停牌）
                    if deviation_action == "Ds":
                        if num_cards > 2:
                            action_info = self.action_codes.get("S", {})
                            return (
                                action_info.get("action", "停牌"),
                                "無法加倍，選擇停牌 (計數偏移)",
                            )
                        else:
                            action_info = self.action_codes.get("D", {})
                            description = deviation.get(
                                "description", action_info.get("description", "")
                            )
                            return action_info.get("action", "加倍"), f"{description} (計數偏移)"
                    else:
                        action_info = self.action_codes.get(deviation_action, {})
                        description = deviation.get(
                            "description", action_info.get("description", "")
                        )
                        return action_info.get("action", ""), f"{description} (計數偏移)"

        # 檢查硬牌偏移（只有非軟牌才應用硬牌偏移）
        if not is_soft_calc:
            hard_key = f"{hand_value}-{dealer_card}"
            if hard_key in self.hard_deviations:
                deviation = self.hard_deviations[hard_key]
                threshold = deviation["true_count_threshold"]
                basic_action = deviation["basic_action"]
                deviation_action = deviation["deviation_action"]

                comparison_op = deviation.get("comparison_operator")

                # 如果沒有指定比較運算子，使用舊的邏輯作為向後相容
                if comparison_op is None:
                    if basic_action in ["H"] and deviation_action in ["S", "D", "R"]:
                        # 基本策略要牌，偏移為停牌/加倍/投降，需要計數 >= 門檻
                        apply_deviation = true_count >= threshold
                    elif basic_action in ["S"] and deviation_action in ["H", "D"]:
                        # 基本策略停牌，偏移為要牌/加倍，需要計數 <= 門檻
                        apply_deviation = true_count <= threshold
                    else:
                        apply_deviation = False
                else:
                    # 使用 YAML 中指定的比較運算子
                    if comparison_op == ">=":
                        apply_deviation = true_count >= threshold
                    elif comparison_op == "<=":
                        apply_deviation = true_count <= threshold
                    else:
                        apply_deviation = False

                if apply_deviation:
                    # 如果偏移動作是加倍但牌數超過2張，改為要牌
                    if deviation_action == "D" and num_cards > 2:
                        action_info = self.action_codes.get("H", {})
                        return action_info.get("action", "要牌"), "無法加倍，改為要牌 (計數偏移)"
                    else:
                        action_info = self.action_codes.get(deviation_action, {})
                        description = deviation.get(
                            "description", action_info.get("description", "")
                        )
                        return action_info.get("action", ""), f"{description} (計數偏移)"

        return None

    def should_take_insurance(self, true_count: float) -> bool:
        """根據真實計數判斷是否應該買保險"""
        return bool(true_count >= self.insurance_threshold)

    def set_allow_surrender(self, allow: bool) -> None:
        """設定是否允許投降"""
        self.allow_surrender = allow

    def get_decision(
        self, player_cards: List[str], dealer_card: str, true_count: Optional[float] = None
    ) -> Tuple[str, str]:
        """取得策略決策（含偏移）"""
        if len(player_cards) == 0:
            return "無手牌", "請加入玩家手牌"

        if dealer_card not in self.dealer_card_index:
            return "無效的莊家牌", "請選擇有效的莊家牌"

        dealer_index = self.dealer_card_index[dealer_card]

        # 計算手牌點數
        hand_value, is_soft = self.calculate_hand_value(player_cards)

        if hand_value > 21:
            return "爆牌", f"手牌點數：{hand_value}"

        # 檢查是否為對子
        is_pair = len(player_cards) == 2 and player_cards[0] == player_cards[1]

        # 1. 先檢查投降偏移（優先級最高）
        surrender_deviation_result = self._check_surrender_deviation(
            hand_value, dealer_card, true_count
        )

        # 處理投降偏移結果
        skip_surrender = False
        if surrender_deviation_result:
            if (
                isinstance(surrender_deviation_result, tuple)
                and surrender_deviation_result[0] == "SKIP_SURRENDER"
            ):
                # 投降偏移指示不投降，跳過基本策略的投降檢查
                skip_surrender = True
            else:
                # 返回投降偏移結果
                return surrender_deviation_result

        # 2. 檢查基本策略的投降（只在沒有投降偏移覆蓋時）
        if not skip_surrender and self.allow_surrender and len(player_cards) == 2 and not is_soft:
            # 對子8,8不應該投降，應該分牌
            if not (is_pair and player_cards[0] == "8"):
                if hand_value in self.surrender_strategy:
                    surrender_decision = self.surrender_strategy[hand_value][dealer_index]
                    if surrender_decision == "Y":
                        action_info = self.action_codes.get("R", {})
                        return action_info.get("action", "投降"), action_info.get(
                            "description", "如允許則投降，否則要牌"
                        )

        # 3. 檢查其他偏移（硬牌、軟牌、分牌）
        other_deviation_result = self._check_other_deviations(
            hand_value, dealer_card, is_pair, true_count, len(player_cards), player_cards
        )
        if other_deviation_result:
            return other_deviation_result

        # 4. 使用基本策略
        if is_pair:
            pair_key = f"{player_cards[0]},{player_cards[1]}"
            if pair_key in self.pair_strategy:
                decision = self.pair_strategy[pair_key][dealer_index]
                if decision == "Y":
                    action_info = self.action_codes.get("Y", {})
                    return action_info.get("action", "分牌"), action_info.get(
                        "description", "分開這對對子"
                    )

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

            # 處理 Ds (Double if allowed, otherwise stand)
            if decision == "Ds":
                # 這裡假設如果手牌超過2張就不能加倍
                if len(player_cards) > 2:
                    return "停牌", "無法加倍，選擇停牌"

            if action:
                return action, explanation

        # 硬牌備用規則
        if hand_value >= 17:
            return "停牌", "手牌點數17或以上"
        else:
            return "要牌", "手牌點數低於17"
