"""
Contains model classes for the API. These classes are atomic data types that
have JSON representations written in marshmallow, and a single representation
in the database.
"""
import os
import uuid
import logging
import json
import jsonschema
import tempfile
from datetime import datetime, timedelta
from flask import url_for
from marshmallow import Schema, fields, post_dump, post_load
from marshmallow_jsonschema import JSONSchema
from sqlalchemy import inspect, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from . import database
from .config import config
from .schema_directory_organizer import SchemaDirectoryOrganizer

LOG = logging.getLogger(__name__)

BASE = declarative_base(metadata=database.METADATA)

FILE_MANAGER = SchemaDirectoryOrganizer(config.SCHEMA_DIRECTORY)


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
    description = __table__.c.description
    last_checked_in = __table__.c.last_checked_in
    heartbeat_timeout = __table__.c.heartbeat_timeout_seconds
    _is_service_available = __table__.c.is_service_available

    jobs = relationship('Job', backref="parent_service")

    def __init__(
            self, name, description='No Description',
            job_registration_schema=None,
            job_result_schema=None,
            heartbeat_timeout=30,
            organizer=FILE_MANAGER
    ):
        self.id = uuid.uuid1()
        self.name = name
        self.description = description
        self.heartbeat_timeout = heartbeat_timeout
        self.file_manager = organizer

        self.last_checked_in = datetime.utcnow()
        self.is_available = True

        self.file_manager.register_service(self)

        if job_registration_schema is None:
            self.job_registration_schema = {'type': 'object'}
        else:
            self.job_registration_schema = job_registration_schema

        if job_result_schema is None:
            self.job_result_schema = {'type': 'object'}
        else:
            self.job_result_schema = job_result_schema

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __repr__(self):
        return '%s(id=%d, name=%s, description=%s, schema=%s)' % (
            self.__class__.__name__, self.id, self.name, self.description,
            self.job_registration_schema
        )

    @classmethod
    def from_session(cls, session, service_id):
        service = session.query(cls).filter_by(id=service_id).first()
        if service is None:
            raise UnableToFindItemError(
                'The service with id %s does not exist' % service_id
            )
        else:
            return service


    def heartbeat(self):
        self.last_checked_in = datetime.utcnow()

    @property
    def has_timed_out(self, date=datetime.utcnow()):
        return (date - self.last_checked_in) > \
               timedelta(seconds=self.heartbeat_timeout)

    @property
    def is_available(self):
        return self._is_service_available and not self.has_timed_out

    @is_available.setter
    def is_available(self, new_value):
        self._is_service_available = new_value

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

    @property
    def registration_schema(self):
        registration_schema_path = os.path.join(
            self.file_manager[self], self.file_manager.REGISTRATION_SCHEMA_NAME
        )

        with open(registration_schema_path, mode='r') as schema_file:
            schema = json.loads(''.join([line for line in schema_file]))

        return JSONSchema().load(schema).data

    @registration_schema.setter
    def registration_schema(self, schema_to_write):
        errors, data = JSONSchema().dumps(schema_to_write)
        if errors: raise ValueError('The supplied schema is not a JSON Schema')

        self.file_manager.write(data)

    @property
    def job_result_schema(self):
        schema_path = os.path.join(
            self.file_manager[self], self.file_manager.RESULT_SCHEMA_NAME
        )

        with open(schema_path, mode='r') as schema_file:
            schema = json.loads(''.join([line for line in schema_file]))

        return JSONSchema().load(schema).data

    @job_result_schema.setter
    def job_result_schema(self, schema_to_write):
        data, errors = JSONSchema().dumps(schema_to_write)

        if errors: raise ValueError('The supplied schema is not a JSON Schema')

        schema_path = os.path.join(
            self.file_manager[self],
            '%s.json' % self.file_manager.RESULT_SCHEMA_NAME
        )

        self.file_manager.write(data, schema_path)

    class ServiceSchema(Schema):
        id = fields.Str()
        name = fields.Str(required=True)
        has_timed_out = fields.Boolean(default=False)

        @post_dump
        def resolve_urls(self, serialized_service):
            serialized_service['url'] = url_for(
                'get_service_data', service_id=serialized_service['id'],
                _external=True
            )

    class DetailedServiceSchema(ServiceSchema):
        description = fields.Str(required=True)
        job_registration_schema = fields.Dict()

        @post_load
        def make_service(self, data):
            try:
                description = data['description']
            except IndexError:
                description = 'No description'

            try:
                schema = data['job_registration_schema']
            except IndexError:
                schema = {'type': 'object'}

            return Service(
                data['name'],
                description=description,
                job_registration_schema=schema,
                organizer=FILE_MANAGER
            )


class Job(BASE):
    """
    Base class for a compute job
    """
    __table__ = database.jobs

    id = __table__.c.job_id
    date_submitted = __table__.c.date_submitted
    status = __table__.c.status
    result = __table__.c.result

    def __init__(self, parent_service, job_parameters,
                 attached_session=Session(bind=config.database_engine),
                 file_manager=SchemaDirectoryOrganizer(config.SCHEMA_DIRECTORY)
                 ):
        self.parent_service = parent_service

        jsonschema.validate(
            job_parameters,
            self.parent_service.job_registration_schema
        )

        self.id = uuid.uuid1()
        self.date_submitted = datetime.utcnow()
        self.status = "REGISTERED"
        self.file_manager = file_manager
        self.session = attached_session

    def __next__(self):
        job = self.session.query(self.__class__).filter(
            self.__class__.date_submitted > self.date_submitted
        ).order_by(
            desc(self.__class__.date_submitted)
        ).first()

        if job is None:
            raise StopIteration

        return job

    @property
    def result_schema(self):
        return self.parent_service.job_result_schema

    @property
    def result(self):
        with open(self.file_manager[self]) as result_file:
            file_data = result_file.read()

        return JSONSchema().loads(file_data).data

    @result.setter
    def result(self, job_result):
        jsonschema.validate(job_result, self.parent_service.job_result_schema)
        self.file_manager.write(
            json.dumps(job_result), self.file_manager[self]
        )

    def __iter__(self):
        return self

    class JobSchema(Schema):
        id = fields.Integer()
        date_submitted = fields.DateTime()
        status = fields.Str()

    class DetailedJobSchema(JobSchema):
        result = fields.Dict()
