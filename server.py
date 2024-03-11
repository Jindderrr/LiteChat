# LiteChat 0.0.1

from flask import Flask, request, send_from_directory

from data_py import db_session
from data_py.users import User

app = Flask(__name__)


@app.route('/')
@app.route('/registration')
def index():
    with open("front/registration.html") as f:
        return f.read()


@app.route('/registration/check_all')
def check_registration():
    inp = {}
    for i in ("email", "username", "name", "password"):
        inp[i] = request.args.get(i)

    # Проверка на уникальность email и username
    response = {}
    db_sess = db_session.create_session()
    if db_sess.query(User).filter(User.email == inp['email']).first():
        response['email'] = False
    else:
        response['email'] = True
    if db_sess.query(User).filter(User.username == inp['username']).first():
        response['username'] = False
    else:
        response['username'] = True

    if response['email'] and response['username']:  # если email и username уникальны, то дабавляю в бд
        user = User(name=inp['name'],
                    username=inp['username'],
                    email=inp['email'])
        user.set_password(inp['password'])
        db_sess.add(user)
        db_sess.commit()
        print('success, user_id :', user.id)
    else:
        print('not success :', response)  # иначе пишу где промах
    return "false"


@app.route('/data/<path:filename>')
def get_image(filename):
    if True:
        print(request.remote_addr + " запросил " + filename)
        return send_from_directory('data', filename)
    else:
        print(request.remote_addr + " запросил " + filename + " - ОТКАЗАНО!")


def main():
    db_session.global_init('db/chat.db')
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
