import socketserver
import cv2
import mysql.connector
import pickle
import time
import numpy as np

def connect_to_database():
    return mysql.connector.connect(
        host='192.168.31.87',
        user='zoom',
        password='0000',
        db='zoom_db',
    )

def insert_data_to_table(data): #회원가입
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

user_list = [123456]


class ClientInfo:
    def __init__(self, request, client_address, window_name):
        self.request = request
        self.client_address = client_address
        self.window_name = window_name
        self.sending_image = False  # 클라이언트가 이미지를 송출하는 상태인지 나타내는 플래그

class MyTCPHandler(socketserver.BaseRequestHandler):
    MAX_CLIENTS = 5
    client_infos = {}
    def check_id(self, data):  # 중복검사
        conn = None
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            insert_query = "SELECT * FROM pi WHERE id = %s"
            cursor.execute(insert_query, (data,))
            result = cursor.fetchone()
            if result:
                self.request.sendall("DUPLICATE".encode())
            else:
                self.request.sendall("AVAILABLE".encode())
        except mysql.connector.Error as e:
            print(f"Database operation failed: {e}")
            return False
        finally:
            if conn is not None and conn.is_connected():
                conn.close()

    def check_meeting_id(self, data):
        conn = None
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            insert_query = "SELECT * FROM new WHERE id = %s"
            cursor.execute(insert_query, (data,))
            result = cursor.fetchone()
            if result:
                id_and_pw = (result[0], result[1])
                serialized_data = pickle.dumps(id_and_pw)
                self.request.sendall(serialized_data)
            else:
                self.request.sendall("DUPLICATE".encode())
        except mysql.connector.Error as e:
            print(f"Database operation failed: {e}")
            return False
        finally:
            if conn is not None and conn.is_connected():
                conn.close()

    def compare_id(self, data): #로그인
        conn = None
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            insert_query = "SELECT * FROM pi WHERE id = %s"
            cursor.execute(insert_query, (data,))
            result = cursor.fetchone()
            print(result)
            if result:
                name_and_pw = (result[1], result[3]) #name, pw
                serialized_data = pickle.dumps(name_and_pw)
                self.request.sendall(serialized_data)
            else:
                self.request.sendall("duplicate".encode())
        except mysql.connector.Error as e:
            print(f"Database operation failed: {e}")
            return False
        finally:
            if conn is not None and conn.is_connected():
                conn.close()

    def insert_meeting_data_to_table(self, data):  # 회의 아이디 비밀번호 부여
        conn = None
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            insert_query = "INSERT INTO new (id, pw) VALUES (%s, %s)"
            cursor.execute(insert_query, data)
            conn.commit()
            cursor.close()
            print("good")
        except mysql.connector.Error as e:
            print(f"Database operation failed: {e}")
        finally:
            if conn is not None and conn.is_connected():
                conn.close()
    def real_exit(self):
        conn = None
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            delete_query = "DELETE FROM new"
            cursor.execute(delete_query)
            conn.commit()
            cursor.close()
            print("All data deleted successfully")
        except mysql.connector.Error as e:
            print(f"Database operation failed: {e}")
        finally:
            if conn is not None and conn.is_connected():
                conn.close()

    def compare_new_meeting(self):
        conn = None
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            select_query = "SELECT id, pw FROM new"
            cursor.execute(select_query)
            existing_data = cursor.fetchall()
            if existing_data:
                self.request.sendall('ok'.encode())
            else:
                self.request.sendall('no'.encode())
            cursor.close()
        except mysql.connector.Error as e:
            print(f"Database operation failed: {e}")
            # 오류 발생 시 예외 처리
            self.request.sendall('x'.encode())
        finally:
            if conn is not None and conn.is_connected():
                conn.close()

    def handle(self):
        if len(self.client_infos) >= self.MAX_CLIENTS:
            print(f"Connection from {self.client_address} refused: Maximum number of clients reached.")
            return
            # for ip,client_info in self.client_infos.items():
            #     client_info.request(b'over')
        window_name = f"Video from {self.client_address}"
        client_info = ClientInfo(self.request, self.client_address, window_name)
        self.client_infos[self.client_address[0]] = client_info
        print(f"Accepted connection from {self.client_address}")
        try:
            while True:
                data = self.request.recv(50000)
                #print(data)
                if not data:
                    break

                if data == b'stop':
                    for client_address, client_info in self.client_infos.items():
                        client_info.request.sendall(b'stop')
                    self.real_exit()
                    time.sleep(2)
                    self.server.shutdown()
                    self.server.server_close()
                    break
                elif data.startswith(b'b987123'):
                    id_value = data[7:].decode()
                    print(f"Received id 1: {id_value}")
                    self.compare_id(id_value)
                elif data.startswith(b'z987123'):
                    print(data)
                    self.compare_new_meeting()

                elif data.startswith(b'a123789'):
                    id_value = data[7:].decode()
                    print(f"Received id: {id_value}")
                    self.check_id(id_value)

                elif data.startswith(b'g987654'):
                    id_value = data[7:].decode()
                    self.check_meeting_id(id_value)

                elif data.startswith(b'm123456'):

                    client_info.sending_image = True
                    id_value = data[7:].decode()
                    #user_list = ["123456"]
                    user_list.append(id_value)
                    for i in range(len(user_list)):
                        print(user_list[i])
                    print("ㅎㅇ" + id_value)
                    self.send_user_to_clients(user_list)

                elif data.startswith(b'quit'):
                    name = data[4:]
                    user_list.remove(name.decode())
                    for i in range(len(user_list)):
                        print(user_list[i])
                    self.send_user_to_clients(user_list)

                elif data.startswith(b'IMG:') and data.endswith(b'END') or data.startswith(b'exit'):
                    client_info.sending_image = True  # 클라이언트가 이미지를 송출하는 상태로 변경
                    self.send_data_to_clients(data)

                else:
                    original_tuple = pickle.loads(data)
                    print(original_tuple)
                    if len(original_tuple) == 4:
                        insert_data_to_table(original_tuple)
                    elif len(original_tuple) == 2:
                        self.insert_meeting_data_to_table(original_tuple)
        except Exception as e:  # 예외 처리 추가
            print(f"An error occurred: {e}")
        finally:
            del self.client_infos[self.client_address[0]]
            print(f"Connection from {self.client_address} closed.")

    def send_data_to_clients(self, data):
        for ip, client_info in self.client_infos.items():
            if client_info.sending_image:  # 클라이언트가 이미지를 송출하는 상태인 경우에만 이미지 전송
                client_info.request.sendall(self.client_address[0].encode() + data)

    def send_user_to_clients(self, data):
        #encode_data = data.encode()
        dumps_data = pickle.dumps(data)
        for ip, client_info in self.client_infos.items():
            if client_info.sending_image:
                client_info.request.sendall(dumps_data)


    def send_message_to_clients(self, data):
        for ip, client_info in self.client_infos.items():
            client_info.request.sendall(data)

class MyTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

def start_server():
    HOST, PORT = "192.168.31.87", 9999
    global server
    server = MyTCPServer((HOST, PORT), MyTCPHandler)
    print("Server listening on port 9999...")
    server.serve_forever()
    return server

def stop_server(server):  # 서버 객체를 인자로 받아 종료합니다.
    if server:
        print("Closing the server...")
        server.shutdown()
        server.server_close()
        print("Server closed.")
    else:
        print("Server is not running.")

if __name__ == "__main__":
    server = start_server()
