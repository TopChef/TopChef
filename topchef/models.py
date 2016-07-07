"""
Contains model classes for the API. These classes are atomic data types that
have JSON representations written in marshmallow, and a single representation
in the database.
"""
import os
import uuid
import json
import tempfile
import logging
from marshmallow import Schema, fields
from marshmallow_jsonschema import JSONSchema
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from . import database
from .config import config


LOG = logging.getLogger(__name__)

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

    jobs = relationship('Job', backref="parent_service")

    def __init__(self, name):
        self.id = uuid.uuid1()
        self.name = name

        self._create_schema_file()

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __repr__(self):
        return '%s(id=%d, name=%s)' % (
            self.__class__.__name__, self.id, self.name
        )

    def _create_schema_file(self):
        with open(self.path_to_schema, mode='w') as file:
            file.write('{}')

    @property
    def path_to_schema(self):
        return os.path.join(config.SCHEMA_DIRECTORY, '%s.json' % self.id)

    @property
    def is_directory_available(self):
        return os.path.isdir(os.path.split(self.path_to_schema)[0])

    @property
    def job_registration_schema(self):
        """
        This schema must be fulfilled in order to allow a job to be registered.
        The getter returns the schema from this service's associated file
        """
        with open(self.path_to_schema, mode='r') as schema_file:
            schema = json.loads(''.join([line for line in schema_file]))
        return JSONSchema().load(schema).data

    @job_registration_schema.setter
    def job_registration_schema(self, new_schema):
        """
        The setter for this method
        :param dict new_schema:
        :return:
        """
        path_to_write = tempfile.mkstemp()
        with open(str(path_to_write[1]), mode='w') as temporary_file:
            temporary_file.write(json.dumps(new_schema))

        os.rename(path_to_write[1], self.path_to_schema)

    def remove_schema_file(self, dangerous_delete=False):
        """
        If a schema file is present, and the conditions for deletion are met,
        then the schema file will be removed

        :param bool dangerous_delete: Suppress all warnings and delte the file
        anyway

        .. warning::

            Calling this method with ```dangerous_delete=True``` may cause the
            database to be inconsistent with the stored schema files.
        """
        inspector_clouseau = inspect(self)

        conditions_for_deletion = any({
            inspector_clouseau.transient,
            inspector_clouseau.deleted,
            inspector_clouseau.detached
        }) and os.path.isfile(self.path_to_schema)

        if conditions_for_deletion or dangerous_delete:
            os.remove(self.path_to_schema)

    class ServiceSchema(Schema):
        id = fields.Str()
        name = fields.Str()
        schema = fields.Dict()


class Job(BASE):
    """
    Base class for a compute job
    """
    __table__ = database.jobs

    id = __table__.c.job_id
