import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from data_py.db_session import SqlAlchemyBase


class Chat(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    users = sqlalchemy.Column(sqlalchemy.JSON)
    messages = orm.relationship("Message", back_populates='chat')
