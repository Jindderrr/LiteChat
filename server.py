import random

from flask import Flask, request, send_from_directory, jsonify
from werkzeug.security import generate_password_hash
import WS
import json
from data_py import db_session
from data_py.messages import Message
from data_py.users import User
from data_py.chats import Chat

app = Flask(__name__)

USERS_REGISTERING_NOW = {}


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
            # отправить письмо по почте с кодом подтверждения.
            # пока не отправляем, а просто выводим в консоль
            print(f"{a_email}: код подтверждения отпрален на почту ({code})")
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
            chat_name = db_sess.query(User).filter(User.id == (
                chat_name[
                    1 if chat_name[0] == user.id else 0])).first().username
            if len(chat.messages) == 0:
                answer.append({'chat_id': chat.id,
                               "chat_name": chat_name,
                               "chat_type": chat.type,
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
                               "chat_type": chat.type,
                               "number_of_unread_messages": chat.unread_messages,
                               "chat_last_message": {
                                   "message_text": last_mess.text,
                                   "message_sender": last_mess.sender,
                                   "message_date": last_mess.date}})
        return answer
    return {"response": False}


@app.route('/front/<path:filename>')
def get_file_in_front(filename):
    if True:
        print(request.remote_addr + " запросил " + filename)
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
            msg_text = args["msg_text"]
            message = Message(text=msg_text,
                              sender=username,
                              chat_id=chat_id)
            db_sess.add(message)
            db_sess.commit()
            print(f'message added: {message.id}')
        elif msg_type == 'change_chat':
            chat = db_sess.query(Chat).filter(
                Chat.id == args['selected_chat_id']).first()
            answer = {'last_mess_id': {}, 'all_messages': []}
            for message in chat.messages:
                answer['all_messages'].append({'msg_text': message.text,
                                               'msg_time': message.date,
                                               'msg_sender': message.sender})

            answer['last_mess_id'] = {'id': chat.messages[-1].id}
            web_socket.send_msg(str(answer))
            print('chats have sent')


WS.new_msg_func = new_message

if __name__ == '__main__':
    db_session.global_init('db/messenger.db')
    print("окно регистрации тут - http://127.0.0.1:8080/registration")
    print("окно входа тут - http://127.0.0.1:8080/login")
    app.run(port=8080, host='127.0.0.1')
