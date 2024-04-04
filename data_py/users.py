import uuid

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    chats = sqlalchemy.Column(sqlalchemy.String, default='')
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    bots = orm.relationship("Bot", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def add_chat(self, chat_id):
        self.chats += str(chat_id) if self.chats == '' else f';{str(chat_id)}'

    def get_information(self):
        return {'id': self.id,
                'bot': self.bot,
                'name': self.name,
                'username': self.username,
                'email': self.email,
                'chats': self.chats
                }
