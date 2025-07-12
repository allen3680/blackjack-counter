#!/usr/bin/env python3
"""測試 CustomTkinter 是否能正常運行"""

try:
    import customtkinter as ctk
    
    # 建立最簡單的視窗
    root = ctk.CTk()
    root.title("CustomTkinter 測試")
    root.geometry("400x300")
    
    # 加個簡單的標籤
    label = ctk.CTkLabel(root, text="CustomTkinter 運行正常！")
    label.pack(pady=20)
    
    # 加個按鈕
    button = ctk.CTkButton(root, text="關閉", command=root.quit)
    button.pack(pady=10)
    
    print("正在啟動 CustomTkinter 測試視窗...")
    root.mainloop()
    print("CustomTkinter 測試完成")
    
except Exception as e:
    print(f"錯誤: {e}")
    print("\n可能的解決方案:")
    print("1. 確認已安裝 customtkinter: pip install customtkinter")
    print("2. 嘗試更新到最新版本: pip install --upgrade customtkinter")
    print("3. 檢查 Python 版本 (需要 3.7+)")