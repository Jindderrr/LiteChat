from data_py import db_session
from data_py.bots import Bot
from data_py.chats import Chat
from data_py.messages import Message
from data_py.users import User

db_session.global_init('db/messenger.db')
db_sess = db_session.create_session()

user = User(name='Петя',username='Petr',email='pety_krutoy@email.com')
user.set_password('password1')
db_sess.add(user)
db_sess.commit()
user = User(name='Вася',username='Vasyan',email='vasya2005@email.com')
user.set_password('password2')
db_sess.add(user)
db_sess.commit()