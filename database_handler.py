import sqlite3 # Thư viện dùng để làm việc với SQLite (một loại DB nhẹ, không cần cài đặt server)
from datetime import datetime # Thư viện dùng để lấy thời gian thực từ máy tính

class DBHandler:
    def __init__(self):
        """Hàm khởi tạo: Chạy ngay khi đối tượng DBHandler được tạo ra"""
        # Kết nối tới file database. Nếu chưa có file này, nó sẽ tự tạo mới.
        self.conn = sqlite3.connect("simulation_pro.db")
        # Cursor (Con trỏ) dùng để thực thi các câu lệnh SQL
        self.cur = self.conn.cursor()
        # Tạo bảng 'logs' nếu nó chưa tồn tại trong file database
        # id: Tự động tăng, file_name: Tên file, match_rate: Tỉ lệ %, timestamp: Thời gian
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                match_rate REAL,
                timestamp TEXT
            )
        """)
        # Xác nhận thay đổi (Lưu lại việc tạo bảng)
        self.conn.commit()

    def add_result(self, name, rate):
        """Hàm lưu kết quả phân tích vào database"""
        # Lấy thời gian hiện tại của máy tính theo định dạng: Năm-Tháng-Ngày Giờ:Phút:Giây
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Thực hiện chèn một dòng dữ liệu mới vào bảng logs
        # Dấu '?' là placeholder để tránh lỗi SQL Injection (bảo mật dữ liệu)
        self.cur.execute(
            "INSERT INTO logs (file_name, match_rate, timestamp) VALUES (?, ?, ?)",
            (name, rate, now)
        )
        # Lưu thay đổi vào file
        self.conn.commit()

    def get_results(self):
        """Hàm lấy toàn bộ dữ liệu từ database để hiển thị lên bảng (Treeview)"""
        # Lấy tất cả các cột từ bảng logs và sắp xếp theo ID từ thấp đến cao
        self.cur.execute("SELECT * FROM logs ORDER BY id ASC")
        # Trả về kết quả dưới dạng danh sách (list) các dòng
        return self.cur.fetchall()

    def delete_result(self, log_id):
        """Hàm xóa một bản ghi dựa trên ID được chọn"""
        # Xóa dòng có ID tương ứng
        self.cur.execute("DELETE FROM logs WHERE id=?", (log_id,))
        # Sau khi xóa, gọi hàm sắp xếp lại ID để danh sách trông gọn gàng hơn
        self.reorder_ids()
        self.conn.commit()

    def reorder_ids(self):
        """Hàm đặc biệt: Đánh số lại ID từ 1 để danh sách luôn liên tục, không bị nhảy số"""
        # 1. Lấy toàn bộ dữ liệu hiện có (trừ cột ID cũ) ra bộ nhớ tạm
        self.cur.execute("SELECT file_name, match_rate, timestamp FROM logs ORDER BY id ASC")
        data = self.cur.fetchall()
        # 2. Xóa sạch dữ liệu trong bảng logs
        self.cur.execute("DELETE FROM logs")
        # 3. Reset bộ đếm tự động tăng của SQLite về 0
        self.cur.execute("DELETE FROM sqlite_sequence WHERE name='logs'")
        # 4. Chèn lại toàn bộ dữ liệu cũ vào bảng.
        # Vì cột ID là AUTOINCREMENT, nó sẽ tự đánh số lại từ 1, 2, 3...
        self.cur.executemany("INSERT INTO logs (file_name, match_rate, timestamp) VALUES (?, ?, ?)", data)