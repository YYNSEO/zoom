import cv2
import socket
import struct
import pickle

HOST = '192.168.31.87'
PORT = 9999

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 프레임을 서버로 전송
    data = pickle.dumps(frame)
    message_size = struct.pack("L", len(data))  # 64비트
    client_socket.sendall(message_size + data)

    # 서버로부터 프레임을 받음
    data = b""
    payload_size = struct.calcsize("L")
    while len(data) < payload_size:
        data += client_socket.recv(4096)
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("L", packed_msg_size)[0]

    while len(data) < msg_size:
        data += client_socket.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]

    # 받은 프레임을 디코드하고 화면에 표시
    frame = pickle.loads(frame_data)
    cv2.imshow('Received', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
client_socket.close()
