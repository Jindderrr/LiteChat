from data_py import db_session
from data_py.chats import Chat
from data_py.messages import Message
from data_py.users import User

db_session.global_init('db/messenger.db')
db_sess = db_session.create_session()

# user = User(name='name',
#             email='email',
#             username='username')
# db_sess.add(user)
# db_sess.commit()
# chat = Chat(users='1 2',
#             type='single')
# db_sess.add(chat)
# db_sess.commit()
# message = Message(
#     text='text1',
#     sender=1,
#     chat_id=1
# )
# db_sess.add(message)
# db_sess.commit()
chat = db_sess.query(Chat).filter(Chat.id == 1).first()
last_mess = sorted(chat.messages, key=lambda x: x.id, reverse=True)[0]
print(chat.users, chat.unread_messages, chat.type, last_mess.text, last_mess.sender, last_mess.date)
