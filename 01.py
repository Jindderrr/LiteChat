from data_py import db_session
from data_py.bots import Bot
from data_py.chats import Chat
from data_py.messages import Message
from data_py.users import User

db_session.global_init('db/messenger.db')
db_sess = db_session.create_session()

user = User(name='name1',username='username1',email='email1@email.com')
user.set_password('password1')
db_sess.add(user)
db_sess.commit()
user = User(name='name2',username='username2',email='email2@email.com')
user.set_password('password2')
db_sess.add(user)
db_sess.commit()