import socketserver
import cv2
import numpy as np

class ClientInfo:
    def __init__(self, request, client_address):
        self.request = request
        self.client_address = client_address

class MyTCPHandler(socketserver.BaseRequestHandler):
    client_infos = []

    def handle(self):
        client_info = ClientInfo(self.request, self.client_address)
        self.client_infos.append(client_info)
        print(f"Accepted connection from {self.client_address}")
        video_window_name = f"Video from {self.client_address}"
        cv2.namedWindow(video_window_name)

        try:
            while True:
                data = self.request.recv(126333)
                if not data:
                    break
                if data.startswith(b'IMG:'):
                    frame_data = data[4:]
                    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                    # Process image or send it to other clients
                    cv2.imshow(video_window_name, frame)
                    cv2.waitKey(1)
                    self.broadcast_image(data, client_info)
                    self.send_image_to_clients(data, client_info)

        finally:
            self.client_infos.remove(client_info)
            print(f"Connection from {self.client_address} closed.")

    def broadcast_image(self, data, sender_info):
        """받은 영상 데이터를 다른 모든 클라이언트에게 전송"""
        for client_info in self.client_infos:
            if client_info.request != sender_info.request:  # 발신자를 제외한 모든 클라이언트에게 전송
                client_info.request.sendall(data)

    def send_image_to_clients(self, data, sender_info):
        for client_info in self.client_infos:
            # 모든 클라이언트에게 데이터를 전송합니다.
            client_info.request.sendall(data)
class MyTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

def start_server():
    HOST, PORT = '192.168.31.87', 9999
    server = MyTCPServer((HOST, PORT), MyTCPHandler)
    print("Server listening on port 9999...")
    server.serve_forever()

if __name__ == "__main__":
    start_server()
