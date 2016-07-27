"""
Contains utilities to manage the schema directory
"""
import os
from uuid import uuid1, UUID


class SchemaDirectoryOrganizer(object):
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

        job_schema_filename = os.path.join(
            service_directory, 'job_registration_schema.json'
        )

        data_to_write = str(service.job_registration_schema)

        with open(job_schema_filename, mode='w') as schema_file:
            schema_file.write(data_to_write)

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