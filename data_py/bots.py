import uuid

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Bot(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'bots'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True)
    chats = sqlalchemy.Column(sqlalchemy.String, default='')
    token = sqlalchemy.Column(sqlalchemy.String)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey('users.id'))
    user = orm.relationship('User')

    def add_chat(self, chat_id):
        self.chats += str(chat_id) if self.chats == '' else f';{str(chat_id)}'

    def set_token(self):
        self.token = str(
            uuid.uuid3(uuid.NAMESPACE_DNS, f'{self.username}'))

    def get_information(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'chats': self.chats,
            'token': self.token
        }
