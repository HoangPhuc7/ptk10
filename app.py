import streamlit as st
import pandas as pd
import os
import re

# 📁 Thư mục chứa file Excel
DATA_FOLDER = "du_lieu_excel"

# 📥 Đọc tất cả dữ liệu từ các file Excel
@st.cache_data
def load_all_exam_data(folder_path):
    all_data = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".xlsx") and not filename.startswith("~$"):
            subject = filename.replace(".xlsx", "")
            filepath = os.path.join(folder_path, filename)

            try:
                xls = pd.ExcelFile(filepath)
            except Exception as e:
                st.warning(f"Lỗi khi đọc file {filename}: {e}")
                continue

            for sheet_name in xls.sheet_names:
                df_raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)

                # 🔍 Tìm dòng chứa "Phòng thi: ..."
                room_row = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains("Phòng thi", na=False).any(), axis=1)]
                if not room_row.empty:
                    room_line_index = room_row.index[0]
                    room_text = room_row.values[0]
                    room_match = re.search(r'Phòng thi[:：]?\s*(\w+)', ' '.join(map(str, room_text)))
                    room = room_match.group(1) if room_match else "Không rõ"
                    header_index = room_line_index + 2
                else:
                    room = "Không rõ"
                    header_index = 0

                df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=header_index)
                required_cols = ["Họ và tên", "Lớp"]

                if all(col in df.columns for col in required_cols):
                    df = df[required_cols].copy()
                    df["Phòng thi"] = room
                    df["Môn"] = subject
                    all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame(columns=["Họ và tên", "Lớp", "Phòng thi", "Môn"])

# 🔍 Tra cứu theo tên và lớp
def tra_cuu(data, ho_ten, lop):
    ho_ten = ho_ten.strip().lower()
    lop = lop.strip().lower()

    df = data.copy()
    df["Họ và tên"] = df["Họ và tên"].astype(str).str.strip().str.lower()
    df["Lớp"] = df["Lớp"].astype(str).str.strip().str.lower()
    
    ket_qua = df[(df["Họ và tên"] == ho_ten) & (df["Lớp"] == lop)]

    return ket_qua[["Môn", "Phòng thi"]] if not ket_qua.empty else None

# 🖼️ Giao diện người dùng
#st.title("📋 Tra cứu phòng thi theo họ tên và lớp")

ten = st.text_input("Họ và tên (Chú ý dấu tên: Thúy,...)")
lop = st.text_input("Lớp (Viết in hoa: 10A2)")

if st.button("Tìm"):
    if not ten or not lop:
        st.warning("Vui lòng nhập đầy đủ họ tên và lớp.")
    else:
        data = load_all_exam_data(DATA_FOLDER)
        result = tra_cuu(data, ten, lop)

        if result is None or result.empty:
            st.error("Không tìm thấy.")
        else:
            st.success(f"Kết quả cho {ten} - {lop}:")
            st.dataframe(result)

