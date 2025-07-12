#!/usr/bin/env python3
"""
21點計牌器 - 現代化桌面應用程式
使用 CustomTkinter 實現美化界面
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, List, Optional, Tuple
import tkinter as tk

from src.core import BasicStrategy, GameState, WongHalvesCounter, HandStatus

# 設定外觀主題
ctk.set_appearance_mode("dark")  # 賭場風格深色主題
ctk.set_default_color_theme("green")  # 使用綠色主題

# 自訂顏色方案
COLORS = {
    # 主要顏色
    "bg_dark": "#0a1f0a",  # 深綠背景
    "bg_medium": "#1a3d1a",  # 中綠背景
    "bg_light": "#2d5a2d",  # 淺綠背景
    "accent_gold": "#FFD700",  # 金色強調
    "accent_red": "#DC143C",  # 紅色強調
    
    # 文字顏色
    "text_primary": "#FFFFFF",
    "text_secondary": "#E0E0E0",
    "text_muted": "#B0B0B0",
    
    # 計數顏色
    "count_positive_strong": "#00FF00",  # 強正計數
    "count_positive": "#90EE90",  # 正計數
    "count_neutral": "#FFFFFF",  # 中性
    "count_negative": "#FF6B6B",  # 負計數
    "count_negative_strong": "#FF0000",  # 強負計數
    
    # 動作顏色
    "action_hit": "#4A90E2",  # 要牌 - 藍色
    "action_stand": "#27AE60",  # 停牌 - 綠色
    "action_double": "#F39C12",  # 加倍 - 橙色
    "action_split": "#9B59B6",  # 分牌 - 紫色
    "action_surrender": "#E74C3C",  # 投降 - 紅色
    "action_bust": "#8B0000",  # 爆牌 - 深紅
}

# 撲克牌符號
SUIT_SYMBOLS = {"♠": "spades", "♥": "hearts", "♦": "diamonds", "♣": "clubs"}


class ModernBlackjackCounterApp:
    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.root.title("21點計牌器 Pro - Wong Halves 系統")
        self.root.geometry("1200x900")
        self.root.minsize(1000, 800)
        
        # 設定背景顏色
        self.root.configure(fg_color=COLORS["bg_dark"])
        
        # 初始化元件
        self.counter = WongHalvesCounter(num_decks=8)
        self.strategy = BasicStrategy()
        self.game_state = GameState()
        
        # GUI 元件參考
        self.count_widgets: Dict[str, ctk.CTkLabel] = {}
        self.hand_frames: List[ctk.CTkFrame] = []
        self.hand_widgets: List[Dict[str, ctk.CTkLabel]] = []
        
        # 建立主要佈局
        self.setup_layout()
        self.create_widgets()
        self.update_display()
    
    def setup_layout(self) -> None:
        """設定響應式網格佈局"""
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
    
    def create_widgets(self) -> None:
        """建立所有 GUI 元件"""
        # 頂部 - 計數顯示面板
        self.create_count_panel()
        
        # 中間 - 遊戲區域
        self.create_game_area()
        
        # 底部 - 控制面板
        self.create_control_panel()
    
    def create_count_panel(self) -> None:
        """建立計數顯示面板"""
        count_frame = ctk.CTkFrame(
            self.root,
            fg_color=COLORS["bg_medium"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["accent_gold"]
        )
        count_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        count_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # 流水計數
        self.create_count_widget(
            count_frame, "流水計數", "running", 0, 0,
            self.counter.running_count
        )
        
        # 真實計數（重點顯示）
        true_count_container = ctk.CTkFrame(
            count_frame,
            fg_color=COLORS["bg_dark"],
            corner_radius=10
        )
        true_count_container.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        ctk.CTkLabel(
            true_count_container,
            text="真實計數",
            font=ctk.CTkFont(family="Microsoft JhengHei", size=16),
            text_color=COLORS["accent_gold"]
        ).pack(pady=(10, 5))
        
        self.count_widgets["true"] = ctk.CTkLabel(
            true_count_container,
            text="0.0",
            font=ctk.CTkFont(family="Arial", size=36, weight="bold"),
            text_color=COLORS["count_neutral"]
        )
        self.count_widgets["true"].pack(pady=(0, 10))
        
        # 剩餘牌組
        self.create_count_widget(
            count_frame, "剩餘牌組", "decks", 0, 2,
            self.counter.get_decks_remaining()
        )
        
        # 已見牌數
        self.create_count_widget(
            count_frame, "已見牌數", "cards", 0, 3,
            self.counter.cards_seen
        )
        
        # 添加優勢指示器
        self.create_advantage_indicator(count_frame)
    
    def create_count_widget(self, parent: ctk.CTkFrame, label: str, key: str, 
                          row: int, col: int, value: float) -> None:
        """建立計數顯示元件"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row, column=col, padx=10, pady=15, sticky="ew")
        
        ctk.CTkLabel(
            container,
            text=label,
            font=ctk.CTkFont(family="Microsoft JhengHei", size=14),
            text_color=COLORS["text_secondary"]
        ).pack()
        
        self.count_widgets[key] = ctk.CTkLabel(
            container,
            text=f"{value:.1f}" if isinstance(value, float) else str(value),
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.count_widgets[key].pack()
    
    def create_advantage_indicator(self, parent: ctk.CTkFrame) -> None:
        """建立玩家優勢指示器"""
        indicator_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_dark"],
            corner_radius=10,
            height=20
        )
        indicator_frame.grid(row=1, column=0, columnspan=4, padx=20, pady=(0, 15), sticky="ew")
        
        # 優勢進度條
        self.advantage_bar = ctk.CTkProgressBar(
            indicator_frame,
            height=15,
            corner_radius=8,
            progress_color=COLORS["count_neutral"],
            fg_color=COLORS["bg_medium"]
        )
        self.advantage_bar.pack(fill="x", padx=10, pady=10)
        self.advantage_bar.set(0.5)  # 中性位置
        
        # 標籤
        label_frame = ctk.CTkFrame(indicator_frame, fg_color="transparent")
        label_frame.pack(fill="x", padx=10)
        
        ctk.CTkLabel(
            label_frame,
            text="莊家優勢",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            label_frame,
            text="玩家優勢",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        ).pack(side="right")
    
    def create_game_area(self) -> None:
        """建立遊戲區域"""
        game_container = ctk.CTkFrame(
            self.root,
            fg_color=COLORS["bg_medium"],
            corner_radius=15
        )
        game_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        game_container.grid_columnconfigure(0, weight=1)
        game_container.grid_rowconfigure(1, weight=1)
        
        # 莊家區域
        self.create_dealer_area(game_container)
        
        # 玩家手牌區域
        self.create_player_hands_area(game_container)
        
        # 決策建議區域
        self.create_decision_area(game_container)
    
    def create_dealer_area(self, parent: ctk.CTkFrame) -> None:
        """建立莊家顯示區域"""
        dealer_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_dark"],
            corner_radius=10,
            height=100
        )
        dealer_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        ctk.CTkLabel(
            dealer_frame,
            text="莊家明牌",
            font=ctk.CTkFont(family="Microsoft JhengHei", size=18, weight="bold"),
            text_color=COLORS["accent_gold"]
        ).pack(pady=(15, 5))
        
        self.dealer_card_label = ctk.CTkLabel(
            dealer_frame,
            text="無牌",
            font=ctk.CTkFont(family="Arial", size=32),
            text_color=COLORS["text_primary"]
        )
        self.dealer_card_label.pack(pady=(0, 15))
    
    def create_player_hands_area(self, parent: ctk.CTkFrame) -> None:
        """建立玩家手牌顯示區域"""
        # 使用可滾動框架以支持多手牌
        self.hands_container = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_light"],
            scrollbar_button_hover_color=COLORS["accent_gold"]
        )
        self.hands_container.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
    
    def create_decision_area(self, parent: ctk.CTkFrame) -> None:
        """建立決策建議區域"""
        decision_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_dark"],
            corner_radius=10,
            border_width=2,
            border_color=COLORS["accent_gold"]
        )
        decision_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
        
        ctk.CTkLabel(
            decision_frame,
            text="建議動作",
            font=ctk.CTkFont(family="Microsoft JhengHei", size=16),
            text_color=COLORS["accent_gold"]
        ).pack(pady=(15, 5))
        
        self.decision_label = ctk.CTkLabel(
            decision_frame,
            text="請加入手牌",
            font=ctk.CTkFont(family="Microsoft JhengHei", size=28, weight="bold"),
            text_color=COLORS["text_muted"]
        )
        self.decision_label.pack()
        
        self.explanation_label = ctk.CTkLabel(
            decision_frame,
            text="",
            font=ctk.CTkFont(family="Microsoft JhengHei", size=14),
            text_color=COLORS["text_secondary"]
        )
        self.explanation_label.pack(pady=(5, 15))
    
    def create_control_panel(self) -> None:
        """建立控制面板"""
        control_frame = ctk.CTkFrame(
            self.root,
            fg_color=COLORS["bg_medium"],
            corner_radius=15
        )
        control_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        # 牌輸入區域
        self.create_card_input_area(control_frame)
        
        # 動作按鈕區域
        self.create_action_buttons(control_frame)
    
    def create_card_input_area(self, parent: ctk.CTkFrame) -> None:
        """建立牌輸入區域"""
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=15)
        
        # 定義牌組
        cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        
        # 玩家牌輸入
        player_section = self.create_card_section(
            input_frame, "玩家手牌", cards, self.add_player_card, 0
        )
        
        # 莊家牌輸入
        dealer_section = self.create_card_section(
            input_frame, "莊家明牌", cards, self.set_dealer_card, 1
        )
        
        # 其他玩家牌輸入
        others_section = self.create_card_section(
            input_frame, "其他玩家", cards, self.add_other_card, 2
        )
    
    def create_card_section(self, parent: ctk.CTkFrame, title: str, 
                          cards: List[str], callback, column: int) -> ctk.CTkFrame:
        """建立牌輸入區段"""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_dark"],
            corner_radius=10
        )
        section.grid(row=0, column=column, padx=10, sticky="nsew")
        parent.grid_columnconfigure(column, weight=1)
        
        ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(family="Microsoft JhengHei", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(10, 5))
        
        # 牌按鈕網格
        button_frame = ctk.CTkFrame(section, fg_color="transparent")
        button_frame.pack(padx=10, pady=10)
        
        for i, card in enumerate(cards):
            # 為不同的牌添加顏色
            if card in ["A", "K"]:
                btn_color = COLORS["accent_gold"]
                hover_color = "#FFE55C"
            elif card in ["Q", "J"]:
                btn_color = "#CD853F"
                hover_color = "#DEB887"
            else:
                btn_color = COLORS["bg_light"]
                hover_color = COLORS["accent_gold"]
            
            # 添加撲克牌符號裝飾
            display_text = f"{card}"
            if card == "A":
                display_text = f"{card}♠"
            elif card == "K":
                display_text = f"{card}♥"
            elif card == "Q":
                display_text = f"{card}♦"
            elif card == "J":
                display_text = f"{card}♣"
            
            btn = ctk.CTkButton(
                button_frame,
                text=display_text,
                width=45,
                height=40,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=btn_color,
                hover_color=hover_color,
                command=lambda c=card: callback(c)
            )
            btn.grid(row=i // 4, column=i % 4, padx=3, pady=3)
        
        return section
    
    def create_action_buttons(self, parent: ctk.CTkFrame) -> None:
        """建立動作按鈕"""
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # 遊戲動作按鈕
        game_actions = ctk.CTkFrame(action_frame, fg_color="transparent")
        game_actions.pack(side="left", padx=10)
        
        self.stand_button = ctk.CTkButton(
            game_actions,
            text="停牌 (S)",
            width=100,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["action_stand"],
            hover_color="#1E8449",
            command=self.stand_hand
        )
        self.stand_button.pack(side="left", padx=5)
        
        self.split_button = ctk.CTkButton(
            game_actions,
            text="分牌 (P)",
            width=100,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["action_split"],
            hover_color="#7D3C98",
            command=self.split_hand,
            state="disabled"
        )
        self.split_button.pack(side="left", padx=5)
        
        # 控制按鈕
        control_actions = ctk.CTkFrame(action_frame, fg_color="transparent")
        control_actions.pack(side="right", padx=10)
        
        ctk.CTkButton(
            control_actions,
            text="清除手牌",
            width=100,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["bg_light"],
            hover_color=COLORS["accent_red"],
            command=self.clear_hand
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_actions,
            text="新牌靴",
            width=100,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["bg_light"],
            hover_color=COLORS["accent_gold"],
            command=self.new_shoe
        ).pack(side="left", padx=5)
    
    def update_display(self) -> None:
        """更新整個顯示"""
        # 更新計數
        self.update_counts()
        
        # 更新莊家牌
        self.dealer_card_label.configure(text=self.game_state.get_dealer_card_string())
        
        # 更新手牌顯示
        self.update_hands_display()
        
        # 更新決策
        self.update_decision_display()
        
        # 更新按鈕狀態
        self.update_button_states()
    
    def update_counts(self) -> None:
        """更新計數顯示（簡化版，無多線程）"""
        running = self.counter.running_count
        true = self.counter.get_true_count()
        decks = self.counter.get_decks_remaining()
        cards = self.counter.cards_seen
        
        # 直接更新數值（無動畫）
        self.count_widgets["running"].configure(text=f"{running:.1f}")
        self.count_widgets["true"].configure(text=f"{true:.1f}")
        self.count_widgets["decks"].configure(text=f"{decks:.1f}")
        self.count_widgets["cards"].configure(text=str(cards))
        
        # 更新真實計數顏色
        if true >= 2:
            color = COLORS["count_positive_strong"]
        elif true >= 1:
            color = COLORS["count_positive"]
        elif true <= -2:
            color = COLORS["count_negative_strong"]
        elif true <= -1:
            color = COLORS["count_negative"]
        else:
            color = COLORS["count_neutral"]
        
        self.count_widgets["true"].configure(text_color=color)
        
        # 更新優勢指示器
        advantage_value = (true + 5) / 10
        advantage_value = max(0, min(1, advantage_value))
        self.advantage_bar.set(advantage_value)
        
        # 更新進度條顏色
        if true >= 1:
            self.advantage_bar.configure(progress_color=COLORS["count_positive"])
        elif true <= -1:
            self.advantage_bar.configure(progress_color=COLORS["count_negative"])
        else:
            self.advantage_bar.configure(progress_color=COLORS["count_neutral"])
    
    def update_hands_display(self) -> None:
        """更新手牌顯示"""
        # 清除舊的手牌框架
        for frame in self.hand_frames:
            frame.destroy()
        self.hand_frames.clear()
        self.hand_widgets.clear()
        
        # 為每個手牌建立顯示
        for idx, hand in enumerate(self.game_state.player_hands):
            hand_frame = self.create_hand_display(idx, hand)
            self.hand_frames.append(hand_frame)
    
    def create_hand_display(self, idx: int, hand) -> ctk.CTkFrame:
        """建立單個手牌顯示"""
        # 手牌容器
        is_active = idx == self.game_state.current_hand_index
        hand_frame = ctk.CTkFrame(
            self.hands_container,
            fg_color=COLORS["bg_dark"] if is_active else COLORS["bg_light"],
            corner_radius=10,
            border_width=3 if is_active else 1,
            border_color=COLORS["accent_gold"] if is_active else COLORS["bg_medium"]
        )
        hand_frame.pack(fill="x", padx=10, pady=5)
        
        # 標題行
        title_frame = ctk.CTkFrame(hand_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        title = f"手牌 {idx + 1}"
        if hand.is_split_hand:
            title += " (分牌)"
        if is_active and hand.status == HandStatus.ACTIVE:
            title += " ◄"
        
        ctk.CTkLabel(
            title_frame,
            text=title,
            font=ctk.CTkFont(family="Microsoft JhengHei", size=16, weight="bold"),
            text_color=COLORS["accent_gold"] if is_active else COLORS["text_primary"]
        ).pack(side="left")
        
        # 手牌點數
        total_text = f"點數: {hand.get_value()}"
        if hand.is_blackjack():
            total_text = "Blackjack! 🎉"
        elif hand.is_bust():
            total_text = f"爆牌! ({hand.get_value()})"
        
        ctk.CTkLabel(
            title_frame,
            text=total_text,
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        ).pack(side="right")
        
        # 手牌內容（添加視覺效果）
        cards_frame = ctk.CTkFrame(hand_frame, fg_color="transparent")
        cards_frame.pack(padx=15, pady=(0, 10))
        
        # 顯示每張牌
        for i, card in enumerate(hand.cards):
            card_label = ctk.CTkLabel(
                cards_frame,
                text=self.format_card_display(card),
                font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
                text_color=self.get_card_color(card),
                fg_color=COLORS["bg_medium"],
                corner_radius=5,
                width=50,
                height=70
            )
            card_label.pack(side="left", padx=3)
        
        # 如果是活動手牌，顯示決策
        if hand.status == HandStatus.ACTIVE and self.game_state.dealer_card:
            action, _ = self.strategy.get_decision(hand.cards, self.game_state.dealer_card)
            action_color = self.get_action_color(action)
            
            ctk.CTkLabel(
                hand_frame,
                text=f"建議: {action}",
                font=ctk.CTkFont(family="Microsoft JhengHei", size=14, weight="bold"),
                text_color=action_color
            ).pack(pady=(0, 10))
        
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
                text_color=self.get_action_color(action)
            )
            self.explanation_label.configure(text=explanation)
        else:
            self.decision_label.configure(
                text="請加入手牌",
                text_color=COLORS["text_muted"]
            )
            self.explanation_label.configure(text="")
    
    def update_button_states(self) -> None:
        """更新按鈕狀態"""
        if self.game_state.can_split_current_hand():
            self.split_button.configure(state="normal")
        else:
            self.split_button.configure(state="disabled")
    
    def get_action_color(self, action: str) -> str:
        """取得動作對應的顏色"""
        color_map = {
            "要牌": COLORS["action_hit"],
            "停牌": COLORS["action_stand"],
            "加倍": COLORS["action_double"],
            "分牌": COLORS["action_split"],
            "投降": COLORS["action_surrender"],
            "爆牌": COLORS["action_bust"],
        }
        return color_map.get(action, COLORS["text_primary"])
    
    def format_card_display(self, card: str) -> str:
        """格式化牌的顯示（添加花色符號）"""
        # 使用旋轉的花色來增加視覺多樣性
        suits = ["♠", "♥", "♦", "♣"]
        # 根據牌值選擇花色（為了視覺效果）
        if card in ["A", "K"]:
            return f"{card}{suits[0]}"
        elif card in ["Q", "J"]:
            return f"{card}{suits[1]}"
        elif card in ["2", "3", "4", "5"]:
            return f"{card}{suits[2]}"
        else:
            return f"{card}{suits[3]}"
    
    def get_card_color(self, card: str) -> str:
        """取得牌的顏色"""
        # 紅色花色（紅心、方塊）的牌
        if card in ["A", "K", "Q", "J", "2", "3", "4", "5"]:
            return "#FF6B6B"  # 亮紅色
        else:
            return COLORS["text_primary"]  # 白色（黑色花色）
    
    # 視覺效果方法
    def flash_button(self, button: ctk.CTkButton) -> None:
        """按鈕點擊閃爍效果"""
        original_color = button.cget("fg_color")
        button.configure(fg_color=COLORS["accent_gold"])
        self.root.after(100, lambda: button.configure(fg_color=original_color))
    
    def show_card_animation(self, card: str) -> None:
        """顯示添加牌的動畫效果（簡化版）"""
        # 創建臨時標籤顯示牌
        temp_label = ctk.CTkLabel(
            self.root,
            text=self.format_card_display(card),
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=COLORS["accent_gold"],
            fg_color=COLORS["bg_dark"],
            corner_radius=10
        )
        temp_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 簡單的消失效果
        self.root.after(500, temp_label.destroy)
    
    # 事件處理方法
    def add_player_card(self, card: str) -> None:
        """新增玩家手牌"""
        self.show_card_animation(card)
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
        # 使用 CTkMessagebox 或標準 messagebox
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


def main() -> None:
    """主程式進入點"""
    root = ctk.CTk()
    app = ModernBlackjackCounterApp(root)
    
    # 設定鍵盤快捷鍵
    root.bind("<s>", lambda e: app.stand_hand())
    root.bind("<S>", lambda e: app.stand_hand())
    root.bind("<p>", lambda e: app.split_hand() if app.split_button.cget("state") == "normal" else None)
    root.bind("<P>", lambda e: app.split_hand() if app.split_button.cget("state") == "normal" else None)
    
    root.mainloop()


if __name__ == "__main__":
    main()