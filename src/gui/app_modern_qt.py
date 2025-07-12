#!/usr/bin/env python3
"""
21點計牌器 - 現代化桌面應用程式
使用 PyQt6 實現美化界面
"""

import sys
from typing import List, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QGroupBox, QGridLayout, QScrollArea,
    QFrame, QTabWidget, QMessageBox,
    QSizePolicy, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect
from PyQt6.QtGui import QFont, QPalette, QColor, QLinearGradient, QCursor, QMouseEvent

from src.core import BasicStrategy, GameState, WongHalvesCounter, HandStatus




class HandFrame(QGroupBox):
    """手牌顯示框架"""
    
    # 定義點擊信號
    clicked = pyqtSignal(int)
    
    def __init__(self, index: int, hand, is_active: bool, parent=None):
        title = f"手牌 {index + 1}"
        if hand.is_split_hand:
            title += " (分牌)"
        if is_active and hand.status == HandStatus.ACTIVE:
            title += " ◄"
        
        super().__init__(title, parent)
        
        # 儲存索引和手牌狀態
        self.index = index
        self.hand = hand
        self.is_active = is_active
        
        # 設定固定寬度以適應網格佈局
        self.setMinimumWidth(150)
        self.setMaximumWidth(200)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        # 設定樣式
        if is_active:
            self.setStyleSheet("""
                QGroupBox {
                    background-color: #3a3a3a;
                    border: 3px solid #f39c12;
                    border-radius: 10px;
                    margin-top: 10px;
                    padding: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    color: #f39c12;
                    font-weight: bold;
                    font-size: 16px;
                }
            """)
        else:
            self.setStyleSheet("""
                QGroupBox {
                    background-color: #2b2b2b;
                    border: 2px solid #444;
                    border-radius: 10px;
                    margin-top: 10px;
                    padding: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    color: #888;
                    font-size: 14px;
                }
            """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # 手牌顯示
        cards_label = QLabel(hand.get_display_string())
        cards_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        cards_label.setWordWrap(True)
        layout.addWidget(cards_label)
        
        # 點數顯示
        value, _ = hand.calculate_value()
        value_text = f"點數: {value}"
        value_style = "color: #888; font-size: 14px;"
        
        if hand.status == HandStatus.BLACKJACK:
            value_text = "Blackjack! 🎉"
            value_style = "color: #27ae60; font-size: 16px; font-weight: bold;"
        elif hand.status == HandStatus.BUSTED:
            value_text = f"爆牌! ({value})"
            value_style = "color: #e74c3c; font-size: 16px; font-weight: bold;"
        
        value_label = QLabel(value_text)
        value_label.setStyleSheet(value_style)
        layout.addWidget(value_label)
        
        self.setLayout(layout)
        
        # 設定游標樣式（可點擊）
        if hand.status == HandStatus.ACTIVE:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """處理滑鼠點擊事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 只有活動手牌可以被選擇
            if self.hand.status == HandStatus.ACTIVE:
                self.clicked.emit(self.index)
        super().mousePressEvent(event)
    
    def enterEvent(self, event) -> None:
        """滑鼠進入時的效果"""
        if self.hand.status == HandStatus.ACTIVE and not self.is_active:
            self.setStyleSheet("""
                QGroupBox {
                    background-color: #3a3a3a;
                    border: 2px solid #666;
                    border-radius: 10px;
                    margin-top: 10px;
                    padding: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    color: #aaa;
                    font-size: 14px;
                }
            """)
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        """滑鼠離開時恢復原樣"""
        if not self.is_active and self.hand.status == HandStatus.ACTIVE:
            self.setStyleSheet("""
                QGroupBox {
                    background-color: #2b2b2b;
                    border: 2px solid #444;
                    border-radius: 10px;
                    margin-top: 10px;
                    padding: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    color: #888;
                    font-size: 14px;
                }
            """)
        super().leaveEvent(event)


class ModernBlackjackCounterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("21點計牌器 Pro - Wong Halves 系統")
        self.setGeometry(100, 100, 1200, 900)
        
        # 初始化元件
        self.counter = WongHalvesCounter(num_decks=8)
        self.strategy = BasicStrategy()
        self.game_state = GameState()
        
        # GUI 元件參考
        self.hand_frames: List[HandFrame] = []
        self.last_card_action: str = "player"  # 追蹤最後的牌操作: "player" 或 "dealer"
        self.other_player_cards: List[str] = []  # 追蹤其他玩家的牌
        
        # 設定深色主題
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666;
            }
            QGroupBox {
                color: white;
                border: 2px solid #444;
                border-radius: 10px;
                margin-top: 10px;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4a4a4a;
            }
        """)
        
        # 建立主介面
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        """設定使用者介面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 10)
        
        # 頂部 - 遊戲區域
        game_area = self.create_game_area()
        main_layout.addWidget(game_area, 1)
        
        # 中間 - 控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # 底部 - 精簡計數狀態列
        count_status_bar = self.create_count_status_bar()
        main_layout.addWidget(count_status_bar)
        
        central_widget.setLayout(main_layout)
    
    def create_count_status_bar(self) -> QWidget:
        """建立精簡的計數狀態列"""
        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.Shape.Box)
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-top: 1px solid #444;
                padding: 5px 10px;
                max-height: 40px;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(20)
        
        # 真實計數
        true_count_label = QLabel("真實計數:")
        true_count_label.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(true_count_label)
        
        self.true_count_value = QLabel("0.0")
        self.true_count_value.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.true_count_value)
        
        # 分隔符
        layout.addWidget(QLabel("|"))
        
        # 流水計數
        running_count_label = QLabel("流水計數:")
        running_count_label.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(running_count_label)
        
        self.running_count_value = QLabel("0")
        self.running_count_value.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(self.running_count_value)
        
        # 分隔符
        layout.addWidget(QLabel("|"))
        
        # 剩餘牌組
        decks_label = QLabel("剩餘牌組:")
        decks_label.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(decks_label)
        
        self.decks_remaining_value = QLabel("8.0")
        self.decks_remaining_value.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(self.decks_remaining_value)
        
        layout.addStretch()
        status_bar.setLayout(layout)
        return status_bar
    
    def create_game_area(self) -> QWidget:
        """建立遊戲區域"""
        game_widget = QWidget()
        game_layout = QVBoxLayout()
        game_layout.setSpacing(15)
        
        # 上半部分：莊家和決策
        top_widget = QWidget()
        top_layout = QHBoxLayout()
        
        # 莊家區域
        dealer_group = QGroupBox("莊家牌")
        dealer_layout = QVBoxLayout()
        
        # 莊家牌顯示容器
        dealer_cards_widget = QWidget()
        dealer_cards_widget.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border: 2px solid #444;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        dealer_cards_layout = QVBoxLayout()
        
        # 牌面顯示
        self.dealer_label = QLabel("無牌")
        self.dealer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dealer_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #f39c12;
                padding: 10px;
            }
        """)
        dealer_cards_layout.addWidget(self.dealer_label)
        
        dealer_cards_widget.setLayout(dealer_cards_layout)
        dealer_layout.addWidget(dealer_cards_widget)
        dealer_group.setLayout(dealer_layout)
        top_layout.addWidget(dealer_group)
        
        # 決策建議區域
        decision_group = QGroupBox("建議動作")
        decision_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #e74c3c;
            }
        """)
        decision_layout = QVBoxLayout()
        
        self.decision_label = QLabel("請加入手牌")
        self.decision_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.decision_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #e74c3c;
                background-color: #2b2b2b;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        decision_layout.addWidget(self.decision_label)
        
        
        decision_group.setLayout(decision_layout)
        top_layout.addWidget(decision_group)
        
        top_widget.setLayout(top_layout)
        game_layout.addWidget(top_widget)
        
        # 下半部分：玩家手牌（可滾動網格佈局）
        hands_group = QGroupBox("玩家手牌")
        hands_group_layout = QVBoxLayout()
        
        # 創建滾動區域
        self.hands_scroll_area = QScrollArea()
        self.hands_scroll_area.setWidgetResizable(True)
        self.hands_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.hands_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.hands_scroll_area.setMinimumHeight(250)
        self.hands_scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
            QScrollBar:horizontal {
                background-color: #2b2b2b;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #555;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #666;
            }
        """)
        
        # 手牌容器
        self.hands_container = QWidget()
        self.hands_container.setObjectName("handsContainer")
        self.hands_container.setStyleSheet("#handsContainer { background-color: #1e1e1e; }")
        self.hands_layout = QGridLayout()
        self.hands_layout.setSpacing(10)
        self.hands_layout.setContentsMargins(10, 10, 10, 10)
        self.hands_container.setLayout(self.hands_layout)
        
        # 設置滾動區域的內容
        self.hands_scroll_area.setWidget(self.hands_container)
        
        hands_group_layout.addWidget(self.hands_scroll_area)
        hands_group.setLayout(hands_group_layout)
        game_layout.addWidget(hands_group)
        
        game_widget.setLayout(game_layout)
        return game_widget
    
    def create_control_panel(self) -> QWidget:
        """建立控制面板"""
        panel = QGroupBox("控制面板")
        layout = QVBoxLayout()
        
        # 牌輸入區域 - 水平佈局
        card_input_layout = QHBoxLayout()
        card_input_layout.setSpacing(15)
        
        # 玩家手牌區域
        player_group = QGroupBox("玩家手牌")
        player_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #3498db;
                subcontrol-origin: margin;
                left: 10px;
            }
        """)
        player_layout = QVBoxLayout()
        player_buttons = self.create_card_buttons("玩家", self.add_player_card, "player")
        player_layout.addWidget(player_buttons)
        player_group.setLayout(player_layout)
        card_input_layout.addWidget(player_group, 1)  # stretch = 1
        
        # 莊家牌區域
        dealer_group = QGroupBox("莊家牌")
        dealer_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #f39c12;
                subcontrol-origin: margin;
                left: 10px;
            }
        """)
        dealer_layout = QVBoxLayout()
        dealer_buttons = self.create_card_buttons("莊家", self.set_dealer_card, "dealer")
        dealer_layout.addWidget(dealer_buttons)
        dealer_group.setLayout(dealer_layout)
        card_input_layout.addWidget(dealer_group, 1)  # stretch = 1
        
        # 其他玩家區域
        others_group = QGroupBox("其他玩家")
        others_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #95a5a6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #95a5a6;
                subcontrol-origin: margin;
                left: 10px;
            }
        """)
        others_layout = QVBoxLayout()
        others_buttons = self.create_card_buttons("其他", self.add_other_card, "other")
        others_layout.addWidget(others_buttons)
        
        # 顯示已輸入的牌
        cards_label = QLabel("已輸入:")
        cards_label.setStyleSheet("color: #95a5a6; font-size: 13px; margin-top: 5px;")
        others_layout.addWidget(cards_label)
        
        self.other_cards_text = QTextEdit()
        self.other_cards_text.setMaximumHeight(30)  # 限制高度
        self.other_cards_text.setReadOnly(True)  # 只讀
        self.other_cards_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)  # 自動換行
        self.other_cards_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.other_cards_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.other_cards_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 4px;
                color: #aaa;
                font-size: 13px;
                padding: 4px 8px;
            }
        """)
        others_layout.addWidget(self.other_cards_text)
        
        others_group.setLayout(others_layout)
        card_input_layout.addWidget(others_group, 1)  # stretch = 1
        
        layout.addLayout(card_input_layout)
        
        # 動作按鈕
        buttons_layout = QHBoxLayout()
        
        # 遊戲動作
        self.split_button = QPushButton("分牌 (P)")
        self.split_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                font-size: 16px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """)
        self.split_button.clicked.connect(self.split_hand)
        self.split_button.setEnabled(False)
        buttons_layout.addWidget(self.split_button)
        
        buttons_layout.addStretch()
        
        # 控制按鈕
        clear_button = QPushButton("新回合")
        clear_button.clicked.connect(self.clear_hand)
        buttons_layout.addWidget(clear_button)
        
        new_shoe_button = QPushButton("新牌靴")
        new_shoe_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
            }
            QPushButton:hover {
                background-color: #f1c40f;
            }
        """)
        new_shoe_button.clicked.connect(self.new_shoe)
        buttons_layout.addWidget(new_shoe_button)
        
        layout.addLayout(buttons_layout)
        panel.setLayout(layout)
        return panel
    
    def create_card_buttons(self, category: str, callback, card_type: str = None) -> QWidget:
        """建立牌按鈕網格"""
        widget = QWidget()
        grid = QGridLayout()
        grid.setSpacing(5)
        
        cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        
        for i, card in enumerate(cards):
            btn = QPushButton(card)
            
            # 特殊牌的顏色
            if card == "A":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f39c12;
                        color: black;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #f1c40f;
                    }
                """)
            elif card in ["K", "Q", "J"]:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                    }
                    QPushButton:hover {
                        background-color: #5dade2;
                    }
                """)
            
            btn.clicked.connect(lambda checked, c=card: callback(c))
            grid.addWidget(btn, i // 4, i % 4)
        
        # 添加退牌按鈕
        if card_type in ["player", "dealer", "other"]:
            backspace_btn = QPushButton("←")
            backspace_btn.setToolTip("退牌")
            
            # 統一使用紅色
            backspace_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            
            backspace_btn.clicked.connect(lambda: self.remove_specific_card(card_type))
            grid.addWidget(backspace_btn, 3, 1)  # 放在K旁邊
        
        widget.setLayout(grid)
        return widget
    
    def update_display(self):
        """更新整個顯示"""
        self.update_counts()
        self.update_dealer_display()
        self.update_hands_display()
        self.update_decision_display()
        self.update_button_states()
        self.update_other_cards_display()
    
    def update_other_cards_display(self):
        """更新其他玩家牌顯示"""
        if not self.other_player_cards:
            self.other_cards_text.clear()
            return
        
        # 反向列表，讓最新的牌在前，用空格分隔以便自動換行
        reversed_cards = list(reversed(self.other_player_cards))
        cards_text = " ".join(reversed_cards)
        
        self.other_cards_text.setText(cards_text)
        
        # 滾動到開頭顯示最新的牌
        cursor = self.other_cards_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self.other_cards_text.setTextCursor(cursor)
    
    def update_counts(self):
        """更新計數顯示"""
        running = self.counter.running_count
        true = self.counter.get_true_count()
        decks = self.counter.get_decks_remaining()
        
        # 更新數值
        self.running_count_value.setText(f"{running:.1f}")
        self.true_count_value.setText(f"{true:.1f}")
        self.decks_remaining_value.setText(f"{decks:.1f}")
        
        # 根據真實計數更新顏色
        if true >= 2:
            color = "#27ae60"  # 深綠 - 強玩家優勢
        elif true >= 1:
            color = "#2ecc71"  # 綠 - 玩家優勢
        elif true <= -2:
            color = "#e74c3c"  # 深紅 - 強莊家優勢
        elif true <= -1:
            color = "#ec7063"  # 紅 - 莊家優勢
        else:
            color = "#f39c12"  # 黃 - 中性
        
        # 只對真實計數應用顏色
        self.true_count_value.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
    
    def update_dealer_display(self):
        """更新莊家牌顯示"""
        if not self.game_state.dealer_cards:
            self.dealer_label.setText("無牌")
        elif len(self.game_state.dealer_cards) == 1:
            # 只有一張牌時，顯示為底牌
            self.dealer_label.setText(f"底牌: {self.game_state.dealer_cards[0]}")
        else:
            # 有多張牌時，分開顯示底牌和其他牌
            upcard = self.game_state.dealer_cards[0]
            other_cards = ", ".join(self.game_state.dealer_cards[1:])
            self.dealer_label.setText(f"底牌: {upcard} | 其他: {other_cards}")
    
    def update_hands_display(self):
        """更新手牌顯示"""
        # 清除舊的手牌框架
        for frame in self.hand_frames:
            frame.setParent(None)
            frame.deleteLater()
        self.hand_frames.clear()
        
        # 清除佈局中的所有項目
        while self.hands_layout.count():
            item = self.hands_layout.takeAt(0)
            if item:
                item = None
        
        # 計算網格配置
        num_hands = len(self.game_state.player_hands)
        if num_hands <= 4:
            columns = num_hands
            rows = 1
        elif num_hands <= 8:
            columns = 4
            rows = 2
        elif num_hands <= 16:
            columns = 4
            rows = 4
        else:
            columns = 4
            rows = 8
        
        # 為每個手牌建立顯示
        for idx, hand in enumerate(self.game_state.player_hands):
            is_active = idx == self.game_state.current_hand_index
            hand_frame = HandFrame(idx, hand, is_active)
            
            # 連接點擊信號
            hand_frame.clicked.connect(self.on_hand_selected)
            
            # 如果是活動手牌，顯示決策
            if hand.status == HandStatus.ACTIVE and self.game_state.dealer_card:
                action, _ = self.strategy.get_decision(hand.cards, self.game_state.dealer_card)
                action_label = QLabel(f"建議: {action}")
                action_label.setStyleSheet(f"color: {self.get_action_color(action)}; font-size: 14px; font-weight: bold;")
                hand_frame.layout().addWidget(action_label)
            
            # 計算網格位置
            row = idx // columns
            col = idx % columns
            
            self.hands_layout.addWidget(hand_frame, row, col)
            self.hand_frames.append(hand_frame)
    
    def update_decision_display(self):
        """更新決策顯示"""
        current_hand = self.game_state.current_hand
        
        if current_hand.cards and self.game_state.dealer_card:
            action, explanation = self.strategy.get_decision(
                current_hand.cards, self.game_state.dealer_card
            )
            self.decision_label.setText(action)
            self.decision_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 32px;
                    font-weight: bold;
                    color: {self.get_action_color(action)};
                    background-color: #2b2b2b;
                    border: 2px solid {self.get_action_color(action)};
                    border-radius: 10px;
                    padding: 20px;
                }}
            """)
        else:
            self.decision_label.setText("請加入手牌")
            self.decision_label.setStyleSheet("""
                QLabel {
                    font-size: 32px;
                    font-weight: bold;
                    color: #888;
                    background-color: #2b2b2b;
                    border: 2px solid #444;
                    border-radius: 10px;
                    padding: 20px;
                }
            """)
    
    def update_button_states(self):
        """更新按鈕狀態"""
        self.split_button.setEnabled(self.game_state.can_split_current_hand())
    
    def get_action_color(self, action: str) -> str:
        """取得動作對應的顏色"""
        color_map = {
            "要牌": "#3498db",    # 藍
            "停牌": "#27ae60",    # 綠
            "加倍": "#f39c12",    # 橙
            "分牌": "#9b59b6",    # 紫
            "投降": "#e74c3c",    # 紅
            "爆牌": "#c0392b",    # 深紅
        }
        return color_map.get(action, "#888")
    
    # 事件處理方法
    def add_player_card(self, card: str):
        """新增玩家手牌"""
        self.counter.add_card(card)
        self.game_state.add_player_card(card)
        self.last_card_action = "player"
        self.update_display()
    
    def set_dealer_card(self, card: str):
        """新增莊家牌"""
        self.counter.add_card(card)
        self.game_state.add_dealer_card(card)
        self.last_card_action = "dealer"
        self.update_display()
    
    def add_other_card(self, card: str):
        """新增其他玩家的牌"""
        self.counter.add_card(card)
        self.other_player_cards.append(card)
        self.last_card_action = "other"
        self.update_display()
    
    def clear_hand(self):
        """清除手牌"""
        self.game_state.clear_hand()
        self.other_player_cards.clear()
        self.update_display()
    
    def remove_last_card(self):
        """移除最後一張牌"""
        # 根據最後的操作決定移除哪邊的牌
        if self.last_card_action == "player":
            removed_card = self.game_state.remove_last_card_from_current_hand()
            if removed_card:
                self.counter.remove_card(removed_card)
                self.update_display()
        elif self.last_card_action == "dealer":
            removed_card = self.game_state.remove_last_dealer_card()
            if removed_card:
                self.counter.remove_card(removed_card)
                self.update_display()
        elif self.last_card_action == "other":
            if self.other_player_cards:
                removed_card = self.other_player_cards.pop()
                self.counter.remove_card(removed_card)
                self.update_display()
    
    def remove_specific_card(self, card_type: str):
        """移除特定類型的牌"""
        if card_type == "player":
            removed_card = self.game_state.remove_last_card_from_current_hand()
            if removed_card:
                self.counter.remove_card(removed_card)
                self.update_display()
        elif card_type == "dealer":
            removed_card = self.game_state.remove_last_dealer_card()
            if removed_card:
                self.counter.remove_card(removed_card)
                self.update_display()
        elif card_type == "other":
            if self.other_player_cards:
                removed_card = self.other_player_cards.pop()
                self.counter.remove_card(removed_card)
                self.update_display()
    
    def new_shoe(self):
        """開始新牌靴"""
        reply = QMessageBox.question(
            self, "新牌靴", "開始新牌靴？這將重置所有計數。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.counter.new_shoe()
            self.game_state.clear_hand()
            self.other_player_cards.clear()
            self.update_display()
    
    def stand_hand(self):
        """當前手牌停牌"""
        self.game_state.stand_current_hand()
        self.update_display()
    
    def split_hand(self):
        """分牌"""
        if self.game_state.split_current_hand():
            self.update_display()
        else:
            QMessageBox.warning(self, "分牌失敗", "無法分牌")
    
    def on_hand_selected(self, index: int):
        """處理手牌選擇事件"""
        if self.game_state.set_current_hand_index(index):
            self.update_display()
    
    def keyPressEvent(self, event):
        """處理鍵盤事件"""
        if event.key() in (Qt.Key.Key_P, Qt.Key.Key_p):
            if self.split_button.isEnabled():
                self.split_hand()
        elif event.key() == Qt.Key.Key_Backspace:
            self.remove_last_card()


def main():
    """主程式進入點"""
    app = QApplication(sys.argv)
    
    # 設定應用程式樣式
    app.setStyle("Fusion")
    
    # 創建主視窗
    window = ModernBlackjackCounterApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()