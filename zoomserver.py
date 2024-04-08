import socketserver
import cv2
import numpy as np
from queue import Queue
import mysql.connector
import pickle

enclosure_queue = Queue()

def connect_to_database():
    return mysql.connector.connect(
        host="192.168.31.87",
        user="zoom",
        password="0000",
        database="zoom_db"
    )

def insert_data_to_table(data):
    conn = None
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        insert_query = "INSERT INTO pi (YEAR, name, id, pw) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, data)
        conn.commit()
        cursor.close()
    except mysql.connector.Error as e:
        print(f"Database operation failed: {e}")
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


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



        while True:
            data = self.request.recv(200000)
           # original_tuple = pickle.loads(data)
            if not data:
                break
            if data.startswith(b'IMG:'):
                print(self.client_infos)
                frame_data = data[4:]
                frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow(video_window_name, frame)
                cv2.waitKey(1)
                self.send_image_to_clients(data, client_info)
            # if len(original_tuple) == 4:
            #     insert_data_to_table(original_tuple)


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