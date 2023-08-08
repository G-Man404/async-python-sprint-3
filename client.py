import datetime
import tkinter as tk
import sys
from threading import Thread
import time
import telnetlib


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
        self.sending_to = ""
        self.chat_with = ""
        self.tn = telnetlib.Telnet(self.host, self.port)
        self.last_message = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S.%f")

    def write(self, code, message=""):
        self.tn.write(f"{code} {message}".encode() + b'\n')

    def read(self):
        data = self.tn.read_until(b"\n")
        if len(data) == 0 or data == b"\n":
            data = b"101"
        str_data = data.decode("utf-8").split()
        code = int(str_data[0])
        text = ""
        if len(str_data) > 1:
            for t in str_data[1:]:
                text += t + " "
            text += "\n"
        return {"code": code, "text": text}

    def sending_request(self, event):
        text = self.textbox_2.get(1.0, "end-1c")
        stext = text.split()
        if len(text) == 0:
            return
        self.textbox_2.delete(1.0, "end-1c")
        if stext[0] == "/exit":
            self.write(120, "exit")
            sys.exit()
        if self.position_code == 0:
            if stext[0] == "/auth":
                self.write(110, f"{stext[1]} {stext[2]}")
            if stext[0] == "/reg":
                self.write(150, f"{stext[1]} {stext[2]} {stext[3]}")
            if stext[0] == "/connect":
                self.write(120, f"{'connect'} {stext[1]}")
            if stext[0] == "/status":
                self.write(120, f"status")
        if self.position_code == 1:
            self.write(131, text[0:-2])

    def app_setting(self):
        self.app.title = "Chat"
        self.textbox_1.pack()
        self.textbox_2.pack()
        self.app.bind("<Return>", self.sending_request)

    def out(self):
        while True:
            message = self.read()
            if self.position_code == 0:
                self.textbox_1.delete(1.0, tk.END)
                if message["code"] == 250:
                    self.textbox_1.insert(1.0,
                                          "Вы успешно зарегистрированы, для авторизации введите /auth login password")
                if message["code"] == 251:
                    self.textbox_1.insert(1.0,
                                          "К сожалению логин занят, попробуйте ещё раз")
                if message["code"] == 210:
                    self.textbox_1.insert(1.0,
                                          "Для авторизации введите /auth login password")
                if message["code"] == 212:
                    self.textbox_1.insert(1.0,
                                          "Неверный логин или пароль.\n"
                                          "Для авторизации введите /auth login password")
                if message["code"] == 211:
                    self.textbox_1.insert(1.0,
                                          f"Здравствуйте, {message['text']}\n"
                                          f"Вы можете выполнить следующие действия:\n"
                                          f"/status - список пользователей в онлайн\n"
                                          f"/connect user/everyone - присоединиться к чату\n"
                                          f"/exit - отключиться\n")
                if message["code"] == 220:
                    self.position_code = 1
                    self.sending_to = message["text"]
                    self.textbox_1.insert(1.0,
                                          "Вы успешно подключились к чату\n")
                    self.write(130)

                if message["code"] == 221:
                    msg = message["text"].replace("|", "\n")
                    self.textbox_1.insert(1.0, msg)

            elif self.position_code == 1:
                if message["code"] == 233 and len(message["text"]) > 0:
                    msg = message["text"].replace("|", "\n")
                    self.textbox_1.insert(1.0, msg)
                    self.last_message = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S.%f")

                if message["code"] == 230:
                    self.textbox_1.delete(1.0, tk.END)
                    msg = message["text"].replace("|", "\n")
                    self.textbox_1.insert(1.0, msg)
                    self.last_message = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S.%f")

    def update_text(self):
        while True:
            self.write(133, self.last_message)
            time.sleep(1)

    def start_app(self):
        self.app_setting()
        out_thread = Thread(target=self.out)
        update_thread = Thread(target=self.update_text)
        out_thread.setDaemon(True)
        update_thread.setDaemon(True)
        out_thread.start()
        update_thread.start()
        self.app.mainloop()


if __name__ == "__main__":
    client = Client()
    client.start_app()
