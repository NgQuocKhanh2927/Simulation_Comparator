import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
from comparator_logic import compare_files_logic
from database_handler import HistoryManager


class SimulationProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulation Core Pro v3.0 - Professional Edition")
        self.root.geometry("1300x950")
        self.root.configure(bg="#f4f7f9")

        self.history_mgr = HistoryManager()
        self.g_pts, self.t_pts = [], []
        self.current_fname = "N/A"

        self.setup_styles()
        self.setup_ui()

        # PHÍM TẮT (HOTKEYS)
        self.root.bind("<Control-Return>", lambda e: self.run_analysis())  # Ctrl + Enter để chạy
        self.root.bind("<Control-s>", lambda e: self.history_mgr.export_excel())  # Ctrl + S để xuất Excel

        # Nạp dữ liệu cũ
        self.refresh_tree()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Arial", 11), rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

    def setup_ui(self):
        # SIDEBAR
        sidebar = tk.Frame(self.root, width=250, bg="white", highlightbackground="#e0e0e0", highlightthickness=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(sidebar, text="SIMULATOR", font=("Arial", 22, "bold"), fg="#1a73e8", bg="white").pack(pady=(40, 5))
        tk.Label(sidebar, text="PROFESSIONAL EDITION", font=("Arial", 10, "bold"), fg="#95a5a6", bg="white").pack(
            pady=(0, 40))

        btn_opt = {"font": ("Arial", 11, "bold"), "relief": "flat", "pady": 15, "cursor": "hand2"}
        tk.Button(sidebar, text="▶ START ANALYSIS", bg="#00b894", fg="white", command=self.run_analysis,
                  **btn_opt).pack(fill=tk.X, padx=20, pady=10)
        tk.Button(sidebar, text="📊 VIEW DASHBOARD", bg="white", fg="#1a73e8", highlightthickness=1,
                  command=self.show_dashboard, **btn_opt).pack(fill=tk.X, padx=20, pady=5)
        tk.Button(sidebar, text="📥 EXPORT EXCEL", bg="white", fg="#636e72", highlightthickness=1,
                  command=self.history_mgr.export_excel, **btn_opt).pack(fill=tk.X, padx=20, pady=5)

        # MAIN CONTENT
        main = tk.Frame(self.root, bg="#f4f7f9")
        main.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=30, pady=20)
        main.rowconfigure(1, weight=1)
        main.columnconfigure(0, weight=1)

        # 1. FILE CONFIGURATION
        cfg = tk.LabelFrame(main, text=" File Configuration ", bg="white", font=("Arial", 14, "bold"), padx=15, pady=15)
        cfg.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        cfg.columnconfigure((0, 1), weight=1)

        self.txt_golden = self.create_editor(cfg, "Golden Reference", 0, self.load_g)
        self.txt_test = self.create_editor(cfg, "Test Subject", 1, self.load_t)

        # 2. EXECUTION HISTORY
        hist = tk.LabelFrame(main, text=" Execution History ", bg="white", font=("Arial", 14, "bold"), padx=15, pady=15)
        hist.grid(row=1, column=0, sticky="nsew")

        # THANH TÌM KIẾM (SEARCH BAR)
        search_fm = tk.Frame(hist, bg="white")
        search_fm.pack(fill=tk.X, pady=(0, 10))
        tk.Label(search_fm, text="🔍 Search File:", bg="white", font=("Arial", 11)).pack(side=tk.LEFT)
        self.ent_search = tk.Entry(search_fm, font=("Arial", 11))
        self.ent_search.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.ent_search.bind("<KeyRelease>", self.filter_history)

        tool = tk.Frame(hist, bg="white")
        tool.pack(fill=tk.X)
        tk.Button(tool, text="Restore List", bg="#636e72", fg="white", font=("Arial", 10, "bold"),
                  command=self.show_restore).pack(side=tk.RIGHT, padx=5)
        tk.Button(tool, text="Delete Selected", bg="#ff7675", fg="white", font=("Arial", 10, "bold"),
                  command=self.delete_item).pack(side=tk.RIGHT)

        self.tree = ttk.Treeview(hist, columns=("id", "name", "match", "date"), show="headings")
        for c, h in zip(("id", "name", "match", "date"), ("ID", "FILE NAME", "MATCH %", "DATE MODIFIED")):
            self.tree.heading(c, text=h)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # 3. SUGGESTION (TÔ MÀU LỖI)
        tk.Label(hist, text="Gợi ý: các dòng sai lệch ", fg="#d63031", bg="white",
                 font=("Arial", 11, "bold")).pack(anchor="w")
        self.txt_diff = scrolledtext.ScrolledText(hist, height=6, bg="#fff5f5", font=("Consolas", 12), borderwidth=0)
        self.txt_diff.pack(fill=tk.X, pady=(5, 0))

        # Định nghĩa các thẻ màu
        self.txt_diff.tag_config("red", foreground="#d63031", font=("Consolas", 12, "bold"))
        self.txt_diff.tag_config("blue", foreground="#0984e3", font=("Consolas", 12, "bold"))
        self.txt_diff.tag_config("green", foreground="#00b894", font=("Consolas", 12, "bold"))

    def create_editor(self, parent, label, col, cmd):
        f = tk.Frame(parent, bg="white")
        f.grid(row=0, column=col, sticky="nsew", padx=10)
        hdr = tk.Frame(f, bg="white")
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=label, bg="white", font=("Arial", 12)).pack(side=tk.LEFT)
        tk.Button(hdr, text="Choose File", font=("Arial", 9), command=cmd).pack(side=tk.RIGHT)
        t = scrolledtext.ScrolledText(f, height=10, font=("Consolas", 12), relief="solid", borderwidth=1)
        t.pack(fill=tk.BOTH, expand=True, pady=5)
        return t

    def refresh_tree(self, data_list=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        target = data_list if data_list is not None else self.history_mgr.records
        for r in target:
            self.tree.insert("", tk.END, values=r)

    def filter_history(self, event=None):
        query = self.ent_search.get().lower()
        filtered = [r for r in self.history_mgr.records if query in r[1].lower()]
        self.refresh_tree(filtered)

    def load_g(self):
        p = filedialog.askopenfilename()
        if p:
            with open(p, 'r', encoding='utf-8') as f:
                self.txt_golden.delete(1.0, tk.END)
                self.txt_golden.insert(tk.END, f.read())

    def load_t(self):
        p = filedialog.askopenfilename()
        if p:
            self.current_fname = p.split('/')[-1]
            with open(p, 'r', encoding='utf-8') as f:
                self.txt_test.delete(1.0, tk.END)
                self.txt_test.insert(tk.END, f.read())

    def run_analysis(self):
        g_raw = self.txt_golden.get(1.0, tk.END)
        t_raw = self.txt_test.get(1.0, tk.END)

        # Gọi logic so sánh (Đã cải tiến Tuple)
        pct, diffs, self.g_pts, self.t_pts = compare_files_logic(g_raw, t_raw)

        self.txt_diff.config(state=tk.NORMAL)
        self.txt_diff.delete(1.0, tk.END)

        if not diffs:
            self.txt_diff.insert(tk.END, "✓ Dữ liệu khớp hoàn hảo!", "green")
        else:
            for line_no, g_val, t_val in diffs:
                if line_no == "...":  # Dòng thông báo giới hạn
                    self.txt_diff.insert(tk.END, f"{g_val}\n")
                    break
                self.txt_diff.insert(tk.END, f"• Dòng {line_no}: ", "normal")
                self.txt_diff.insert(tk.END, f"Golden[{g_val}]", "blue")
                self.txt_diff.insert(tk.END, " ≠ ", "normal")
                self.txt_diff.insert(tk.END, f"Test[{t_val}]\n", "red")

        self.txt_diff.config(state=tk.DISABLED)

        rec = self.history_mgr.add_record(self.current_fname, pct)
        self.refresh_tree()

    def delete_item(self):
        for s in self.tree.selection():
            val = list(self.tree.item(s)['values'])
            self.history_mgr.move_to_trash(val)
            self.tree.delete(s)

    def show_restore(self):
        if not self.history_mgr.trash:
            messagebox.showinfo("Trống", "Thùng rác đang trống!")
            return
        win = tk.Toplevel(self.root)
        win.title("Restore List")
        win.geometry("500x400")
        lb = tk.Listbox(win, width=60, font=("Arial", 11))
        lb.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        for r in self.history_mgr.trash:
            lb.insert(tk.END, f"ID {r[0]}: {r[1]} - {r[2]}")

        def do_res():
            if lb.curselection():
                idx = lb.curselection()[0]
                rec_id = self.history_mgr.trash[idx][0]
                res = self.history_mgr.restore_specific(rec_id)
                self.refresh_tree()
                win.destroy()

        tk.Button(win, text="Restore Selected Item", font=("Arial", 10, "bold"), command=do_res, pady=10).pack(pady=10)

    def show_dashboard(self):
        if not self.g_pts:
            messagebox.showwarning(title="Lỗi", message="Vui lòng START ANALYSIS trước!")
            return

        win = tk.Toplevel(self.root)
        win.title("View Dashboard")
        fig, ax = plt.subplots(figsize=(10, 6))

        indices = list(range(1, len(self.g_pts) + 1))
        ax.plot(indices, self.g_pts, label="Golden", color="black", linewidth=2, marker='o', markersize=4)
        ax.plot(indices, self.t_pts, label="Test", color="#ff4757", linestyle="--", linewidth=2, marker='x',
                markersize=5)

        ax.set_xticks(indices)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        ax.set_title("So sánh số liệu Golden vs Test", fontdict={'fontsize': 14, 'fontweight': 'bold'})
        ax.set_xlabel("Dòng dữ liệu (Time Index)")
        ax.set_ylabel("Giá trị (Value)")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # NÚT LƯU ẢNH DASHBOARD
        def save_img():
            path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if path:
                fig.savefig(path)
                messagebox.showinfo("Thành công", "Đã lưu ảnh Dashboard!")

        btn_save = tk.Button(win, text="📸 Save Dashboard as Image", command=save_img, bg="#1a73e8", fg="white",
                             font=("Arial", 10, "bold"))
        btn_save.pack(pady=5)

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)