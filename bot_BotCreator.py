import time
from threading import Thread
from data_py import db_session
from data_py.users import User


def run(get_msgs_func, send_msgs_func, token):
    cmsgs = get_msgs_func(token, last_id=0)
    last_id = 0
    if len(cmsgs) != 0:
        last_id = cmsgs[-1]["message_id"]
    while True:
        time.sleep(1)
        gmsgs = get_msgs_func(token, last_id=last_id)
        if len(gmsgs) != 0:
            last_id = gmsgs[-1]["message_id"]
            print(last_id)
            print(gmsgs)
            for msg in gmsgs:
                # тут собственно обработка сообщения
                text = msg["text"]
                if text in ["/info", "/help"]:
                    send_text = """I am a Bot Creator, With my help, you can create and configure bots for this messenger.🤓

·Use /create_bot to create a bot;
·Use /configure_bot to edit the created bot;
·Use /api_info if you want to learn how to work with the api for our bots;"""
                    send_msgs_func(token, text=send_text,
                                   chat_id=msg["chat_id"])
                elif text == "/configure_bot":
                    sender = msg['sender']
                    db_sess = db_session.create_session()
                    user_bots = db_sess.get(User, sender).bots
                    db_sess.close()
                    if len(user_bots) == 0:
                        send_text = """You don't have any bots yet.
You can use /create_bot to create a new bot. 😉😉😉😉😉"""
                    else:
                        answer = []
                        for bot in user_bots:
                            answer.append(bot.get_information())
                        send_text = str(answer)
                        # !тут логика, если у пользователя есть боты
                    send_msgs_func(token, text=send_text,
                                   chat_id=msg["chat_id"])
                elif text == "/api_info":
                    send_text = """And so, using our api is very easy😉:


In order to receive the messages sent to your bot, send a request like: "http://127.0.0.1:8080/bot/get_msgs?token =[your bot's token]&last_id=[message id starting from which you want to receive messages]";

You will get the result in json format like:
array[
{"sender": [username of the message sender], "text": [message text], "date": [date the message was sent], "message_id": [message id], "chat_id": [site id],
...
]


In order to send a message, send a request like: "http://127.0.0.1:8080/bot/send_msg ?token=[your bot's token]&chat_id=[id of the chat you are sending a message to]&text=[message text]";


I hope I helped you figure out our api, if you still have questions, then you can contact the support service."""
                    send_msgs_func(token, text=send_text,
                                   chat_id=msg["chat_id"])


def start(get_msgs_func, send_msgs_func, token):
    Thread(target=run, args=[get_msgs_func, send_msgs_func, token]).start()
