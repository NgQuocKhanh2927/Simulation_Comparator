import pandas as pd

def run_comparison(path_g, path_t):

    try:

        df_g = pd.read_csv(path_g)
        df_t = pd.read_csv(path_t)

        if df_g.shape != df_t.shape:
            return 0.0, ["Kích thước file không khớp (Dòng/Cột khác nhau)"]

        comparison_matrix = (df_g == df_t)
        match_count = comparison_matrix.values.sum()
        total_elements = df_g.size
        # Tỉ lệ
        rate = round((match_count / total_elements) * 100, 2)


        diff_points = []
        #từng hàng của bảng
        for r in range(len(df_g)):
            #từng cột của bảng
            for c in range(len(df_g.columns)):
                # .iloc[r, c] dùng để truy cập giá trị tại hàng , cột
                if df_g.iloc[r, c] != df_t.iloc[r, c]:
                    col_name = df_g.columns[c] #lấy tên của cột đang bị lỗi
                    val_g = df_g.iloc[r, c] #giá trị đúng (Golden)
                    val_t = df_t.iloc[r, c] # Giá trị sai (Test)

                    diff_points.append(f"• Hàng {r + 1}, Cột '{col_name}': Gốc={val_g} vs Test={val_t}")

                if len(diff_points) >= 50: break
            if len(diff_points) >= 50: break

        return rate, diff_points
    except Exception as e:
        return None, [f"Lỗi đọc file: {str(e)}"]