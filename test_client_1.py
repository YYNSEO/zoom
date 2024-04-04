import socket
import cv2
import threading
import numpy as np
import tkinter




class App():
    def __init__(self, master):
        self.master = master
        self.master.geometry("872x624")  # 해상도 선언
        self.master.title("Zoom")

        self.canvas=tkinter.Canvas(self.master,width=640,height=480)
        self.canvas.pack()

        self.list=tkinter.Listbox(self.master)
        self.list.pack()

        self.chatbox=tkinter.Entry(self.master)
        self.chatbox.pack()


def send_message(client_socket):
    while True:
        try:
            message = input("Enter message: ")
            if message:
                client_socket.send(b'MSG:' + message.encode())
        except Exception as e:
            print("Error sending message:", e)
            break


def send_video(client_socket):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while cap.isOpened():
        try:
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
        except Exception as e:
            print("Error sending video:", e)
            break
    cap.release()

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.31.87', 9999))

    message_thread = threading.Thread(target=send_message, args=(client_socket,))
    video_thread = threading.Thread(target=send_video, args=(client_socket,))

    message_thread.start()
    video_thread.start()

    message_thread.join()
    video_thread.join()

    client_socket.close()

if __name__ == "__main__":
    main()
    root=tkinter.Tk()
    zoom=App(root)
    zoom.master.mainloop()