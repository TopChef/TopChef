"""
Contains model classes for the API. These classes are atomic data types that
have JSON representations written in marshmallow, and a single representation
in the database.
"""
import uuid
from sqlalchemy.ext.declarative import declarative_base
from . import database
from marshmallow import Schema, fields, post_load
from sqlalchemy.orm import relationship


BASE = declarative_base(metadata=database.METADATA)


class UnableToFindItemError(Exception):
    """
    Thrown if the constructor is unable to find a user with the given
    session
    """
    pass


class Service(BASE):
    """
    A basic compute service
    """
    __table__ = database.services

    id = __table__.c.service_id

    def __init__(self):
        self.id = uuid.uuid1()
