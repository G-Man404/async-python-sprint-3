import asyncio
from asyncio.streams import StreamReader, StreamWriter

import db_controller
from db_controller import *
from config import Commands
from logger import logger


class Communication:
    @staticmethod
    async def write(writer: StreamWriter, code, message=""):
        writer.write(f"{code} {message}".encode() + b'\n')
        await writer.drain()

    @staticmethod
    def message_processing(data: bytes):
        if len(data) == 0 or data == b"\n":
            data = b"101"
        str_data = data.decode("utf-8").split()
        code = int(str_data[0])
        text = ""
        if len(str_data) > 1:
            text = str_data[1:]
        return code, text

    @staticmethod
    async def read(reader: StreamReader):
        data = await reader.readline()
        code, text = Communication.message_processing(data)
        return {"code": code, "text": text}


class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.host = host
        self.port = port
        self.users = {}

    async def client_connected(self, reader: StreamReader, writer: StreamWriter):
        address = writer.get_extra_info('peername')
        logger.info('Start serving %s', address)

        current_user = False
        connect = False
        while True:
            message = await Communication.read(reader)
            if message["code"] == Commands.CHECK_CONNECTION:
                await Communication.write(writer, Commands.CONNECT_OK)
                continue

            if not current_user:
                if message["code"] not in [Commands.AUTH, Commands.REG]:
                    await Communication.write(writer, Commands.NEED_AUTH)
                    continue
                elif message["code"] == Commands.AUTH:
                    user = db_controller.auth(message["text"][0], message["text"][1])
                    if isinstance(user, db_controller.Users):
                        current_user = user
                        self.users[address] = user
                        await Communication.write(writer, Commands.AUTH_OK, user.name)
                        continue
                    else:
                        await Communication.write(writer, Commands.AUTH_ERROR)
                        continue
                elif message["code"] == 150:
                    user = db_controller.reg(message["text"][0], message["text"][1], message["text"][2])
                    if isinstance(user, db_controller.Users):
                        await Communication.write(writer, Commands.REG_OK)
                        continue
                    elif message["text"] == "login_busy":
                        await Communication.write(writer, Commands.LOGIN_BUSY)
                        continue
                    else:
                        await Communication.write(writer, Commands.REG_ERROR)
                        continue

            if message["code"] == Commands.COMMAND:
                command = message["text"][0]
                arg = message["text"][1:]
                if command == "connect":
                    connect = arg[0]
                    await Communication.write(writer, Commands.CONNECT_CHAT, connect)
                    continue
                if command == "exit":
                    del self.users[address]
                    await Communication.write(writer, Commands.CONNECT_END)
                    writer.close()
                    break
                if command == "status":
                    new_message = "Пользователи онлайн:|"
                    for user in self.users.values():
                        new_message += user.login + "|"
                    await Communication.write(writer, Commands.STATUS_MESSAGE, new_message)

            if connect:
                if message["code"] == Commands.SEND_MESSAGE_EVERYONE:
                    db_controller.send_message(current_user, message["text"][0:], connect)
                    await Communication.write(writer, Commands.MESSAGE_EVERYONE_SAVE)
                    continue
                if message["code"] == Commands.SEND_HISTORY:
                    if connect == "everyone":
                        new_messages = db_controller.give_received_message_for_everyone(current_user)
                        messages = ""
                        for new_message in new_messages:
                            messages += f"{new_message.sender.name} {new_message.text}|"
                        await Communication.write(writer, Commands.MESSAGE_HISTORY, messages)
                    else:
                        new_messages = db_controller.give_received_message_ptp(current_user, connect)
                        messages = ""
                        for new_message in new_messages:
                            messages += f"{new_message.sender.name} {new_message.text}"
                        await Communication.write(writer, Commands.MESSAGE_HISTORY, messages)
                if message["code"] == Commands.SEND_NEW_MESSAGE:
                    new_messages = db_controller.give_new_message(current_user, connect,
                                                                  datetime.datetime.strptime(message["text"][0],
                                                                                             '%Y-%m-%d-%H:%M:%S.%f'))
                    messages = ""
                    for new_message in new_messages:
                        messages += f"{new_message.sender.name} {new_message.text}\n"
                    await Communication.write(writer, Commands.NEW_MESSAGE, messages)

    async def main(self):
        srv = await asyncio.start_server(
            self.client_connected, self.host, self.port)

        async with srv:
            await srv.serve_forever()


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.main())
