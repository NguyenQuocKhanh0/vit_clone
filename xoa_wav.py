import os

folder_path = "/mnt/g/download/Audio_tung_30h/1_50/meger/InfoRe"

# Lấy danh sách tất cả các tệp trong thư mục
file_list = os.listdir(folder_path)

# Lọc ra các tệp WAV và xóa chúng
for file_name in file_list:
    if file_name.lower().endswith(".textgrid"):
        file_path = os.path.join(folder_path, file_name)
        os.remove(file_path)
        print(f"Đã xóa: {file_name}")
