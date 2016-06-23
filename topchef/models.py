"""
Contains model classes for the API. These classes are atomic data types that
have JSON representations written in marshmallow, and a single representation
in the database.
"""
from sqlalchemy import asc, desc
from sqlalchemy.ext.declarative import declarative_base
from .database import users_table, job_table, METADATA
from marshmallow import Schema, fields, post_load
from sqlalchemy.orm import relationship

BASE = declarative_base(metadata=METADATA)


class UnableToFindItemError(Exception):
    """
    Thrown if the constructor is unable to find a user with the given
    session
    """
    pass


class User(BASE):
    __table__ = users_table

    username = __table__.c.username
    email = __table__.c.email
    jobs = relationship('Job', backref='job_owner', lazy='dynamic')

    def __init__(self, username, email):
        self.username = username
        self.email = email

    @classmethod
    def from_session(cls, username, session):
        """
        Construct the user from a given database session. If the user doesn't
        exist in the DB, throw an error

        :param str username: The username of the user to fetch
        :param Session session: the session to use for the construction
        :return: The user
        :rtype: User
        :raises: User.UnableToFindItemError if unable to retrieve the user
        """
        user = session.query(cls).filter_by(username=username).first()

        if not user or user is None:
            raise UnableToFindItemError(
                'Unable to find user with username %s' % username
            )

        return user

    class UserSchema(Schema):
        """
        Marshmallow schema responsible for providing a general schema, as well
        as creating a new user
        """
        username = fields.Str()
        email = fields.Email()

        @post_load
        def make_user(self, data):
            """
            Loader that takes in parsed JSON, and returns a new user

            :param data: A dictionary with data used to make a user
            :return:
            """
            return User(data['username'], data['email'])

    def __repr__(self):
        return '<%s(username=%s, email=%s)>' % (
            self.__class__.__name__, self.username, self.email
        )

    class DetailedUserSchema(Schema):
        username = fields.Str()
        email = fields.Email()


class Job(BASE):
    """
    Base class for a programming job initiated by the user
    """
    __table__ = job_table

    id = __table__.c.job_id
    due_date = __table__.c.due_date
    program = __table__.c.program
    status = __table__.c.status

    def __init__(self, program, due_date, owner=None):
        self.due_date = due_date
        self.program = program
        self.status = 'QUEUED'
        self.job_owner = owner

    @classmethod
    def from_session(cls, job_id, session):
        job = session.query(cls).filter_by(id=job_id).first()

        if not job:
            raise UnableToFindItemError(
                'A job with id=%d could not be found' % job_id
            )
        return job

    @classmethod
    def next_job(cls, user, session):
        next_job = session.query(cls).filter(
            cls.status == "QUEUED"
        ).filter(
            cls.job_owner == user
        ).order_by(asc(cls.due_date)).first()

        if next_job is None:
            raise UnableToFindItemError('No next jobs located')

        return next_job

    class JobSchema(Schema):
        id = fields.Int(required=False)
        due_date = fields.DateTime(format="iso")
        status = fields.Str()
        program = fields.Integer()
        job_owner = fields.Nested(User.UserSchema)

        @post_load
        def make_job(self, data):
            return Job(data['program'], data['due_date'])

    class DetailedJobSchema(Schema):
        id = fields.Int()
        due_date = fields.DateTime(format='iso')
        status = fields.Str()
        program = fields.Integer()
        job_owner = fields.Nested(User.UserSchema)

    def __repr__(self):
        return '<%s(id=%s, due_date=%s, program=%d, status=%s)>' % (
            self.__class__.__name__, str(self.id), self.due_date.isoformat,
            self.program, self.status
        )
