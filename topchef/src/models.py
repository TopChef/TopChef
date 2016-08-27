"""
Contains model classes for the API. These classes are atomic data types that
have JSON representations written in marshmallow, and a single representation
in the database.
"""
import os
import shutil
import tempfile
import uuid
import logging
import json
from uuid import UUID

import jsonschema
from datetime import datetime, timedelta
from flask import url_for
from marshmallow import Schema, fields, post_dump, post_load
from marshmallow_jsonschema import JSONSchema
from sqlalchemy import inspect, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from . import database
from .config import config

LOG = logging.getLogger(__name__)

BASE = declarative_base(metadata=database.METADATA)


class SchemaDirectoryOrganizer(object):
    """
    Directory manager responsible for organizing the directory
    where services and jobs can store their required JSON Schemas.

    The top directory that is to be managed is passed into the constructor.
    Under normal execution, this directory is given by ``SCHEMA_DIRECTORY``
    in :mod:`config.py`.

    Each service is given a directory based on the service ID.
    Each job is given a directory based on the job ID under the service
    ID. 
    
    For a service ``1`` and a job ``2``. The directory tree will look like

    ::

        /schema_directory
         |
         |__/1
         |   |
         |   |__/2

    The SchemaDirectoryOrganizer also acts as a repository for constants
    for the model classes that have to do with writing the models to their
    required schema directories

    :var str root_path: The name of the top directory that this manager
        is to organize.
    """
    REGISTRATION_SCHEMA_NAME = 'job_registration_schema.json'
    RESULT_SCHEMA_NAME = 'job_result_schema.json'
    
    JOB_PARAMETER_FILE_NAME = 'parameters.json'
    JOB_RESULT_FILE_NAME = 'result.json'

    def __init__(self, schema_directory_path):
        """
        Instantiates the variables listed in the class description
        """
        self.root_path = schema_directory_path

    @property
    def services(self):
        """
        Returns the id of all services that are registered with this manager.
        The IDs are retrieved by crawling through the directory.

        :return: A list of UUIDs corresponding to the IDs of all services
            registered with an instance of this directory manager.
        :rtype: list(UUID)
        """
        return [
            UUID(service_id) for service_id in os.listdir(self.root_path)
                if self._is_guid(service_id)
            ]

    def register(self, model):
        """
        Register a model class with this manager. Creates a directory
        for the required model class.

        :param model: The model class to register with this manager
        :type model: :class:`topchef.models.Job` | 
            :class:`topchef.models.Service`
        :raises: ValueError if an invalid model is registered
        """
        if isinstance(model, Service):
            self._register_service(model)
        elif isinstance(model, Job):
            self._register_job(model)
        else:
            raise ValueError("Attempted to register an invalid model class")

    def _register_service(self, service):
        """
        Register a service
        
        :raises: ValueError if the service directory already exists
        """
        service_path = os.path.join(self.root_path, str(service.id))
        
        if os.path.isdir(service_path):
            raise ValueError("Attempted to register service %s. \
                    A directory for this service already exists at %s" % (
                    service, service_path)
                  )
        else:
            os.mkdir(service_path)

        print(service_path)
        assert os.path.isdir(service_path)

    def _register_job(self, job):
        """
        Register a job

        :raises: ValueError if the job directory exists or the job's service
            directory doesn't exist
        """
        service_path = os.path.join(self.root_path, str(job.parent_service.id))

        if not os.path.isdir(service_path):
            raise ValueError("Attempted to register job %s. \
                    The job's service %s has no service directory. \
                    Expected service directory to be %s." % (
                    job, job.parent_service, service_path)
            )

        job_path = os.path.join(service_path, str(job.id))
        
        if os.path.isdir(job_path):
            raise ValueError("Attempted to register job %s. \
                    A directory for this job already exists at %s." % (
                    job, job_path)
            )
        else:
            os.mkdir(job_path)

    def __getitem__(self, model):
        """
        Return the directory where each model is located

        :param model: The model class for which the directory must be found
        :return: The path to the working directory for the model
        :rtype: str
        """
        if isinstance(model, Service):
            return os.path.join(
                self.root_path, str(model.id)
            )
        elif isinstance(model, Job):
            return os.path.join(
                self.root_path, str(model.parent_service.id),
                str(model.id)
            )
        else:
            raise ValueError(
                'The model class %s is not a Service or Job',
                model.__repr__()
            )

    def write(self, data_to_write, target_path):
        """
        Write the required data to the target path
        """
        file_descriptor, temporary_filename = tempfile.mkstemp(suffix='.json')

        with open(temporary_filename, mode='w') as temporary_file:
            temporary_file.write(data_to_write)

        os.close(file_descriptor)
        
        if os.path.isfile(target_path):
            os.remove(target_path)
        
        if not os.path.isdir(os.path.split(target_path)[0]):
            raise FileNotFoundError("The parent directory %s to which this "
            "file is to be written does not exist" % os.path.split(target_path)[0])

        shutil.move(temporary_filename, target_path)

        
        if os.path.isfile(temporary_filename):
            os.remove(temporary_filename)

    @staticmethod
    def _is_guid(dirname):
        try:
            UUID(dirname)
            return True
        except ValueError:
            return False

    def __repr__(self):
        return '%s(schema_directory_path=%s)' % (
            self.__class__.__name__, self.root_path
        )


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
        self.file_manager.register(self)
        
        self.last_checked_in = datetime.utcnow()
        self.is_available = True

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
    def has_timed_out(self, date=None):
        if date is None:
            date = datetime.utcnow()
        return (date - self.last_checked_in) >= \
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
    def job_registration_schema(self):
        registration_schema_path = os.path.join(
            self.file_manager[self],
            self.file_manager.REGISTRATION_SCHEMA_NAME
        )

        with open(registration_schema_path, mode='r') as schema_file:
            file_data = ''.join([line for line in schema_file])

        return JSONSchema().loads(file_data).data

    @job_registration_schema.setter
    def job_registration_schema(self, schema_to_write):
        schema_path = os.path.join(
            self.file_manager[self],
            self.file_manager.REGISTRATION_SCHEMA_NAME
        )

        JSONSchema().validate(schema_to_write)

        self.file_manager.write(json.dumps(schema_to_write), schema_path)

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
            self.file_manager[self], self.file_manager.RESULT_SCHEMA_NAME
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
        job_registration_schema = fields.Dict(required=True)

        @post_load
        def make_service(self, data):
            try:
                description = data['description']
            except IndexError:
                description = 'No description'

            try:
                schema = data['job_registration_schema']
            except KeyError:
                schema = {'type': 'object'}

            try:
                result_schema = data['job_result_schema']
            except KeyError:
                result_schema = {'type': 'object'}

            return Service(
                data['name'],
                description=description,
                job_registration_schema=schema,
                organizer=FILE_MANAGER,
                job_result_schema=result_schema
            )


class Job(BASE):
    """
    Base class for a compute job
    """
    __table__ = database.jobs

    id = __table__.c.job_id
    date_submitted = __table__.c.date_submitted
    status = __table__.c.status

    def __init__(self, parent_service, job_parameters,
                 attached_session=Session(bind=config.database_engine),
                 file_manager=FILE_MANAGER
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
        self.file_manager.register(self)

        self.session = attached_session
        self.parameters = job_parameters

    def next(self, session):
        job = session.query(self.__class__).filter(
            self.__class__.date_submitted > self.date_submitted
        ).order_by(
            desc(self.__class__.date_submitted)
        ).first()

        if job is None:
            return None

        return job

    def update(self, new_dictionary):
        """
        Update job data with new data
        :param dict new_dictionary:
        :return:
        """
        self.DetailedJobSchema().validate(new_dictionary)

        self.status = new_dictionary['status']
        self.result = new_dictionary['result']

    @property
    def parameters(self):
        schema_path = os.path.join(
            self.file_manager[self], self.file_manager.JOB_PARAMETER_FILE_NAME
        )

        if not os.path.isfile(schema_path):
            with open(schema_path, mode='w+') as file:
                file.write(json.dumps({}))

        with open(schema_path, mode='r') as file:
            data = ''.join([line for line in file])

        return json.loads(data)

    @parameters.setter
    def parameters(self, new_schema):
        schema_path = os.path.join(
            self.file_manager[self], self.file_manager.JOB_PARAMETER_FILE_NAME
        )

        JSONSchema().validate(new_schema)

        with open(schema_path, mode='w+') as schema_file:
            schema_file.write(json.dumps(new_schema))

    @property
    def result_schema(self):
        return self.parent_service.job_result_schema

    @property
    def result(self):
        schema_path = os.path.join(
            self.file_manager[self], 
            self.file_manager.JOB_RESULT_FILE_NAME
        )

        if not os.path.isfile(schema_path):
            return None

        with open(schema_path) as result_file:
            file_data = result_file.read()

        return JSONSchema().loads(file_data).data

    @result.setter
    def result(self, job_result):
        path_to_write = os.path.join(
            self.file_manager[self],
            self.file_manager.JOB_RESULT_FILE_NAME
        )

        jsonschema.validate(job_result, self.parent_service.job_result_schema)
        self.file_manager.write(
            json.dumps(job_result), path_to_write
        )

    class JobSchema(Schema):
        id = fields.Str()
        date_submitted = fields.DateTime()
        status = fields.Str()
        parameters = fields.Dict(required=True)

    class DetailedJobSchema(JobSchema):
        result = fields.Dict(required=False)

    def __repr__(self):
        return '%s(parent_service=%s, ' \
               'job_parameters=%s, attached_session=%s, file_manager=%s)' % (
            self.__class__.__name__, self.parent_service, self.parameters,
            self.session, self.file_manager
        )

