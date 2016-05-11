from sqlalchemy.ext.declarative import declarative_base
from .database import users_table, METADATA
from passlib

BASE = declarative_base(metadata=METADATA)


class User(BASE):
    __table__ = users_table

    username = __table__.c.username
    email = __table__.c.email
    password_hash = __table__.c.password_hash


    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = self.hash_password(password)


    def hash_password(self, password_to_hash):