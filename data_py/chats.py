import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from data_py.db_session import SqlAlchemyBase
from data_py.users import User


class Chat(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    users = sqlalchemy.Column(sqlalchemy.String)
    type = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    administrators = sqlalchemy.Column(sqlalchemy.String)
    unread_messages = sqlalchemy.Column(sqlalchemy.Integer,
                                        default=0)
    messages = orm.relationship("Message", back_populates='chat')

    def get_information(self):
        return {'id': self.id,
                'users': self.users.split(';'),
                'unread_messages': self.unread_messages}

    def add_administrator(self, administrator: User.username):
        if len(self.administrators) == 0:
            self.administrators += administrator
        else:
            self.administrators += f';{administrator}'

    def add_user(self, user):
        self.users += f';{user}'

    def delete_administrator(self, username):
        if username in self.administrators:
            admins = self.administrators[:].split(';')
            admins.remove(username)
            self.administrators = ';'.join(admins)
        else:
            return 'no such admin'

    def delete_user(self, username):
        if username in self.users:
            users = self.users[:].split(';')
            users.remove(username)
            self.users = users
