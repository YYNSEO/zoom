import socket
import cv2  # OpenCV

import tkinter  # Tkinter 및 GUI 관련
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import numpy as np
import threading  # Thread
import tkinter.font
from PIL import Image, ImageTk
from PIL import Image as PILImage, ImageTk

import PIL.Image, PIL.ImageTk

from tkinter import *
import webbrowser
from datetime import datetime
import pickle
import tkinter
from PIL import Image, ImageTk
import pymysql
from io import BytesIO
import random
import string
import queue
from rembg import remove

import asyncio

root = tk.Tk()
rgb = (45, 101, 246)
root.configure(bg="#%02x%02x%02x" % rgb)


result_img = 0  # 전역변수로 최종 이미지를 받도록 했다

width = 0  # ----->240402
height = 0  # ----->240402
chat_flags = 0  # ----->240402
l = 20      # 파장(wave length)
amp = 15    # 진폭(amplitude)
parlist = 0


HOST = "192.168.31.87"
PORT = 9999

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

watch = PhotoImage(file = "watch.png")

connected_clients = 0
flags=0
flag = 0
# 이미지 및 관련 변수
im = ""
im2 = ""
im3 = ""
im4 = ""
im5 = ""
ip_list = []  # IP 주소를 저장할 리스트

# 이미지 큐
image_queue = queue.Queue(maxsize=5)


def add(frame):
    #지그재그 함수
    rows, cols = frame.shape[:2]
    # 초기 매핑 배열 생성
    mapy, mapx = np.indices((rows, cols), dtype=np.float32)

    # sin, cos 함수를 적용한 변형 매핑 연산
    sinx = mapx + amp * np.sin(mapy / l)
    cosy = mapy + amp * np.cos(mapx / l)

    # 영상 매핑
    img_sinx = cv2.remap(frame, sinx, mapy, cv2.INTER_LINEAR)  # x축만 sin 곡선 적용
    img_cosy = cv2.remap(frame, mapx, cosy, cv2.INTER_LINEAR)  # y축만 cos 곡선 적용
    # x,y 축 모두 sin, cos 곡선 적용 및 외곽 영역 보정
    img_both = cv2.remap(frame, sinx, cosy, cv2.INTER_LINEAR, None, cv2.BORDER_REPLICATE)
    return img_both

def add2(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output_rgb = remove(frame_rgb)
    output_bgr = cv2.cvtColor(output_rgb, cv2.COLOR_RGB2BGR)

    return output_bgr

def add3(frame):
    rows, cols = frame.shape[:2]

    # ---① 설정 값 셋팅
    exp = 2  # 볼록, 오목 지수 (오목 : 0.1 ~ 1, 볼록 : 1.1~)
    scale = 1  # 변환 영역 크기 (0 ~ 1)

    # 매핑 배열 생성 ---②
    mapy, mapx = np.indices((rows, cols), dtype=np.float32)

    # 좌상단 기준좌표에서 -1~1로 정규화된 중심점 기준 좌표로 변경 ---③
    mapx = 2 * mapx / (cols - 1) - 1
    mapy = 2 * mapy / (rows - 1) - 1

    # 직교좌표를 극 좌표로 변환 ---④
    r, theta = cv2.cartToPolar(mapx, mapy)

    # 왜곡 영역만 중심확대/축소 지수 적용 ---⑤
    r[r < scale] = r[r < scale] ** (1 / exp)

    # 극 좌표를 직교좌표로 변환 ---⑥
    mapx, mapy = cv2.polarToCart(r, theta)

    # 중심점 기준에서 좌상단 기준으로 변경 ---⑦
    mapx = ((mapx + 1) * cols - 1) / 2
    mapy = ((mapy + 1) * rows - 1) / 2
    # 재매핑 변환
    distorted = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
    return distorted

def add4(frame):
    rows, cols = frame.shape[:2]

    # ---① 설정 값 셋팅
    exp = 2  # 볼록, 오목 지수 (오목 : 0.1 ~ 1, 볼록 : 1.1~)
    scale = 1  # 변환 영역 크기 (0 ~ 1)

    # 매핑 배열 생성 ---②
    mapy, mapx = np.indices((rows, cols), dtype=np.float32)

    # 좌상단 기준좌표에서 -1~1로 정규화된 중심점 기준 좌표로 변경 ---③
    mapx = 2 * mapx / (cols - 1) - 1
    mapy = 2 * mapy / (rows - 1) - 1

    # 직교좌표를 극 좌표로 변환 ---④
    r, theta = cv2.cartToPolar(mapx, mapy)

    # 왜곡 영역만 중심확대/축소 지수 적용 ---⑤
    r[r < scale] = r[r < scale] ** exp

    # 극 좌표를 직교좌표로 변환 ---⑥
    mapx, mapy = cv2.polarToCart(r, theta)

    # 중심점 기준에서 좌상단 기준으로 변경 ---⑦
    mapx = ((mapx + 1) * cols - 1) / 2
    mapy = ((mapy + 1) * rows - 1) / 2
    # 재매핑 변환
    distorted = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
    return distorted


def filters(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, src_bin = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU) #이진화로 바꿔줌 thresh : 임계값 maxval : 0보다 큰 값을 255로 바꿈 , 뒤에 있는 것이 효과

    contours, _ = cv2.findContours(src_bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE) # 외각선 찾기

    h, w = gray.shape[:2] #
    dst = np.zeros((h, w, 3), np.uint8) #h, w 만큼의 검은색 화면으로 channel 3만큼 생성, uint8은 양수만 표현 가능

    for i in range(len(contours)):
        c = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) # rgb 랜덤으로 주기
        cv2.drawContours(dst, contours, i, c, 1, cv2.LINE_AA) #선 그리기
    return dst


def send_message(client_socket, message,name=None):
    try:
        if message:
            if name:
                client_socket.send(b'MSG:' + f"{name}: ".encode() + message.encode() + b'END')
            else:
                client_socket.send(b'MSG:' + f"{hostname[8:]}: ".encode()+message.encode() + b'END')

    except Exception as e:
        print("Error sending message:", e)

def send_video_to_server(client_socket):
    cap = cv2.VideoCapture(0)
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error: Couldn't capture frame.")
                break

            # 프레임 크기를 변경하여 낮은 해상도로 설정
            width = 320  # 변경할 너비
            height = 240  # 변경할 높이
            frame = cv2.resize(frame, (width, height))
            if flags == 1:
                frame = hide_video(frame)
            if flags == 2:
                frame = filters(frame)
            if flags == 3:
                frame = add(frame)
            if flags == 4:
                frame = add2(frame)
            if flags == 5:
                frame = add3(frame)
            if flags == 6:
                frame = add4(frame)
            # 프레임을 JPEG 형식으로 인코딩하여 전송
            encoded_frame = cv2.imencode('.jpg', frame)[1].tobytes()
            client_socket.sendall(b'IMG:' + encoded_frame + b'END')
    except Exception as e:
        print("Error receiving video:", e)
    finally:
        cap.release()  # 캠 송출 중지

def receive_data(client_socket, self):
    global ip_list, main

    while True:
        try:
            data = client_socket.recv(50000)

            if data.startswith(b'MSG:') and data.endswith(b'END'):  # 메시지 수신
                message = data[4:-3].decode()
                self.chatlist.insert(tk.END, message)
                self.chatlist.see(tk.END)
            elif data == b'stop':  # 'stop' 메시지 수신 시 프로그램 종료
                root.destroy()
            else:  # 비디오 데이터 수신 및 처리
                ip, frame_data = extract_ip_and_frame_data(data)
                if ip is not None and frame_data is not None:
                    image = create_image_from_frame(frame_data)

                    if image is not None:  # 빈 이미지가 아닌 경우에만 처리
                        if ip == ip_address.encode():  # 내 아이피와 일치하는 경우
                            image = create_image_from_frame(frame_data, resize=True)
                            image_queue.put((0, image))
                        else:
                            if ip not in ip_list:  # 리스트에 아직 존재하지 않는 경우
                                ip_list.append(ip)  # IP 주소를 리스트에 추가합니다
                            index = ip_list.index(ip)  # IP 주소의 인덱스를 가져옵니다.
                            if index < 4:
                                image_queue.put((index + 1, image))

        except Exception as e:
            print("Error receiving data:", e)
            root.destroy()

# def receive_video(client_socket):
#     global ip_list
#     while True:
#         try:
#             data = client_socket.recv(50000)
#
#             ip, frame_data = extract_ip_and_frame_data(data)
#             if ip is not None and frame_data is not None:
#                 image = create_image_from_frame(frame_data)
#
#                 if image is not None:  # 빈 이미지가 아닌 경우에만 처리
#                     if ip == ip_address.encode():  # 내 아이피와 일치하는 경우
#                         #print(ip)
#                         image = create_image_from_frame(frame_data, resize=True)
#                         image_queue.put((0, image))
#                     else:
#                         if ip not in ip_list:  # 리스트에 아직 존재하지 않는 경우
#                             ip_list.append(ip)  # IP 주소를 리스트에 추가합니다
#                         index = ip_list.index(ip)  # IP 주소의 인덱스를 가져옵니다.
#                         if index == 0:  # 첫 번째 IP 주소인 경우
#                             image_queue.put((1, image))
#                         elif index == 1:  # 두 번째 IP 주소인 경우
#                             image_queue.put((2, image))
#                         elif index == 2:
#                             image_queue.put((3, image))
#                         elif index == 3:
#                             image_queue.put((4, image))
#
#
#         except Exception as e:
#             print("Error receiving video1:", e)
#             break
# def receive_message(client_socket, self):
#     global main
#     while True:
#         try:
#             data = client_socket.recv(50000)
#             if data.startswith(b'MSG:') and data.endswith(b'END'):
#                 message = data[4:-3].decode()
#                 self.chatlist.insert(tk.END, message)
#                 self.chatlist.see(tk.END)
#             if data == b'stop':
#                 root.destroy()
#         except Exception as e:
#             print("Error receiving message:", e)
#             root.destroy()


def update_images():
    global im, im2, im3, im4,im5
    while True:
        try:
            index, image = image_queue.get(timeout=1)  # 이미지 큐에서 이미지를 가져옴
            if index == 0:
                im = image
            elif index == 1:
                im2 = image
            elif index == 2:
                im3 = image
            elif index == 3:
                im4 = image
            elif index == 4:
                im5 = image
            image_queue.task_done()
        except queue.Empty:
            pass

def streaming(self):
    video_thread = threading.Thread(target=send_video_to_server, args=(client_socket,))
    receive_data_thread = threading.Thread(target=receive_data, args=(client_socket,self))
    update_images_thread = threading.Thread(target=update_images)

    video_thread.start()
    receive_data_thread.start()
    update_images_thread.start()

    video_thread.join()
    receive_data_thread.join()
    update_images_thread.join()

    client_socket.close()

def extract_ip_and_frame_data(data):
    ip_start_index = data.find(b'IMG:')
    end_index = data.find(b'END')

    if ip_start_index != -1 and end_index != -1:
        ip = data[:ip_start_index]  # IP 주소를 추출합니다.
        #print("IP:", ip)

        frame_data = data[ip_start_index + 4:end_index]  # 프레임 데이터를 추출합니다.
        # print("Frame data:", frame_data)

        return ip, frame_data
    return None, None
def create_image_from_frame(frame_data, resize=False):
    # 이미지 데이터가 비어 있는지 확인
    if not frame_data:
        print("Frame data is empty.")
        return None

    try:
        # 이미지 디코딩 시도
        frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if resize:

            # 이미지 크기를 1320x521로 조정
            frame = cv2.resize(frame, (640, 420))
        else:
            # 이미지 크기를 320x240으로 유지
            frame = cv2.resize(frame, (320, 240))

        return PIL.Image.fromarray(frame)
    except Exception as e:
        print("Error decoding frame data:", e)
        return None

def change():
    global flags
    if flags == 0:
        flags = 1
    else:
        flags = 0

def hide_video(frame):
    #가운데 라벨 어떻게 띄우는지 모르겠다.
    # self.labels = tkinter.Label(self.video_canvas, fg="white", text="이윤서", width=100, height=50)
    # self.labels.pack()
    black_screen = np.zeros_like(frame)
    black_screen[:] = (0, 0, 0)  # 모든 픽셀을 검정색으로 채움
    return black_screen


def flagschange():
    global flags
    flags=2

def flagchange():
    global flags
    flags=3

def flagchange2():
    global flags
    flags=4
def flagchange3():
    global flags
    flags=5
def flagchange4():
    global flags
    flags=6
def flagchange5():
    global flags
    flags=0

class App:
    def __init__(self, master):
        self.master = master
        self.master.geometry("872x624")  # 해상도 선언
        self.master.title("Zoom")
        # 로고
        self.labelA = tkinter.Label(self.master, border=0, borderwidth=0, highlightthickness=0)
        self.labelA.pack(pady=100)
        # 버튼감싸고있는 라벨
        self.labelB = tkinter.Label(self.master, bg="#%02x%02x%02x" % rgb, border=0, borderwidth=0,
                                    highlightthickness=0)
        self.labelB.pack()

        # 버튼
        self.par = tkinter.Button(self.labelB, border=0, text="회의 참가",
                                  command=self.join_s, borderwidth=0,highlightthickness=0,
                                  relief="flat", compound="none", padx=30, pady=30,takefocus=False)
       # self.par.bind("<Enter>", self.on_1)
        # self.par.bind("<Leave>", self.leave_1)
        self.par.pack(padx=35, pady=30)

        self.join = tkinter.Button(self.labelB, border=0, text="가입", command=self.show_signup_frame,
                                   borderwidth=0, highlightthickness=0, relief="flat", compound="none")
        # self.join.bind("<Enter>", self.on_2)
        # self.join.bind("<Leave>", self.leave_2)
        self.join.pack(padx=20)

        self.login = tkinter.Button(self.labelB, border=0, text="로그인", command=self.show_login_frame,
                                    borderwidth=0, highlightthickness=0, relief="flat", compound="none")
        # self.login.bind("<Enter>", self.on_3)
        # self.login.bind("<Leave>", self.leave_3)
        self.login.pack(padx=35, pady=30)

        self.flags = 0  # 캔버스 업데이트를 위한 쓰레드 시작
        self.check_par = True
        self.get_name = ""
        self.per = True
        self.get_image_from_db()
        self.meeting_id = ""
        self.meeting_pw = ""
        self.case = True
        self.case_2 = True
        #self.join_entry_id = ""
        #self.join_entry_pw = ""

    def get_image_from_db(self):
        try:
            conn = pymysql.connect(
                host='192.168.31.87',
                user='zoom',
                password='0000',
                db='zoom_db',
            )
            cursor = conn.cursor()

            # 이미지 데이터 가져오기
            cursor.execute("SELECT image FROM images WHERE id IN (%s, %s, %s, %s, %s)", (1, 2, 3, 4, 5))
            images_data = cursor.fetchall()

            # 이미지 데이터만 추출해서 사용
            image_data_1 = images_data[0][0]
            image_data_2 = images_data[1][0]
            image_data_3 = images_data[2][0]
            image_data_4 = images_data[3][0]
            image_data_5 = images_data[4][0]
            # 첫 번째 이미지를 사용
            image_1 = Image.open(BytesIO(image_data_1))
            photo_1 = ImageTk.PhotoImage(image_1)
            self.labelA.config(image=photo_1)
            self.labelA.image = photo_1


            # 두 번째 이미지를 사용
            image_2 = Image.open(BytesIO(image_data_2))
            photo_2 = ImageTk.PhotoImage(image_2)
            self.labelB.config(image=photo_2)
            self.labelB.image = photo_2
            # 세 번째 이미지를 사용
            image_3 = Image.open(BytesIO(image_data_3))
            photo_3 = ImageTk.PhotoImage(image_3)
            self.par.config(image=photo_3)
            self.par.image = photo_3

            image_4 = Image.open(BytesIO(image_data_4))
            photo_4 = ImageTk.PhotoImage(image_4)
            self.login.config(image=photo_4)
            self.login.image = photo_4

            image_5 = Image.open(BytesIO(image_data_5))
            photo_5 = ImageTk.PhotoImage(image_5)
            self.join.config(image=photo_5)
            self.join.image = photo_5

        except pymysql.Error as e:
            print("데이터베이스 오류:", e)

        finally:
            if conn:
                conn.close()


    def open_url(self, event):
        webbrowser.open("https://zoom.us/web/sso/login?en=signin#/sso")

    def open_url_2(self, event):
        webbrowser.open(
            "https://appleid.apple.com/auth/authorize?response_type=code&client_id=us.zoom.videomeetings.appleidsign&redirect_uri=https%3A%2F%2Fus05web.zoom.us%2Fapple%2Foauth&scope=name%20email&response_mode=form_post&state=clRibkJISVdRSG1iczZMby1XSWVGQSxjbGllbnRfYXBwbGVfc2lnbmlu&_x_zm_rtaid=ClaAyojPTzWd6b7eqyTe7w.1712042208685.4be2f03db44f2681ccf5a5022bef0d6b&_x_zm_rhtaid=725")

    def open_url_3(self, event):
        webbrowser.open(
            "https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?response_type=code&access_type=offline&client_id=849883241272-ed6lnodi1grnoomiuknqkq2rbvd2udku.apps.googleusercontent.com&prompt=consent&scope=profile%20email&redirect_uri=https%3A%2F%2Fzoom.us%2Fgoogle%2Foauth&state=clRibkJISVdRSG1iczZMby1XSWVGQSxjbGllbnRfZ29vZ2xlX2xvZ2lu&_x_zm_rtaid=ClaAyojPTzWd6b7eqyTe7w.1712042208685.4be2f03db44f2681ccf5a5022bef0d6b&_x_zm_rhtaid=725&service=lso&o2v=2&theme=mn&ddm=0&flowName=GeneralOAuthFlow")

    def open_url_4(self, event):
        webbrowser.open(
            "https://www.facebook.com/login.php?skip_api_login=1&api_key=113289095462482&kid_directed_site=0&app_id=113289095462482&signed_next=1&next=https%3A%2F%2Fwww.facebook.com%2Fv18.0%2Fdialog%2Foauth%3Fresponse_type%3Dcode%26client_id%3D113289095462482%26scope%3Demail%252Cpublic_profile%26redirect_uri%3Dhttps%253A%252F%252Fzoom.us%252Ffacebook%252Foauth%26state%3DclRibkJISVdRSG1iczZMby1XSWVGQSxjbGllbnRfZmFjZWJvb2tfbG9naW4%26_x_zm_rtaid%3DClaAyojPTzWd6b7eqyTe7w.1712042208685.4be2f03db44f2681ccf5a5022bef0d6b%26_x_zm_rhtaid%3D725%26ret%3Dlogin%26fbapp_pres%3D0%26logger_id%3Dcd5995e6-9f6f-4cfa-80ca-b67c62535d9a%26tp%3Dunspecified&cancel_url=https%3A%2F%2Fzoom.us%2Ffacebook%2Foauth%3Ferror%3Daccess_denied%26error_code%3D200%26error_description%3DPermissions%2Berror%26error_reason%3Duser_denied%26state%3DclRibkJISVdRSG1iczZMby1XSWVGQSxjbGllbnRfZmFjZWJvb2tfbG9naW4%23_%3D_&display=page&locale=ko_KR&pl_dbl=0")

    def show_signup_frame(self):  # 가입 페이지

        self.labelA.pack_forget()  # 로고 이미지 라벨
        self.labelB.pack_forget()  # 버튼들을 담고 있는 라벨
        # 버튼들을 개별적으로 숨깁니다.
        self.par.pack_forget()
        self.join.pack_forget()
        self.login.pack_forget()

        # 새로운 프레임(가입) 생성
        self.signup_frame = tk.Frame(self.master, bg="white")
        self.signup_frame.pack(fill="both", expand=True)

        # 이미지 넣기
        self.participate_image_label = tk.Label(self.signup_frame, border=0)
        self.participate_image_label.place(x=30, rely=1.0, y=-100, anchor="sw")

        # 연령 인증 라벨 추가
        age_verification_font = tkinter.font.Font(family="Helvetica", size=17, weight="bold")  # 폰트 설정
        self.age_verification_label = tk.Label(self.signup_frame, text="연령 인증", bg="white", font=age_verification_font)
        self.age_verification_label.place(x=30 + 350, y=20, anchor="nw")

        # 출생 연도를 확인하세요 라벨 추가
        check_bitrh_label = tkinter.font.Font(size=11)
        self.check_birth_label = tk.Label(self.signup_frame, text="출생 연도를 확인하세요. 이 데이터는 저장되지 않습니다.", bg="white",
                                          font=check_bitrh_label)
        self.check_birth_label.place(x=630, y=230, anchor="center")

        # (출생연도)엔트리 생성
        style = ttk.Style()
        style.configure("TEntry", borderwidth=2, relief="flat", background="#ffffff")
        vcmd = self.master.register(self.validate)
        self.entry = ttk.Entry(self.signup_frame, width=48, style="TEntry", validate="key",
                               validatecommand=(vcmd, '%P'))
        self.entry.configure(font=("", 12))
        self.entry.place(x=630, y=275, anchor="center")

        # 계속 버튼
        self.continue_button = tk.Button(self.signup_frame, text="계속", command=self.contract_and_start)
        self.continue_button.configure(font=("", 12, "bold"), width=39, height=2, bg="#f1f4f6", fg="#7d858e", border=0,
                                       activebackground="#3f48cc", activeforeground="white")
        self.continue_button.place(x=630, y=325, anchor="center")

        # participate_back 이미지 불러오기 및 PhotoImage 객체 생성
        self.participate_back_image_label = tk.Label(self.signup_frame, border=0)
        self.participate_back_image_label.place(x=10, rely=1.0, y=-10, anchor="sw")
        self.participate_back_image_label.bind("<Button-1>", self.go_back)

        # 로그인 화면으로 이동하는 버튼 옆에 있는 이미지
        self.already_account_label = tk.Label(self.signup_frame, border=0)
        self.already_account_label.place(x=640, rely=1.0, y=-10, anchor="sw")

        # 로그인 화면으로 이동하는 버튼
        self.go_to_login_label = tk.Label(self.signup_frame, border=0)
        self.go_to_login_label.place(x=800, rely=1.0, y=-19, anchor="sw")
        self.go_to_login_label.bind("<Button-1>", self.go_login)

        # 시간/날짜 업데이트 시작
        self.get_image_from_db2()

    def validate(self, new_text):
        if new_text.isdigit() or new_text == "":
            return len(new_text) <= 4
        else:
            return False


    def get_image_from_db2(self):
        try:
            conn = pymysql.connect(
                host='192.168.31.87',
                user='zoom',
                password='0000',
                db='zoom_db',
            )
            cursor = conn.cursor()

            # 이미지 데이터 가져오기
            cursor.execute("SELECT image FROM imagess WHERE id IN (%s,%s,%s,%s)", (1, 2, 3, 4,))
            images_data = cursor.fetchall()

            # 이미지 데이터만 추출해서 사용
            image_data_1 = images_data[0][0]
            image_data_2 = images_data[1][0]
            image_data_3 = images_data[2][0]
            image_data_4 = images_data[3][0]
            # 첫 번째 이미지를 사용
            image_1 = Image.open(BytesIO(image_data_1))
            photo_1 = ImageTk.PhotoImage(image_1)
            self.participate_image_label.config(image=photo_1)
            self.participate_image_label.image = photo_1

            image_2 = Image.open(BytesIO(image_data_2))
            photo_2 = ImageTk.PhotoImage(image_2)
            self.participate_back_image_label.config(image=photo_2)
            self.participate_back_image_label.image = photo_2

            image_3 = Image.open(BytesIO(image_data_3))
            photo_3 = ImageTk.PhotoImage(image_3)
            self.already_account_label.config(image=photo_3)
            self.already_account_label.image = photo_3

            image_4 = Image.open(BytesIO(image_data_4))
            photo_4 = ImageTk.PhotoImage(image_4)
            self.go_to_login_label.config(image=photo_4)
            self.go_to_login_label.image = photo_4

        except pymysql.Error as e:
            print("데이터베이스 오류:", e)

        finally:
            if conn:
                conn.close()



    def contract_and_start(self):  # 가입페이지 두번째
        # 오버레이 넣기
        # self.overlay = tk.Toplevel(self.master, bg="black")
        # self.overlay.overrideredirect(True)
        # self.overlay.geometry("872x624+48+0")
        # self.overlay.attributes('-alpha', 0.4)

        input_value = self.entry.get()
        if not input_value.isdigit():
            messagebox.showerror("Error", "유효한 출생 연도를 입력하세요.")
            return
        input_year = int(input_value)
        if input_year < 1903 or input_year > 2024:
            messagebox.showerror("Error", "유효한 출생 연도를 입력하세요.")
            return
        if len(input_value) != 4:
            messagebox.showerror("Error", "유효한 출생 연도를 입력하세요.")
            return

        # 이전 화면 안보이게
        self.signup_frame.pack_forget()

        # 새로운 프레임 생성(뒤)
        self.signup_frame_2 = tk.Frame(self.master, bg="white")
        # self.signup_frame_2.attribute('-alpha', 0.4)
        self.signup_frame_2.pack(fill="both", expand=True)

        # 뒤 프레임 이미지 넣기
        self.participate_image_label = tk.Label(self.signup_frame_2, border=0)
        self.participate_image_label.place(x=30, rely=1.0, y=-100, anchor="sw")

        # 시작하자 라벨 넣기
        age_verification_font = tkinter.font.Font(family="Helvetica", size=17, weight="bold")  # 폰트 설정
        self.age_verification_label = tk.Label(self.signup_frame_2, text="시작하자", bg="white", font=age_verification_font)
        self.age_verification_label.place(x=30 + 350, y=20, anchor="nw")

        # 이름 엔트리
        self.name_entry = ttk.Entry(self.signup_frame_2, width=43, style="TEntry")
        self.name_entry.configure(font=("", 12))
        self.name_entry.place(x=640, y=180, anchor="center")
        self.name_entry.insert(0, "이름")

        # 아이디 엔트리와 중복 버튼을 포함하는 프레임 생성
        id_frame = tk.Frame(self.signup_frame_2, bg="white")
        id_frame.place(x=660, y=220, anchor="center")

        # 아이디 엔트리
        style = ttk.Style()
        style.configure("TEntry", borderwidth=2, relief="flat", background="#ffffff")
        self.id_entry = ttk.Entry(id_frame, width=43, style="TEntry")
        self.id_entry.configure(font=("", 12))
        self.id_entry.pack(side="left", padx=(0, 5))
        self.id_entry.insert(0, "아이디")

        # 중복 버튼
        self.overlap_button = tk.Button(id_frame, text="중복", font=("Arial", 10), bg="lightgray",
                                        command=self.overlap_check)
        self.overlap_button.pack(side="left")

        # 비밀번호 엔트리
        style = ttk.Style()
        style.configure("TEntry", borderwidth=2, relief="flat", background="#ffffff")
        self.pw_entry = ttk.Entry(self.signup_frame_2, width=43, style="TEntry")
        self.pw_entry.configure(font=("", 12))
        self.pw_entry.place(x=640, y=260, anchor="center")
        self.pw_entry.insert(0, "비밀번호")

        # 비밀번호 엔트리
        style = ttk.Style()
        style.configure("TEntry", borderwidth=2, relief="flat", background="#ffffff")
        self.pw_entry = ttk.Entry(self.signup_frame_2, width=43, style="TEntry")
        self.pw_entry.configure(font=("", 12))
        self.pw_entry.place(x=640, y=260, anchor="center")
        self.pw_entry.insert(0, "비밀번호")

        # 비밀번호 확인 엔트리
        style = ttk.Style()
        style.configure("TEntry", borderwidth=2, relief="flat", background="#ffffff")
        self.check_pw_entry = ttk.Entry(self.signup_frame_2, width=43, style="TEntry")
        self.check_pw_entry.configure(font=("", 12))
        self.check_pw_entry.place(x=640, y=300, anchor="center")
        self.check_pw_entry.insert(0, "비밀번호 확인")

        # 회원가입 버튼
        self.join_button = tk.Button(self.signup_frame_2, text="회원가입", font=("Arial", 10), bg="lightgray",
                                     command=self.join_button_click)
        self.join_button.place(relx=1.0, rely=1.0, x=-10, y=-20, anchor="se")

        # 뒤로가기 버튼
        participate_back_image = PILImage.open("participate_back.png")
        self.participate_back_photo = ImageTk.PhotoImage(participate_back_image)
        self.participate_back_image_label = tk.Label(self.signup_frame_2, image=self.participate_back_photo, border=0)
        self.participate_back_image_label.place(x=10, rely=1.0, y=-10, anchor="sw")
        self.participate_back_image_label.bind("<Button-1>", self.go_back_4)

        # 새로운 프레임 생성(앞)
        self.signup_frame_3 = tk.Frame(self.master, bg="white", width=650, height=311)
        self.signup_frame_3.place(x=10, y=-60, relx=0.5, rely=0.5, anchor="center")

        # (Zoom 계약) 라벨
        self.contract_label = tk.Label(self.signup_frame_3, text="Zoom 계약", bg="white", fg="black",
                                       font=("Arial", 18, "bold"))
        self.contract_label.place(x=80, y=40, anchor="center")

        # (설명) 라벨
        self.explain_label = tk.Label(self.signup_frame_3, text="계속하려면 필수 항목에 동의하세요. 동의하지 않으면 Zoom에 가입할 수 없습니다. *가 표시된",
                                      bg="white", fg="black", font=("Arial", 10))
        self.explain_label.place(x=290, y=80, anchor="center")

        # (설명) 라벨 2
        self.explain_label_2 = tk.Label(self.signup_frame_3, text="항목은 필수입니다.", bg="white", fg="black",
                                        font=("Arial", 10))
        self.explain_label_2.place(x=75, y=100, anchor="center")

        self.checkbox_var_1 = tk.BooleanVar()
        self.checkbox_var_2 = tk.BooleanVar()
        self.checkbox_var_3 = tk.BooleanVar()

        # 체크박스 생성 및 배치
        self.checkbox_1 = tk.Checkbutton(self.signup_frame_3, text="본인은 Zoom의 개인정보 처리방침 및 서비스약관에 동의합니다.*",
                                         command=self.update_button_text, variable=self.checkbox_var_1, onvalue=True,
                                         offvalue=False, bg="white", font=("Arial", 10))
        self.checkbox_1.place(x=15, y=100 + 40, anchor="w")

        self.checkbox_2 = tk.Checkbutton(self.signup_frame_3, text="본인은 Zoom의 데이터 수집 및 사용 동의에 동의합니다.*",
                                         command=self.update_button_text, variable=self.checkbox_var_2, onvalue=True,
                                         offvalue=False, bg="white", font=("Arial", 10))
        self.checkbox_2.place(x=15, y=100 + 70, anchor="w")

        self.checkbox_3 = tk.Checkbutton(self.signup_frame_3,
                                         text="본인은 Zoom에서 제품, 제안 및 산업 동향에 대한 마케팅 커뮤니케이션 정보를 받고 싶습니",
                                         variable=self.checkbox_var_3, onvalue=True, offvalue=False, bg="white",
                                         font=("Arial", 10))
        self.checkbox_3.place(x=15, y=100 + 100, anchor="w")

        self.explain_label_3 = tk.Label(self.signup_frame_3, text="다. 나는 언제든지 구독을 철회할 수 있음을 이해합니다.", bg="white",
                                        fg="black", font=("Arial", 10))
        self.explain_label_3.place(x=35, y=100 + 120, anchor="w")

        # 취소 버튼
        self.cancel_button = tk.Button(self.signup_frame_3, text="취소", font=("Arial", 10), bg="lightgray",
                                       command=self.go_back_3)
        self.cancel_button.place(relx=1.0, rely=1.0, x=-80, y=-20, anchor="se")

        # 모두 선택 버튼
        self.confirm_button = tk.Button(self.signup_frame_3, text="모두 선택", font=("Arial", 10), bg="lightgray", command=self.select_all_checkbox)
        self.confirm_button.place(relx=1.0, rely=1.0, x=-10, y=-20, anchor="se")

        self.get_image_from_db222()
        # 시간/날짜 업데이트 시작

    def get_image_from_db222(self):
        try:
            conn = pymysql.connect(
                host='192.168.31.87',
                user='zoom',
                password='0000',
                db='zoom_db',
            )
            cursor = conn.cursor()

            # 이미지 데이터 가져오기
            cursor.execute("SELECT image FROM imagess WHERE id IN (%s)", (1, ))
            images_data = cursor.fetchall()

            # 이미지 데이터만 추출해서 사용
            image_data_1 = images_data[0][0]

            # 첫 번째 이미지를 사용
            image_1 = Image.open(BytesIO(image_data_1))
            photo_1 = ImageTk.PhotoImage(image_1)
            self.participate_image_label.config(image=photo_1)
            self.participate_image_label.image = photo_1



        except pymysql.Error as e:
            print("데이터베이스 오류:", e)

        finally:
            if conn:
                conn.close()

    def overlap_check(self): #중복체크 함수
        # HOST = "192.168.31.53"
        # PORT = 9999
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client_socket.connect((HOST, PORT))
        client_socket.send(("a123789" + self.id_entry.get()).encode())
        response = client_socket.recv(1024).decode()
        if response == "DUPLICATE":
            messagebox.showinfo("Duplicate", "이미 사용 중인 아이디입니다.")
        else:
            messagebox.showinfo("Available", "사용 가능한 아이디입니다.")
            self.overlap_button.pack_forget()
            self.check_par = False

    def join_button_click(self):
        if self.pw_entry.get() != self.check_pw_entry.get():
            messagebox.showerror("Error", "비밀번호가 같지 않습니다.")
            return
        if not self.check_par:
            messagebox.showinfo("Message", "회원가입이 완료되었습니다")
            # HOST = "192.168.31.53"
            # PORT = 9999
            # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # client_socket.connect((HOST, PORT))
            self.signup_frame_2.pack_forget()
            self.show_login_frame()
            self.message_tuple = (
            self.entry.get(), self.name_entry.get(), self.id_entry.get(), self.pw_entry.get())  # year, name, id, pw
            serialized_data = pickle.dumps(self.message_tuple)
            client_socket.send(serialized_data)
            #client_socket.close()
        else:
            messagebox.showerror("Error", "중복검사를 해주세요")

    def select_all_checkbox(self):
        # 모든 체크박스 변수의 값을 True로 설정
        self.checkbox_var_1.set(True)
        self.checkbox_var_2.set(True)
        self.checkbox_var_3.set(True)
        self.confirm_button.place_forget()
        self.all_choice_button = tk.Button(self.signup_frame_3, text="완료", font=("Arial", 10), bg="lightgray", width=8, command=self.completion_click)
        self.all_choice_button.place(relx=1.0, rely=1.0, x=-10, y=-20, anchor="se")

    def update_button_text(self):
        # 체크박스 1과 2가 모두 체크되어 있거나, 체크박스 1, 2, 3이 모두 체크되어 있을 때
        if (self.checkbox_var_1.get() and self.checkbox_var_2.get()) or (
                self.checkbox_var_1.get() and self.checkbox_var_2.get() and self.checkbox_var_3.get()):
            self.confirm_button.place_forget()
            self.all_choice_button = tk.Button(self.signup_frame_3, text="완료", font=("Arial", 10), bg="lightgray", width=8, command=self.completion_click)
            self.all_choice_button.place(relx=1.0, rely=1.0, x=-10, y=-20, anchor="se")
        else:
            self.all_choice_button.place_forget()
            self.confirm_button.place(relx=1.0, rely=1.0, x=-10, y=-20, anchor="se")

    def completion_click(self):
        self.signup_frame_3.place_forget()

    def show_login_frame(self):  # 로그인 페이지
        # 이전 화면 안보이게
        self.labelA.pack_forget()
        self.labelB.pack_forget()
        self.par.pack_forget()
        self.join.pack_forget()
        self.login.pack_forget()

        # 새로운 프레임(로그인) 생성
        self.login_frame = tk.Frame(self.master, bg="white")
        self.login_frame.pack(fill="both", expand=True)

        # (줌)이미지 넣기
        self.login_zoom_label = tk.Label(self.login_frame, border=0)
        self.login_zoom_label.place(x=430, rely=1.0, y=-585, anchor="center")

        # 엔트리 추가(아이디)
        style = ttk.Style()
        style.configure("TEntry", borderwidth=2, relief="flat", background="#ffffff")
        self.login_id_entry = ttk.Entry(self.login_frame, width=43, style="TEntry")
        self.login_id_entry.configure(font=("", 12))
        self.login_id_entry.place(x=440, y=120, anchor="center")

        # 엔트리 추가(비밀번호)
        style.configure("TEntry", borderwidth=2, relief="flat", background="#ffffff")
        self.login_pw_entry = ttk.Entry(self.login_frame, width=43, style="TEntry")
        self.login_pw_entry.configure(font=("", 12))
        self.login_pw_entry.place(x=440, y=150, anchor="center")

        # 로그인 버튼 추가
        self.login_button = ttk.Button(self.login_frame, text="로그인", width=49)
        self.login_button.place(x=440, y=180, anchor="center")
        self.login_button.bind("<Button-1>", self.go_main)

        # 추가 이미지
        self.plus_image_label = tk.Label(self.login_frame, border=0)
        self.plus_image_label.place(x=440, y=220, anchor="center")

        # sso 이미지
        self.sso_image_label = tk.Label(self.login_frame, border=0)
        self.sso_image_label.place(x=300, y=300, anchor="center")
        self.sso_image_label.bind("<Button-1>", self.open_url)

        # apple 이미지
        self.apple_image_label = tk.Label(self.login_frame, border=0)
        self.apple_image_label.place(x=400, y=300, anchor="center")
        self.apple_image_label.bind("<Button-1>", self.open_url_2)

        # google 이미지
        self.google_image_label = tk.Label(self.login_frame, border=0)
        self.google_image_label.place(x=500, y=300, anchor="center")
        self.google_image_label.bind("<Button-1>", self.open_url_3)

        # facebook 이미지
        self.facebook_image_label = tk.Label(self.login_frame, border=0)
        self.facebook_image_label.place(x=600, y=300, anchor="center")
        self.facebook_image_label.bind("<Button-1>", self.open_url_4)

        # 뒤로가기 버튼
        self.participate_back_image_label = tk.Label(self.login_frame, border=0)
        self.participate_back_image_label.place(x=10, rely=1.0, y=-10, anchor="sw")
        self.participate_back_image_label.bind("<Button-1>", self.go_back_2)

        # 가입창으로 이동하는 버튼
        self.login_to_participate_label = tk.Label(self.login_frame, border=0)
        self.login_to_participate_label.place(x=800, rely=1.0, y=-10, anchor="sw")
        self.login_to_participate_label.bind("<Button-1>", self.go_participate)

        self.get_image_from_db22222222()
        # 시간/날짜 업데이트 시작

    def get_image_from_db22222222(self):
        try:
            conn = pymysql.connect(
                host='192.168.31.87',
                user='zoom',
                password='0000',
                db='zoom_db',
            )
            cursor = conn.cursor()

            # 이미지 데이터 가져오기
            cursor.execute("SELECT image FROM Imagessssss WHERE id IN (%s,%s,%s,%s,%s,%s,%s,%s)", (1,2,3,4,5,6,7,8,))
            images_data = cursor.fetchall()

            # 이미지 데이터만 추출해서 사용
            image_data_1 = images_data[0][0]
            image_data_2 = images_data[1][0]
            image_data_3 = images_data[2][0]
            image_data_4 = images_data[3][0]
            image_data_5 = images_data[4][0]
            image_data_6 = images_data[5][0]
            image_data_7 = images_data[6][0]
            image_data_8 = images_data[7][0]

            # 첫 번째 이미지를 사용
            image_1 = Image.open(BytesIO(image_data_1))
            photo_1 = ImageTk.PhotoImage(image_1)
            self.login_zoom_label.config(image=photo_1)
            self.login_zoom_label.image = photo_1

            image_2 = Image.open(BytesIO(image_data_2))
            photo_2 = ImageTk.PhotoImage(image_2)
            self.plus_image_label.config(image=photo_2)
            self.plus_image_label.image = photo_2

            image_3 = Image.open(BytesIO(image_data_3))
            photo_3 = ImageTk.PhotoImage(image_3)
            self.sso_image_label.config(image=photo_3)
            self.sso_image_label.image = photo_3

            image_4 = Image.open(BytesIO(image_data_4))
            photo_4 = ImageTk.PhotoImage(image_4)
            self.apple_image_label.config(image=photo_4)
            self.apple_image_label.image = photo_4

            image_5 = Image.open(BytesIO(image_data_5))
            photo_5 = ImageTk.PhotoImage(image_5)
            self.google_image_label.config(image=photo_5)
            self.google_image_label.image = photo_5

            image_6 = Image.open(BytesIO(image_data_6))
            photo_6 = ImageTk.PhotoImage(image_6)
            self.facebook_image_label.config(image=photo_6)
            self.facebook_image_label.image = photo_6

            image_7 = Image.open(BytesIO(image_data_7))
            photo_7 = ImageTk.PhotoImage(image_7)
            self.participate_back_image_label.config(image=photo_7)
            self.participate_back_image_label.image = photo_7

            image_8 = Image.open(BytesIO(image_data_8))
            photo_8 = ImageTk.PhotoImage(image_8)
            self.login_to_participate_label.config(image=photo_8)
            self.login_to_participate_label.image = photo_8

        except pymysql.Error as e:
            print("데이터베이스 오류:", e)

        finally:
            if conn:
                conn.close()

    def go_back(self, event):
        # 현재 프레임 숨기기
        self.signup_frame.pack_forget()
        self.__init__(self.master)

    def go_back_2(self, event):
        self.login_frame.pack_forget()
        self.__init__(self.master)

    def go_back_3(self):
        self.signup_frame_2.pack_forget()
        self.signup_frame_3.place_forget()
        self.__init__(self.master)

    def go_back_4(self, event):
        self.signup_frame_2.pack_forget()
        self.signup_frame_3.place_forget()
        self.__init__(self.master)
        self.check_par = True

    def go_participate(self, event):
        self.login_frame.pack_forget()
        self.show_signup_frame()

    def go_login(self, event):
        self.signup_frame.pack_forget()
        self.show_login_frame()

    def go_main(self, event):
        # HOST = "192.168.31.53"
        # PORT = 9999
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client_socket.connect((HOST, PORT))
        client_socket.send(("b987123" + self.login_id_entry.get()).encode())
        response = client_socket.recv(1024)
        name_and_pw = pickle.loads(response)
        if response == b"duplicate":
            messagebox.showerror("Error", "존재하지 않는 아이디입니다.")
        else:
            if name_and_pw[1] == self.login_pw_entry.get():
                self.get_name = name_and_pw[0]
                root.withdraw()
                self.login_frame.pack_forget()
                self.show_main_frame()
            else:
                messagebox.showerror("Error", "비밀번호 오류")

        #client_socket.close()

    def show_main_frame(self): # 로그인 하고 나서 화면
        self.main = tk.Toplevel(root, bg="white")
        self.main.geometry("1040x560")

        # 상단 바
        self.after_login_top_frame = tk.Frame(self.main, bg="#f2f2f5")
        self.after_login_top_frame.place(relx=0, rely=0, relwidth=1, height=50)

        # 유저 이름 넣기
        self.user_name_label = tk.Label(self.after_login_top_frame, text=self.get_name + "님 안녕하세요.", bg="#f2f2f5")
        self.user_name_label.pack(expand=True, fill="both")

        # 로그아웃 버튼
        self.logout_button = tk.Button(self.after_login_top_frame, text="로그아웃", command=self.logout)
        self.logout_button.place(relx=1.0, rely=0, anchor="ne")

        # 새 회의 버튼 및 라벨 배치
        self.new_button = tk.Button(self.main, text="새 회의", border=0, borderwidth=0, highlightthickness=0, command = self.new_meeting)
        self.new_button.pack(side=LEFT, padx=150)
        self.new_button.place(x=150, y=130)  # 버튼 위치 조정
        self.new_label = tk.Label(self.main, text="새 회의", bg="white")
        self.new_label.place(x=172, y=225)  # 라벨 위치 조정

        # 참가 버튼 및 라벨 배치
        self.join_button = tk.Button(self.main, text="참가", border=0, borderwidth=0, highlightthickness=0, command = self.participate_meeting)
        self.join_button.pack(side=LEFT, padx=150)
        self.join_button.place(x=450, y=130)  # 버튼 위치 조정
        self.join_label = tk.Label(self.main, text="참가", bg="white")
        self.join_label.place(x=480, y=225)  # 라벨 위치 조정

        # 이미지 라벨 생성
        self.image_label = tk.Label(self.main, image=watch, bg="white")
        self.image_label.place(x=600, y=90)

        # 현재 시간/날짜 표시 라벨 생성
        self.current_time = datetime.now().strftime('%H:%M')
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        global label_time, label_date  # 전역 변수로 지정
        label_time = tk.Label(self.main, text=self.current_time, font=("Arial", 40))
        label_time.place(x=650, y=200)
        self.label_date = tk.Label(self.main, text=self.current_date, font=("Arial", 24))
        self.label_date.place(x=650, y=150)
        self.get_image_from_db22()
        # 시간/날짜 업데이트 시작
        self.update_clock()

    def new_meeting(self):
        self.meeting_id = "{} {} {}".format(random.randint(100, 999),random.randint(100, 999), random.randint(1000, 9999))
        password_length = 6  # 비밀번호 길이
        password_characters = string.ascii_letters + string.digits  # 알파벳과 숫자를 포함한 문자열
        self.meeting_pw = ''.join(random.choice(password_characters) for i in range(password_length))
        self.per = False
        self.new_meeting_tuple = (self.meeting_id, self.meeting_pw)
        print("아이디 : " + self.meeting_id + " 비밀번호 : " + self.meeting_pw)
        serialized_data = pickle.dumps(self.new_meeting_tuple)
        # HOST = "192.168.31.53"
        # PORT = 9999
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client_socket.connect((HOST,PORT))
        client_socket.send(serialized_data)
        #client_socket.close()

        self.inin()

    def participate_meeting(self):
        self.per = False
        self.case = False
        self.join_s()


    def logout(self):
        self.main.destroy()
        root.deiconify()
        self.show_login_frame()



    def get_image_from_db22(self):
        try:
            conn = pymysql.connect(
                host='192.168.31.87',
                user='zoom',
                password='0000',
                db='zoom_db',
            )
            cursor = conn.cursor()

            # 이미지 데이터 가져오기
            cursor.execute("SELECT image FROM imagesss WHERE id IN (%s,%s)", (1, 2,  ))
            images_data = cursor.fetchall()

            # 이미지 데이터만 추출해서 사용
            image_data_1 = images_data[0][0]
            image_data_2 = images_data[1][0]

            # 첫 번째 이미지를 사용
            image_1 = Image.open(BytesIO(image_data_1))
            photo_1 = ImageTk.PhotoImage(image_1)
            self.join_button.config(image=photo_1)
            self.join_button.image = photo_1

            image_2 = Image.open(BytesIO(image_data_2))
            photo_2 = ImageTk.PhotoImage(image_2)
            self.new_button.config(image=photo_2)
            self.new_button.image = photo_2

        except pymysql.Error as e:
            print("데이터베이스 오류:", e)

        finally:
            if conn:
                conn.close()
    def update_clock(self):
        current_time = datetime.now().strftime('%H:%M')
        current_date = datetime.now().strftime('%Y-%m-%d')
        label_time.config(text=current_time)
        label_date.config(text=current_date)
        label_time.after(1000, self.update_clock)  # 1초마다 업데이트

    def join_s(self):
        root.withdraw()
        self.new = tk.Toplevel(root)
        self.new["bg"] = "#FFFFFF"
        self.new.geometry("395x406")

        font = tk.font.Font(family="맑은 고딕", size=20, weight="bold")
        label = tk.Label(self.new, text="회의 참가", font=font, bg="white")

        c1 = tk.Checkbutton(self.new, text="이후 회의에서 내 이름 기억", bg="white")
        c1.configure(bg='white')
        self.var_c2 = tk.BooleanVar()  # BooleanVar를 사용하여 체크 버튼 상태 추적
        self.c2 = tk.Checkbutton(self.new, text="내 비디오 끄기", bg="white", variable=self.var_c2,
                                 command=self.check_button_clicked)
        label.pack(anchor="w", pady=25, padx=40)

        self.join_entry_id = tk.Entry(self.new, width=35, relief="solid", borderwidth=1)
        self.join_entry_id.configure(font=("", 12))
        self.join_entry_id.pack(pady=5, ipady=7)
        self.join_entry_id.pack()

        self.join_entry_pw = tk.Entry(self.new, width=35, relief="solid", borderwidth=1)
        self.join_entry_pw.configure(font=("", 12))
        self.join_entry_pw.pack(pady=7, ipady=7)
        self.join_entry_pw.pack()

        c1.pack(anchor="w", padx=48, pady=5)
        self.c2.pack(anchor="w", padx=48, pady=5)
        label1 = tk.Label(self.new, text='"참가"를 클릭하면 서비스 약관 및 개인정보 처리방침에\n동의하게 됩니다.', bg="white")
        label1.pack(pady=5)
        label2 = tk.Label(self.new)
        label2.pack(anchor="e")
        self.case_2 = False
        self.join_btn = tk.Button(label2, text="참가", command=self.before_inin)
        self.join_btn.pack(side="left", padx=20, pady=5)
        self.join_cancel_btn = tk.Button(label2, text="취소", command=self.close_main_form)
        self.join_cancel_btn.pack(side="left", padx=20, pady=5)

    def check_button_clicked(self):
        global flags
        if self.var_c2.get():  # 체크 버튼이 선택된 경우
            flags = 1
        else:  # 체크 버튼이 선택되지 않은 경우
            flags = 0

    def final_exit(self):
        client_socket.sendall("Client IP: {}".format(socket.gethostbyname(socket.gethostname())).encode())
        self.into.withdraw()  # 창 없애기
        client_socket.close()

    def close_main_form(self): # 영상 참가하기 전에 화면에서 취소 버튼을 누르면
        self.new.withdraw()
        if self.case == True: # 로그인을 안하고 회의 참가했을 경우 취소 버튼을 누르면 다시 메인화면이 뜨게 만듬
            self.master.deiconify()

    def before_inin(self): # 영상 들어가기 전에
        # HOST = "192.168.31.53"
        # PORT = 9999
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client_socket.connect((HOST, PORT))
        client_socket.send(("g987654" + self.join_entry_id.get()).encode())
        response = client_socket.recv(1024)
        if response == b"DUPLICATE":
            messagebox.showerror("Error", "아이디가 옳지 않습니다.")
            return
        else:
            id_and_pw = pickle.loads(response)
            if id_and_pw[1] == self.join_entry_pw.get():
                self.inin()
            else:
                messagebox.showerror("Error", "비밀번호 오류")
                return
        #client_socket.close()

    def inin(self):
        global connected_clients
        if self.per == True:
            self.new.withdraw()  # 창 없애기
        self.into = tk.Toplevel(root)
        self.into.geometry("1320x761")  # 해상도 선언
        self.into.title(self.meeting_id +' / '+ self.meeting_pw)
        self.into.resizable(False, False)

        self.label_canvas = tkinter.Label(self.into)
        self.label_canvas.pack()

        self.video_canvas = tkinter.Canvas(self.label_canvas, width=640, height=420)
        self.video_canvas.pack(side=BOTTOM)
        self.update_canvas()

        self.video_canvas2 = tkinter.Canvas(self.label_canvas, width=320, height=240)
        self.video_canvas2.pack(side=LEFT)
        self.update_canvas2()

        self.video_canvas3 = tkinter.Canvas(self.label_canvas, width=320, height=240)
        self.video_canvas3.pack(side=LEFT)
        self.update_canvas3()

        self.video_canvas4 = tkinter.Canvas(self.label_canvas, width=320, height=240)
        self.video_canvas4.pack(side=LEFT)
        self.update_canvas4()

        self.video_canvas5 = tkinter.Canvas(self.label_canvas, width=320, height=240)
        self.video_canvas5.pack(side=LEFT)
        self.update_canvas5()

        self.label_bottom = tkinter.Label(self.into)
        self.label_bottom.pack()

        self.button = tk.Button(self.label_bottom, text="비디오중지", command=change)  # 숨겨진 버튼 생성
        self.button.pack(side="left")
        self.button1 = tk.Button(self.label_bottom, text="참가자")
        self.button1.pack(side="left")
        self.button2 = tk.Button(self.label_bottom, text="채팅")
        self.button2.pack(side="left")
        self.button3 = tk.Button(self.label_bottom, text="필터", command=self.filter)
        self.button3.pack(side="left")
        self.button4 = tk.Button(self.label_bottom, text="종료", command=self.out)  # command=self.out
        self.button4.pack(side="left")

        main_streaming = threading.Thread(target=streaming, args=(self,))
        main_streaming.daemon = True
        main_streaming.start()

        self.label_bottom.bind("<Motion>",
                               lambda event: on_mouse_move(event, self.button, self.button1, self.button2, self.button3,
                                                           self.button4))
        self.label_bottom.bind("<Leave>", lambda event: on_mouse_leave(event, self.button, self.button1, self.button2,
                                                                       self.button3, self.button4))
        self.button2.bind("<Button-1>", self.chat_open)
        self.chatlist = tk.Listbox(self.into, width=38)
        self.labelC = tk.Label(self.into, width=38)
        self.chat_text = tk.Text(self.into, width=38)

        self.button1.bind("<Button-1>", self.par_listbox)
        self.chat_text.bind("<Return>", self.send_message_from_entry)

        # receive_msg = threading.Thread(target=receive_message, args=(client_socket, self.chatlist))
        # receive_msg.daemon = True
        # receive_msg.start()

        self.main_db()

    def main_db(self):
        try:
            conn = pymysql.connect(
                host='192.168.31.87',
                user='zoom',
                password='0000',
                db='zoom_db',
            )
            cursor = conn.cursor()

            # 이미지 데이터 가져오기
            cursor.execute("SELECT image FROM main WHERE id IN (%s, %s, %s, %s, %s)", (1, 2, 3, 4, 5,))
            images_data = cursor.fetchall()

            # 이미지 데이터만 추출해서 사용
            image_data_1 = images_data[0][0]
            image_data_2 = images_data[1][0]
            image_data_3 = images_data[2][0]
            image_data_4 = images_data[3][0]
            image_data_5 = images_data[4][0]

            image_1 = Image.open(BytesIO(image_data_1))
            photo_1 = ImageTk.PhotoImage(image_1)
            self.button.config(image=photo_1)
            self.button.image = photo_1

            image_2 = Image.open(BytesIO(image_data_2))
            photo_2 = ImageTk.PhotoImage(image_2)
            self.button1.config(image=photo_2)
            self.button1.image = photo_2

            image_3 = Image.open(BytesIO(image_data_3))
            photo_3 = ImageTk.PhotoImage(image_3)
            self.button2.config(image=photo_3)
            self.button2.image = photo_3

            image_4 = Image.open(BytesIO(image_data_4))
            photo_4 = ImageTk.PhotoImage(image_4)
            self.button3.config(image=photo_4)
            self.button3.image = photo_4

            image_5 = Image.open(BytesIO(image_data_5))
            photo_5 = ImageTk.PhotoImage(image_5)
            self.button4.config(image=photo_5)
            self.button4.image = photo_5


        except pymysql.Error as e:
            print("데이터베이스 오류:", e)

        finally:
            if conn:
                conn.close()

    def send_message_from_entry(self, event=None):
        message = self.chat_text.get("1.0", tk.END)
        if message !="":  # 메시지가 비어 있지 않은 경우에만 전송
        # 엔트리 박스의 내용을 지웁니다.
            send_message(client_socket, message,self.get_name)
            self.chat_text.after(5, self.clear_entry_box)

    def clear_entry_box(self):
        self.chat_text.delete("1.0", "end")
        self.chat_text.insert("1.0", "")  # 첫 번째 줄의 첫 번째 문자에 빈 문자열을 삽입하여 엔트리 박스를 초기화합니다.
        # 엔트리 박스에 포커스를 다시 설정합니다.
        self.chat_text.focus_set()
        # 엔트리 박스의 insert cursor를 처음 위치로 이동합니다.
        self.chat_text.mark_set(tk.INSERT, "1.0")
        #print(self.chat_text.index(tk.INSERT))  # 디버깅을 위한 출력

    def update_canvas(self):
        global im
        if im:
            self.video_canvas.photo = ImageTk.PhotoImage(image=im)
            self.video_canvas.create_image(0, 0, anchor=tkinter.NW, image=self.video_canvas.photo)
        elif im == "":
            self.video_canvas.delete("all")
        self.into.update()
        self.video_canvas.master.after(1, self.update_canvas)


    def update_canvas2(self):
        global im2
        if im2:
            self.video_canvas2.photo = ImageTk.PhotoImage(image=im2)
            self.video_canvas2.create_image(0, 0, anchor=tkinter.NW, image=self.video_canvas2.photo)
        elif im2 == "":
            self.video_canvas2.delete("all")
        self.into.update()
        self.video_canvas2.master.after(1, self.update_canvas2)

    def update_canvas3(self):
        global im3
        if im3:
            self.video_canvas3.photo = ImageTk.PhotoImage(image=im3)
            self.video_canvas3.create_image(0, 0, anchor=tkinter.NW, image=self.video_canvas3.photo)
        elif im3 == "":
            self.video_canvas3.delete("all")
        self.into.update()
        self.video_canvas3.master.after(1, self.update_canvas3)

    def update_canvas4(self):
        global im4
        if im4:
            self.video_canvas4.photo = ImageTk.PhotoImage(image=im4)
            self.video_canvas4.create_image(0, 0, anchor=tkinter.NW, image=self.video_canvas4.photo)
        elif im4 == "":
            self.video_canvas4.delete("all")
        self.into.update()
        self.video_canvas4.master.after(1, self.update_canvas4)

    def update_canvas5(self):
        global im5
        if im5:
            self.video_canvas5.photo = ImageTk.PhotoImage(image=im5)
            self.video_canvas5.create_image(0, 0, anchor=tkinter.NW, image=self.video_canvas5.photo)
        elif im5 == "":
            self.video_canvas5.delete("all")
        self.into.update()
        self.video_canvas5.master.after(1, self.update_canvas5)

    def chat_open(self, event):
        global chat_flags
        if chat_flags == 0:
            self.chatlist.place(relx=0.89, rely=0.60, relheight=0.55, anchor=tk.CENTER)  # 채팅 리스트를 우측 상단에 배치
            self.chat_text.place(relx=0.89, rely=0.94, relheight=0.1, anchor=tk.CENTER)  # 채팅 텍스트를 우측 하단에 배치
            self.button.place(relx=0.1, rely=1, anchor="s")
            self.button1.place(relx=0.3, rely=1, anchor="s")
            self.button2.place(relx=0.5, rely=1, anchor="s")
            self.button3.place(relx=0.7, rely=1, anchor="s")
            self.button4.place(relx=0.9, rely=1, anchor="s")
            chat_flags = 1
        else:
            self.chatlist.place_forget()
            self.chat_text.place_forget()
            chat_flags = 0

    def par_listbox(self, event):
        global parlist
        if parlist == 0:
            self.parlist = tk.Listbox(self.into, width=38)
            self.parlist.place(relx=0.03, rely=0.94, anchor="sw")
            parlist = 1
        else:
            self.parlist.place_forget()
            parlist = 0


    def out(self):
        # 버튼감싸고있는 라벨
        self.la = tkinter.Label(self.into, border=0, highlightthickness=0)

        # 투명 이미지 배경 설정
        self.la.configure(background='#242424')  # 투명 이미지 위에 다른 위젯 배치를 위해 흰색 배경 설정

        # 이미지가 레이블의 크기와 일치하도록 크기 조정
        #self.la.image = label_imagew
        self.la.pack()

        self.button5 = tk.Button(self.into, text="취소", command=self.remove_buttons)

        self.button6 = tk.Button(self.into, text = "회의 나가기", bg="#242424", border=0,
                                 borderwidth=0, width=220, height=50, command=self.final_exit)
        self.button7 = tk.Button(self.into, text="모두에 대해 회의종료", bg="#242424", border=0, borderwidth=0,
                                 width=220, height=50, command=self.exit)

        self.la.place(x=1060, y=570)
        self.button6.place(x=1080, y=575)
        self.button7.place(x=1080, y=615)
        self.button5.place(x=1148, y=675)
        self.button5.place(x=1148, y=675)
        # 마우스 이벤트 다시 바인딩
        # self.video_canvas.bind("<Leave>", lambda event: on_mouse_leave(event, self.button, self.button1, self.button2,self.button3, self.button4))

        self.exit_db()

    def exit_db(self):
        try:
            conn = pymysql.connect(
                host='192.168.31.87',
                user='zoom',
                password='0000',
                db='zoom_db',
            )
            cursor = conn.cursor()

            # 이미지 데이터 가져오기
            cursor.execute("SELECT image FROM exits WHERE id IN (%s, %s, %s, %s)", (1, 2, 3, 4,))
            images_data = cursor.fetchall()

            # 이미지 데이터만 추출해서 사용
            image_data_1 = images_data[0][0]
            image_data_2 = images_data[1][0]
            image_data_3 = images_data[2][0]
            image_data_4 = images_data[3][0]

            # 첫 번째 이미지를 사용
            image_1 = Image.open(BytesIO(image_data_1))
            photo_1 = ImageTk.PhotoImage(image_1)
            self.button6.config(image=photo_1)
            self.button6.image = photo_1

            # 두 번째 이미지를 사용
            image_2 = Image.open(BytesIO(image_data_2))
            photo_2 = ImageTk.PhotoImage(image_2)
            self.button7.config(image=photo_2)
            self.button7.image = photo_2

            # 세 번째 이미지를 사용
            image_3 = Image.open(BytesIO(image_data_3))
            photo_3 = ImageTk.PhotoImage(image_3)
            self.la.config(image=photo_3)
            self.la.image = photo_3

            image_4 = Image.open(BytesIO(image_data_4))
            photo_4 = ImageTk.PhotoImage(image_4)
            self.button5.config(image=photo_4)
            self.button5.image = photo_4


        except pymysql.Error as e:
            print("데이터베이스 오류:", e)

        finally:
            if conn:
                conn.close()

    def exit(self):
        client_socket.sendall(b'stop')

    def remove_buttons(self):
        # 취소 버튼을 누르면 생성된 버튼들 제거
        self.la.destroy()
        self.button5.destroy()
        self.button6.destroy()
        self.button7.destroy()

    def filter(self):
        global flag
        if flag == 0:
            self.label_filter = tkinter.Label(self.label_canvas)
            self.label_filter.place(relx=0.1, rely=0.6, anchor="w")
            self.button_1 = tkinter.Button(self.label_filter, text="필터", command=flagschange, pady=5, padx=40)
            self.button_1.pack(pady=5, padx=10)
            self.button_2 = tkinter.Button(self.label_filter, text="물결필터", command=flagchange, pady=5, padx=30)
            self.button_2.pack(pady=5, padx=10)
            self.button_3 = tkinter.Button(self.label_filter, text="누끼", command=flagchange2, pady=5, padx=40)
            self.button_3.pack(pady=5, padx=10)
            self.button_4 = tkinter.Button(self.label_filter, text="오목거울", command=flagchange3, pady=5, padx=30)
            self.button_4.pack(pady=5, padx=10)
            self.button_5 = tkinter.Button(self.label_filter, text="볼록거울", command=flagchange4, pady=5, padx=30)
            self.button_5.pack(pady=5, padx=10)
            self.button_6 = tkinter.Button(self.label_filter, text="원본", command=flagchange5, pady=5, padx=40)
            self.button_6.pack(pady=5, padx=10)
            flag = 1
        else:
            self.label_filter.destroy()
            flag = 0



    def hide_buttons(self):
        self.button.pack_forget()
        self.button1.pack_forget()
        self.button2.pack_forget()
        self.button3.pack_forget()
        self.button4.pack_forget()


def on_mouse_move(event, button, button1, button2, button3, button4):
    button.place(relx=0.1, rely=1, anchor="s")
    button1.place(relx=0.3, rely=1, anchor="s")
    button2.place(relx=0.5, rely=1, anchor="s")
    button3.place(relx=0.7, rely=1, anchor="s")
    button4.place(relx=0.9, rely=1, anchor="s")


def on_mouse_leave(event, button, button1, button2, button3, button4):
    button.place_forget()
    button1.place_forget()
    button2.place_forget()
    button3.place_forget()
    button4.place_forget()

if __name__ == "__main__":
    csv_webeditor = App(root)

    root.mainloop()