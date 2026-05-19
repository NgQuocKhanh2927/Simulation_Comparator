import sqlite3
from datetime import datetime


class DBHandler:
    def __init__(self):
        # Kết nối tới database chuẩn
        self.conn = sqlite3.connect("simulation_pro.db")
        self.cur = self.conn.cursor()

        # Tạo bảng với cột is_deleted để hỗ trợ khôi phục (Undo)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                match_rate REAL,
                timestamp TEXT,
                is_deleted INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def add_result(self, name, rate):
        """Lưu kết quả phân tích kèm thời gian thực"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute("""
            INSERT INTO logs (file_name, match_rate, timestamp, is_deleted) 
            VALUES (?, ?, ?, 0)
        """, (name, rate, now))
        self.conn.commit()

    def soft_delete_latest(self):
        """Đánh dấu bản ghi mới nhất là 'đã xóa' (is_deleted = 1)"""
        self.cur.execute("""
            UPDATE logs SET is_deleted = 1 
            WHERE id = (SELECT max(id) FROM logs WHERE is_deleted = 0)
        """)
        self.conn.commit()

    def restore_latest(self):
        """Khôi phục bản ghi bị xóa gần đây nhất (is_deleted = 0)"""
        self.cur.execute("""
            UPDATE logs SET is_deleted = 0 
            WHERE id = (SELECT max(id) FROM logs WHERE is_deleted = 1)
        """)
        self.conn.commit()