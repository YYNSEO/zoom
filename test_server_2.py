import socket
import cv2
import numpy
from queue import Queue
from _thread import *
import mysql.connector

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
        insert_query = "INSERT INTO date (YEAR) VALUES (%s)"
        cursor.execute(insert_query, (data,))
        conn.commit()
        cursor.close()
    except mysql.connector.Error as e:
        print(f"Database operation failed: {e}")
    finally:
        if conn is not None and conn.is_connected():
            conn.close()

def threaded(client_socket, addr, queue):
    print("connected by :", addr[0], ':', addr[1])
    while True:
        try:
            data = client_socket.recv(1024)
            dataSplit = data.decode().split(":")
            if dataSplit[0] == "1":
                print(dataSplit[0])
                # 데이터베이스에 값을 삽입하는 부분
                insert_data_to_table(dataSplit[1])
                pass
            print(dataSplit)
            stringData = queue.get()

            client_socket.send(str(len(stringData)).ljust(16).encode())
            client_socket.send(stringData)

        except:
            print('Disconnected by ' + addr[0], ':', addr[1])
            break
    client_socket.close()

def webcam(queue):
    global count
    capture = cv2.VideoCapture(0)

    while True:
        ret, frame = capture.read()
        if not ret:
            continue
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()
        queue.put(stringData)
        cv2.imshow('server', frame)

        key = cv2.waitKey(1)
        if key == 27:
            break

HOST = '192.168.31.87'
PORT = 9999
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print('server start')
start_new_thread(webcam, (enclosure_queue,))
while True:
    print("wait")
    client_socket, addr = server_socket.accept()
    start_new_thread(threaded, (client_socket, addr, enclosure_queue,))

server_socket.close()