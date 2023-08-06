import logging
import sys
import asyncio
from asyncio.streams import StreamReader, StreamWriter

import db_controller
from db_controller import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


async def write(writer: StreamWriter, code, message = ""):
    writer.write(f"{code} {message}".encode())
    await writer.drain()

async def read(reader: StreamReader):
    data = await reader.readline()
    str_data = data.decode("utf-8").split()
    return {"code": int(str_data[0]), "text": str_data[1:]}


class Server:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.users = {}


    async def client_connected(self, reader: StreamReader, writer: StreamWriter):
        address = writer.get_extra_info('peername')
        logger.info('Start serving %s', address)

        current_user = False
        connect = False
        while True:
            message = await read(reader)
            if not current_user:
                if message["code"] not in [110, 150]:
                    await write(writer, 210)
                    continue
                elif message["code"] == 110:
                    user = db_controller.auth(message["text"][0], message["text"][1])
                    if isinstance(user, db_controller.Users):
                        current_user = user
                        self.users[address] = user
                        await write(writer, 211)
                        continue
                    else:
                        await write(writer, 212)
                        continue
                elif message["code"] == 150:
                    user = db_controller.reg(message["text"][0], message["text"][1], message["text"][2])
                    if isinstance(user, db_controller.Users):
                        await write(writer, 250)
                        continue
                    elif message["text"] == "login_busy":
                        await write(writer, 251)
                        continue
                    else:
                        await write(writer, 252)
                        continue

            if message["code"] == 120:
                command = message["text"][0]
                arg = message["text"][1:]
                if command == "connect":
                    connect = arg[0]
                    await write(writer, 220)
                    continue
                if command == "exit":
                    await write(writer, 240)
                    writer.close()
                    break

            if connect:
                if message["code"] == 131:
                    db_controller.send_message(current_user, "everyone", message["text"][0:])
                    await write(writer, 231)
                    continue
                if message["code"] == 132:
                    db_controller.send_message(current_user, "ptp", message["text"][0:], connect)
                    await write(writer, 231)
                    continue
                if message["code"] == 130:
                    if connect == "everyone":
                        new_messages = db_controller.give_received_message_for_everyone(current_user)
                        messages = ""
                        for new_message in new_messages:
                            messages += f"{new_message.sender.name} {new_message.text}\n"
                        print(messages)
                        await write(writer, 230, messages)
                    else:
                        new_messages = db_controller.give_received_message_ptp(current_user, connect)
                        messages = ""
                        for new_message in new_messages:
                            messages += f"{new_message.sender.name} {new_message.text}\n"
                        print(messages)
                        await write(writer, 230, messages)


    async def main(self):
        srv = await asyncio.start_server(
            self.client_connected, self.host, self.port)

        async with srv:
            await srv.serve_forever()


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.main())