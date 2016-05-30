from sqlalchemy.ext.declarative import declarative_base
from .database import users_table, job_table, METADATA
from marshmallow import Schema, fields, post_load
from sqlalchemy.orm import relationship

BASE = declarative_base(metadata=METADATA)


class UnableToFindItemError(Exception):
    """
    Thrown if the constructor is unable to find a user with the given session
    """
    pass


class User(BASE):
    __table__ = users_table

    username = __table__.c.username
    email = __table__.c.email

    def __init__(self, username, email):
        self.username = username
        self.email = email

    @classmethod
    def from_session(cls, username, session):
        """
        Construct the user from a session
        :param username:
        :param session:
        :return:
        """
        user = session.query(cls).filter_by(username=username).first()

        if not user or user is None:
            raise UnableToFindItemError('Unable to find user with username %s' % username)

        return user

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

    class DetailedUserSchema(Schema):
        username = fields.Str()
        email = fields.Email()


class Job(BASE):
    __table__ = job_table

    id = __table__.c.job_id
    due_date = __table__.c.due_date
    program = __table__.c.program
    status = __table__.c.status

    job_owner = relationship(User, backref='jobs', lazy='dynamic', uselist=True)

    class JobSchema(Schema):
        id = fields.Int()
        due_date = fields.DateTime()
        status = fields.Str()
