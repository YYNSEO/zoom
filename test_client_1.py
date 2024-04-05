import cv2
import numpy as np
import socket
import threading
import tkinter
from PIL import Image, ImageTk

class App:
    def __init__(self, master):
        self.master = master
        self.master.geometry("640x480")
        self.master.title("Video Client")
        self.canvas = tkinter.Canvas(self.master, width=640, height=480)
        self.canvas.pack()
        self.photo = None  # PhotoImage 객체를 유지하기 위한 속성 추가

def send_video_to_server(client_socket):
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't capture frame.")
            break

        # 프레임 크기를 변경하여 낮은 해상도로 설정
        width = 320  # 변경할 너비
        height = 240  # 변경할 높이
        frame = cv2.resize(frame, (width, height))

        # 프레임을 JPEG 형식으로 인코딩하여 전송
        encoded_frame = cv2.imencode('.jpg', frame)[1].tobytes()
        client_socket.sendall(b'IMG:' + encoded_frame)

def receive_video_from_server(client_socket, app):
    while True:
        try:
            data = client_socket.recv(65536)
            if not data:
                break

            if data[:4] == b'IMG:':
                frame_data = data[4:]
                frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                app.photo = ImageTk.PhotoImage(image=image)  # photo를 App 클래스의 속성으로 유지
                app.canvas.create_image(0, 0, anchor=tkinter.NW, image=app.photo)
        except Exception as e:
            print("Error receiving video:", e)
            break

def main():
    HOST = '192.168.31.87'  # 서버의 IP 주소
    PORT = 9999  # 서버의 포트 번호

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    root = tkinter.Tk()
    app = App(root)  # App 클래스의 인스턴스 생성
    send_thread = threading.Thread(target=send_video_to_server, args=(client_socket,))
    send_thread.start()

    receive_thread = threading.Thread(target=receive_video_from_server, args=(client_socket, app))
    receive_thread.start()

    root.mainloop()

    send_thread.join()
    receive_thread.join()

    client_socket.close()

if __name__ == "__main__":
    main()
