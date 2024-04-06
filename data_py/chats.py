import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from data_py.db_session import SqlAlchemyBase


class Chat(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    users = sqlalchemy.Column(sqlalchemy.String)
    type = sqlalchemy.Column(sqlalchemy.String)
    unread_messages = sqlalchemy.Column(sqlalchemy.Integer,
                                        default=0)
    messages = orm.relationship("Message", back_populates='chat')

    def get_information(self):
        return {'id': self.id,
                'users': self.users.split(';'),
                'unread_messages': self.unread_messages}
