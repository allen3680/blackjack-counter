#!/usr/bin/env python3
"""
21點計牌器 - 現代化桌面應用程式
使用 PyQt6 實現美化界面
"""

import sys
import yaml
from typing import List, Optional, Dict, Any
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QGridLayout,
    QScrollArea,
    QFrame,
    QTabWidget,
    QMessageBox,
    QSizePolicy,
    QTextEdit,
    QDialog,
    QDialogButtonBox,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect
from PyQt6.QtGui import QFont, QPalette, QColor, QLinearGradient, QCursor, QMouseEvent, QPixmap, QPainter, QIcon

from src.core import BasicStrategy, GameState, WongHalvesCounter, HandStatus
from src.config import SHORTCUTS_CONFIG


class ClickableGroupBox(QGroupBox):
    """可點擊的群組框"""
    
    # 定義點擊信號
    clicked = pyqtSignal()
    
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        # 設定游標樣式（可點擊）
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """處理滑鼠點擊事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


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
            self.setStyleSheet(
                """
                QGroupBox {
                    background-color: #3a3a3a;
                    border: 3px solid #f39c12;
                    border-radius: 10px;
                    margin-top: 2px;
                    padding: 5px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    color: #f39c12;
                    font-weight: bold;
                    font-size: 12px;
                }
            """
            )
        else:
            self.setStyleSheet(
                """
                QGroupBox {
                    background-color: #2b2b2b;
                    border: 2px solid #444;
                    border-radius: 10px;
                    margin-top: 2px;
                    padding: 5px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    color: #888;
                    font-size: 11px;
                }
            """
            )

        layout = QVBoxLayout()
        layout.setSpacing(2)

        # 手牌顯示
        cards_label = QLabel(hand.get_display_string())
        cards_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        cards_label.setWordWrap(True)
        layout.addWidget(cards_label)

        # 點數顯示
        value, _ = hand.calculate_value()
        value_text = f"點數: {value}"
        value_style = "color: #888; font-size: 11px;"

        if hand.status == HandStatus.BLACKJACK:
            value_text = "Blackjack! 🎉"
            value_style = "color: #27ae60; font-size: 14px; font-weight: bold;"
        elif hand.status == HandStatus.BUSTED:
            value_text = f"爆牌! ({value})"
            value_style = "color: #e74c3c; font-size: 14px; font-weight: bold;"

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
            self.setStyleSheet(
                """
                QGroupBox {
                    background-color: #3a3a3a;
                    border: 2px solid #666;
                    border-radius: 10px;
                    margin-top: 2px;
                    padding: 5px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    color: #aaa;
                    font-size: 11px;
                }
            """
            )
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """滑鼠離開時恢復原樣"""
        if not self.is_active and self.hand.status == HandStatus.ACTIVE:
            self.setStyleSheet(
                """
                QGroupBox {
                    background-color: #2b2b2b;
                    border: 2px solid #444;
                    border-radius: 10px;
                    margin-top: 2px;
                    padding: 5px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    color: #888;
                    font-size: 11px;
                }
            """
            )
        super().leaveEvent(event)


class NewShoeDialog(QDialog):
    """自定義新牌靴確認對話框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新牌靴確認")
        self.setModal(True)
        self.setFixedSize(420, 220)
        
        # 設定深色主題樣式
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                border: 2px solid #444;
                border-radius: 15px;
            }
        """)
        
        # 移除標題欄
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        # 主佈局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 20)
        
        # 標題
        title_label = QLabel("開始新牌靴？")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #f39c12;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title_label)
        
        # 警告文字
        warning_label = QLabel("這將重置所有計數並清除手牌")
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 14px;
                padding: 10px;
            }
        """)
        layout.addWidget(warning_label)
        
        # 按鈕區域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # 取消按鈕
        cancel_button = QPushButton("取消")
        cancel_button.setFixedSize(120, 40)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 2px solid #555;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #666;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # 確認按鈕
        confirm_button = QPushButton("開始新牌靴")
        confirm_button.setFixedSize(120, 40)
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f1c40f;
            }
            QPushButton:pressed {
                background-color: #d68910;
            }
        """)
        confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(confirm_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # 淡入動畫
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(200)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
    def showEvent(self, event):
        """顯示時播放淡入動畫"""
        super().showEvent(event)
        self.fade_in_animation.start()
        
        # 將對話框置中於父視窗
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.center().x() - self.width() // 2
            y = parent_rect.center().y() - self.height() // 2
            self.move(x, y)


class ModernBlackjackCounterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlackJack Counter Pro")
        self.setGeometry(100, 100, 800, 650)
        self.setMinimumHeight(650)
        
        # 設定應用程式圖標
        self.setWindowIcon(self.create_blackjack_icon())

        # 初始化元件
        self.counter = WongHalvesCounter(num_decks=8)
        self.strategy = BasicStrategy()
        self.game_state = GameState()

        # 載入快捷鍵設定
        self.shortcuts: Dict[str, Dict[str, Any]] = self.load_shortcuts()

        # GUI 元件參考
        self.hand_frames: List[HandFrame] = []
        self.last_card_action: str = "player"  # 追蹤最後的牌操作: "player" 或 "dealer"
        self.other_player_cards: List[str] = []  # 追蹤其他玩家的牌
        
        # 控制面板群組參考
        self.player_group: Optional[ClickableGroupBox] = None
        self.dealer_group: Optional[ClickableGroupBox] = None
        self.others_group: Optional[ClickableGroupBox] = None
        
        # 面板切換追蹤
        self.panel_order = ["player", "dealer", "other"]
        self.current_panel_index = 0  # 從玩家手牌開始

        # 設定深色主題
        self.setStyleSheet(
            """
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
                padding: 4px 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4a4a4a;
            }
        """
        )

        # 建立主介面
        self.setup_ui()
        self.update_display()
        self.update_panel_selection()

    def create_blackjack_icon(self) -> QIcon:
        """生成BlackJack應用圖標"""
        # 創建 64x64 的圖標
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 繪製背景圓圈
        painter.setBrush(QColor("#2c3e50"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        
        # 繪製撲克牌符號 - 黑桃
        painter.setBrush(QColor("#ecf0f1"))
        # 黑桃形狀
        spade_path = [
            (32, 15),  # 頂點
            (22, 30),  # 左邊
            (26, 35),  # 左下
            (32, 30),  # 中心
            (38, 35),  # 右下
            (42, 30),  # 右邊
            (32, 15),  # 回到頂點
        ]
        
        for i in range(len(spade_path) - 1):
            painter.drawLine(spade_path[i][0], spade_path[i][1], 
                           spade_path[i+1][0], spade_path[i+1][1])
        
        # 繪製黑桃底部
        painter.drawLine(28, 35, 32, 45)  # 左側到中心
        painter.drawLine(36, 35, 32, 45)  # 右側到中心
        
        # 繪製 "21" 文字
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.setPen(QColor("#e74c3c"))
        painter.drawText(20, 50, "21")
        
        painter.end()
        
        return QIcon(pixmap)

    def setup_ui(self):
        """設定使用者介面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 5)

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
        status_bar.setStyleSheet(
            """
            QFrame {
                background-color: #2b2b2b;
                border-top: 1px solid #444;
                padding: 3px 5px;
                max-height: 40px;
            }
        """
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)

        # 真實計數
        true_count_label = QLabel("真實計數:")
        true_count_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(true_count_label)

        self.true_count_value = QLabel("0.0")
        self.true_count_value.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.true_count_value)

        # 分隔符
        layout.addWidget(QLabel("|"))

        # 流水計數
        running_count_label = QLabel("流水計數:")
        running_count_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(running_count_label)

        self.running_count_value = QLabel("0")
        self.running_count_value.setStyleSheet("color: white; font-size: 12px;")
        layout.addWidget(self.running_count_value)

        # 分隔符
        layout.addWidget(QLabel("|"))

        # 剩餘張數
        cards_label = QLabel("剩餘張數:")
        cards_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(cards_label)

        self.cards_remaining_value = QLabel("416")
        self.cards_remaining_value.setStyleSheet("color: white; font-size: 12px;")
        layout.addWidget(self.cards_remaining_value)

        layout.addStretch()
        status_bar.setLayout(layout)
        return status_bar

    def create_game_area(self) -> QWidget:
        """建立遊戲區域"""
        game_widget = QWidget()
        game_layout = QVBoxLayout()
        game_layout.setSpacing(8)

        # 上半部分：莊家和決策
        top_widget = QWidget()
        top_layout = QHBoxLayout()

        # 莊家區域
        dealer_group = QGroupBox("莊家牌")
        dealer_layout = QVBoxLayout()

        # 莊家牌顯示容器
        dealer_cards_widget = QWidget()
        dealer_cards_widget.setStyleSheet(
            """
            QWidget {
                background-color: #2b2b2b;
                border: 2px solid #444;
                border-radius: 10px;
                padding: 8px;
            }
        """
        )
        dealer_cards_layout = QVBoxLayout()

        # 牌面顯示
        self.dealer_label = QLabel("無牌")
        self.dealer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dealer_label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #f39c12;
                padding: 3px;
            }
        """
        )
        dealer_cards_layout.addWidget(self.dealer_label)

        dealer_cards_widget.setLayout(dealer_cards_layout)
        dealer_layout.addWidget(dealer_cards_widget)
        dealer_group.setLayout(dealer_layout)
        top_layout.addWidget(dealer_group)

        # 決策建議區域
        decision_group = QGroupBox("建議動作")
        decision_group.setStyleSheet(
            """
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #e74c3c;
            }
        """
        )
        decision_layout = QVBoxLayout()

        self.decision_label = QLabel("請加入手牌")
        self.decision_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.decision_label.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #e74c3c;
                background-color: #2b2b2b;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                padding: 5px;
            }
        """
        )
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
        self.hands_scroll_area.setMinimumHeight(80)
        self.hands_scroll_area.setStyleSheet(
            """
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
        """
        )

        # 手牌容器
        self.hands_container = QWidget()
        self.hands_container.setObjectName("handsContainer")
        self.hands_container.setStyleSheet("#handsContainer { background-color: #1e1e1e; }")
        self.hands_layout = QGridLayout()
        self.hands_layout.setSpacing(5)
        self.hands_layout.setContentsMargins(5, 5, 5, 5)
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
        card_input_layout.setSpacing(8)

        # 玩家手牌區域
        self.player_group = ClickableGroupBox("玩家手牌")
        self.player_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 2px;
                padding-top: 2px;
            }
            QGroupBox::title {
                color: #3498db;
                subcontrol-origin: margin;
                left: 10px;
            }
        """
        )
        self.player_group.clicked.connect(lambda: self.on_panel_clicked("player"))
        player_layout = QVBoxLayout()
        player_buttons = self.create_card_buttons("玩家", self.add_player_card, "player")
        player_layout.addWidget(player_buttons)

        # 分牌按鈕
        self.split_button = QPushButton("分牌 (P)")
        self.split_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                font-size: 14px;
                padding: 4px 8px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """
        )
        self.split_button.clicked.connect(self.split_hand)
        self.split_button.setEnabled(False)
        player_layout.addWidget(self.split_button)

        self.player_group.setLayout(player_layout)
        card_input_layout.addWidget(self.player_group, 1)  # stretch = 1

        # 莊家牌區域
        self.dealer_group = ClickableGroupBox("莊家牌")
        self.dealer_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 2px;
                padding-top: 2px;
            }
            QGroupBox::title {
                color: #f39c12;
                subcontrol-origin: margin;
                left: 10px;
            }
        """
        )
        self.dealer_group.clicked.connect(lambda: self.on_panel_clicked("dealer"))
        dealer_layout = QVBoxLayout()
        dealer_buttons = self.create_card_buttons("莊家", self.set_dealer_card, "dealer")
        dealer_layout.addWidget(dealer_buttons)
        self.dealer_group.setLayout(dealer_layout)
        card_input_layout.addWidget(self.dealer_group, 1)  # stretch = 1

        # 其他玩家區域
        self.others_group = ClickableGroupBox("其他玩家")
        self.others_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #95a5a6;
                border-radius: 8px;
                margin-top: 2px;
                padding-top: 2px;
            }
            QGroupBox::title {
                color: #95a5a6;
                subcontrol-origin: margin;
                left: 10px;
            }
        """
        )
        self.others_group.clicked.connect(lambda: self.on_panel_clicked("other"))
        others_layout = QVBoxLayout()
        others_buttons = self.create_card_buttons("其他", self.add_other_card, "other")
        others_layout.addWidget(others_buttons)

        # 顯示已輸入的牌
        cards_label = QLabel("已輸入:")
        cards_label.setStyleSheet("color: #95a5a6; font-size: 11px; margin-top: 2px;")
        others_layout.addWidget(cards_label)

        self.other_cards_text = QTextEdit()
        self.other_cards_text.setMaximumHeight(20)  # 限制高度
        self.other_cards_text.setReadOnly(True)  # 只讀
        self.other_cards_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)  # 自動換行
        self.other_cards_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.other_cards_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.other_cards_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 4px;
                color: #aaa;
                font-size: 13px;
                padding: 2px 4px;
            }
        """
        )
        others_layout.addWidget(self.other_cards_text)

        self.others_group.setLayout(others_layout)
        card_input_layout.addWidget(self.others_group, 1)  # stretch = 1

        layout.addLayout(card_input_layout)

        # 動作按鈕
        buttons_layout = QHBoxLayout()

        buttons_layout.addStretch()

        # 控制按鈕
        clear_button = QPushButton("新回合")
        clear_button.clicked.connect(self.clear_hand)
        buttons_layout.addWidget(clear_button)

        new_shoe_button = QPushButton("新牌靴")
        new_shoe_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f39c12;
            }
            QPushButton:hover {
                background-color: #f1c40f;
            }
        """
        )
        new_shoe_button.clicked.connect(self.new_shoe)
        buttons_layout.addWidget(new_shoe_button)

        layout.addLayout(buttons_layout)
        panel.setLayout(layout)
        return panel

    def create_card_buttons(self, category: str, callback, card_type: str = None) -> QWidget:
        """建立牌按鈕網格"""
        widget = QWidget()
        grid = QGridLayout()
        grid.setSpacing(2)

        cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

        for i, card in enumerate(cards):
            btn = QPushButton(card)

            # 特殊牌的顏色
            if card == "A":
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #f39c12;
                        color: black;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #f1c40f;
                    }
                """
                )
            elif card in ["K", "Q", "J"]:
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #3498db;
                    }
                    QPushButton:hover {
                        background-color: #5dade2;
                    }
                """
                )

            btn.clicked.connect(lambda checked, c=card: callback(c))
            grid.addWidget(btn, i // 4, i % 4)

        # 添加退牌按鈕
        if card_type in ["player", "dealer", "other"]:
            backspace_btn = QPushButton("←")
            backspace_btn.setToolTip("退牌")

            # 統一使用紅色
            backspace_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """
            )

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
        cards = self.counter.get_cards_remaining()

        # 更新數值
        self.running_count_value.setText(f"{running:.1f}")
        self.true_count_value.setText(f"{true:.1f}")
        self.cards_remaining_value.setText(f"{cards}")

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
        self.true_count_value.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")

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
                action_label.setStyleSheet(
                    f"color: {self.get_action_color(action)}; font-size: 12px; font-weight: bold;"
                )
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
            self.decision_label.setStyleSheet(
                f"""
                QLabel {{
                    font-size: 20px;
                    font-weight: bold;
                    color: {self.get_action_color(action)};
                    background-color: #2b2b2b;
                    border: 2px solid {self.get_action_color(action)};
                    border-radius: 10px;
                    padding: 5px;
                }}
            """
            )
        else:
            self.decision_label.setText("請加入手牌")
            self.decision_label.setStyleSheet(
                """
                QLabel {
                    font-size: 20px;
                    font-weight: bold;
                    color: #888;
                    background-color: #2b2b2b;
                    border: 2px solid #444;
                    border-radius: 10px;
                    padding: 5px;
                }
            """
            )

    def update_button_states(self):
        """更新按鈕狀態"""
        self.split_button.setEnabled(self.game_state.can_split_current_hand())
    
    def update_panel_selection(self):
        """更新控制面板選中狀態"""
        # 定義選中和未選中的樣式
        selected_style = """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 2px;
                padding-top: 2px;
            }
            QGroupBox::title {
                color: #f39c12;
                subcontrol-origin: margin;
                left: 10px;
            }
        """
        
        unselected_style = """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #95a5a6;
                border-radius: 8px;
                margin-top: 2px;
                padding-top: 2px;
            }
            QGroupBox::title {
                color: #95a5a6;
                subcontrol-origin: margin;
                left: 10px;
            }
        """
        
        # 根據 last_card_action 更新樣式
        if self.player_group:
            self.player_group.setStyleSheet(
                selected_style if self.last_card_action == "player" else unselected_style
            )
        
        if self.dealer_group:
            self.dealer_group.setStyleSheet(
                selected_style if self.last_card_action == "dealer" else unselected_style
            )
        
        if self.others_group:
            self.others_group.setStyleSheet(
                selected_style if self.last_card_action == "other" else unselected_style
            )

    def get_action_color(self, action: str) -> str:
        """取得動作對應的顏色"""
        color_map = {
            "要牌": "#3498db",  # 藍
            "停牌": "#27ae60",  # 綠
            "加倍": "#f39c12",  # 橙
            "分牌": "#9b59b6",  # 紫
            "投降": "#e74c3c",  # 紅
            "爆牌": "#c0392b",  # 深紅
        }
        return color_map.get(action, "#888")

    # 事件處理方法
    def add_player_card(self, card: str):
        """新增玩家手牌"""
        self.counter.add_card(card)
        self.game_state.add_player_card(card)
        self.last_card_action = "player"
        self.update_display()
        self.update_panel_selection()

    def set_dealer_card(self, card: str):
        """新增莊家牌"""
        self.counter.add_card(card)
        self.game_state.add_dealer_card(card)
        self.last_card_action = "dealer"
        self.update_display()
        self.update_panel_selection()

    def add_other_card(self, card: str):
        """新增其他玩家的牌"""
        self.counter.add_card(card)
        self.other_player_cards.append(card)
        self.last_card_action = "other"
        self.update_display()
        self.update_panel_selection()

    def add_card_smart(self, card: str):
        """根據最後操作位置智慧新增卡牌"""
        if self.last_card_action == "player":
            self.add_player_card(card)
        elif self.last_card_action == "dealer":
            self.set_dealer_card(card)
        elif self.last_card_action == "other":
            self.add_other_card(card)

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
        # 顯示自定義對話框
        dialog = NewShoeDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
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
    
    def on_panel_clicked(self, panel_type: str):
        """處理控制面板點擊事件"""
        self.last_card_action = panel_type
        # 同步更新當前面板索引
        if panel_type in self.panel_order:
            self.current_panel_index = self.panel_order.index(panel_type)
        self.update_panel_selection()
    
    def switch_to_next_panel(self):
        """切換到下一個面板"""
        self.current_panel_index = (self.current_panel_index + 1) % len(self.panel_order)
        self.on_panel_clicked(self.panel_order[self.current_panel_index])
    
    def switch_to_previous_panel(self):
        """切換到上一個面板"""
        self.current_panel_index = (self.current_panel_index - 1) % len(self.panel_order)
        self.on_panel_clicked(self.panel_order[self.current_panel_index])
    
    def focusNextPrevChild(self, next: bool) -> bool:
        """覆蓋焦點切換行為，將 Tab 鍵用於面板切換"""
        if next:
            self.switch_to_next_panel()
        else:
            self.switch_to_previous_panel()
        return True  # 返回 True 表示我們處理了焦點切換

    def load_shortcuts(self) -> Dict[str, Dict[str, Any]]:
        """載入快捷鍵設定"""
        try:
            with open(SHORTCUTS_CONFIG, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get("shortcuts", {})
        except FileNotFoundError:
            print(f"找不到快捷鍵設定檔：{SHORTCUTS_CONFIG}")
            return {}
        except yaml.YAMLError as e:
            print(f"快捷鍵設定檔格式錯誤：{e}")
            return {}

    def get_qt_key(self, key_name: str):
        """將按鍵名稱轉換為Qt按鍵常數"""
        # 處理組合鍵
        if "+" in key_name:
            # 暫時不處理組合鍵，留待未來擴充
            return None
            
        # 按鍵映射表
        key_map = {
            "Backspace": Qt.Key.Key_Backspace,
            "Return": Qt.Key.Key_Return,
            "Enter": Qt.Key.Key_Return,
            "Space": Qt.Key.Key_Space,
            "Tab": Qt.Key.Key_Tab,
            "Escape": Qt.Key.Key_Escape,
            "Delete": Qt.Key.Key_Delete,
        }
        
        # 檢查是否為特殊按鍵
        if key_name in key_map:
            return key_map[key_name]
            
        # 處理單個字母或數字
        if len(key_name) == 1:
            if key_name.isalpha():
                # PyQt6 只有大寫字母的Key常數
                return getattr(Qt.Key, f"Key_{key_name.upper()}", None)
            elif key_name.isdigit():
                return getattr(Qt.Key, f"Key_{key_name}", None)
                
        return None

    def keyPressEvent(self, event):
        """處理鍵盤事件"""
        pressed_key = event.key()
        
        # 遍歷所有快捷鍵設定
        for action_name, shortcut_config in self.shortcuts.items():
            keys = shortcut_config.get("keys", [])
            
            # 檢查按下的鍵是否匹配任何設定的按鍵
            for key_name in keys:
                qt_key = self.get_qt_key(key_name)
                if qt_key and pressed_key == qt_key:
                    # 檢查條件（如果有）
                    condition = shortcut_config.get("condition")
                    
                    # 執行對應的動作
                    if action_name == "split_hand":
                        if not condition or (condition == "split_enabled" and self.split_button.isEnabled()):
                            self.split_hand()
                            return
                    elif action_name == "remove_card":
                        self.remove_last_card()
                        return
                    # 處理卡牌輸入
                    elif action_name.startswith("card_"):
                        # 從 action_name 中提取卡牌值
                        card_map = {
                            "card_ace": "A",
                            "card_2": "2",
                            "card_3": "3",
                            "card_4": "4",
                            "card_5": "5",
                            "card_6": "6",
                            "card_7": "7",
                            "card_8": "8",
                            "card_9": "9",
                            "card_10": "10",
                            "card_jack": "J",
                            "card_queen": "Q",
                            "card_king": "K"
                        }
                        if action_name in card_map:
                            self.add_card_smart(card_map[action_name])
                            return


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
