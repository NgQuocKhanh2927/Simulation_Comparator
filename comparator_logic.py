def compare_files_logic(golden_text, test_text):
    # Loại bỏ khoảng trắng thừa (Ignore Whitespace)
    g_lines = [l.strip() for l in golden_text.strip().splitlines() if l.strip()]
    t_lines = [l.strip() for l in test_text.strip().splitlines() if l.strip()]

    # Trừ dòng tiêu đề
    g_data = g_lines[1:] if len(g_lines) > 0 else []
    t_data = t_lines[1:] if len(t_lines) > 0 else []

    max_len = len(g_data)
    matches = 0
    diffs = []
    g_pts, t_pts = [], []

    # Giới hạn tìm tối đa 50 lỗi
    MAX_ERRORS = 50

    for i in range(max_len):
        gv = g_data[i]
        tv = t_data[i] if i < len(t_data) else "MISSING"

        if gv == tv:
            matches += 1
        else:
            if len(diffs) < MAX_ERRORS:
                diffs.append((i + 1, gv, tv))  # Trả về tuple (dòng, giá trị G, giá trị T)
            elif len(diffs) == MAX_ERRORS:
                diffs.append(("...", "... [Đã đạt giới hạn 50 lỗi, dừng tìm kiếm]", ""))

        def to_num(s):
            try:
                return float(s.split(',')[-1])
            except:
                return 0.0

        g_pts.append(to_num(gv))
        t_pts.append(to_num(tv) if tv != "MISSING" else 0.0)

    match_pct = round((matches / max_len) * 100, 2) if max_len > 0 else 0
    return match_pct, diffs, g_pts, t_pts