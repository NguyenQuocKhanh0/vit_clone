from pydub import AudioSegment
import os

# Đường dẫn đến thư mục chứa các tệp M4A
input_folder = "/mnt/g/download/Audio_tung_30h/1_50/meger/InfoRe"

# Đường dẫn đến thư mục đích cho tệp MP3
output_folder = "/mnt/g/download/Audio_tung_30h/1_50/meger/InfoRe"

# Lấy danh sách các tệp M4A trong thư mục nguồn
m4a_files = [f for f in os.listdir(input_folder) if f.endswith(".wav")]
count = 0
for m4a_file in m4a_files:
    count = count +1
    if count % 100 ==0:
        print(count)
    # Tạo đối tượng AudioSegment từ tệp M4A
    audio = AudioSegment.from_file(os.path.join(input_folder, m4a_file), format="wav")

    # Tạo tên tệp MP3 bằng cách thay đổi phần mở rộng
    mp3_file = os.path.splitext(m4a_file)[0] + ".mp3"

    # Lưu đối tượng AudioSegment dưới dạng tệp MP
    audio.export(os.path.join(output_folder, mp3_file), format="mp3")

print("Chuyển đổi hoàn thành.")