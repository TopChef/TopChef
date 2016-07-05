"""
Contains model classes for the API. These classes are atomic data types that
have JSON representations written in marshmallow, and a single representation
in the database.
"""
import os
import uuid
import json
import tempfile
from sqlalchemy.ext.declarative import declarative_base
from . import database
from . import config
from marshmallow import Schema, fields, post_load
from marshmallow_jsonschema import JSONSchema
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
    name = __table__.c.name

    jobs = relationship(Job, backref="parent_service")

    def __init__(self, name):
        self.id = uuid.uuid1()
        self.name = name

    def __repr__(self):
        return '%s(id=%d, name=%s)' % (
            self.__class__.__name__, self.id, self.name
        )

    @property
    def path_to_schema(self):
        return os.path.join(config.SCHEMA_DIRECTORY, '%s.json' % self.id)

    @property
    def schema(self):
        with open(self.path_to_schema, mode='r') as schema_file:
            schema = json.loads(''.join([line for line in schema_file]))
        return JSONSchema().loads(schema)

    @schema.setter
    def schema(self, new_schema):
        path_to_write = tempfile.mkstemp()
        with open(path_to_write[0], mode='rw') as temporary_file:
            temporary_file.write(json.dumps(new_schema))

        os.rename(path_to_write[1], self.path_to_schema)


class Job(BASE):
    """
    Base class for a compute job
    """
    __table__ = database.jobs

    id = __table__.c.job_id
