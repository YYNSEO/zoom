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
                data = self.request.recv(200000)
                print(len(data))
                if not data:
                    break
                if data.startswith(b'IMG:'):
                    # print(self.client_infos)
                    frame_data = data[4:]
                    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                    # Process image or send it to other clients
                    cv2.imshow(video_window_name, frame)
                    cv2.waitKey(1)
                    self.send_image_to_clients(data, client_info)

        finally:
            self.client_infos.remove(client_info)
            print(f"Connection from {self.client_address} closed.")

    def send_image_to_clients(self, data, sender_info):
        connected_clients = len(self.client_infos)
        print(connected_clients)
        for client_info in self.client_infos:
            # 모든 클라이언트에게 데이터를 전송합니다.
            # 클라이언트 주소와 이미지 데이터를 조합하여 바이트 형식으로 전송합니다.
            message = f"{connected_clients}{client_info.client_address[0]}".encode() + data
            client_info.request.sendall(message)
class MyTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

def start_server():
    HOST, PORT = '192.168.31.87', 9999
    server = MyTCPServer((HOST, PORT), MyTCPHandler)
    print("Server listening on port 9999...")
    server.serve_forever()

if __name__ == "__main__":
    start_server()