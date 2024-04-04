import cv2
import socket
import pickle
import struct
import threading

def send_frames(ip, port):
    # 카메라 또는 동영상
    capture = cv2.VideoCapture(0)

    # 프레임 크기 지정
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 가로
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 세로

    # 소켓 객체 생성
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # 서버와 연결
            client_socket.connect((ip, port))
            print(f"서버 {ip}:{port}와 연결 성공")

            # 메시지 수신
            while True:
                # 프레임 읽기
                retval, frame = capture.read()

                # imencode : 이미지(프레임) 인코딩
                retval, frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])

                # dumps : 데이터를 직렬화
                frame = pickle.dumps(frame)

                print(f"전송 프레임 크기 : {len(frame)} bytes")

                # sendall : 데이터(프레임) 전송
                client_socket.sendall(struct.pack(">L", len(frame)) + frame)

        except ConnectionRefusedError:
            print(f"서버 {ip}:{port}에 연결할 수 없습니다.")
        finally:
            # 메모리를 해제
            capture.release()

if __name__ == "__main__":
    # 서버들의 IP 주소 및 포트 번호 리스트
    servers = [("192.168.31.87", 9999)]  # 예시 서버 IP 주소 및 포트 번호

    threads = []
    for server in servers:
        thread = threading.Thread(target=send_frames, args=server)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()