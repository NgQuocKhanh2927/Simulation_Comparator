import pandas as pd
from tkinter import filedialog, messagebox
import datetime
import json
import os

class HistoryManager:
    def __init__(self):
        self.db_file = "history_data.json"  # Tên file lưu trữ
        self.records = []
        self.trash = []
        self.load_data() # Tự động tải dữ liệu khi khởi chạy

    def save_data(self):
        """Lưu toàn bộ danh sách vào file JSON"""
        data = {
            "records": self.records,
            "trash": self.trash
        }
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        """Tải dữ liệu từ file JSON lên nếu tồn tại"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.records = data.get("records", [])
                    self.trash = data.get("trash", [])
            except Exception as e:
                print(f"Lỗi tải dữ liệu: {e}")

    def add_record(self, filename, match_pct):
        date_str = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        # Tính ID dựa trên tổng số lượng để không bị trùng
        record_id = len(self.records) + len(self.trash) + 1
        new_record = [record_id, filename, f"{match_pct}%", date_str]
        self.records.insert(0, new_record)
        self.save_data() # Lưu lại ngay sau khi thêm
        return new_record

    def move_to_trash(self, values):
        if values in self.records:
            self.records.remove(values)
            self.trash.append(values)
            self.save_data() # Lưu lại sau khi xóa

    def restore_specific(self, record_id):
        for item in self.trash:
            if item[0] == record_id:
                self.trash.remove(item)
                self.records.insert(0, item)
                self.save_data() # Lưu lại sau khi khôi phục
                return item
        return None

    def export_excel(self):
        if not self.records:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất!")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if path:
            pd.DataFrame(self.records, columns=["ID", "File Name", "Match %", "Date Modified"]).to_excel(path, index=False)
            messagebox.showinfo("Thành công", "Đã xuất Excel!")