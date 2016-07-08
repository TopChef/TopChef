"""
Contains tests for :mod:`topchef.models`
"""
import pytest
import os
from uuid import UUID
from topchef.models import Service
from topchef.config import config
from .test_api_server import app_client
from uuid import uuid4

SERVICE_NAME = 'TestService'
SERVICE_DESCRIPTION = 'A service made from the ``service`` test fixture ' \
                      'used for unit testing'

SERVICE_SCHEMA = {'type': 'object'}


@pytest.yield_fixture
def schema_directory():
    if not os.path.isdir(config.SCHEMA_DIRECTORY):
        os.mkdir(config.SCHEMA_DIRECTORY)

    yield

    if not os.listdir(config.SCHEMA_DIRECTORY):
        os.removedirs(config.SCHEMA_DIRECTORY)


@pytest.yield_fixture
def service(schema_directory):

    test_service = Service(
        SERVICE_NAME, description=SERVICE_DESCRIPTION, schema=SERVICE_SCHEMA
    )

    service_file = test_service.path_to_schema

    yield test_service

    os.remove(service_file)


class TestService(object):

    def test_constructor(self, service):
        assert service.name == SERVICE_NAME
        assert isinstance(service.id, UUID)
        assert service.description == SERVICE_DESCRIPTION
        assert service.job_registration_schema == SERVICE_SCHEMA
        assert os.path.isfile(service.path_to_schema)

    def test_constructor_no_schema(self, schema_directory):
        minimum_param_service = Service(SERVICE_NAME)

        assert minimum_param_service.name == SERVICE_NAME
        assert minimum_param_service.description
        assert minimum_param_service.job_registration_schema == {
            'type': 'object'
        }
        assert os.path.isfile(minimum_param_service.path_to_schema)


@pytest.yield_fixture
def twin_services(schema_directory):
    services = (Service('Service1'), Service('Service2'))

    created_schema_files = {serv.path_to_schema for serv in services}

    yield services

    for path in created_schema_files:
        os.remove(path)


class TestComparisons(object):

    def test_eq(self, twin_services):
        service1 = twin_services[0]
        service2 = twin_services[1]

        service1.id = service2.id

        assert service1 == service2


    def test_ne(self, twin_services):
        service1 = twin_services[0]
        service2 = twin_services[1]

        assert service1 != service2


def test_repr(service):
    assert service.__repr__() == \
           '%s(id=%d, name=%s, description=%s, schema=%s)' % (
        service.__class__.__name__, service.id, service.name,
        service.description, service.job_registration_schema
    )


def test_is_directory_available(service):
    assert service.is_directory_available


class TestServiceSchema(object):

    def test_post_dump(self, service):
        with app_client('/'):
            service_dict = service.ServiceSchema().dump(service)

        assert service_dict.data
        assert service_dict.data['url']
        assert not service_dict.errors

class TestDetailedServiceSchema(object):
    data_to_load = {
        'name': 'TheService',
        'description': "A test service loaded in through Marshmallow",
        "schema": {"type": "object"}
    }

    def test_make_service_all_args(self):
        with app_client('/'):
            loader_result = Service.DetailedServiceSchema().load(
                self.data_to_load
            )

        assert isinstance(loader_result.data, Service)
        assert not loader_result.errors