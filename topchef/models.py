from sqlalchemy.ext.declarative import declarative_base
from .database import users_table, METADATA
from marshmallow import Schema, fields, post_load

BASE = declarative_base(metadata=METADATA)


class User(BASE):
    __table__ = users_table

    username = __table__.c.username
    email = __table__.c.email

    def __init__(self, username, email):
        self.username = username
        self.email = email

    class UserSchema(Schema):
        username = fields.Str()
        email = fields.Email()

        @post_load
        def make_user(self, data):
            return User(data['username'], data['email'])

    def __repr__(self):
        return '<%s(username=%s, email=%s)>' % (
            self.__class__.__name__, self.username, self.email
        )