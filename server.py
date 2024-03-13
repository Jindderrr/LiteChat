import random

from flask import Flask, request, send_from_directory, jsonify

app = Flask(__name__)

USERS_REGISTERING_NOW = {}

@app.route('/')
@app.route('/login')
def main_page():
    with open("front/login/index.html") as f:
        return f.read()

@app.route('/registration')
def login_page():
    with open("front/registration/index.html") as f:
        return f.read()

@app.route('/request/<path:path>')
def check_registration(path): # эта функция для обработки запросов от js'а
    print(path)
    print(request.args)
    if path == "registration/check_email":
        a_email = request.args.get("email")
        email_is_free = True # email свободен? !!!
        return jsonify(email_is_free)

    if path == "registration/check_username":
        a_username = request.args.get("username")
        username_is_free = True # username свободен? !!!
        return jsonify(username_is_free)

    if path == "registration/send_email": # пользователь запрашивает код подтверждения
        a_email = request.args.get("email")
        a_username = request.args.get("username")
        # тут надо ещё раз проверить, что всё ок (нет пользователей с такой почтой и username),
        is_ok = True # всё ок? !!!
        if is_ok:
            code = random.randint(100000, 999999) # код подтверждения
            # отправить письмо по почте с кодом подтверждения.
            # пока не отправляем, а просто выводим в консоль
            print(f"{a_email}: код подтверждения отпрален на почту ({code})")
            USERS_REGISTERING_NOW[a_email] = (code, a_username)
        return jsonify(is_ok)

    if path == "registration/check_code": # от пользователя получены данные для регистрации
        a_email = request.args.get("email")
        a_code = request.args.get("code")

        # тут надо проверить, что код верный,
        is_success = False  # всё ок?
        if a_email in USERS_REGISTERING_NOW:
            is_success = USERS_REGISTERING_NOW[a_email][0] == a_code
            if is_success:
                a_username = USERS_REGISTERING_NOW[a_email][1]
                del USERS_REGISTERING_NOW[a_email]
                a_name = request.args.get("name")
                a_password = request.args.get("password")
                # если код верный, то внести пользовотеля в БД !!!

        return jsonify(is_success)

    if path == "login": # от пользователя получены данные для регистрации
        a_email = request.args.get("email")
        a_password = request.args.get("password")
        is_ok = True # проверка, существует ли пользователь с такой почтой и паролем !!!
        return jsonify(is_ok)

    return {"responce": False}

@app.route('/front/<path:filename>')
def get_file_in_front(filename):
    if True:
        print(request.remote_addr + " запросил " + filename)
        return send_from_directory('front', filename)
    else:
        print(request.remote_addr + " запросил " + filename + " - ОТКАЗАНО!")

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')

