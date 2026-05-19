import customtkinter as ctk
from tkinter import filedialog, messagebox
import os


class SimulationApp:
    def __init__(self, root, db_handler):
        self.root = root
        self.db = db_handler
        self.root.title("ADVANCED SIMULATOR V3.0")
        self.root.geometry("1100x750")

        # Theme màu tối
        self.color_bg = "#1a1a1a"
        self.color_sidebar = "#252525"
        self.color_accent = "#2ecc71"  # Xanh lá cho Start
        self.color_danger = "#e74c3c"  # Đỏ cho Delete

        self.file1_path = ""
        self.file2_path = ""

        self.setup_ui()

    def setup_ui(self):
        self.root.configure(fg_color=self.color_bg)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        sidebar = ctk.CTkFrame(self.root, width=220, corner_radius=0, fg_color=self.color_sidebar)
        sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(sidebar, text="CONTROL PANEL", font=("Arial", 20, "bold")).pack(pady=(30, 20))

        # Nút chọn file
        ctk.CTkButton(sidebar, text="📂 Chọn File 1", command=lambda: self.pick_file(1)).pack(pady=10, padx=20)
        ctk.CTkButton(sidebar, text="📂 Chọn File 2", command=lambda: self.pick_file(2)).pack(pady=10, padx=20)

        # Nút chức năng chính
        ctk.CTkButton(sidebar, text="▶ START ANALYSIS", fg_color=self.color_accent,
                      hover_color="#27ae60", command=self.run_analysis).pack(pady=(40, 10), padx=20)

        ctk.CTkButton(sidebar, text="🗑 Delete Latest", fg_color=self.color_danger,
                      hover_color="#c0392b", command=self.delete_latest).pack(pady=10, padx=20)

        ctk.CTkButton(sidebar, text="🔄 Undo Restore", command=self.undo_restore).pack(pady=10, padx=20)

        # --- MAIN AREA ---
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Headers
        ctk.CTkLabel(main_frame, text="NỘI DUNG FILE 1", font=("Arial", 12, "bold")).grid(row=0, column=0)
        ctk.CTkLabel(main_frame, text="NỘI DUNG FILE 2", font=("Arial", 12, "bold")).grid(row=0, column=1)

        # Textboxes
        self.txt1 = ctk.CTkTextbox(main_frame, font=("Consolas", 12))
        self.txt1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.txt2 = ctk.CTkTextbox(main_frame, font=("Consolas", 12))
        self.txt2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Status
        self.status = ctk.CTkLabel(main_frame, text="Status: Ready", text_color="#64748B")
        self.status.grid(row=2, column=0, columnspan=2, pady=10)

    def pick_file(self, num):
        path = filedialog.askopenfilename()
        if path:
            if num == 1:
                self.file1_path = path
                self.load_text(path, self.txt1)
            else:
                self.file2_path = path
                self.load_text(path, self.txt2)

    def load_text(self, path, widget):
        with open(path, 'r', encoding='utf-8') as f:
            widget.delete("1.0", "end")
            widget.insert("1.0", f.read())

    def run_analysis(self):
        if self.file1_path and self.file2_path:
            name = f"{os.path.basename(self.file1_path)} vs {os.path.basename(self.file2_path)}"
            self.db.add_result(name, 92.0)  # Ví dụ 92%
            self.status.configure(text=f"Saved: {name} (92%)", text_color=self.color_accent)
            messagebox.showinfo("Success", "Đã lưu kết quả vào Database!")
        else:
            messagebox.showwarning("Warning", "Vui lòng chọn đủ 2 file!")

    def delete_latest(self):
        self.db.soft_delete_latest()
        self.status.configure(text="Status: Deleted latest entry", text_color=self.color_danger)
        messagebox.showinfo("Deleted", "Đã xóa tạm thời. Nhấn Undo để khôi phục.")

    def undo_restore(self):
        self.db.restore_latest()
        self.status.configure(text="Status: Restored successfully!", text_color=self.color_accent)
        messagebox.showinfo("Restored", "Đã khôi phục dữ liệu!")