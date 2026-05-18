import pandas as pd # Nạp thư viện pandas - công cụ mạnh nhất để xử lý bảng dữ liệu (CSV, Excel)

def run_comparison(path_g, path_t):
    """
        Hàm thực hiện so sánh hai file CSV.
        Input: Đường dẫn file Golden (gốc) và file Test.
        Output: Tỉ lệ phần trăm khớp (%) và danh sách các điểm sai lệch.
        """
    try:
        # Đọc nội dung file CSV từ đường dẫn và chuyển thành đối tượng DataFrame (dạng bảng)
        df_g = pd.read_csv(path_g)
        df_t = pd.read_csv(path_t)

        # Kiểm tra kích thước (số hàng và số cột) của 2 bảng
        # Nếu một file có 10 hàng mà file kia có 11 hàng thì không thể so sánh công bằng được
        if df_g.shape != df_t.shape:
            return 0.0, ["Kích thước file không khớp (Dòng/Cột khác nhau)"]

        # --- PHẦN TÍNH TOÁN TỈ LỆ ---

        # So sánh toàn bộ 2 bảng cùng lúc.
        # Kết quả 'comparison_matrix' là một bảng chứa các giá trị True (nếu khớp) và False (nếu lệch)
        comparison_matrix = (df_g == df_t)
        # .values.sum() sẽ cộng tất cả các giá trị True lại (trong lập trình True = 1)
        # Kết quả là tổng số ô dữ liệu trùng khớp hoàn toàn
        match_count = comparison_matrix.values.sum()
        # .size trả về tổng số ô dữ liệu có trong bảng (hàng x cột)
        total_elements = df_g.size
        # Tính tỉ lệ phần trăm: (Số ô khớp / Tổng số ô) * 100, làm tròn đến 2 chữ số thập phân
        rate = round((match_count / total_elements) * 100, 2)

        # --- PHẦN TÌM ĐIỂM SAI LỆCH ---

        diff_points = [] # Khởi tạo danh sách rỗng để chứa các dòng thông báo lỗi
        # Vòng lặp chạy qua từng hàng (r) của bảng
        for r in range(len(df_g)):
            # Vòng lặp chạy qua từng cột (c) của bảng
            for c in range(len(df_g.columns)):
                # .iloc[r, c] dùng để truy cập chính xác giá trị tại hàng r, cột c
                # Nếu giá trị tại ô này ở file Golden khác với file Test
                if df_g.iloc[r, c] != df_t.iloc[r, c]:
                    col_name = df_g.columns[c] # Lấy tên của cột đang bị lỗi
                    val_g = df_g.iloc[r, c] # Giá trị đúng (Golden)
                    val_t = df_t.iloc[r, c] # Giá trị sai (Test)
                    # Tạo một dòng thông báo dễ hiểu và thêm vào danh sách
                    diff_points.append(f"• Hàng {r + 1}, Cột '{col_name}': Gốc={val_g} vs Test={val_t}")
                # Để tránh bảng thông báo quá dài, nếu tìm thấy đủ 5 lỗi thì dừng lại không tìm tiếp nữa
                if len(diff_points) >= 5: break
            if len(diff_points) >= 5: break
        # Trả về kết quả cuối cùng: con số tỉ lệ và danh sách lỗi (tối đa 5 lỗi)
        return rate, diff_points
    except Exception as e:
        # Nếu file bị lỗi định dạng hoặc không đọc được, trả về None và nội dung lỗi
        return None, [f"Lỗi đọc file: {str(e)}"]