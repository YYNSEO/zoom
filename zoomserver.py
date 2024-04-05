import socketserver
import cv2
import numpy as np
from queue import Queue
import mysql.connector
from mysql.connector import Error
import threading

enclosure_queue = Queue()

connection = mysql.connector.connect(
    host='localhost',
    user='zooms',
    password='0000',
    database='zoom'
)

def login(username):
    cursor = connection.cursor()
    try:
        insert_query = f"INSERT INTO login (date) VALUES ('{username}')"
        cursor.execute(insert_query)
        connection.commit()
        print("Inserted username:", username)
    except Error as e:
        print("Error while inserting username:", e)

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print('Connected by:', self.client_address[0], ":", self.client_address[1])
        try:
            username = self.request.recv(1024).decode()
            print("Received username:", username)
            login(username)
            while True:
                stringData = enclosure_queue.get()
                self.request.send(str(len(stringData)).ljust(16).encode())
                self.request.send(stringData)
        except ConnectionResetError as e:
            print('Disconnected by:', self.client_address[0], ":", self.client_address[1])
        finally:
            self.request.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def webcam(queue):
    capture = cv2.VideoCapture(0)
    while True:
        ret, frame = capture.read()
        if not ret:
            continue
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = np.array(imgencode)
        stringData = data.tobytes()
        queue.put(stringData)
        cv2.imshow('server', frame)
        if cv2.waitKey(1) == 27:  # ESC
            break
    capture.release()
    cv2.destroyAllWindows()

def clear_queue(queue):
    while not queue.empty():
        queue.get()

if __name__ == "__main__":
    HOST, PORT = '192.168.31.87', 9999
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("Server loop running in thread:", server_thread.name)
    webcam(enclosure_queue)