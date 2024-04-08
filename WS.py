import asyncio, json, websockets
from threading import Thread
from data_py import db_session
from data_py.users import User


class WebSocket:
    def __init__(self, websocket, init_info):
        self.init_info = init_info
        self.websocket = websocket
        self.honest = check_hones_func(self.init_info)
        self.selected_chat_id = None

    def send_msg(self, msgText):
        if asyncio.create_task(_send_msg_as(msgText, self.websocket)) == None:
            print(connected_clients.index(self))



async def _send_msg_as(msg, websocket):
    try:
        await websocket.send(msg)
        return True
    except websockets.exceptions:
        for i in range(len(connected_clients)):
            if connected_clients[i].websocket == websocket:
                connected_clients.pop(i)
                break
        await websocket.close()
        print("WebSocket соединение с клиентом было закрыто")


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


def check_hones_func(user_info: dict):
    db_session.global_init('db/messenger.db')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == user_info['username']).first()
    if user is not None:
        if user.hashed_password == user_info['password_hash']:
            return True
    return False


connected_clients = []
new_msg_func = new_msg
Thread(target=run).start()
