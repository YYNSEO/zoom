import socket
import struct
import pickle
import cv2
import threading

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, address):
        super().__init__()
        self.client_socket = client_socket
        self.address = address

    def run(self):
        print(f"클라이언트 연결: {self.address}")
        data_buffer = b""
        data_size = struct.calcsize("L")

        try:
            while True:
                while len(data_buffer) < data_size:
                    data_buffer += self.client_socket.recv(4096)

                packed_data_size = data_buffer[:data_size]
                data_buffer = data_buffer[data_size:]

                frame_size = struct.unpack(">L", packed_data_size)[0]

                while len(data_buffer) < frame_size:
                    data_buffer += self.client_socket.recv(4096)

                frame_data = data_buffer[:frame_size]
                data_buffer = data_buffer[frame_size:]

                frame = pickle.loads(frame_data)
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                cv2.imshow('Frame', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
        finally:
            self.client_socket.close()
            print(f"클라이언트 연결 종료: {self.address}")

class VideoServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.client_handlers = []

    def start(self):
        self.server_socket.listen(10)
        print('클라이언트 연결 대기')

        try:
            while True:
                client_socket, address = self.server_socket.accept()

                client_handler = ClientHandler(client_socket, address)
                client_handler.start()

                self.client_handlers.append(client_handler)
        except KeyboardInterrupt:
            print("서버 종료")
            for client_handler in self.client_handlers:
                client_handler.join()
                client_handler.client_socket.close()

            self.server_socket.close()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    ip = "192.168.31.87"
    port = 9999

    server = VideoServer(ip, port)
    server.start()
