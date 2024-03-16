import random

from flask import Flask, request, send_from_directory, jsonify
from werkzeug.security import generate_password_hash

from data_py import db_session
from data_py.users import User

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
        email_is_free = not db_sess.query(User).filter(User.email == a_email).first()  # email свободен?
        print("email is free: " + email_is_free)
        return jsonify(email_is_free)  # <-<-<-

    if path == "registration/check_username":  # ->->->
        a_username = request.args.get("username")
        db_sess = db_session.create_session()
        username_is_free = not db_sess.query(User).filter(User.username == a_username).first()  # username свободен?
        print("username is free: " + username_is_free)
        return jsonify(username_is_free)  # <-<-<-

    if path == "registration/send_email":  # пользователь запрашивает код подтверждения
        a_email = request.args.get("email")
        a_username = request.args.get("username")
        # тут надо ещё раз проверить, что всё ок (нет пользователей с такой почтой и username),
        db_sess = db_session.create_session()
        is_ok = not db_sess.query(User).filter(User.username == a_username).first() and not db_sess.query(User).filter(
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
                db_sess.add(user)
                db_sess.commit()
                print('user register')
        return {"response": is_success}

    if path == "login":  # от пользователя получены данные для входа
        a_email_username = request.args.get("email-username")
        a_password = request.args.get("password")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(a_email_username == User.email).first()
        if user is None: user = db_sess.query(User).filter(a_email_username == User.username).first()
        is_ok = user and user.check_password(
            a_password)  # проверка, существует ли пользователь с такой почтой и паролем
        if is_ok is None: is_ok = False
        print(is_ok)
        return {"response": is_ok}
    return {"response": False}


@app.route('/front/<path:filename>')
def get_file_in_front(filename):
    if True:
        print(request.remote_addr + " запросил " + filename)
        return send_from_directory('front', filename)
    else:
        print(request.remote_addr + " запросил " + filename + " - ОТКАЗАНО!")


if __name__ == '__main__':
    db_session.global_init('db/chat.db')
    print("окно регистрации тут - http://127.0.0.1:8080/registration")
    print("окно входа тут - http://127.0.0.1:8080/login")
    app.run(port=8080, host='127.0.0.1')
