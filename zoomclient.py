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

root = tk.Tk()
rgb = (45, 101, 246)
root.configure(bg="#%02x%02x%02x" % rgb)
label_image = PhotoImage(file="label.png")
image_width = label_image.width()
image_height = label_image.height()
zoom = PhotoImage(file="logo.png")
par1 = PhotoImage(file="par.png")
join1 = PhotoImage(file="join.png")
login1 = PhotoImage(file="login.png")
par2 = PhotoImage(file="par2.png")
join2 = PhotoImage(file="join2.png")
login2 = PhotoImage(file="login2.png")

exit_button = PhotoImage(file="3.png")
out_button = PhotoImage(file="4.png")
label_imagew = PhotoImage(file="label2.png")
save_label = PhotoImage(file="save2.png")

button_width = par1.width()
button_height = par1.height()
result_img = 0  # 전역변수로 최종 이미지를 받도록 했다

width = 0  # ----->240402
height = 0  # ----->240402
chat_flags = 0  # ----->240402

HOST = "192.168.31.87"
PORT = 9999

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

main_join = PhotoImage(file = "main_join.png")
main_join2 = PhotoImage(file = "main_join2.png")
new_meet = PhotoImage(file = "new_meet.png")
new_meet2 = PhotoImage(file = "new_meet2.png")
watch = PhotoImage(file = "watch.png")

connected_clients = 0


def send_message(client_socket):
    while True:
        try:
            message = ""
            # 채팅 엔트리.겟으로 바꿔야함
            if message:
                client_socket.send(b'MSG:' + message.encode())
        except Exception as e:
            print("Error sending message:", e)
            break


def send_video_to_server(client_socket):
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't capture frame.")
            break

        # 프레임 크기를 변경하여 낮은 해상도로 설정
        width = 320  # 변경할 너비
        height = 240  # 변경할 높이
        frame = cv2.resize(frame, (width, height))

        # 프레임을 JPEG 형식으로 인코딩하여 전송
        encoded_frame = cv2.imencode('.jpg', frame)[1].tobytes()
        client_socket.sendall(b'IMG:' + encoded_frame)


def receive_and_update_video(client_socket, canvas):
    global connected_clients
    while True:
        try:
            data = client_socket.recv(200000)
            connected_clients = data[:1].decode()
            print(data[:1])
            if data[1:14] == ip_address.encode():
                print(data[14:18])
                if data[14:18] == b'IMG:':
                    frame_data = data[18:]
                    print(frame_data)
                    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = PILImage.fromarray(frame)

                    # 업데이트 함수를 호출하여 화면 업데이트
                    canvas.master.after(1, update_canvas_with_image, canvas, image)
            elif data[1:15] == ip_address.encode():
                print(data[15:19])
                if data[15:19] == b'IMG:':
                    frame_data = data[19:]
                    print(frame_data)
                    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = PILImage.fromarray(frame)

                    # 업데이트 함수를 호출하여 화면 업데이트
                    canvas.master.after(1, update_canvas_with_image, canvas, image)
        except Exception as e:
            print("Error receiving video:", e)
            break


def update_canvas_with_image(canvas, image):
    canvas.photo = ImageTk.PhotoImage(image=image)
    canvas.create_image(0, 0, anchor=tkinter.NW, image=canvas.photo)



def streaming(app_instance):
    #app=App(root)
    message_thread = threading.Thread(target=send_message, args=(client_socket,))
    video_thread = threading.Thread(target=send_video_to_server, args=(client_socket,))

    message_thread.start()
    video_thread.start()

    receive_video_thread = threading.Thread(target=receive_and_update_video, args=(client_socket, app_instance))
    receive_video_thread.start()

    message_thread.join()
    video_thread.join()

    receive_video_thread.join()

    client_socket.close()


class App:
    def __init__(self, master):
        self.master = master
        self.master.geometry("872x624")  # 해상도 선언
        self.master.title("Zoom")
        # 로고
        self.labelA = tkinter.Label(self.master, image=zoom, border=0, borderwidth=0, highlightthickness=0)
        self.labelA.pack(pady=100)
        # 버튼감싸고있는 라벨
        self.labelB = tkinter.Label(self.master, image=label_image, bg="#%02x%02x%02x" % rgb, border=0, borderwidth=0,
                                    highlightthickness=0)
        self.labelB.pack()

        # 버튼
        self.par = tkinter.Button(self.labelB, image=par1, border=0, text="회의 참가", command=self.join_s, borderwidth=0,
                                  highlightthickness=0, relief="flat", compound="none", padx=30, pady=30,
                                  takefocus=False)
        self.par.bind("<Enter>", self.on_1)
        self.par.bind("<Leave>", self.leave_1)
        self.par.pack(padx=35, pady=30)

        self.join = tkinter.Button(self.labelB, image=join1, border=0, text="가입", command=self.show_signup_frame,
                                   borderwidth=0, highlightthickness=0, relief="flat", compound="none")
        self.join.bind("<Enter>", self.on_2)
        self.join.bind("<Leave>", self.leave_2)
        self.join.pack(padx=20)

        self.login = tkinter.Button(self.labelB, image=login1, border=0, text="로그인", command=self.show_login_frame,
                                    borderwidth=0, highlightthickness=0, relief="flat", compound="none")
        self.login.bind("<Enter>", self.on_3)
        self.login.bind("<Leave>", self.leave_3)
        self.login.pack(padx=35, pady=30)

        self.flags = 0  # 캔버스 업데이트를 위한 쓰레드 시작

    def on_1(self, event):
        self.par.config(image=par2)

    def on_2(self, event):
        self.join.config(image=join2)

    def on_3(self, event):
        self.login.config(image=login2)

    def leave_1(self, event):
        self.par.config(image=par1)

    def leave_2(self, event):
        self.join.config(image=join1)

    def leave_3(self, event):
        self.login.config(image=login1)

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
        # self.image.pack_forget()  # 기존에 있던 이미지 안보이게
        # self.label.pack_forget()  # 기존에 있던 이미지 안보이게

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
        participate_image = PILImage.open("participate_image.png")
        self.participate_photo = ImageTk.PhotoImage(participate_image)
        self.participate_image_label = tk.Label(self.signup_frame, image=self.participate_photo, border=0)
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

        # 엔트리 생성
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
        participate_back_image = PILImage.open("participate_back.png")
        self.participate_back_photo = ImageTk.PhotoImage(participate_back_image)
        self.participate_back_image_label = tk.Label(self.signup_frame, image=self.participate_back_photo, border=0)
        self.participate_back_image_label.place(x=10, rely=1.0, y=-10, anchor="sw")
        self.participate_back_image_label.bind("<Button-1>", self.go_back)

        # 로그인 화면으로 이동하는 버튼 옆에 있는 이미지
        signup_to_participate_image = PILImage.open("already_account.png")
        self.already_account_photo = ImageTk.PhotoImage(signup_to_participate_image)
        self.already_account_label = tk.Label(self.signup_frame, image=self.already_account_photo, border=0)
        self.already_account_label.place(x=640, rely=1.0, y=-10, anchor="sw")

        # 로그인 화면으로 이동하는 버튼
        go_to_login_image = PILImage.open("go_to_login.png")
        self.go_to_login_photo = ImageTk.PhotoImage(go_to_login_image)
        self.go_to_login_label = tk.Label(self.signup_frame, image=self.go_to_login_photo, border=0)
        self.go_to_login_label.place(x=800, rely=1.0, y=-19, anchor="sw")
        self.go_to_login_label.bind("<Button-1>", self.go_login)

    def validate(self, new_text):
        if new_text.isdigit() or new_text == "":
            return len(new_text) <= 4
        else:
            return False

    def contract_and_start(self):  # 가입페이지 두번째
        HOST = "192.168.31.87"
        PORT = 9999
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        message = self.entry.get()
        client_socket.send(("1:" + message).encode())

        client_socket.close()

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

        # 뒤 프레임
        participate_image = PILImage.open("participate_image.png")
        self.participate_photo = ImageTk.PhotoImage(participate_image)
        self.participate_image_label = tk.Label(self.signup_frame_2, image=self.participate_photo, border=0)
        self.participate_image_label.place(x=30, rely=1.0, y=-100, anchor="sw")

        # 시작하자 라벨 넣기
        age_verification_font = tkinter.font.Font(family="Helvetica", size=17, weight="bold")  # 폰트 설정
        self.age_verification_label = tk.Label(self.signup_frame_2, text="시작하자", bg="white", font=age_verification_font)
        self.age_verification_label.place(x=30 + 350, y=20, anchor="nw")

        # 이름 엔트리
        style = ttk.Style()
        style.configure("TEntry", borderwidth=2, relief="flat", background="#ffffff")
        self.name_entry = ttk.Entry(self.signup_frame_2, width=43, style="TEntry")
        self.name_entry.configure(font=("", 12))
        self.name_entry.place(x=640, y=180, anchor="center")
        self.name_entry.insert(0, "이름")

        # 아이디 엔트리
        style = ttk.Style()
        style.configure("TEntry", borderwidth=2, relief="flat", background="#ffffff")
        self.id_entry = ttk.Entry(self.signup_frame_2, width=43, style="TEntry")
        self.id_entry.configure(font=("", 12))
        self.id_entry.place(x=640, y=220, anchor="center")
        self.id_entry.insert(0, "아이디")

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
        self.confirm_button = tk.Button(self.signup_frame_3, text="모두 선택", font=("Arial", 10), bg="lightgray",
                                        command=self.select_all_checkbox)
        self.confirm_button.place(relx=1.0, rely=1.0, x=-10, y=-20, anchor="se")

    def join_button_click(self):
        messagebox.showinfo("Message", "회원가입이 완료되었습니다")
        self.signup_frame_2.pack_forget()
        self.show_login_frame()

    def select_all_checkbox(self):
        # 모든 체크박스 변수의 값을 True로 설정
        self.checkbox_var_1.set(True)
        self.checkbox_var_2.set(True)
        self.checkbox_var_3.set(True)
        self.confirm_button.place_forget()
        self.all_choice_button = tk.Button(self.signup_frame_3, text="완료", font=("Arial", 10), bg="lightgray", width=8,
                                           command=self.completion_click)
        self.all_choice_button.place(relx=1.0, rely=1.0, x=-10, y=-20, anchor="se")

    def update_button_text(self):
        # 체크박스 1과 2가 모두 체크되어 있거나, 체크박스 1, 2, 3이 모두 체크되어 있을 때
        if (self.checkbox_var_1.get() and self.checkbox_var_2.get()) or (
                self.checkbox_var_1.get() and self.checkbox_var_2.get() and self.checkbox_var_3.get()):
            self.confirm_button.place_forget()
            self.all_choice_button = tk.Button(self.signup_frame_3, text="완료", font=("Arial", 10), bg="lightgray",
                                               width=8, command=self.completion_click)
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
        login_zoom = PILImage.open("login_zoom.png")
        self.login_photo = ImageTk.PhotoImage(login_zoom)
        self.login_zoom_label = tk.Label(self.login_frame, image=self.login_photo, border=0)
        self.login_zoom_label.place(x=430, rely=1.0, y=-585, anchor="center")

        # 엔트리 추가(아이디)
        style = ttk.Style()
        style.configure("TEntry", borderwidth=2, relief="flat", background="#ffffff")
        self.entry = ttk.Entry(self.login_frame, width=43, style="TEntry")
        self.entry.configure(font=("", 12))
        self.entry.place(x=440, y=120, anchor="center")

        # 엔트리 추가(비밀번호)
        style.configure("TEntry", borderwidth=2, relief="flat", background="#ffffff")
        self.entry = ttk.Entry(self.login_frame, width=43, style="TEntry")
        self.entry.configure(font=("", 12))
        self.entry.place(x=440, y=150, anchor="center")

        # 로그인 버튼 추가
        self.login_button = ttk.Button(self.login_frame, text="로그인", width=49)
        self.login_button.place(x=440, y=180, anchor="center")
        self.login_button.bind("<Button-1>", self.go_main)

        # 추가 이미지
        plus_image = PILImage.open("plus_image.png")
        self.plus_image_photo = ImageTk.PhotoImage(plus_image)
        self.plus_image_label = tk.Label(self.login_frame, image=self.plus_image_photo, border=0)
        self.plus_image_label.place(x=440, y=220, anchor="center")

        # sso 이미지
        sso_image = PILImage.open("sso.png")
        self.sso_image_photo = ImageTk.PhotoImage(sso_image)
        self.sso_image_label = tk.Label(self.login_frame, image=self.sso_image_photo, border=0)
        self.sso_image_label.place(x=300, y=300, anchor="center")
        self.sso_image_label.bind("<Button-1>", self.open_url)

        # apple 이미지
        apple_image = PILImage.open("apple.png")
        self.apple_image_photo = ImageTk.PhotoImage(apple_image)
        self.apple_image_label = tk.Label(self.login_frame, image=self.apple_image_photo, border=0)
        self.apple_image_label.place(x=400, y=300, anchor="center")
        self.apple_image_label.bind("<Button-1>", self.open_url_2)

        # google 이미지
        google_image = PILImage.open("google.png")
        self.google_image_photo = ImageTk.PhotoImage(google_image)
        self.google_image_label = tk.Label(self.login_frame, image=self.google_image_photo, border=0)
        self.google_image_label.place(x=500, y=300, anchor="center")
        self.google_image_label.bind("<Button-1>", self.open_url_3)

        # facebook 이미지
        facebook_image = PILImage.open("facebook.png")
        self.facebook_image_photo = ImageTk.PhotoImage(facebook_image)
        self.facebook_image_label = tk.Label(self.login_frame, image=self.facebook_image_photo, border=0)
        self.facebook_image_label.place(x=600, y=300, anchor="center")
        self.facebook_image_label.bind("<Button-1>", self.open_url_4)

        # 뒤로가기 버튼
        participate_back_image = PILImage.open("participate_back.png")
        self.participate_back_photo = ImageTk.PhotoImage(participate_back_image)
        self.participate_back_image_label = tk.Label(self.login_frame, image=self.participate_back_photo, border=0)
        self.participate_back_image_label.place(x=10, rely=1.0, y=-10, anchor="sw")
        self.participate_back_image_label.bind("<Button-1>", self.go_back_2)

        # 가입창으로 이동하는 버튼
        login_to_participate_image = PILImage.open("login_to_participate.png")
        self.login_to_participate_photo = ImageTk.PhotoImage(login_to_participate_image)
        self.login_to_participate_label = tk.Label(self.login_frame, image=self.login_to_participate_photo, border=0)
        self.login_to_participate_label.place(x=800, rely=1.0, y=-10, anchor="sw")
        self.login_to_participate_label.bind("<Button-1>", self.go_participate)

    def after_login(self):  # 로그인 후 화면
        self.login_frame.pack_forget()

        # 로그인 후 화면
        self.after_login_frame = tk.Frame(self.master, bg="white")
        self.after_login_frame.pack(expand=True, fill=tk.BOTH)

        # 로그인 후 상단 프레임
        self.after_login_top_frame = tk.Frame(self.after_login_frame, bg="#f2f2f5")
        self.after_login_top_frame.place(relx=0, rely=0, relwidth=1, height=50)

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

    def go_participate(self, event):
        self.login_frame.pack_forget()
        self.show_signup_frame()

    def go_login(self, event):
        self.signup_frame.pack_forget()
        self.show_login_frame()

    def go_main(self, event):
        root.withdraw()
        self.login_frame.pack_forget()
        self.show_main_frame()

    def show_main_frame(self):
        self.main = tk.Toplevel(root, bg="white")
        self.main.geometry("1040x560")

        # 새 회의 버튼 및 라벨 배치
        self.new_button = tk.Button(self.main, text="새 회의", image=new_meet, border=0, borderwidth=0,
                                    highlightthickness=0)
        self.new_button.pack(side=LEFT, padx=150)
        self.new_button.place(x=150, y=130)  # 버튼 위치 조정
        self.new_label = tk.Label(self.main, text="새 회의", bg="white")
        self.new_label.place(x=172, y=225)  # 라벨 위치 조정

        # 참가 버튼 및 라벨 배치
        self.join_button = tk.Button(self.main, text="참가", image=main_join, border=0, borderwidth=0,
                                     highlightthickness=0)
        self.join_button.pack(side=LEFT, padx=150)
        self.join_button.place(x=450, y=130)  # 버튼 위치 조정
        self.join_label = tk.Label(self.main, text="참가", bg="white")
        self.join_label.place(x=480, y=225)  # 라벨 위치 조정

        # 이미지 라벨 생성
        self.image_label = tk.Label(self.main, bg="white", image=watch)
        self.image_label.place(x=600, y=90)

        # 현재 시간/날짜 표시 라벨 생성
        self.current_time = datetime.now().strftime('%H:%M')
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        global label_time, label_date  # 전역 변수로 지정
        label_time = tk.Label(self.main, text=self.current_time, font=("Arial", 40))
        label_time.place(x=650, y=200)
        self.label_date = tk.Label(self.main, text=self.current_date, font=("Arial", 24))
        self.label_date.place(x=650, y=150)

        # 시간/날짜 업데이트 시작
        self.update_clock()

    def update_clock(self):
        current_time = datetime.now().strftime('%H:%M')
        current_date = datetime.now().strftime('%Y-%m-%d')
        label_time.config(text=current_time)
        label_date.config(text=current_date)
        label_time.after(1000, self.update_clock)  # 1초마다 업데이트

    def join_s(self):
        root.withdraw()  # 창 없애기
        self.new = tk.Toplevel(root)
        self.new["bg"] = "#FFFFFF"
        self.new.geometry("395x406")  # 해상도 선언

        font = tk.font.Font(family="맑은 고딕", size=20, weight="bold")
        label = tk.Label(self.new, text="회의 참가", font=font, bg="white")
        entry = tk.Entry(self.new, width=35, relief="solid", borderwidth=1)

        entry1 = tk.Entry(self.new, width=35, relief="solid", borderwidth=1)

        c1 = tk.Checkbutton(self.new, text="이후 회의에서 내 이름 기억", bg="white")
        c1.configure(bg='white')
        c2 = tk.Checkbutton(self.new, text="내 비디오 끄기", bg="white")
        label.pack(anchor="w", pady=25, padx=40)
        entry.configure(font=("", 12))
        entry.pack(pady=5, ipady=7)
        entry1.configure(font=("", 12))
        entry1.pack(pady=7, ipady=7)
        entry.pack()
        entry1.pack()
        c1.pack(anchor="w", padx=48, pady=5)
        c2.pack(anchor="w", padx=48, pady=5)
        label1 = tk.Label(self.new, text='"참가"를 클릭하면 서비스 약관 및 개인정보 처리방침에\n동의하게 됩니다.', bg="white")
        label1.pack(pady=5)
        label2 = tk.Label(self.new)
        label2.pack(anchor="e")
        btn = tk.Button(label2, text="참가", command=self.inin)
        btn1 = tk.Button(label2, text="취소")
        btn.pack(side="left", padx=20, pady=5)
        btn1.pack(side="left", padx=20, pady=5)

    def final_exit(self):
        self.into.withdraw()  # 창 없애기

    def close_main_form(self):
        self.master.deiconify()

    def inin(self):
        global connected_clients
        # print("1111111",connected_clients)
        self.new.withdraw()  # 창 없애기
        self.into = tk.Toplevel(root)
        self.into.geometry("1320x761")  # 해상도 선언
        self.into.resizable(False, False)

        self.video_canvas = tkinter.Canvas(self.into, width=1320, height=761, bg="gray")
        self.video_canvas.pack(side=tk.LEFT)

        self.button = tk.Button(self.video_canvas, text="비디오중지", width=15, height=5, command=self.change)  # 숨겨진 버튼 생성
        self.button1 = tk.Button(self.video_canvas, text="참가자", width=15, height=5, command=self.start)
        self.button2 = tk.Button(self.video_canvas, text="채팅", width=15, height=5)
        self.button3 = tk.Button(self.video_canvas, text="필터", width=15, height=5)
        self.button4 = tk.Button(self.video_canvas, text="종료", width=10, height=5)  # command=self.out

        main_streaming = threading.Thread(target=streaming, args=(self.video_canvas,))
        main_streaming.daemon = True
        main_streaming.start()

        self.video_canvas.bind("<Motion>",
                               lambda event: on_mouse_move(event, self.button, self.button1, self.button2, self.button3,
                                                           self.button4))
        self.video_canvas.bind("<Leave>", lambda event: on_mouse_leave(event, self.button, self.button1, self.button2,
                                                                       self.button3, self.button4))
        self.button2.bind("<Button-1>", self.chat_open)

        self.chatlist = tk.Listbox(self.into, width=38)
        self.labelC = tk.Label(self.into, width=38)
        self.chat_text = tk.Text(self.into, width=38)

    def chat_open(self, event):
        global chat_flags
        if chat_flags == 1:
            self.into.geometry("1600x761")  # self.into로 변경
            self.chatlist.place(relx=0.913, rely=0.35, relheight=0.7, anchor=tk.CENTER)  # 채팅 리스트를 우측 상단에 배치
            self.chat_text.place(relx=0.913, rely=0.9, relheight=0.2, anchor=tk.CENTER)  # 채팅 텍스트를 우측 하단에 배치
            chat_flags = 0

        else:
            self.into.geometry("1320x761")  # self.into로 변경
            self.chatlist.place_forget()
            self.chat_text.place_forget()
            chat_flags = 1

    def start(self):
        self.flags = 0

    def out(self):
        # 버튼감싸고있는 라벨
        self.la = tkinter.Label(self.into, image=label_imagew, border=0, highlightthickness=0)
        # 레이블에 투명 이미지 설정
        self.la.config(image=label_imagew)

        # 투명 이미지 배경 설정
        self.la.configure(background='#242424')  # 투명 이미지 위에 다른 위젯 배치를 위해 흰색 배경 설정

        # 이미지가 레이블의 크기와 일치하도록 크기 조정
        self.la.image = label_imagew
        self.la.pack()

        self.button5 = tk.Button(self.into, text="취소", width=10, height=5, command=self.remove_buttons)

        self.button6 = tk.Button(self.into, text="모두에 대해 회의종료", bg="#242424", image=exit_button, border=0,
                                 borderwidth=0, width=220, height=50, command=self.final_exit)
        self.button7 = tk.Button(self.into, text="회의 나가기", bg="#242424", image=out_button, border=0, borderwidth=0,
                                 width=220, height=50, command=self.labelx)

        self.la.place(x=1060, y=570)
        self.button6.place(x=1080, y=575)
        self.button7.place(x=1080, y=615)
        self.button5.place(x=1148, y=675)
        self.button5.place(x=1148, y=675)
        # 마우스 이벤트 다시 바인딩
        self.video_canvas.bind("<Leave>", lambda event: on_mouse_leave(event, self.button, self.button1, self.button2,
                                                                       self.button3, self.button4))

    def hide_webcam(self, frame):
        height, width = frame.shape[:2]
        scale_factor = 2
        new_height = int(height * scale_factor)
        delta = int((new_height - height) / 2)
        stretched_frame = cv2.resize(frame, (width, new_height))
        if delta > 0:
            stretched_frame = stretched_frame[delta:-delta, :]
        return stretched_frame

    def labelx(self):
        # 버튼감싸고있는 라벨
        self.label = tkinter.Label(self.into, image=label_imagew, border=0, highlightthickness=0)
        # 레이블에 투명 이미지 설정
        self.label.config(image=label_imagew)

        # 투명 이미지 배경 설정
        self.label.configure(background='#242424')  # 투명 이미지 위에 다른 위젯 배치를 위해 흰색 배경 설정

        # 이미지가 레이블의 크기와 일치하도록 크기 조정
        self.label.image = label_imagew
        self.label.pack()
        self.label.place(x=1060, y=570)
        self.label2 = tkinter.Label(self.label, text="새 호스트 지정", fg="white", bg="#242424")
        self.label2.pack(padx=10, pady=10)
        self.button_save = tkinter.Button(self.label, bg="#242424", image=save_label, width=250, height=50, border=0,
                                          borderwidth=0, highlightthickness=0, command=self.final_exit)
        self.button_save.pack()

    def remove_buttons(self):
        # 취소 버튼을 누르면 생성된 버튼들 제거
        self.la.destroy()
        self.button5.destroy()
        self.button6.destroy()
        self.button7.destroy()

    def change(self):
        self.flags = 1

    def hide_video(self, frame):
        # 가운데 라벨 어떻게 띄우는지 모르겠다.
        # self.labels = tkinter.Label(self.video_canvas, fg="white", text="이윤서", width=100, height=50)
        # self.labels.pack()
        black_screen = np.zeros_like(frame)
        black_screen[:] = (0, 0, 0)  # 모든 픽셀을 검정색으로 채움
        return black_screen

    def filter(self, frame):
        blank_frame = 0 * frame

        return blank_frame

    def hide_buttons(self):
        self.button.pack_forget()
        self.button1.pack_forget()
        self.button2.pack_forget()
        self.button3.pack_forget()
        self.button4.pack_forget()


def on_mouse_move(event, button, button1, button2, button3, button4):
    button.place(relx=0.1, rely=1, anchor="s")
    button1.place(relx=0.4, rely=1, anchor="s")
    button2.place(relx=0.5, rely=1, anchor="s")
    button3.place(relx=0.6, rely=1, anchor="s")
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