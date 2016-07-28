"""
Contains utilities to manage the schema directory
"""
import os
import shutil
import tempfile
import json
from uuid import uuid1, UUID
from . import models


class SchemaDirectoryOrganizer(object):
    REGISTRATION_SCHEMA_NAME = 'job_registration_schema'
    RESULT_SCHEMA_NAME = 'job_result_schema'

    def __init__(self, schema_directory_path):
        self.root_path = schema_directory_path

    @property
    def services(self):
        return [
            service_id for service_id in os.listdir(self.root_path)
                if self._is_guid(service_id)
            ]

    def register_service(self, service):
        service_directory = os.path.join(self.root_path, str(service.id))

        os.mkdir(service_directory)

    def __getitem__(self, model):
        if isinstance(model, models.Service):
            return os.path.join(
                self.root_path, str(model.id)
            )
        elif isinstance(model, models.Job):
            return os.path.join(
                self.root_path, str(model.parent_service.id),
                '%s.json' % str(model.id)
            )
        else:
            raise ValueError(
                'The model class %s is not a Service or Job',
                model.__repr__()
            )

    def write(self, data_to_write, target_path):

        _, temporary_filename = tempfile.mkstemp(suffix='.json')

        with open(temporary_filename, mode='w') as temporary_file:
            temporary_file.write(data_to_write)

        if os.path.isfile(target_path):
            os.remove(target_path)

        os.rename(temporary_file.name, target_path)

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