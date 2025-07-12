#!/usr/bin/env python3
"""
21點計牌器 - 桌面應用程式
使用 Wong Halves 計牌系統與 8 副牌基本策略
"""

import tkinter as tk
from tkinter import messagebox, ttk

from src.core import BasicStrategy, GameState, WongHalvesCounter, HandStatus


class BlackjackCounterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root: tk.Tk = root
        self.root.title("21點計牌器 - Wong Halves 系統")
        self.root.geometry("1000x800")

        # 初始化元件
        self.counter: WongHalvesCounter = WongHalvesCounter(num_decks=8)
        self.strategy: BasicStrategy = BasicStrategy()
        self.game_state: GameState = GameState()

        # 設定樣式
        style = ttk.Style()
        style.configure("Active.TFrame", background="lightblue", relief="solid", borderwidth=3)

        # GUI 元件
        self.running_count_label: ttk.Label
        self.true_count_label: ttk.Label
        self.decks_label: ttk.Label
        self.cards_seen_label: ttk.Label
        self.player_hand_label: ttk.Label
        self.dealer_card_label: ttk.Label
        self.decision_label: ttk.Label
        self.explanation_label: ttk.Label

        # 手牌顯示框架和標籤
        self.hands_frame: ttk.LabelFrame
        self.hand_frames: list[ttk.Frame] = []
        self.hand_labels: list[ttk.Label] = []
        self.hand_decision_labels: list[ttk.Label] = []
        self.split_button: ttk.Button

        # 建立使用者介面
        self.create_widgets()
        self.update_display()

    def create_widgets(self) -> None:
        # 頂部框架 - 計數顯示
        count_frame = ttk.Frame(self.root, padding="10")
        count_frame.grid(row=0, column=0, columnspan=2, sticky="WE")

        # 計數標籤
        ttk.Label(count_frame, text="流水計數：", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        self.running_count_label = ttk.Label(count_frame, text="0.0", font=("Arial", 16, "bold"))
        self.running_count_label.grid(row=0, column=1, padx=5)

        ttk.Label(count_frame, text="真實計數：", font=("Arial", 12)).grid(row=0, column=2, padx=5)
        self.true_count_label = ttk.Label(count_frame, text="0.0", font=("Arial", 16, "bold"))
        self.true_count_label.grid(row=0, column=3, padx=5)

        ttk.Label(count_frame, text="剩餘牌組：", font=("Arial", 12)).grid(row=0, column=4, padx=5)
        self.decks_label = ttk.Label(count_frame, text="8.0", font=("Arial", 16))
        self.decks_label.grid(row=0, column=5, padx=5)

        ttk.Label(count_frame, text="已見牌數：", font=("Arial", 12)).grid(row=1, column=0, padx=5)
        self.cards_seen_label = ttk.Label(count_frame, text="0", font=("Arial", 16))
        self.cards_seen_label.grid(row=1, column=1, padx=5)

        # 中間框架 - 遊戲狀態
        game_frame = ttk.LabelFrame(self.root, text="遊戲狀態", padding="10")
        game_frame.grid(row=1, column=0, columnspan=2, sticky="WE", padx=10, pady=5)

        # 莊家牌
        ttk.Label(game_frame, text="莊家明牌：", font=("Arial", 12)).grid(
            row=0, column=0, sticky=tk.W, padx=5
        )
        self.dealer_card_label = ttk.Label(game_frame, text="無牌", font=("Arial", 14))
        self.dealer_card_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        # 手牌顯示框架
        self.hands_frame = ttk.LabelFrame(self.root, text="玩家手牌", padding="10")
        self.hands_frame.grid(row=2, column=0, columnspan=2, sticky="WE", padx=10, pady=5)

        # 初始化手牌顯示（向後相容）
        initial_hand_frame = ttk.Frame(self.hands_frame)
        initial_hand_frame.grid(row=0, column=0, sticky="WE", padx=5)
        self.player_hand_label = ttk.Label(initial_hand_frame, text="無手牌", font=("Arial", 14))
        self.player_hand_label.pack(side=tk.LEFT)

        # 決策顯示（主要決策）
        decision_frame = ttk.LabelFrame(self.root, text="建議動作", padding="10")
        decision_frame.grid(row=3, column=0, columnspan=2, sticky="WE", padx=10, pady=5)

        self.decision_label = ttk.Label(
            decision_frame,
            text="請加入手牌以查看建議",
            font=("Arial", 18, "bold"),
            foreground="blue",
        )
        self.decision_label.grid(row=0, column=0, pady=5)

        self.explanation_label = ttk.Label(decision_frame, text="", font=("Arial", 12))
        self.explanation_label.grid(row=1, column=0)

        # 牌輸入區域 - 分為三個部分
        input_container = ttk.Frame(self.root, padding="5")
        input_container.grid(row=4, column=0, columnspan=2, sticky="WE")

        # 玩家手牌輸入區
        player_frame = ttk.LabelFrame(input_container, text="玩家手牌", padding="10")
        player_frame.grid(row=0, column=0, padx=5, pady=5, sticky="NS")

        cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        for i, card in enumerate(cards):
            btn = ttk.Button(
                player_frame, text=card, width=4, command=lambda c=card: self.add_player_card(c)  # type: ignore
            )
            btn.grid(row=i // 5, column=i % 5, padx=2, pady=2)

        # 莊家明牌輸入區
        dealer_frame = ttk.LabelFrame(input_container, text="莊家明牌", padding="10")
        dealer_frame.grid(row=0, column=1, padx=5, pady=5, sticky="NS")

        for i, card in enumerate(cards):
            btn = ttk.Button(
                dealer_frame, text=card, width=4, command=lambda c=card: self.set_dealer_card(c)  # type: ignore
            )
            btn.grid(row=i // 5, column=i % 5, padx=2, pady=2)

        # 其他玩家牌輸入區
        others_frame = ttk.LabelFrame(input_container, text="其他玩家的牌", padding="10")
        others_frame.grid(row=0, column=2, padx=5, pady=5, sticky="NS")

        for i, card in enumerate(cards):
            btn = ttk.Button(
                others_frame, text=card, width=4, command=lambda c=card: self.add_other_card(c)  # type: ignore
            )
            btn.grid(row=i // 5, column=i % 5, padx=2, pady=2)

        # 動作按鈕框架
        action_frame = ttk.Frame(self.root, padding="10")
        action_frame.grid(row=5, column=0, columnspan=2, sticky="WE")

        # 遊戲動作按鈕
        ttk.Button(action_frame, text="停牌", command=self.stand_hand).pack(side=tk.LEFT, padx=5)
        self.split_button = ttk.Button(
            action_frame, text="分牌", command=self.split_hand, state="disabled"
        )
        self.split_button.pack(side=tk.LEFT, padx=5)

        # 控制按鈕
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=6, column=0, columnspan=2, sticky="WE")

        ttk.Button(control_frame, text="清除手牌", command=self.clear_hand).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(control_frame, text="新牌靴", command=self.new_shoe).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="結束", command=self.root.quit).pack(side=tk.RIGHT, padx=5)

    def add_player_card(self, card: str) -> None:
        """新增玩家手牌"""
        self.counter.add_card(card)
        self.game_state.add_player_card(card)
        self.update_display()

    def set_dealer_card(self, card: str) -> None:
        """設定莊家明牌"""
        self.counter.add_card(card)
        self.game_state.set_dealer_card(card)
        self.update_display()

    def add_other_card(self, card: str) -> None:
        """新增其他玩家的牌（只計數）"""
        self.counter.add_card(card)
        self.update_display()

    def clear_hand(self) -> None:
        self.game_state.clear_hand()
        self.update_display()

    def new_shoe(self) -> None:
        result = messagebox.askyesno("新牌靴", "開始新牌靴？這將重置所有計數。")
        if result:
            self.counter.new_shoe()
            self.game_state.clear_hand()
            self.update_display()

    def stand_hand(self) -> None:
        """當前手牌停牌"""
        self.game_state.stand_current_hand()
        self.update_display()

    def split_hand(self) -> None:
        """分牌"""
        if self.game_state.split_current_hand():
            self.update_display()
        else:
            messagebox.showwarning("分牌失敗", "無法分牌")

    def update_display(self) -> None:
        # 更新計數
        running = self.counter.running_count
        true = self.counter.get_true_count()
        decks = self.counter.get_decks_remaining()

        self.running_count_label.config(text=f"{running:.1f}")
        self.true_count_label.config(text=f"{true:.1f}")
        self.decks_label.config(text=f"{decks:.1f}")
        self.cards_seen_label.config(text=str(self.counter.cards_seen))

        # 計數顏色編碼
        if true >= 2:
            color = "darkgreen"
        elif true >= 1:
            color = "green"
        elif true <= -2:
            color = "darkred"
        elif true <= -1:
            color = "red"
        else:
            color = "black"

        self.true_count_label.config(foreground=color)

        # 更新莊家牌
        self.dealer_card_label.config(text=self.game_state.get_dealer_card_string())

        # 更新手牌顯示
        self.update_hands_display()

        # 更新分牌按鈕狀態
        if self.game_state.can_split_current_hand():
            self.split_button.config(state="normal")
        else:
            self.split_button.config(state="disabled")

        # 更新主要決策顯示（當前手牌）
        self.update_main_decision()

        # 向後相容：更新單一手牌標籤
        self.player_hand_label.config(text=self.game_state.get_player_hand_string())

    def update_hands_display(self) -> None:
        """更新多手牌顯示"""
        # 清除舊的手牌框架
        for frame in self.hand_frames:
            frame.destroy()
        self.hand_frames.clear()
        self.hand_labels.clear()
        self.hand_decision_labels.clear()

        # 為每個手牌建立框架
        for idx, hand in enumerate(self.game_state.player_hands):
            # 建立手牌框架
            hand_frame = ttk.Frame(self.hands_frame, relief="solid", borderwidth=2)
            hand_frame.grid(row=idx // 2, column=idx % 2, padx=10, pady=5, sticky="WE")

            # 設定框架顏色（活動手牌高亮）
            if idx == self.game_state.current_hand_index:
                hand_frame.configure(style="Active.TFrame")

            # 手牌標題
            title = f"手牌 {idx + 1}"
            if hand.is_split_hand:
                title += " (分牌)"
            if idx == self.game_state.current_hand_index and hand.status == HandStatus.ACTIVE:
                title += " <<<"

            ttk.Label(hand_frame, text=title, font=("Arial", 12, "bold")).grid(
                row=0, column=0, columnspan=2, padx=5, pady=2
            )

            # 手牌內容
            hand_label = ttk.Label(hand_frame, text=hand.get_display_string(), font=("Arial", 14))
            hand_label.grid(row=1, column=0, columnspan=2, padx=5, pady=2)
            self.hand_labels.append(hand_label)

            # 如果是活動手牌，顯示決策
            if hand.status == HandStatus.ACTIVE and self.game_state.dealer_card:
                action, _ = self.strategy.get_decision(hand.cards, self.game_state.dealer_card)
                decision_label = ttk.Label(
                    hand_frame,
                    text=f"建議: {action}",
                    font=("Arial", 11),
                    foreground=self.get_action_color(action),
                )
                decision_label.grid(row=2, column=0, columnspan=2, padx=5, pady=2)
                self.hand_decision_labels.append(decision_label)

            self.hand_frames.append(hand_frame)

    def update_main_decision(self) -> None:
        """更新主要決策顯示"""
        current_hand = self.game_state.current_hand

        if current_hand.cards and self.game_state.dealer_card:
            action, explanation = self.strategy.get_decision(
                current_hand.cards, self.game_state.dealer_card
            )
            self.decision_label.config(text=action, foreground=self.get_action_color(action))
            self.explanation_label.config(text=explanation)
        else:
            self.decision_label.config(text="請加入手牌以查看建議", foreground="gray")
            self.explanation_label.config(text="")

    def get_action_color(self, action: str) -> str:
        """取得動作對應的顏色"""
        color_map = {
            "要牌": "blue",
            "停牌": "green",
            "加倍": "orange",
            "分牌": "purple",
            "投降": "red",
            "爆牌": "darkred",
        }
        return color_map.get(action, "black")


def main() -> None:
    """主程式進入點"""
    root = tk.Tk()
    BlackjackCounterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
