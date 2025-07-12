#!/usr/bin/env python3
"""測試 ttkbootstrap 是否能正常運行"""

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    
    # 建立視窗，使用深色主題
    root = ttk.Window(themename="darkly")
    root.title("ttkbootstrap 測試")
    root.geometry("500x400")
    
    # 主框架
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill=BOTH, expand=YES)
    
    # 標題
    title = ttk.Label(
        main_frame,
        text="ttkbootstrap 運行正常！",
        font=("Helvetica", 18, "bold"),
        bootstyle="success"
    )
    title.pack(pady=20)
    
    # 測試不同樣式的按鈕
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=10)
    
    ttk.Button(button_frame, text="成功", bootstyle=SUCCESS).pack(side=LEFT, padx=5)
    ttk.Button(button_frame, text="資訊", bootstyle=INFO).pack(side=LEFT, padx=5)
    ttk.Button(button_frame, text="警告", bootstyle=WARNING).pack(side=LEFT, padx=5)
    ttk.Button(button_frame, text="危險", bootstyle=DANGER).pack(side=LEFT, padx=5)
    
    # 進度條測試
    progress_label = ttk.Label(main_frame, text="進度條測試:", font=("Helvetica", 12))
    progress_label.pack(pady=(20, 5))
    
    progress = ttk.Progressbar(
        main_frame,
        length=300,
        mode="determinate",
        bootstyle="success-striped"
    )
    progress.pack(pady=5)
    progress['value'] = 65
    
    # 計量器測試
    meter_frame = ttk.Frame(main_frame)
    meter_frame.pack(pady=20)
    
    meter = ttk.Meter(
        meter_frame,
        metersize=150,
        padding=5,
        amountused=75,
        amounttotal=100,
        metertype="semi",
        subtext="真實計數",
        bootstyle="success"
    )
    meter.pack(side=LEFT, padx=10)
    
    # 關閉按鈕
    close_btn = ttk.Button(
        main_frame,
        text="關閉",
        command=root.quit,
        bootstyle="danger-outline"
    )
    close_btn.pack(pady=20)
    
    print("正在啟動 ttkbootstrap 測試視窗...")
    root.mainloop()
    print("ttkbootstrap 測試完成")
    
except ImportError as e:
    print(f"導入錯誤: {e}")
    print("\n請安裝 ttkbootstrap:")
    print("pip install ttkbootstrap")
    
except Exception as e:
    print(f"錯誤: {e}")
    print("\n可能的解決方案:")
    print("1. 確認已安裝 ttkbootstrap: pip install ttkbootstrap")
    print("2. 嘗試更新到最新版本: pip install --upgrade ttkbootstrap")
    print("3. 檢查 Python 版本 (需要 3.7+)")