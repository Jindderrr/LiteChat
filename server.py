import os
import random
from email.mime.multipart import MIMEMultipart

import asyncio
from flask import Flask, request, send_from_directory, jsonify

import format_msg
from config import EMAIL_LOGIN, EMAIL_PASSWORD
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import WS
import json
from data_py import db_session
from data_py.messages import Message
from data_py.users import User
from data_py.chats import Chat
import bot_BotCreator

app = Flask(__name__)

USERS_REGISTERING_NOW = {}

def BotApi_get_msgs(token="", **args):
    db_sess = db_session.create_session()
    bot = db_sess.query(User).filter(
        User.token == token).first()  # вместо "None" - ссылка на бота из таблицы
    if bot is not None:  # если есть бот с таким токеном
        last_id = int(args["last_id"])
        bot_chats = tuple(map(int, bot.chats.split(';')))
        answer = []
        for chat_id in bot_chats:
            chat = db_sess.query(Chat).filter(Chat.id == chat_id).first()
            messages = chat.messages[last_id:]
            for mess in messages:
                answer.append(
                    {"sender": mess.sender,
                     "text": mess.text,
                     "date": str(mess.date),
                     "message_id": mess.id,
                     "chat_id": mess.chat_id})

        # answer - сообщения полученные ботом, id которых больше last_id
        db_sess.close()
        return answer

def BotApi_send_msg(token="", **args):
    db_sess = db_session.create_session()
    bot = db_sess.query(User).filter(User.token == token).first()  # вместо "None" - ссылка на бота из таблицы
    if bot is not None:  # если есть бот с таким токеном
        text, chat_id = format_msg.format(args['text']), args['chat_id']
        message = Message(text=text, chat_id=chat_id, sender=bot.id)
        db_sess.add(message)
        db_sess.commit()
        aasitc = [sess for sess in WS.connected_clients if sess.selected_chat_id == chat_id]
        for sess in aasitc:
            async def f():
                await sess.websocket.send(json.dumps({"type": "new_msg_in_your_chat",
                                          "message": {"msg_text": text,
                                                      "msg_sender": bot.username,
                                                      "msg_time": str(
                                                          message.date)}}))
            asyncio.run(f())
        return message.get_information()

@app.route('/bot/<path:path>')
def bot_http_api(path):

    bot_token = request.args.get("token")

    if path == "get_msgs":
        return BotApi_get_msgs(bot_token, last_id=int(request.args.get("last_id")))
    if path == 'send_msg':  # для добавления сообщения нужен токен бота, текст, id чата
        return BotApi_send_msg(bot_token, text=request.args.get("text"), chat_id=request.args.get("chat_id"))


    # else:
    #     return {'error': 'no such bot with this token'}
    return 'unknown request'


@app.route('/login')
def login_page():
    with open("front/login/index.html") as f:
        return f.read()


@app.route('/registration')
def registration_page():
    with open("front/registration/index.html") as f:
        return f.read()


@app.route('/')
def main_page():
    with open("front/main/index.html") as f:
        return f.read()


@app.route('/request/<path:path>')
def check_registration(path):  # эта функция для обработки запросов от js'а
    print(f'request from "{path}"')
    print(f'arguments: {request.args}')
    if path == "registration/check_email":  # ->->->
        a_email = request.args.get("email")
        db_sess = db_session.create_session()
        email_is_free = not db_sess.query(User).filter(
            User.email == a_email).first()  # email свободен?
        print("email is free: " + email_is_free)
        return jsonify(email_is_free)  # <-<-<-

    if path == "registration/check_username":  # ->->->
        a_username = request.args.get("username")
        db_sess = db_session.create_session()
        username_is_free = not db_sess.query(User).filter(
            User.username == a_username).first()  # username свободен?
        print("username is free: " + username_is_free)
        return jsonify(username_is_free)  # <-<-<-

    if path == "registration/send_email":  # пользователь запрашивает код подтверждения
        a_email = request.args.get("email")
        a_username = request.args.get("username")
        # тут надо ещё раз проверить, что всё ок (нет пользователей с такой почтой и username),
        db_sess = db_session.create_session()
        is_ok = not db_sess.query(User).filter(
            User.username == a_username).first() and not db_sess.query(
            User).filter(
            User.email == a_email).first() and "@" not in a_username  # всё ок?
        print(is_ok)
        if is_ok:
            code = random.randint(100000, 999999)  # код подтверждения

            html_template = open(
                'front/registration/code_registration.html').read()

            msg = MIMEMultipart("alternative")
            msg['Subject'] = Header('Подтверждение почты', 'utf-8')
            msg['From'] = EMAIL_LOGIN
            msg['To'] = a_email

            text_part = MIMEText(str(code), 'plain', 'utf-8')
            html_part = MIMEText(html_template.format(code=code), 'html',
                                 'utf-8')

            msg.attach(text_part)
            msg.attach(html_part)

            smtp_server = smtplib.SMTP('smtp.yandex.ru', 587)
            try:
                smtp_server.starttls()
                smtp_server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
                smtp_server.sendmail(EMAIL_LOGIN, a_email, msg.as_string())
                print(
                    f"{a_email}: код подтверждения отправлен на почту ({code})")
            except Exception as error:
                print('ERROR:', error)
            finally:
                smtp_server.close()

            USERS_REGISTERING_NOW[a_email] = (code, a_username)
        return {"response": is_ok}

    if path == "registration/check_code":  # от пользователя получены данные для регистрации
        a_email = request.args.get("email")
        a_code = request.args.get("code")

        # тут надо проверить, что код верный,
        is_success = False  # всё ок?
        hashed_pass = None
        if a_email in USERS_REGISTERING_NOW:
            is_success = int(USERS_REGISTERING_NOW[a_email][0]) == int(a_code)
            print("code is valid - " + str(is_success))
            if is_success:
                a_username = USERS_REGISTERING_NOW[a_email][1]
                del USERS_REGISTERING_NOW[a_email]
                a_name = request.args.get("name")
                a_password = request.args.get("password")
                # если код верный, то внести пользовотеля в БД
                db_sess = db_session.create_session()
                user = User(name=a_name,
                            username=a_username,
                            email=a_email)
                user.set_password(a_password)
                hashed_pass = user.hashed_password
                db_sess.add(user)
                db_sess.commit()
                print('user register')
        return {"response": is_success, 'hash': hashed_pass}

    if path == "login":  # от пользователя получены данные для входа
        a_email_username = request.args.get("email-username")
        a_password = request.args.get("password")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            a_email_username == User.email).first()
        if user is None:
            user = db_sess.query(User).filter(
                a_email_username == User.username).first()
        is_ok = user and user.check_password(a_password)
        if is_ok is None:
            is_ok = False
            hashed_pass, username, name, email = None, None, None, None
        else:
            hashed_pass = user.hashed_password
            name, email, username = user.name, user.email, user.username
        print(is_ok)
        return {"response": is_ok, 'hash': hashed_pass, 'username': username,
                'name': name, 'email': email}
    if path == "start_chat":
        pass_hash = request.args.get("password_hash")
        db_sess = db_session.create_session()
        fst_user = db_sess.query(User).filter(
            User.username == request.args.get("my_username")).first()
        scnd_user = db_sess.query(User).filter(
            User.username == request.args.get("another_username")).first()
        if (db_sess.query(Chat).filter(
                Chat.users == f'{fst_user.id};{scnd_user.id}').first() or
                db_sess.query(Chat).filter(
                    Chat.users == f'{scnd_user.id};{fst_user.id}').first()):
            return {'error': 'this chat has already been created'}
            if fst_user.id == scnd_user.id:
                return {'error': 'can not create chat with yourself'}
        if scnd_user is None:
            return {'error': 'No such user'}
        check_password_hash(fst_user, pass_hash)
        chat = Chat(users=f'{fst_user.id};{scnd_user.id}',
                    type='single')
        db_sess.add(chat)
        db_sess.commit()
        fst_user.add_chat(chat.id)
        scnd_user.add_chat(chat.id)
        db_sess.commit()
        print(f'added chat: {chat.id}')
        return {'added chat': chat.id}
    if path == 'get_my_chats':  # {"chat_name", "chat_type", "chat_last_message", "number_of_unread_messages"}
        pass_hash = request.args.get("password_hash")
        db_sess = db_session.create_session()

        user = db_sess.query(User).filter(
            User.username == request.args.get('username')).first()
        check_password_hash(user, pass_hash)
        user_chats_id = user.chats.split(';')
        if user_chats_id == ['']:
            return []
        answer = []
        for chat_id in user_chats_id:
            chat = db_sess.query(Chat).filter(Chat.id == chat_id).first()
            chat_name = list(map(int, chat.users.split(';')))
            interlocutor = db_sess.query(User).filter(User.id == (chat_name[1 if chat_name[0] == user.id else 0])).first()
            chat_name = interlocutor.name
            chat_ico = interlocutor.username
            if len(chat.messages) == 0:
                answer.append({'chat_id': chat.id,
                               "chat_name": chat_name,
                               "chat_type": chat.type,
                               "chat_ico": chat_ico,
                               "number_of_unread_messages": chat.unread_messages,
                               "chat_last_message": {
                                   "message_text": '',
                                   "message_sender": '',
                                   "message_date": ''}})
            else:
                last_mess = \
                    sorted(chat.messages, key=lambda x: x.id, reverse=True)[0]
                answer.append({'chat_id': chat.id,
                               "chat_name": chat_name,
                               "chat_ico": chat_ico,
                               "chat_type": chat.type,
                               "number_of_unread_messages": chat.unread_messages,
                               "chat_last_message": {
                                   "message_text": last_mess.text,
                                   "message_sender": last_mess.sender,
                                   "message_date": last_mess.date}})
        return answer
    if path == 'start_group':
        pass_hash = request.args.get('password_hash')
        users = list(map(int, request.args.get('users').split(
            ',')))  # users задаются запросом users=1,2,3....?
        db_sess = db_session.create_session()
        if len(users) < 2:
            return {'error': 'add two or more users'}
        for user_id in users:
            if db_sess.get(User, user_id):
                pass
            else:
                return {'error': f'no such user with this id: {user_id}'}
        if db_sess.query(User).filter(
                User.hashed_password == pass_hash) is None:
            return {'error': 'this hashed password is incorrect'}
        chat = Chat(type='group',
                    users=';'.join(list(map(str, users))))
        db_sess.add(chat)
        db_sess.commit()
        return f'added group: {chat.id}'
    return {"response": False}


@app.route('/front/<path:filename>')
def get_file_in_front(filename):
    if True:
        print(request.remote_addr + " запросил " + filename)
        if os.path.isfile(os.path.join('front', filename)):
            return send_from_directory('front', filename)
        if filename[:6] == "icons/":
            return send_from_directory('front', 'data/no_ico.jpg')
        return send_from_directory('front', filename)
    else:
        print(request.remote_addr + " запросил " + filename + " - ОТКАЗАНО!")


def check_password_hash(user, pass_hash):
    if user.hashed_password != pass_hash:
        return {"response": False, 'error': 'Hash does not match'}


def new_message(msg, web_socket: WS.WebSocket):
    msg = json.loads(msg)
    print(msg)
    if web_socket.honest:
        args = msg["args"]
        msg_type = msg["type"]
        db_sess = db_session.create_session()

        if msg_type == "send_msg":
            username = web_socket.init_info["username"]
            chat_id = args["chat_id"]
            user = db_sess.query(User).filter(
                User.username == username).first()
            check_user_chat(user, chat_id)

            msg_text = args["msg_text"]
            message = Message(text=msg_text,
                              sender=username,
                              chat_id=chat_id)
            db_sess.add(message)
            db_sess.commit()
            print(f'message added: {message.id}')
            aasitc = [sess for sess in WS.connected_clients if
                      sess.selected_chat_id == chat_id]
            for sess in aasitc:
                sess.send_msg(json.dumps({"type": "new_msg_in_your_chat",
                                          "message": {"msg_text": msg_text,
                                                      "msg_sender": username,
                                                      "msg_time": str(
                                                          message.date)}}))
        elif msg_type == 'change_chat':
            chat = db_sess.query(Chat).filter(
                Chat.id == args['selected_chat_id']).first()
            answer = {'last_mess_id': {}, 'all_messages': [],
                      'type': 'change_chat_answer'}
            for message in chat.messages:
                answer['all_messages'].append({'msg_text': message.text,
                                               'msg_time': str(message.date),
                                               'msg_sender': message.sender})

            if len(chat.messages) > 0:
                answer['last_mess_id'] = {'id': chat.messages[-1].id}
            else:
                answer['last_mess_id'] = {'id': None}
            web_socket.send_msg(json.dumps(answer))
            print('chats have sent')
            web_socket.selected_chat_id = args['selected_chat_id']


def check_user_chat(user: User, chat_id: int):
    user_chats = user.chats.split(';')
    if str(chat_id) in user_chats:
        print('Successful check user is right to send')
    return {'error': 'this user has not rights for sending in this chat'}


WS.new_msg_func = new_message


def create_bot_creator():
    db_sess = db_session.create_session()
    bot_creator = db_sess.query(User).filter(
        User.username == 'bot_creator').first()
    print(bot_creator)
    if bot_creator:
        pass
    else:
        bot_creator = User(bot=True,
                           username='bot_creator',
                           name='Bot Creator',
                           )
        bot_creator.set_token()
        db_sess.add(bot_creator)
        db_sess.commit()


if __name__ == '__main__':
    db_session.global_init('db/messenger.db')
    bot_BotCreator.start(BotApi_get_msgs, BotApi_send_msg, token="")
    create_bot_creator()
    print("окно регистрации тут - http://127.0.0.1:8080/registration")
    print("окно входа тут - http://127.0.0.1:8080/login")
    app.run(port=8080, host='127.0.0.1')
