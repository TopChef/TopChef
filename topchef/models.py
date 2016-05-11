from sqlalchemy.ext.declarative import declarative_base
from .database import users_table, METADATA

BASE = declarative_base(metadata=METADATA)


class User(BASE):
    __table__ = users_table

    username = __table__.c.username
    email = __table__.c.email

    def __init__(self, username, email):
        self.username = username
        self.email = email

    @property
    def short_json_representation(self):
        return {
            'username': self.username,
            'email': self.email
        }