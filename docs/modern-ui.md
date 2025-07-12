# 現代化 GUI 美化版本

## 概述

新的現代化版本使用 ttkbootstrap 框架實現了美觀的深色主題界面，提供了更好的視覺體驗和互動性。由於 CustomTkinter 在 Linux 上存在兼容性問題，我們改用 ttkbootstrap 作為替代方案。

## 主要特色

### 1. 現代化深色主題
- 使用 ttkbootstrap 的 "darkly" 主題
- Bootstrap 風格的按鈕和元件
- 專業的配色方案提升視覺層次

### 2. 視覺化元件
- **Meter 元件**：圓形儀表盤顯示真實計數
- **進度條**：顯示玩家優勢的動態進度條
- **Tab 分頁**：使用 Notebook 組織牌輸入區域
- **彩色按鈕**：不同類型的牌使用不同顏色

### 3. 視覺增強
- 使用 LabelFrame 創建分組區域
- Bootstrap 風格的按鈕（success, info, warning, danger）
- 不同狀態的視覺區分（活動手牌高亮）
- 反色標籤突出重要信息

### 4. 優勢指示器
- 動態進度條顯示真實計數
- 根據計數自動變換顏色和樣式
- 條紋進度條增加視覺效果

### 5. 改進的佈局
- 響應式設計，支持窗口縮放
- 使用網格和框架組織佈局
- 清晰的功能分區
- Canvas 實現的可滾動手牌區域

### 6. 快捷鍵支持
- S / s：停牌
- P / p：分牌（當可用時）

## 運行方式

### 方法 1：使用 Makefile
```bash
make run-modern
```

### 方法 2：直接運行
```bash
python3 -m src.gui.app_modern_ttk
```

### 方法 3：使用腳本
```bash
python3 scripts/run_modern_ttk.py
```

## 安裝依賴

確保已安裝必要的依賴：
```bash
pip install ttkbootstrap
```

或使用完整安裝：
```bash
make install
```

## 與原版本的比較

| 特性 | 原版本 | 現代化版本 |
|------|--------|------------|
| UI 框架 | Tkinter + ttk | ttkbootstrap |
| 主題 | 系統默認 | Darkly 深色主題 |
| 視覺元件 | 基本元件 | Meter、進度條、Tab |
| 顏色方案 | 基本顏色 | Bootstrap 配色系統 |
| 視覺反饋 | 最小 | 豐富的樣式變化 |
| 按鈕樣式 | 標準按鈕 | Bootstrap 風格按鈕 |

## 技術細節

- 使用 ttkbootstrap 1.10.0+ 版本
- 支持 Python 3.7+
- 基於標準 tkinter，兼容性更好
- 使用 Bootstrap 風格系統

## 未來改進方向

1. 添加音效支持（可選）
2. 實現拖放功能
3. 添加更多動畫過渡效果
4. 支持自定義主題切換
5. 添加統計圖表顯示