import time
from threading import Thread
from data_py import db_session
from data_py.bots import Bot
from data_py.users import User
from server import db_sess


def run(get_msgs_func, send_msgs_func, token):
    cmsgs = get_msgs_func(token, last_id=0)
    creating_bot_name = False
    creating_bot_username = False
    bot_parts = {}
    last_id = 0
    if len(cmsgs) != 0:
        last_id = cmsgs[-1]["message_id"]
    while True:
        time.sleep(1)
        gmsgs = get_msgs_func(token, last_id=last_id)
        if len(gmsgs) != 0:
            last_id = gmsgs[-1]["message_id"]
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
                    user_bots = db_sess.query(User).filter(
                        User.username == sender).first().bots
                    if len(user_bots) == 0:
                        send_text = """You don't have any bots yet.
You can use /create_bot to create a new bot. 😉😉😉😉😉"""
                    else:
                        answer = []
                        for bot in user_bots:
                            inf = bot.get_information()
                            answer.append(str(inf))
                        send_text = '\n'.join(answer)
                    send_msgs_func(token, text=send_text,
                                   chat_id=msg["chat_id"])
                elif text == "/api_info":
                    send_text = """And so, using our api is very easy😉:


In order to receive the messages sent to your bot, send a request like: "http://127.0.0.1:8080/bot/get_msgs?token=[your bot's token]&last_id=[message id starting from which you want to receive messages]";

You will get the result in json format like:
array[
{"sender": [username of the message sender], "text": [message text], "date": [date the message was sent], "message_id": [message id], "chat_id": [site id],
...
]


In order to send a message, send a request like: "http://127.0.0.1:8080/bot/send_msg?token=[your bot's token]&chat_id=[id of the chat you are sending a message to]&text=[message text]";

In order to get all chats with bots, send a request like "http://127.0.0.1:8080/bot/get_chats?token=your bots's token. You will get an array, like [{id:1/2/N, users:'useranme1;username2;usernameN',unread_messages:1/2/N,type:'single/group'},...]

I hope I helped you figure out our api, if you still have questions, then you can contact the support service."""

                    send_msgs_func(token, text=send_text,
                                   chat_id=msg["chat_id"])
                elif text == '/create_bot':
                    send_text = 'Write your bot name. It can be any combination of english symbols and numbers'
                    creating_bot_name = True
                    bot_parts[msg['sender']] = {'name': '', 'username': ''}
                    send_msgs_func(token, text=send_text,
                                   chat_id=msg["chat_id"])
                elif creating_bot_name and msg['sender'] != 1:
                    if len(text) <= 15:
                        bot_parts[msg['sender']]['name'] = text
                        creating_bot_name = False
                        creating_bot_username = True
                        send_text = 'Write your bot username. It must end with bot, example: MyFiRstbot or MeME_bot'
                    else:
                        send_text = 'Try again. Bot name must be less than 15 characters'
                    send_msgs_func(token, text=send_text,
                                   chat_id=msg["chat_id"])
                elif creating_bot_username and msg['sender'] != 1:
                    sender = db_sess.query(User).filter(
                        User.username == msg['sender']).first()
                    if 15 >= len(text) > 3 and text[-3:] == 'bot':
                        if db_sess.query(Bot).filter(
                                Bot.username == text).first() is not None:
                            send_text = 'Sorry, this username is already busy. Try again'
                            send_msgs_func(token, text=send_text,
                                           chat_id=msg["chat_id"])
                        else:
                            bot = Bot(name=bot_parts[sender.username]['name'],
                                      username=text,
                                      creator_id=sender.id)
                            bot.set_token()
                            db_sess.add(bot)
                            db_sess.commit()
                            send_text = f'Bot has created. Token for your bot: {bot.token}'
                            bot_parts.pop(sender.username)
                            send_msgs_func(token, text=send_text,
                                           chat_id=msg["chat_id"])
                            creating_bot_username = False
                    else:
                        send_text = 'Bot username must be more than 3 symbols, less than 15 symbols and must and must end with "bot"'
                        send_msgs_func(token, text=send_text,
                                       chat_id=msg["chat_id"])


def start(get_msgs_func, send_msgs_func, token):
    Thread(target=run, args=[get_msgs_func, send_msgs_func, token]).start()
