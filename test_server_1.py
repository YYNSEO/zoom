import socketserver
import cv2
import numpy as np
import threading

class ClientInfo:
    def __init__(self, client_address, video_window_name):
        self.client_address = client_address
        self.video_window_name = video_window_name

class MyTCPHandler(socketserver.BaseRequestHandler):
    client_infos = []

    @classmethod
    def find_client_info(cls, client_address):
        for client_info in cls.client_infos:
            if client_info.client_address == client_address:
                return client_info
        return None

    def handle(self):
        print(f"Accepted connection from {self.client_address}")

        video_window_name = f"Video from {self.client_address}"
        cv2.namedWindow(video_window_name)

        client_info = ClientInfo(self.client_address, video_window_name)
        self.client_infos.append(client_info)

        try:
            while True:
                data = self.request.recv(126333)
                if not data:
                    break
                if data[:4] == b'MSG:':
                    message = data[4:].decode()
                    print(f"Received message from {self.client_address}: {message}")
                    # Process message or send it to other clients
                    for client_info in self.client_infos:
                        if client_info.client_address != self.client_address:
                            client_info.request.sendall(data)

                elif data[:4] == b'IMG:':
                    frame_data = data[4:]
                    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                    # Process image or send it to other clients

                    client_info.request.sendall(data[4:])


        except Exception as e:
            print(f"Error handling client {self.client_address}: {e}")
        finally:
            print(f"Connection from {self.client_address} closed.")
            cv2.destroyWindow(video_window_name)
            self.client_infos.remove(client_info)

class MyTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

def start_server():
    HOST, PORT = '192.168.31.87', 9999
    server = MyTCPServer((HOST, PORT), MyTCPHandler)
    print("Server listening on port 9999...")
    server.serve_forever()

if __name__ == "__main__":
    start_server()