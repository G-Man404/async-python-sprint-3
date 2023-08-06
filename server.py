import logging
import sys
import asyncio
from asyncio.streams import StreamReader, StreamWriter
from db_controller import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class Server:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.users = {}

    async def client_connected(self, reader: StreamReader, writer: StreamWriter):
        address = writer.get_extra_info('peername')
        logger.info('Start serving %s', address)
        writer.write("Для авторизации введите команду: /auth login password\n".encode())
        writer.write("Для регистрации введите команду: /reg login password name\n".encode())
        await writer.drain()
        current_user = False

        while True:
            data = await reader.readline()
            str_data = data.decode("utf-8").split()

            if len(str_data) == 0:
                continue

            if not current_user:
                if str_data[0] == "/auth":
                    user = Users.auth(str_data)
                    if user:
                        self.users[address] = user
                        user.status = "online"
                        user.save()
                        current_user = user
                        writer.write(f"Добро пожаловать {user.name}\n".encode())
                        writer.write(f"Для просмотра списка участников введите /users\n".encode())
                        writer.write(f"Для написания личного сообщения введите /to user_id message\n".encode())
                        writer.write(f"Для отключения введите /exit\n".encode())
                        await writer.drain()
                    else:
                        writer.write("Неверно введён логин или пароль".encode())
                        await writer.drain()
                        continue

                if str_data[0] == "/reg":
                        user = Users.reg(str_data)
                        if user:
                            writer.write(f"Учётная запись успешно создана!\n".encode())
                            writer.write(f"Для авторизации введите /auth login password\n".encode())
                            await writer.drain()
                            continue
                        else:
                            writer.write(f"Введённые данные некорректны, попробуйте ещё раз\n".encode())

                if address not in self.users.keys():
                    writer.write("Для авторизации введите команду: /auth login password\n".encode())
                    writer.write("Для регистрации введите команду: /reg login password\n".encode())
                    await writer.drain()
                    continue
            # new 123
            if str_data[0] == "/exit":
                current_user.status = "offline"
                current_user.save()
                print(self.users)
                del self.users[address]
                print(self.users)
                logger.info('Stop serving %s', address)
                writer.close()
                break






    async def main(self):
        srv = await asyncio.start_server(
            self.client_connected, self.host, self.port)

        async with srv:
            await srv.serve_forever()


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.main())