#!/usr/bin/env python3
"""
21點計牌器 - 現代化桌面應用程式
使用 ttkbootstrap 實現美化界面
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from typing import Dict, List, Optional
import tkinter as tk

from src.core import BasicStrategy, GameState, WongHalvesCounter, HandStatus


class ModernBlackjackCounterApp:
    def __init__(self, root: ttk.Window) -> None:
        self.root = root
        self.root.title("21點計牌器 Pro - Wong Halves 系統")
        self.root.geometry("1200x900")
        self.root.minsize(1000, 800)
        
        # 初始化元件
        self.counter = WongHalvesCounter(num_decks=8)
        self.strategy = BasicStrategy()
        self.game_state = GameState()
        
        # GUI 元件參考
        self.count_widgets: Dict[str, ttk.Label] = {}
        self.hand_frames: List[ttk.Frame] = []
        
        # 設定樣式
        self.setup_styles()
        
        # 建立主要佈局
        self.create_widgets()
        self.update_display()
    
    def setup_styles(self) -> None:
        """設定自訂樣式"""
        self.style = ttk.Style()
        
        # 自訂顏色
        self.colors = {
            "count_positive": "success",
            "count_negative": "danger",
            "count_neutral": "light",
            "action_hit": "primary",
            "action_stand": "success",
            "action_double": "warning",
            "action_split": "info",
            "action_surrender": "danger",
        }
    
    def create_widgets(self) -> None:
        """建立所有 GUI 元件"""
        # 主容器
        main_container = ttk.Frame(self.root, padding=10)
        main_container.pack(fill=BOTH, expand=YES)
        
        # 頂部 - 計數顯示面板
        self.create_count_panel(main_container)
        
        # 中間 - 遊戲區域
        self.create_game_area(main_container)
        
        # 底部 - 控制面板
        self.create_control_panel(main_container)
    
    def create_count_panel(self, parent) -> None:
        """建立計數顯示面板"""
        # 使用 LabelFrame 創建有邊框的區域
        count_frame = ttk.LabelFrame(parent, text="計數資訊", padding=15, bootstyle="success")
        count_frame.pack(fill=X, pady=(0, 10))
        
        # 創建網格佈局
        count_container = ttk.Frame(count_frame)
        count_container.pack(fill=X)
        
        # 使用大型標籤和進度條顯示真實計數
        true_count_frame = ttk.LabelFrame(count_container, text="真實計數", padding=10, bootstyle="warning")
        true_count_frame.pack(side=LEFT, padx=20)
        
        # 大型計數顯示
        self.count_widgets["true"] = ttk.Label(
            true_count_frame,
            text="0.0",
            font=("", 48, "bold"),
            bootstyle="inverse-warning"
        )
        self.count_widgets["true"].pack(pady=10)
        
        # 圓形進度指示（使用進度條模擬）
        self.true_count_progress = ttk.Progressbar(
            true_count_frame,
            length=180,
            mode="determinate",
            bootstyle="warning"
        )
        self.true_count_progress.pack(pady=(0, 10))
        self.true_count_progress['value'] = 50  # 中性位置
        
        # 其他計數信息
        info_frame = ttk.Frame(count_container)
        info_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=20)
        
        # 流水計數
        self.create_count_widget(info_frame, "流水計數", "running", 0, 0, "0.0")
        
        # 剩餘牌組
        self.create_count_widget(info_frame, "剩餘牌組", "decks", 0, 1, "8.0")
        
        # 已見牌數
        self.create_count_widget(info_frame, "已見牌數", "cards", 1, 0, "0")
        
        # 優勢指示
        advantage_frame = ttk.Frame(info_frame)
        advantage_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        ttk.Label(advantage_frame, text="優勢:").pack(side=LEFT)
        self.advantage_bar = ttk.Progressbar(
            advantage_frame,
            length=150,
            mode="determinate",
            bootstyle="success"
        )
        self.advantage_bar.pack(side=LEFT, padx=(10, 0), fill=X, expand=YES)
        self.advantage_bar['value'] = 50  # 中性位置
    
    def create_count_widget(self, parent, label: str, key: str, row: int, col: int, value: str) -> None:
        """建立計數顯示元件"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        
        ttk.Label(frame, text=label, font=("", 12)).pack()
        self.count_widgets[key] = ttk.Label(
            frame,
            text=value,
            font=("", 20, "bold"),
            bootstyle="inverse-dark"
        )
        self.count_widgets[key].pack()
    
    def create_game_area(self, parent) -> None:
        """建立遊戲區域"""
        game_frame = ttk.LabelFrame(parent, text="遊戲狀態", padding=15, bootstyle="primary")
        game_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        # 莊家區域
        dealer_frame = ttk.Frame(game_frame)
        dealer_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            dealer_frame,
            text="莊家明牌：",
            font=("", 14, "bold")
        ).pack(side=LEFT, padx=(0, 10))
        
        self.dealer_card_label = ttk.Label(
            dealer_frame,
            text="無牌",
            font=("", 24),
            bootstyle="inverse-warning"
        )
        self.dealer_card_label.pack(side=LEFT)
        
        # 玩家手牌區域（可滾動）
        hands_label_frame = ttk.LabelFrame(game_frame, text="玩家手牌", padding=10)
        hands_label_frame.pack(fill=BOTH, expand=YES)
        
        # 使用 Canvas 和 Scrollbar 實現滾動
        canvas = tk.Canvas(hands_label_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(hands_label_frame, orient="vertical", command=canvas.yview)
        self.hands_container = ttk.Frame(canvas)
        
        self.hands_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.hands_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 決策建議區域
        self.create_decision_area(game_frame)
    
    def create_decision_area(self, parent) -> None:
        """建立決策建議區域"""
        decision_frame = ttk.LabelFrame(
            parent,
            text="建議動作",
            padding=15,
            bootstyle="warning"
        )
        decision_frame.pack(fill=X, pady=(15, 0))
        
        self.decision_label = ttk.Label(
            decision_frame,
            text="請加入手牌",
            font=("", 24, "bold"),
            bootstyle="warning"
        )
        self.decision_label.pack()
        
        self.explanation_label = ttk.Label(
            decision_frame,
            text="",
            font=("", 12)
        )
        self.explanation_label.pack()
    
    def create_control_panel(self, parent) -> None:
        """建立控制面板"""
        control_frame = ttk.LabelFrame(parent, text="控制面板", padding=10)
        control_frame.pack(fill=X, pady=(10, 0))
        
        # 牌輸入區域
        self.create_card_input_area(control_frame)
        
        # 動作按鈕區域
        self.create_action_buttons(control_frame)
    
    def create_card_input_area(self, parent) -> None:
        """建立牌輸入區域"""
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=X, pady=(0, 10))
        
        cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        
        # 使用 Notebook 組織不同的輸入區
        notebook = ttk.Notebook(input_frame, bootstyle="dark")
        notebook.pack(fill=X)
        
        # 玩家牌頁面
        player_tab = ttk.Frame(notebook)
        notebook.add(player_tab, text="玩家手牌")
        self.create_card_buttons(player_tab, cards, self.add_player_card)
        
        # 莊家牌頁面
        dealer_tab = ttk.Frame(notebook)
        notebook.add(dealer_tab, text="莊家明牌")
        self.create_card_buttons(dealer_tab, cards, self.set_dealer_card)
        
        # 其他玩家牌頁面
        others_tab = ttk.Frame(notebook)
        notebook.add(others_tab, text="其他玩家")
        self.create_card_buttons(others_tab, cards, self.add_other_card)
    
    def create_card_buttons(self, parent, cards: List[str], callback) -> None:
        """創建牌按鈕網格"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack()
        
        for i, card in enumerate(cards):
            # 特殊牌使用不同顏色
            if card == "A":
                style = "warning"
            elif card in ["K", "Q", "J"]:
                style = "info"
            else:
                style = "secondary"
            
            btn = ttk.Button(
                frame,
                text=card,
                width=4,
                bootstyle=style,
                command=lambda c=card: callback(c)
            )
            btn.grid(row=i // 7, column=i % 7, padx=3, pady=3)
    
    def create_action_buttons(self, parent) -> None:
        """建立動作按鈕"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=X)
        
        # 左側：遊戲動作
        game_frame = ttk.Frame(action_frame)
        game_frame.pack(side=LEFT, padx=(0, 20))
        
        self.stand_button = ttk.Button(
            game_frame,
            text="停牌 (S)",
            bootstyle="success",
            command=self.stand_hand
        )
        self.stand_button.pack(side=LEFT, padx=5)
        
        self.split_button = ttk.Button(
            game_frame,
            text="分牌 (P)",
            bootstyle="info",
            command=self.split_hand,
            state="disabled"
        )
        self.split_button.pack(side=LEFT, padx=5)
        
        # 右側：控制按鈕
        control_frame = ttk.Frame(action_frame)
        control_frame.pack(side=RIGHT)
        
        ttk.Button(
            control_frame,
            text="清除手牌",
            bootstyle="secondary-outline",
            command=self.clear_hand
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="新牌靴",
            bootstyle="warning-outline",
            command=self.new_shoe
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="結束",
            bootstyle="danger-outline",
            command=self.root.quit
        ).pack(side=LEFT, padx=5)
    
    def update_display(self) -> None:
        """更新整個顯示"""
        self.update_counts()
        self.dealer_card_label.configure(text=self.game_state.get_dealer_card_string() or "無牌")
        self.update_hands_display()
        self.update_decision_display()
        self.update_button_states()
    
    def update_counts(self) -> None:
        """更新計數顯示"""
        running = self.counter.running_count
        true = self.counter.get_true_count()
        decks = self.counter.get_decks_remaining()
        cards = self.counter.cards_seen
        
        # 更新文字
        self.count_widgets["running"].configure(text=f"{running:.1f}")
        self.count_widgets["true"].configure(text=f"{true:.1f}")
        self.count_widgets["decks"].configure(text=f"{decks:.1f}")
        self.count_widgets["cards"].configure(text=str(cards))
        
        # 更新真實計數進度條
        # 將真實計數映射到 0-100 範圍（-5 到 +5）
        progress_value = int((true + 5) * 10)
        progress_value = max(0, min(100, progress_value))
        self.true_count_progress['value'] = progress_value
        
        # 根據計數更新顏色和樣式
        if true >= 2:
            count_style = "success"
            bar_style = "success"
        elif true >= 1:
            count_style = "info"
            bar_style = "info"
        elif true <= -2:
            count_style = "danger"
            bar_style = "danger"
        elif true <= -1:
            count_style = "warning"
            bar_style = "warning"
        else:
            count_style = "secondary"
            bar_style = "secondary"
        
        self.count_widgets["true"].configure(bootstyle=f"inverse-{count_style}")
        self.true_count_progress.configure(bootstyle=bar_style)
        
        # 更新優勢指示器
        advantage_value = int((true + 5) * 10)
        self.advantage_bar['value'] = max(0, min(100, advantage_value))
        
        if true >= 1:
            bar_style = "success"
        elif true <= -1:
            bar_style = "danger"
        else:
            bar_style = "primary"
        
        self.advantage_bar.configure(bootstyle=bar_style)
    
    def update_hands_display(self) -> None:
        """更新手牌顯示"""
        # 清除舊的手牌框架
        for frame in self.hand_frames:
            frame.destroy()
        self.hand_frames.clear()
        
        # 為每個手牌建立顯示
        for idx, hand in enumerate(self.game_state.player_hands):
            hand_frame = self.create_hand_display(idx, hand)
            self.hand_frames.append(hand_frame)
    
    def create_hand_display(self, idx: int, hand) -> ttk.Frame:
        """建立單個手牌顯示"""
        is_active = idx == self.game_state.current_hand_index
        
        # 使用不同樣式標識活動手牌
        if is_active:
            frame_style = "warning"
        else:
            frame_style = "secondary"
        
        hand_frame = ttk.LabelFrame(
            self.hands_container,
            text=f"手牌 {idx + 1}" + (" (分牌)" if hand.is_split_hand else ""),
            padding=10,
            bootstyle=frame_style
        )
        hand_frame.pack(fill=X, pady=5)
        
        # 手牌內容
        content_frame = ttk.Frame(hand_frame)
        content_frame.pack(fill=X)
        
        # 顯示牌
        cards_label = ttk.Label(
            content_frame,
            text=hand.get_display_string(),
            font=("", 16),
            bootstyle="inverse-dark"
        )
        cards_label.pack(side=LEFT, padx=(0, 20))
        
        # 顯示點數
        value_text = f"點數: {hand.get_value()}"
        if hand.is_blackjack():
            value_text = "Blackjack! 🎉"
            value_style = "success"
        elif hand.is_bust():
            value_text = f"爆牌! ({hand.get_value()})"
            value_style = "danger"
        else:
            value_style = "info"
        
        ttk.Label(
            content_frame,
            text=value_text,
            font=("", 14),
            bootstyle=value_style
        ).pack(side=LEFT)
        
        # 如果是活動手牌，顯示決策
        if hand.status == HandStatus.ACTIVE and self.game_state.dealer_card:
            action, _ = self.strategy.get_decision(hand.cards, self.game_state.dealer_card)
            action_style = self.get_action_style(action)
            
            ttk.Label(
                content_frame,
                text=f"建議: {action}",
                font=("", 14, "bold"),
                bootstyle=action_style
            ).pack(side=RIGHT)
        
        return hand_frame
    
    def update_decision_display(self) -> None:
        """更新主要決策顯示"""
        current_hand = self.game_state.current_hand
        
        if current_hand.cards and self.game_state.dealer_card:
            action, explanation = self.strategy.get_decision(
                current_hand.cards, self.game_state.dealer_card
            )
            self.decision_label.configure(
                text=action,
                bootstyle=self.get_action_style(action)
            )
            self.explanation_label.configure(text=explanation)
        else:
            self.decision_label.configure(
                text="請加入手牌",
                bootstyle="secondary"
            )
            self.explanation_label.configure(text="")
    
    def update_button_states(self) -> None:
        """更新按鈕狀態"""
        if self.game_state.can_split_current_hand():
            self.split_button.configure(state="normal")
        else:
            self.split_button.configure(state="disabled")
    
    def get_action_style(self, action: str) -> str:
        """取得動作對應的樣式"""
        style_map = {
            "要牌": "primary",
            "停牌": "success",
            "加倍": "warning",
            "分牌": "info",
            "投降": "danger",
            "爆牌": "danger",
        }
        return style_map.get(action, "secondary")
    
    # 事件處理方法
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
        """新增其他玩家的牌"""
        self.counter.add_card(card)
        self.update_display()
    
    def clear_hand(self) -> None:
        """清除手牌"""
        self.game_state.clear_hand()
        self.update_display()
    
    def new_shoe(self) -> None:
        """開始新牌靴"""
        result = Messagebox.yesno(
            "新牌靴",
            "開始新牌靴？這將重置所有計數。",
            bootstyle="warning"
        )
        if result == "Yes":
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
            Messagebox.show_warning("無法分牌", "分牌失敗")


def main() -> None:
    """主程式進入點"""
    # 使用深色主題
    root = ttk.Window(themename="darkly")
    app = ModernBlackjackCounterApp(root)
    
    # 設定鍵盤快捷鍵
    root.bind("<s>", lambda e: app.stand_hand())
    root.bind("<S>", lambda e: app.stand_hand())
    root.bind("<p>", lambda e: app.split_hand() if app.split_button['state'] == "normal" else None)
    root.bind("<P>", lambda e: app.split_hand() if app.split_button['state'] == "normal" else None)
    
    root.mainloop()


if __name__ == "__main__":
    main()