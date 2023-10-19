
''' CẮT AUDIO
'''
print("CẮT AUDIO")
import os
from pydub import AudioSegment
import re


# Đọc thông tin từ tệp SRT
def read_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    segments = []
    current_segment = {'start': '', 'end': '', 'text': ''}

    for line in lines:
        line = line.strip()
        if re.match(r'\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+', line):
            if current_segment['start'] != '':
                segments.append(current_segment)
            current_segment = {'start': line.split(' --> ')[0], 'end': line.split(' --> ')[1], 'text': ''}
        elif line:
            current_segment['text'] += ' ' + line

    if current_segment['start'] != '':
        segments.append(current_segment)

    return segments


# Cắt và lưu các đoạn âm thanh
def cut_audio(audio_file, segments, output_folder, idx):
    audio = AudioSegment.from_file(audio_file)
    for segment_idx, segment in enumerate(segments):
        start_time = segment['start']
        end_time = segment['end']
        start_ms = (int(start_time.split(':')[0]) * 3600 +
                    int(start_time.split(':')[1]) * 60 +
                    float(start_time.split(':')[2].replace(',', '.'))) * 1000
        end_ms = (int(end_time.split(':')[0]) * 3600 +
                  int(end_time.split(':')[1]) * 60 +
                  float(end_time.split(':')[2].replace(',', '.'))) * 1000
        segment_audio = audio[start_ms:end_ms]
        output_path = os.path.join(output_folder, f'{idx + segment_idx + 1}.mp3')  # Đặt tên tệp đầu ra
        segment_audio.export(output_path, format='mp3')


# Thư mục chứa các tệp mp3 và srt
input_folder = "/mnt/g/download/Audio_Tung_Vits" # Đường dẫn thư mục chứa các tệp mp3 và srt
output_folder = "/mnt/g/download/Audio_Tung_Vits/data"  # Đường dẫn thư mục cho các tệp mp3 cắt
os.makedirs(output_folder, exist_ok=True)

# Biến đếm số thứ tự của tệp âm thanh đầu ra
output_file_count = 0

# Lặp qua từng tệp mp3 và cắt theo tệp srt tương ứng
for filename in os.listdir(input_folder):
    if filename.endswith('.mp3'):
        mp3_path = os.path.join(input_folder, filename)
        srt_path = os.path.join(input_folder, filename.replace('.mp3', '.srt'))

        if os.path.exists(srt_path):
            srt_segments = read_srt(srt_path)
            cut_audio(mp3_path, srt_segments, output_folder, output_file_count)
            output_file_count += len(srt_segments)

print("Đã cắt và lưu các tệp mp3 thành công.")

# '''CHUẨN HÓA SRT
# '''
# import os
#
#
# def load_dictionary(file_path):
#     dictionary = {}
#     with open(file_path, "r", encoding="utf-8") as file:
#         for line in file:
#             old_word, new_word = line.strip().split("|")
#             dictionary[old_word] = new_word
#     return dictionary
#
#
# def replace_words_in_text(text, dictionary):
#     pattern = r'\b(?!0)\d+\b'
#     numbers = re.findall(pattern, text)
#     numbers.sort(key=len, reverse=True)
#
#     # Thay thế số bằng chữ
#     for num in numbers:
#         num_words = n2w_large_number(num)
#         text = text.replace(num, num_words)
#     for old_word, new_word in dictionary.items():
#         text = text.replace(old_word, new_word)
#     text = text.replace('.', " chấm ")
#     text = text.replace(' b ', ' bê ')
#     text = text.replace(' c ', ' xê ')
#     text = text.replace(' d ', ' đê ')
#     text = text.replace('-', ' ')
#     text = text.replace("'", ' ')
#     text = text.replace('"', ' ')
#     text = text.replace('?', ' ')
#     text = text.replace('!', ' ')
#     text = text.replace(';', ' ')
#     text = text.replace(':', ' ')
#     text = text.replace('  ', ' ')
#     text = text.replace('  ', ' ')
#     text = text.replace('  ', ' ')
#     return text
#
#
# def process_directory(input_directory, output_directory, dictionary):
#     for filename in os.listdir(input_directory):
#         if filename.endswith(".srt"):
#             srt_file = os.path.join(input_directory, filename)
#             output_file = os.path.join(output_directory, filename)
#
#             with open(srt_file, "r", encoding="utf-8") as input_file:
#                 srt_content = input_file.read()
#
#             modified_srt_content = replace_words_in_text(srt_content, dictionary)
#
#             with open(output_file, "w", encoding="utf-8") as output_file:
#                 output_file.write(modified_srt_content)
#
#             print(f"Processed {filename}")
#
#
#
# dictionary_file = "dict.txt"
# input_directory = meger
# output_directory = meger
#
# dictionary = load_dictionary(dictionary_file)
# process_directory(input_directory, output_directory, dictionary)
#
# print("Chương trình đã hoàn thành!")


'''CẮT SRT
'''
def process_srt_line(line):
    return line.strip().lstrip(" ")

def split_srt_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_file_counter = 1  # Khởi tạo số thứ tự cho các tệp văn bản đầu ra

    for filename in os.listdir(input_folder):
        if filename.endswith(".srt"):
            input_path = os.path.join(input_folder, filename)
            with open(input_path, 'r', encoding='utf-8') as input_file:
                lines = input_file.readlines()

            current_line = ""

            for line in lines:
                processed_line = process_srt_line(line)
                if processed_line:
                    current_line = processed_line
                elif current_line:
                    output_filename = f"{output_file_counter}.txt"
                    output_path = os.path.join(output_folder, output_filename)
                    with open(output_path, 'w', encoding='utf-8') as output_file:
                        output_file.write(current_line.lower())
                    current_line = ""
                    output_file_counter += 1

            if current_line:
                output_filename = f"{output_file_counter}.txt"
                output_path = os.path.join(output_folder, output_filename)
                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(current_line)
                output_file_counter += 1

    print("Processing complete.")



split_srt_files(input_folder, output_folder)
''' NỐI SRT
'''
import os

def concatenate_text_files_in_directory(directory, output_file):
    with open(output_file, "w", encoding="utf-8") as output:
        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                file_path = os.path.join(directory, filename)
                with open(file_path, "r", encoding="utf-8") as input_file:
                    output.write(input_file.read())
                # Thêm khoảng trống hoặc dấu xuống dòng giữa các tệp nếu bạn muốn
                output.write(filename+"\n")


input_directory = data  # Thay đổi đường dẫn tới thư mục chứa các tệp .txt
output_file = os.path.join(meger, "tong_hop.txt")
