"""
Contains tests for :mod:`topchef.models`
"""
import pytest
import os
from uuid import UUID
from topchef.models import Service
from topchef.config import config

SERVICE_NAME = 'TestService'
SERVICE_DESCRIPTION = 'A service made from the ``service`` test fixture ' \
                      'used for unit testing'

SERVICE_SCHEMA = {'type': 'object'}


@pytest.yield_fixture
def service():
    if not os.path.isdir(config.SCHEMA_DIRECTORY):
        os.mkdir(config.SCHEMA_DIRECTORY)

    test_service = Service(
        SERVICE_NAME, description=SERVICE_DESCRIPTION, schema=SERVICE_SCHEMA
    )

    yield test_service

    test_service.remove_schema_file()
    if not os.listdir(config.SCHEMA_DIRECTORY):
        os.removedirs(config.SCHEMA_DIRECTORY)


class TestService(object):

    def test_constructor(self, service):
        assert service.name == SERVICE_NAME
        assert isinstance(service.id, UUID)
        assert service.description == SERVICE_DESCRIPTION
        assert service.job_registration_schema == SERVICE_SCHEMA
        assert os.path.isfile(service.path_to_schema)

    def test_constructor_no_schema(self, service):
        minimum_param_service = Service(SERVICE_NAME)

        assert minimum_param_service.name == SERVICE_NAME
        assert minimum_param_service.description
        assert minimum_param_service.job_registration_schema == {
            'type': 'object'
        }
        assert os.path.isfile(minimum_param_service.path_to_schema)