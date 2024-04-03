import socket
import cv2 #cv2 필터 제공 함수
import numpy # 영상 풀어 헤치기 위한 함수
from queue import Queue
from _thread import *
import mysql.connector
from mysql.connector import Error
enclosure_queue = Queue() #큐라는 함수의 대기줄

connection = mysql.connector.connect(
    host='localhost',  # 데이터베이스 호스트
    user='zooms',  # 데이터베이스 사용자 이름
    password='0000',  # 데이터베이스 패스워드
    database='zoom'
)
try:
    # 데이터베이스 연결


    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("MySQL 서버 버전:", db_Info)
        cursor = connection.cursor()

        # example_db 데이터베이스 사용 설정

        # 테이블 생성 SQL 명령문
        create_table_query = """
        CREATE TABLE IF NOT EXISTS login (
            date INT VARCHAR(255) NOT NULL

        )
        """
        cursor.execute(create_table_query)
        print("users 테이블이 생성되었습니다.")

except Error as e:
    print("Error while connecting to MySQL", e)

finally:
    # 데이터베이스 연결 종료
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
def threaded(client_socket, addr, queue):
    print('Connected by : ', addr[0], ":", addr[1])
    login(client_socket)
    while True:
        try:
            data = client_socket.recv(1024) # 클라이언트가 보낸 메세지 1을 받아옴
            if not data:
                print('Disconnencted by' + addr[0] , ":", addr[1])
                break
            stringData = queue.get() # 데이터 저장
            client_socket.send(str(len(stringData)).ljust(16).encode()) #ljust -> 왼쪽부터 정렬 16글자 형태로 맞춰라 encode 번역해서 보냄 <-> decode 번역해서 가져옴
            client_socket.send(stringData) # 실제 데이터를 보낸다.
        except ConnectionResetError as e:
            print('Disconnencted by' + addr[0] , ":", addr[1])
            break
    client_socket.close()
counnt = 0
def login(self):
    # 커서 생성
    cursor = connection.cursor()

    username = self.request.recv(1024)
    username = username.decode().strip()

    # 사용자 이름을 데이터베이스에 저장
    insert_query = f"INSERT INTO login (date) VALUES ('{username}')"
    cursor.execute(insert_query)
    connection.commit()



def webcam(queue):
    global  counnt
    video_path = 'v.mp4'
    capture = cv2.VideoCapture(0)
    # capture.set(cv2.CAP_PROP_FRAME_WIDTH,1320)
    # capture.set(cv2.CAP_PROP_FRAME_HEIGHT,761)
    while True:
        ret, frame = capture.read()
        if ret == False:
            continue
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()
        if counnt == 0:
            print(stringData)
        counnt=1
        queue.put(stringData) # 데이터 출력
        cv2.imshow('server', frame)
        key = cv2.waitKey(1)
        if key == 27:  # 27번 esc 종료 버튼
            break


HOST = '192.168.31.87'
PORT = 9999
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #reuseaddr는 1로 걸리게??
server_socket.bind((HOST, PORT))
server_socket.listen() # client가 server에 접속되었는지 확인하는 것


def clear_queue(queue):
    while not queue.empty():
        queue.get()


print('server start')
start_new_thread(webcam, (enclosure_queue,)) #웹 캠 먼저 키고
while True:
    print('wait')
    client_socket, addr = server_socket.accept() # thread를 켜서 받아준다.
    clear_queue(enclosure_queue)
    start_new_thread(threaded,(client_socket,addr, enclosure_queue,))
server_socket.close()