import sqlalchemy
import datetime
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from data_py.db_session import SqlAlchemyBase


class Message(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'messages'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.DateTime,
                             default=datetime.datetime.now)
    sender = sqlalchemy.Column(sqlalchemy.Integer)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("chats.id"))
    chat = orm.relationship('Chat')

    def get_information(self):
        return {'id': self.id,
                'text': self.text,
                'date': self.date,
                'sender': self.sender,
                'chat_id': self.chat_id}
