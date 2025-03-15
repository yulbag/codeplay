import tkinter as tk
import cv2
from PIL import Image, ImageTk
import serial
import threading

# 시리얼 포트 설정 (아두이노가 연결된 포트로 변경)
arduino = serial.Serial('COM20', 9600)

def read_from_arduino():
    while True:
        if arduino.in_waiting > 0:
            data = arduino.readline().decode('utf-8').strip()
            print(f"Received from Arduino: {data}")
            button_label.config(text=f"Button State: {data}")

def check_presence():
    ret, frame = cap.read()
    if not ret:
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        result_label.config(text="사람이 있다")
        arduino.write(b'1')  # 아두이노에 '1' 전송
    else:
        result_label.config(text="")
        arduino.write(b'0')  # 아두이노에 '0' 전송

    # 카메라 프레임을 tkinter 창에 표시
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)
    camera_label.imgtk = imgtk
    camera_label.configure(image=imgtk)

    root.after(10, check_presence)

# 메인 윈도우 생성
root = tk.Tk()
root.title("Presence Checker")

# 결과를 표시할 레이블 생성
result_label = tk.Label(root, text="")
result_label.pack(pady=10)

# 버튼 상태를 표시할 레이블 생성
button_label = tk.Label(root, text="Button State: ---")
button_label.pack(pady=10)

# 카메라 프레임을 표시할 레이블 생성
camera_label = tk.Label(root)
camera_label.pack()

# OpenCV를 사용하여 카메라 초기화
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 사람 존재 여부를 주기적으로 확인
root.after(10, check_presence)

# 아두이노에서 데이터를 읽는 스레드 시작
arduino_thread = threading.Thread(target=read_from_arduino)
arduino_thread.daemon = True
arduino_thread.start()

# 메인 루프 실행
root.mainloop()

# 프로그램 종료 시 카메라 해제
cap.release()
cv2.destroyAllWindows()
arduino.close()