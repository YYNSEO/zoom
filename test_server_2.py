import socketserver
import cv2
import numpy as np
from queue import Queue
import threading

# 연결된 모든 클라이언트의 소켓을 보관할 리스트
clients = []

class ClientInfo:
    def __init__(self, client_address, video_window_name):
        self.client_address = client_address
        self.video_window_name = video_window_name

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"Accepted connection from {self.client_address}")
        clients.append(self.request)  # 새 클라이언트의 소켓을 clients 리스트에 추가

        try:
            while True:
                data = self.request.recv(1024)
                if not data:
                    break

                # 데이터가 이미지인 경우 모든 클라이언트에게 전송
                if data[:4] == b'IMG:':
                    frame_data = data[4:]
                    for client in clients:
                        if client != self.request:  # 현재 클라이언트를 제외한 모든 클라이언트에게 전송
                            client.sendall(b'IMG:' + frame_data)

        except Exception as e:
            print(f"Error handling client {self.client_address}: {e}")
        finally:
            print(f"Connection from {self.client_address} closed.")
            clients.remove(self.request)  # 연결이 끊긴 클라이언트를 clients 리스트에서 제거

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def start_server():
    HOST, PORT = '192.168.31.87', 9999
    server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
    print("Server listening on port 9999...")
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("Server started on thread:", server_thread.name)

if __name__ == "__main__":
    start_server()
