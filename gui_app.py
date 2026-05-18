import customtkinter as ctk # Import thư viện giao diện hiện đại (nút bo góc, màu sắc đẹp)
from tkinter import filedialog, messagebox, ttk # Các công cụ chọn file, hộp thoại thông báo và bảng dữ liệu
from database_handler import DBHandler # Import lớp Databas đã viết
from comparator_logic import run_comparison # Import hàm so sánh dữ liệu logic
import matplotlib.pyplot as plt # Thư viện để vẽ biểu đồ

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class SimulationApp:
    def __init__(self, root):
        self.root = root # Lưu cửa sổ chính vào biến self để dùng toàn chương trình
        self.db = DBHandler() # Khởi tạo kết nối đến file Database sqlite
        self.g_path = "" # Biến lưu đường dẫn file Golden (mặc định để rỗng)
        self.t_path = "" # Biến lưu đường dẫn file Test (mặc định để rỗng)

        # Bảng màu
        self.color_bg = "#F8FAFC" # Màu nền xám nhạt
        self.color_sidebar = "#FFFFFF" # Màu trắng cho thanh bên
        self.color_primary = "#3B82F6" # Màu xanh dương thương hiệu
        self.color_accent = "#10B981" # Màu xanh lá (dùng khi thành công/khớp 100%)
        self.color_text = "#1E293B" # Màu chữ đen xanh thẫm

        self.setup_ui()  # Gọi hàm xây dựng giao diện

    def setup_ui(self):
        """Hàm kiến trúc: Chia khung và sắp xếp các thành phần lên màn hình"""
        self.root.configure(fg_color=self.color_bg) # Đặt màu nền cho cửa sổ chính
        self.root.grid_columnconfigure(1, weight=1) # Cột 1 (chính) sẽ dãn rộng theo màn hình
        self.root.grid_rowconfigure(0, weight=1) # Hàng 0 sẽ dãn cao theo màn hình

        # --- SIDEBAR: Thanh điều khiển bên trái ---
        self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0, fg_color=self.color_sidebar)
        self.sidebar.grid(row=0, column=0, sticky="nsew") # Đặt sidebar ở cột 0, bám sát các cạnh
        # Các nhãn tiêu đề cho ứng dụng
        ctk.CTkLabel(self.sidebar, text="SIMULATOR", text_color=self.color_primary, font=("Arial", 24, "bold")).pack(
            pady=(40, 5))
        ctk.CTkLabel(self.sidebar, text=" ", text_color="#64748B", font=("Arial", 11, "bold")).pack(
            pady=(0, 40))
        # Nút bấm chạy phân tích (màu xanh lá bắt mắt)
        self.btn_run = ctk.CTkButton(self.sidebar, text="▶ START ANALYSIS", height=45, fg_color=self.color_accent,
                                     command=self.process)
        self.btn_run.pack(pady=10, padx=20)
        # Nút bấm xem biểu đồ (dạng viền trong suốt chuyên nghiệp)
        self.btn_chart = ctk.CTkButton(self.sidebar, text="📊 VIEW DASHBOARD", height=45, fg_color="transparent",
                                       border_width=2, text_color=self.color_primary, command=self.view_chart)
        self.btn_chart.pack(pady=10, padx=20)

        # --- MAIN AREA: Vùng hiển thị nội dung bên phải ---
        self.main = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main.grid_columnconfigure(0, weight=1) # Căn chỉnh để nội dung dãn đều

        # Input Card: Khung chọn file (có bo góc và viền nhẹ)
        self.card_in = ctk.CTkFrame(self.main, fg_color="white", corner_radius=15, border_width=1,
                                    border_color="#E2E8F0")
        self.card_in.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.create_input_ui()

        # Table Card: Khung chứa bảng lịch sử kết quả
        self.card_tbl = ctk.CTkFrame(self.main, fg_color="white", corner_radius=15, border_width=1,
                                     border_color="#E2E8F0")
        self.card_tbl.grid(row=1, column=0, sticky="nsew")
        self.card_tbl.grid_columnconfigure(0, weight=1)

        # Phần tiêu đề bảng và nút xóa
        self.table_header = ctk.CTkFrame(self.card_tbl, fg_color="transparent")
        self.table_header.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        ctk.CTkLabel(self.table_header, text="Execution Logs", font=("Arial", 18, "bold")).pack(side="left")
        ctk.CTkButton(self.table_header, text="🗑 DELETE", fg_color="#FEE2E2", text_color="#991B1B", width=90, height=30,
                      command=self.delete_item).pack(side="right")

        # Cấu hình Bảng (Treeview): Nơi hiển thị các bản ghi dữ liệu
        style = ttk.Style()
        style.theme_use("clam") # Dùng theme 'clam' để dễ tùy chỉnh màu sắc
        style.configure("Treeview", background="white", rowheight=40, font=("Segoe UI", 11))
        style.configure("Treeview.Heading", background="#F1F5F9", font=("Segoe UI", 11, "bold"))

        cols = ("ID", "File Name", "Match %", "Time") # Định nghĩa các cột
        self.tree = ttk.Treeview(self.card_tbl, columns=cols, show='headings', height=7)
        for c in cols:
            self.tree.heading(c, text=c) # Đặt tên tiêu đề cho từng cột
            self.tree.column(c, anchor="center") # Căn giữa dữ liệu trong cột
        self.tree.grid(row=1, column=0, sticky="ew", padx=20)

        # Hint Area: Vùng hiển thị lỗi sai chi tiết (nằm dưới bảng)
        self.hint_box = ctk.CTkFrame(self.card_tbl, fg_color="#F8FAFC", corner_radius=10)
        self.hint_box.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        self.lbl_hint = ctk.CTkLabel(self.hint_box, text="💡 GỢI Ý SAI LỆCH: Vui lòng chạy phân tích để xem chi tiết...",
                                     text_color="#64748B", justify="left", wraplength=600)
        self.lbl_hint.pack(padx=20, pady=15)

        self.update_table() # Cập nhật dữ liệu từ DB lên bảng khi vừa mở app

    def create_input_ui(self):
        f = self.card_in
        ctk.CTkLabel(f, text="File Selection", font=("Arial", 16, "bold")).grid(row=0, column=0, padx=20, pady=10,
                                                                                sticky="w")
        self.lbl_g = ctk.CTkLabel(f, text="Golden: None", text_color="#94A3B8")
        self.lbl_g.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        ctk.CTkButton(f, text="Select Golden", width=120, fg_color="#F1F5F9", text_color="black",
                      command=self.select_g).grid(row=1, column=1, padx=20, pady=5)
        self.lbl_t = ctk.CTkLabel(f, text="Test: None", text_color="#94A3B8")
        self.lbl_t.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        ctk.CTkButton(f, text="Select Test", width=120, fg_color="#F1F5F9", text_color="black",
                      command=self.select_t).grid(row=2, column=1, padx=20, pady=5)

    def select_g(self):
        """Hàm chọn file Golden: Mở Explorer và lấy đường dẫn file"""
        self.g_path = filedialog.askopenfilename()
        if self.g_path: # Nếu người dùng thực sự chọn file (không bấm Cancel)
            self.lbl_g.configure(text=f"✔ {self.g_path.split('/')[-1]}", text_color=self.color_primary)

    def select_t(self):
        self.t_path = filedialog.askopenfilename()
        if self.t_path:
            self.lbl_t.configure(text=f"✔ {self.t_path.split('/')[-1]}", text_color=self.color_primary)

    def process(self):
        """Hàm xử lý chính khi bấm nút START"""
        if not self.g_path or not self.t_path: # Kiểm tra xem đã chọn đủ 2 file chưa
            messagebox.showwarning("Lỗi", "Vui lòng chọn đủ 2 file!")
            return
        # Gọi hàm so sánh từ file logic và nhận về tỉ lệ khớp + danh sách lỗi
        rate, diffs = run_comparison(self.g_path, self.t_path)
        if rate is not None:
            # Lưu kết quả vào Database (lấy tên file ngắn gọn)
            self.db.add_result(self.t_path.split('/')[-1], rate)
            self.update_table() # Làm mới lại bảng trên giao diện
            # Hiển thị gợi ý
            msg = "\n".join(diffs) if rate < 100 else "Khớp hoàn hảo!"
            self.lbl_hint.configure(text=f"Tỉ lệ: {rate}%\n{msg}",
                                    text_color=self.color_accent if rate == 100 else "#E11D48")

    def update_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.db.get_results(): self.tree.insert('', 'end', values=r)

    def delete_item(self):
        try:
            sel = self.tree.selection()[0]
            log_id = self.tree.item(sel)['values'][0]
            self.db.delete_result(log_id)
            self.update_table()
        except:
            messagebox.showwarning("Lỗi", "Hãy chọn dòng cần xóa!")

    def view_chart(self):
        if not self.g_path or not self.t_path:
            messagebox.showwarning("Thông báo", "Vui lòng chọn cả 2 file Golden và Test để xem biểu đồ so sánh!")
            return

        try:
            import pandas as pd
            import matplotlib.ticker as ticker  # Thêm thư viện để chia tỉ lệ trục

            df_g = pd.read_csv(self.g_path)
            df_t = pd.read_csv(self.t_path)

            # Xác định trục X (Thời gian / Số lần)
            x_col = None
            for col in df_g.columns:
                if 'time' in str(col).lower() or 'lần' in str(col).lower():
                    x_col = col
                    break

            x_g = df_g[x_col] if x_col else df_g.index + 1  # +1 để bắt đầu từ 1 thay vì 0
            x_t = df_t[x_col] if x_col else df_t.index + 1

            # Xác định trục Y (Giá trị)
            y_col_g = [c for c in df_g.columns if c != x_col][0]
            y_col_t = [c for c in df_t.columns if c != x_col][0]

            plt.figure(figsize=(12, 6), facecolor="white")
            ax = plt.axes()
            ax.set_facecolor("#F8FAFC")

            # Vẽ đường sóng
            plt.plot(x_g, df_g[y_col_g], label=f"Golden", color="#3B82F6", linewidth=2.5)
            plt.plot(x_t, df_t[y_col_t], label=f"Test", color="#EF4444", linewidth=1.5, linestyle='--')

            # --- CHIA LẠI TỈ LỆ CỘT NGANG (1, 2, 3...) ---
            # Ép trục X chỉ hiển thị số nguyên
            ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

            # Nếu dữ liệu ít (dưới 20 điểm), hiển thị từng số một
            if len(x_g) <= 20:
                ax.xaxis.set_major_locator(ticker.MultipleLocator(1))

            plt.title("So sánh dạng sóng: Golden vs Test", fontsize=15, fontweight='bold', pad=15)
            plt.xlabel(f"Trục ngang (Lần): {x_col if x_col else 'Số thứ tự'}", fontsize=12)
            plt.ylabel("Giá trị dữ liệu", fontsize=12)

            plt.margins(x=0.02, y=0.1)  # Cân đối khoảng cách biên
            plt.grid(True, linestyle=':', alpha=0.6)
            plt.legend(loc="upper right")

            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể vẽ biểu đồ: {str(e)}")