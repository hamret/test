import tkinter as tk
from tkinter import messagebox
import pandas as pd
from deep_translator import GoogleTranslator

# CSV 파일 경로
file_path = 'C:\dev\Bert_project\server tester\mainfiles.csv'  # 경로 수정

# CSV 불러오기
try:
    # 인코딩을 추정하여 지정 (예: 'euc-kr', 'cp949', 'latin1' 등)
    df = pd.read_csv(file_path, encoding='euc-kr')  # 필요한 경우 다른 인코딩으로 변경
except UnicodeDecodeError as e:
    messagebox.showerror("파일 읽기 오류", f"CSV 파일을 불러올 수 없습니다.\n오류: {str(e)}")
    exit()

# 라벨이 비어있는 행만 작업 대상
df = df[df['label'].isnull()].reset_index(drop=True)

# 현재 인덱스
current_index = 0


# 저장 함수
def save_label():
    global current_index
    label = entry_label.get().strip()
    if label:
        df.loc[current_index, 'label'] = label
        entry_label.delete(0, tk.END)
        current_index += 1
        if current_index < len(df):
            show_text()
        else:
            # 데이터 저장
            df.to_csv(file_path, index=False, encoding='euc-kr')  # 동일한 인코딩으로 저장
            messagebox.showinfo('완료', '모든 데이터 라벨링이 완료되었습니다.')
            window.destroy()
    else:
        messagebox.showwarning('입력 오류', '라벨을 입력하세요.')


# 텍스트 표시 함수
def show_text():
    english_text = df.loc[current_index, 'text']
    try:
        korean_translation = GoogleTranslator(source='en', target='ko').translate(english_text)
    except Exception:
        korean_translation = "(번역 실패)"

    label_original.config(text=english_text)
    label_translated.config(text=korean_translation)


# GUI 구성
window = tk.Tk()
window.title("CSV 라벨링 툴 (영→한 번역 포함)")

frame = tk.Frame(window)
frame.pack(padx=10, pady=10)

# 제목
tk.Label(frame, text="영문 원문", font=('Arial', 12, 'bold')).grid(row=0, column=0, padx=10)
tk.Label(frame, text="한글 번역", font=('Arial', 12, 'bold')).grid(row=0, column=1, padx=10)

# 원문 및 번역 출력
label_original = tk.Label(frame, text="", wraplength=300, justify='left')
label_original.grid(row=1, column=0, padx=10, pady=5)
label_translated = tk.Label(frame, text="", wraplength=300, justify='left')
label_translated.grid(row=1, column=1, padx=10, pady=5)

# 라벨 입력창
entry_label = tk.Entry(window, width=60)
entry_label.pack(padx=10, pady=10)

# 저장 버튼
btn_save = tk.Button(window, text="라벨 저장", command=save_label)
btn_save.pack(padx=10, pady=10)

# 첫 문장 보여주기
show_text()

# GUI 실행
window.mainloop()


