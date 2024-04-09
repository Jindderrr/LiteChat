import os
import random
from email.mime.multipart import MIMEMultipart

import asyncio

from flask import Flask, request, send_from_directory, jsonify, Blueprint
from werkzeug.security import generate_password_hash

import format_msg
from config import EMAIL_LOGIN, EMAIL_PASSWORD
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import WS
import json
from data_py import db_session
from data_py.bots import Bot
from data_py.messages import Message
from data_py.users import User
from data_py.chats import Chat
import bot_BotCreator

app = Flask(__name__)
USERS_REGISTERING_NOW = {}
db_session.global_init('db/messenger.db')
db_sess = db_session.create_session()
blueprint = Blueprint(
    'chat_api',
    __name__
)


@blueprint.route('/api/get_chats', methods=['GET'])
def get_chats():
    username = request.args['username']
    user = db_sess.query(User).filter(User.username == username).first()
    password = request.args['password']
    if not user.check_password(password):
        return {'access denied': 'wrong username or password'}
    chats = user.chats.split(';')
    answer = []
    for chat_id in chats:
        chat = db_sess.get(Chat, int(chat_id))
        answer.append(chat.get_information())
    return answer


@blueprint.route('/api/send_message', methods=['POST'])
def send_msg():
    username = request.args['username']
    user = db_sess.query(User).filter(User.username == username).first()
    password = request.args['password']
    if not user.check_password(password):
        return {'access denied': 'wrong username or password'}
    message = Message(text=request.args['text'],
                      chat_id=request.args['chat_id'],
                      sender=username)
    db_sess.add(message)
    db_sess.commit()


def BotApi_get_msgs(token="", **args):
    bot = db_sess.query(Bot).filter(
        Bot.token == token).first()
    check_bot(token)  # если есть бот с таким токеном
    last_id = int(args["last_id"])
    if len(bot.chats) > 0:
        bot_chats = tuple(map(int, bot.chats.split(';')))
    else:
        bot_chats = []
    answer = []
    for chat_id in bot_chats:
        chat = db_sess.query(Chat).filter(Chat.id == chat_id).first()
        if chat is not None:
            messages = [mess for mess in chat.messages if mess.id > last_id]
            for mess in messages:
                if mess.sender[-3:] != 'bot':
                    answer.append(
                        {"sender": mess.sender,
                         "text": mess.text,
                         "date": str(mess.date),
                         "message_id": mess.id,
                         "chat_id": mess.chat_id})
    # answer - сообщения полученные ботом, id которых больше last_id
    return answer


def BotApi_send_msg(token="", **args):
    check_bot(token)  # если есть бот с таким токеном
    bot = db_sess.query(Bot).filter(Bot.token == token).first()
    text, chat_id = format_msg.format(args['text']), args['chat_id']
    message = Message(text=text, chat_id=chat_id, sender=bot.username)
    db_sess.add(message)
    db_sess.commit()
    # db_sess.close()
    aasitc = [sess for sess in WS.connected_clients if
              sess.selected_chat_id == chat_id]
    for sess in aasitc:
        async def f():
            sess.send_msg(
                json.dumps({"type": "new_msg_in_your_chat",
                            "message": {"msg_text": text,
                                        "msg_sender": bot.username,
                                        "msg_time": str(
                                            message.date)}}))

        asyncio.run(f())
    return message.get_information()


def BotApi_get_chats(token=''):
    check_bot(token)
    bot = db_sess.query(Bot).filter(Bot.token == token).first()
    answer = []
    chats_id = tuple(map(int, bot.chats.split(';')))
    for chat_id in chats_id:
        chat = db_sess.get(Chat, chat_id)
        answer.append(chat.get_information())
    return answer


@app.route('/bot/<path:path>')
def bot_http_api(path):
    bot_token = request.args.get("token")
    check_bot(bot_token)
    if path == "get_msgs":
        return jsonify(BotApi_get_msgs(bot_token,
                                       last_id=int(
                                           request.args.get("last_id"))))
    if path == 'send_msg':  # для добавления сообщения нужен токен бота, текст, id чата
        return BotApi_send_msg(bot_token, text=request.args.get("text"),
                               chat_id=request.args.get("chat_id"))
    if path == 'get_chats':
        return BotApi_get_chats(bot_token)
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
        email_is_free = not db_sess.query(User).filter(
            User.email == a_email).first()  # email свободен?
        print("email is free: " + email_is_free)
        return jsonify(email_is_free)  # <-<-<-

    if path == "registration/check_username":  # ->->->
        a_username = request.args.get("username")
        if a_username[-3:] == 'bot':
            return jsonify(
                {'error': 'can not create user with bot at the end'})
        username_is_free = len([c for c in a_username if
                                c not in "0123456789"]) != 0 and not db_sess.query(
            User).filter(
            User.username == a_username).first()  # username свободен?
        print("username is free: " + username_is_free)
        return jsonify(username_is_free)  # <-<-<-

    if path == "registration/send_email":  # пользователь запрашивает код подтверждения
        a_email = request.args.get("email")
        a_username = request.args.get("username")
        # тут надо ещё раз проверить, что всё ок (нет пользователей с такой почтой и username),
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
                user = User(name=a_name,
                            username=a_username,
                            email=a_email)
                user.set_password(a_password)
                hashed_pass = user.hashed_password
                db_sess.add(user)
                db_sess.commit()
                # db_sess.close()
                print('user register')
        return {"response": is_success, 'hash': hashed_pass}

    if path == "login":  # от пользователя получены данные для входа
        a_email_username = request.args.get("email-username")
        a_password = request.args.get("password")
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
        fst_user = db_sess.query(User).filter(
            User.username == request.args.get("my_username")).first()
        scnd_user = db_sess.query(User).filter(
            User.username == request.args.get("another_username")).first()
        if scnd_user is None:
            scnd_user = db_sess.query(Bot).filter(
                Bot.username == request.args.get("another_username")).first()
        if (db_sess.query(Chat).filter(
                Chat.users == f'{fst_user.username};{scnd_user.username}').first() or
                db_sess.query(Chat).filter(
                    Chat.users == f'{scnd_user.username};{fst_user.username}').first()):
            return {'error': 'this chat has already been created'}
        if fst_user.username == scnd_user.username:
            return {'error': 'can not create chat with yourself'}
        if scnd_user is None:
            return {'error': 'No such user'}
        check_password_hash(fst_user, pass_hash)
        chat = Chat(users=f'{fst_user.username};{scnd_user.username}',
                    type='single')
        db_sess.add(chat)
        db_sess.commit()
        fst_user.add_chat(chat.id)
        scnd_user.add_chat(chat.id)
        db_sess.commit()

        print(f'added chat: {chat.id}')
        # db_sess.close()
        return {'added chat': chat.id}
    if path == 'get_my_chats':  # {"chat_name", "chat_type", "chat_last_message", "number_of_unread_messages"}
        pass_hash = request.args.get("password_hash")
        username = request.args.get('username')
        user = db_sess.query(User).filter(
            User.username == username).first()
        check_password_hash(user, pass_hash)
        user_chats_id = user.chats.split(';')
        if user_chats_id == ['']:
            return []
        answer = {}
        known_users = []
        user_chats = []
        for chat_id in user_chats_id:
            chat = db_sess.query(Chat).filter(Chat.id == chat_id).first()
            if chat.type == 'single' or chat.type == 'group':
                print(chat.users)
                chat_name = chat.users.split(';')
                chat_name.remove(username)
                interlocutor = db_sess.query(User).filter(
                    User.username == chat_name[0]).first()
                if interlocutor is None:  # ищем в ботах
                    interlocutor = db_sess.query(Bot).filter(
                        Bot.username == chat_name[0]).first()
                if interlocutor is not None:
                    if chat.type == 'single':
                        chat_name = interlocutor.name
                        known_users.append({'username': interlocutor.username,
                                            'name': interlocutor.name})
                    else:
                        chat_name = "GroupName"
                    chat_ico = interlocutor.username
                else:
                    return {'error': 'can not find user'}
            all_users = db_sess.query(User).filter(
                User.username.in_(chat.users.split(';'))).all()
            all_users += db_sess.query(Bot).filter(
                Bot.username.in_(chat.users.split(';'))).all()
            all_users = [{'username': user.username, 'name': user.name} for
                         user in all_users]
            if len(chat.messages) == 0:
                user_chats.append({'chat_id': chat.id,
                                   "chat_name": chat_name,
                                   "chat_type": chat.type,
                                   "chat_ico": chat_ico,
                                   "all_users": all_users,
                                   "all_admins": chat.administrators.split(
                                       ';') if chat.administrators is not None else None,
                                   "number_of_unread_messages": chat.unread_messages,
                                   "chat_last_message": {
                                       "message_text": '',
                                       "message_sender": '',
                                       "message_date": ''}})
            else:
                last_mess = \
                    sorted(chat.messages, key=lambda x: x.id, reverse=True)[0]
                user_chats.append({'chat_id': chat.id,
                                   "chat_name": chat_name,
                                   "chat_ico": chat_ico,
                                   "chat_type": chat.type,
                                   "all_users": all_users,
                                   "all_admins": chat.administrators.split(
                                       ';') if chat.administrators is not None else None,
                                   "number_of_unread_messages": chat.unread_messages,
                                   "chat_last_message": {
                                       "message_text": last_mess.text,
                                       "message_sender": last_mess.sender,
                                       "message_date": last_mess.date}})
        answer['chats_and_groups'] = user_chats
        answer['known_users'] = list(tuple(known_users))
        return answer
    if path == 'start_group':  # для создания группы нужно больше 2 человек, хеш.пароль создателя,
        # username всех участников
        creator_username = request.args.get('username')
        pass_hash = request.args.get('password_hash')
        chat_name = request.args.get('chat_name')
        users = request.args.get('users').split(
            ',')  # users задаются запросом users=1,2,3....?
        creator = db_sess.query(User).filter(
            User.username == creator_username).first()
        if creator is None:
            return jsonify({'error': 'no such user with this username'})
        check_password_hash(creator, pass_hash)
        if len(users) < 2:
            return {'error': 'add two or more users'}
        for username in users:
            if db_sess.query(User).filter(User.username == username):
                pass
            else:
                return {
                    'error': f'no such user with this username: {username}'}
        if creator is None:
            return {'error': 'this hashed password is incorrect'}
        chat = Chat(type='group',
                    users=';'.join(users),
                    administrators=creator.username,
                    name=chat_name)
        db_sess.add(chat)
        db_sess.commit()
        for username in users:
            user = find_user(username)
            if user is None:
                user = db_sess.query(Bot).filter(
                    Bot.username == username).first()
            user.add_chat(chat.id)
        db_sess.commit()
        return jsonify({'added group': chat.id})
    return jsonify({"response": False})


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


def check_password_hash(user: User, pass_hash: str):
    if user.hashed_password != pass_hash:
        return {"response": False, 'error': 'Hash does not match'}


def new_message(msg, web_socket: WS.WebSocket):
    msg = json.loads(msg)
    print(msg)
    if web_socket.honest:
        args = msg["args"]
        msg_type = msg["type"]

        if msg_type == "send_msg":
            username = web_socket.init_info["username"]
            chat_id = args["chat_id"]
            user = find_user(username)
            check_user_chat(user, chat_id)

            msg_text = format_msg.format(args["msg_text"])
            message = Message(text=msg_text,
                              sender=username,
                              chat_id=chat_id)
            db_sess.add(message)
            db_sess.commit()
            print(f'message added: {message.id}')
            # db_sess.close()
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
        elif msg_type == 'add_administrator':  # для добавления админа нужны username добвляющего и добавляемого, id группы
            editor = args['editor']
            username = args['username']
            group_id = args['group_id']
            group = db_sess.get(Chat, group_id)
            check_admins_editor(group, editor)
            if group.type == 'group' and username not in group.administrators:
                group.add_administrator(username)
                db_sess.commit()
                return jsonify({'success': 'user added to group'})
            else:
                return jsonify({'error': 'user already in administrators'})
        elif msg_type == 'delete_administrator':
            editor = args['editor']
            username = args['username']
            group_id = args['group_id']
            group = db_sess.get(Chat, group_id)
            check_admins_editor(group, editor)
            if group.type == 'group' and username == \
                    group.administrators.split(';')[0]:
                group.delete_administrator(username)
                db_sess.commit()
            else:
                return jsonify({'error': 'no such administrator'})
        elif msg_type == 'add_user':
            editor = args['editor']
            username = args['username']
            group_id = args['group_id']
            group = db_sess.get(Chat, group_id)
            if group.type == 'group' and editor in group.administrators.split(
                    ';'):
                group.add_user(username)
            else:
                return jsonify({'error': 'have no rights'})
        elif msg_type == 'delete_user':
            editor = args['editor']
            username = args['username']
            group_id = args['group_id']
            group = db_sess.get(Chat, group_id)

            if group.type == 'group' and editor in group.administrators and username in group.administrators:
                if editor == group.administrators.split(';')[0]:
                    group.delete_user(username)
                else:
                    return jsonify(
                        {'error': 'you must be chat creator to delete admin'})
            elif editor in group.administrators:
                group.delete_user(username)
            else:
                return jsonify({'error': 'have no rights'})


def check_user_chat(user: User, chat_id: int):
    user_chats = user.chats.split(';')
    if str(chat_id) in user_chats:
        print('Successful check user is right to send')
    return {'error': 'this user has not rights for sending in this chat'}


WS.new_msg_func = new_message


def check_bot(token: str):
    if db_sess.query(Bot).filter(Bot.token == token).first() is None:
        return {'error': 'invalid token'}


def create_creator_bot():
    creator_bot = db_sess.query(Bot).filter(
        Bot.username == 'creator_bot').first()
    if creator_bot:
        pass
    else:
        creator_bot = Bot(username='creator_bot',
                          name='Bot Creator'
                          )
        creator_bot.set_token()
        db_sess.add(creator_bot)
        db_sess.commit()


def find_user(username: str or User.username):
    return db_sess.query(User).filter(
        User.username == username).first()


def check_admins_editor(group: Chat, editor: str):
    if editor != group.administrators.split(';')[0]:
        return jsonify(
            {'error': 'editor has no right for adding administrator'})


if __name__ == '__main__':
    create_creator_bot()
    creator_token = db_session.create_session().query(Bot).filter(
        Bot.username == 'creator_bot').first().token

    bot_BotCreator.start(BotApi_get_msgs, BotApi_send_msg, token=creator_token)
    print("окно регистрации тут - http://127.0.0.1:8080/registration")
    print("окно входа тут - http://127.0.0.1:8080/login")

    app.register_blueprint(blueprint)
    app.run(port=8080, host='127.0.0.1')
