import asyncio, json, websockets
from threading import Thread


class WebSocket:
    def __init__(self, websocket, init_info):
        self.init_info = init_info
        self.websocket = websocket

    def send_msg(self, msgText):
        asyncio.create_task(_send_msg_as(msgText, self.websocket))


async def _send_msg_as(msg, websocket):
    await websocket.send(msg)


async def _main(websocket):
    print("Client connected")
    client = await websocket.recv()
    client = WebSocket(websocket, json.loads(client))
    connected_clients.append(client)
    while True:
        msg = await websocket.recv()
        new_msg_func(msg, client)


def new_msg(msg, client):
    print(f"сообщение от {client.init_info['username']}: {msg}")
    client.send_msg("ответ")


def run():
    asyncio.set_event_loop(asyncio.new_event_loop())
    start_server = websockets.serve(_main, "localhost", 5000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


connected_clients = []
new_msg_func = new_msg
Thread(target=run).start()
