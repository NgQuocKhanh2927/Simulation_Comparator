import tkinter as tk
from gui_app import SimulationProApp

if __name__ == "__main__":
    root = tk.Tk()

    # Hỗ trợ độ phân giải cao (DPI Awareness) để chữ không bị mờ
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = SimulationProApp(root)
    root.mainloop()