import customtkinter as ctk
from tkinter import filedialog, messagebox
import os


class SimulationApp:
    def __init__(self, root, db_handler):
        self.root = root
        self.db = db_handler
        self.root.title("SIMULATOR - File Comparison Tool")
        self.root.geometry("1100x700")

        # Cấu hình màu sắc
        self.color_bg = "#1a1a1a"
        self.color_sidebar = "#252525"
        self.color_accent = "#2ecc71"
        self.color_primary = "#ffffff"

        self.setup_ui()

    def setup_ui(self):
        # Chia layout chính thành 2 cột: Sidebar và Main Area
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.configure(fg_color=self.color_bg)

        # --- SIDEBAR (Bên trái) ---
        self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0, fg_color=self.color_sidebar)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="SIMULATOR", text_color=self.color_accent,
                     font=("Arial", 24, "bold")).pack(pady=(40, 5))
        ctk.CTkLabel(self.sidebar, text="V3.0 REAL-TIME", text_color="#64748B",
                     font=("Arial", 11, "bold")).pack(pady=(0, 40))

        # Nút chọn File 1
        self.btn_file1 = ctk.CTkButton(self.sidebar, text="📂 Chọn File 1",
                                       command=lambda: self.select_file(1))
        self.btn_file1.pack(pady=10, padx=20)

        # Nút chọn File 2
        self.btn_file2 = ctk.CTkButton(self.sidebar, text="📂 Chọn File 2",
                                       command=lambda: self.select_file(2))
        self.btn_file2.pack(pady=10, padx=20)

        # Nút Chạy phân tích
        self.btn_run = ctk.CTkButton(self.sidebar, text="▶ START ANALYSIS",
                                     fg_color=self.color_accent, hover_color="#27ae60",
                                     command=self.process_analysis)
        self.btn_run.pack(pady=30, padx=20)

        # --- MAIN AREA (Vùng hiển thị nội dung bên phải) ---
        self.main_area = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_area.grid_columnconfigure((0, 1), weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        # Tiêu đề khung nội dung
        ctk.CTkLabel(self.main_area, text="NỘI DUNG FILE 1", font=("Arial", 13, "bold")).grid(row=0, column=0,
                                                                                              pady=(0, 10))
        ctk.CTkLabel(self.main_area, text="NỘI DUNG FILE 2", font=("Arial", 13, "bold")).grid(row=0, column=1,
                                                                                              pady=(0, 10))

        # Khung văn bản hiển thị File 1
        self.txt_display1 = ctk.CTkTextbox(self.main_area, font=("Consolas", 12))
        self.txt_display1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Khung văn bản hiển thị File 2
        self.txt_display2 = ctk.CTkTextbox(self.main_area, font=("Consolas", 12))
        self.txt_display2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Khung hiển thị kết quả nhanh bên dưới
        self.status_label = ctk.CTkLabel(self.main_area, text="Trạng thái: Sẵn sàng", font=("Arial", 12))
        self.status_label.grid(row=2, column=0, columnspan=2, pady=10)

        # Lưu đường dẫn file
        self.file1_path = ""
        self.file2_path = ""

    def select_file(self, file_num):
        path = filedialog.askopenfilename(title=f"Chọn file thứ {file_num}",
                                          filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            if file_num == 1:
                self.file1_path = path
                self.read_and_display(path, self.txt_display1)
                self.btn_file1.configure(text=f"✔ {os.path.basename(path)}")
            else:
                self.file2_path = path
                self.read_and_display(path, self.txt_display2)
                self.btn_file2.configure(text=f"✔ {os.path.basename(path)}")

    def read_and_display(self, path, textbox):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                textbox.delete("1.0", "end")
                textbox.insert("1.0", content)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file: {e}")

    def process_analysis(self):
        if not self.file1_path or not self.file2_path:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đủ 2 file để phân tích!")
            return

        # Giả lập logic tính toán tỉ lệ khớp (Bạn có thể thay bằng logic thực tế)
        match_rate = 85.5  # Ví dụ kết quả
        file_name = f"{os.path.basename(self.file1_path)} vs {os.path.basename(self.file2_path)}"

        # Lưu vào database (Sử dụng database_handler của bạn)
        try:
            self.db.add_result(file_name, match_rate)
            self.status_label.configure(text=f"Kết quả: Khớp {match_rate}% - Đã lưu vào Database!",
                                        text_color=self.color_accent)
            messagebox.showinfo("Thành công", "Phân tích hoàn tất và đã lưu vào database!")
        except Exception as e:
            messagebox.showerror("Lỗi Database", f"Không thể lưu kết quả: {e}")