import tkinter as tk
import socket
from threading import Thread



class User:
    def __init__(self, login: str, name: str):
        self.login = login
        self.name = name


class Client:
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.user: User
        self.app = tk.Tk()
        self.textbox_1 = tk.Text(self.app, height=30)
        self.textbox_2 = tk.Text(self.app, height=10)
        self.position_code = 0
        self.chat_with = ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect = False

    def write(self, code, message=""):
        print(message)
        print(f"{code} {message}".encode() + b'\n')
        self.socket.send(f"{code} {message}".encode() + b'\n')

    def read(self):
        data = b""
        new_char = self.socket.recv(1)
        while new_char != b"\n":
            data += new_char
            new_char = self.socket.recv(1)
        text = data.decode("utf-8").split()
        message = {"code": int(text[0]), "text": text[1:]}
        return message



    def connect(self):
        self.socket.connect((self.host, self.port))
        self._connect = True


    def sending_request(self, event):
        text = self.textbox_2.get(1.0, "end-1c").split()
        if len(text) == 0:
            return
        self.textbox_2.delete(1.0, "end-1c")
        if self.position_code == 0:
            if text[0] == "/auth":
                print(text)
                self.write(110, f"{text[1]} {text[2]}")

            # if "status" in text:
            #         self.write(120, "status")

    def app_setting(self):
        self.app.title = "Chat"
        self.textbox_1.pack()
        self.textbox_2.pack()
        self.app.bind("<Return>", self.sending_request)


    def text_update(self):
        while True:
            message = self.read()
            if self.position_code == 0:
                if message["code"] == 210:
                    self.textbox_1.insert(1.0,
                                          "Для авторизации введите /auth login password")
                if message["code"] == 212:
                    self.textbox_1.insert(1.0,
                                          "Неверный логин или пароль.\n"
                                          "Для авторизации введите /auth login password")
                if message["code"] == 211:
                    self.textbox_1.insert(1.0,
                                          "Здравствуйте ")



    def start_app(self):
        self.app_setting()
        self.connect()
        out_thread = Thread(target=self.text_update)
        out_thread.start()
        self.app.mainloop()


if __name__ == "__main__":
    client = Client()
    client.start_app()