import socket
import cv2 #cv2 필터 제공 함수
import numpy # 영상 풀어 헤치기 위한 함수
from queue import Queue
from _thread import *
enclosure_queue = Queue() #큐라는 함수의 대기줄

def threaded(clinet_socket, addr, queue):
    print('Connected by : ', addr[0], ":", addr[1])
    while True:
        try:
            data = clinet_socket.recv(1024) # 클라이언트가 보낸 메세지 1을 받아옴
            if not data:
                print('Disconnencted by' + addr[0] , ":", addr[1])
                break
            stringData = queue.get() # 데이터 저장
            clinet_socket.send(str(len(stringData)).ljust(16).encode()) #ljust -> 왼쪽부터 정렬 16글자 형태로 맞춰라 encode 번역해서 보냄 <-> decode 번역해서 가져옴
            clinet_socket.send(stringData) # 실제 데이터를 보낸다.
        except ConnectionResetError as e:
            print('Disconnencted by' + addr[0] , ":", addr[1])
            break
    clinet_socket.close()
counnt = 0
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