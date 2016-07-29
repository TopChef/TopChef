"""
Contains tests for :mod:`topchef.models`
"""
import pytest
import os
import jsonschema
import shutil
from uuid import UUID
from topchef.models import SchemaDirectoryOrganizer
from topchef import models
from topchef.config import config
from topchef.api_server import app
from .test_api_server import app_client


SERVICE_NAME = 'TestService'
SERVICE_DESCRIPTION = 'A service made from the ``service`` test fixture ' \
                      'used for unit testing'

SERVICE_SCHEMA = {
    'type': 'object',
    "properties": {
        "value": {
            "type": "integer",
            "minimum": 0,
            "maximum": 10
        }
    }
}

SCHEMA_DIRECTORY = os.path.join(config.BASE_DIRECTORY, 'testing_schemas')


@pytest.yield_fixture
def schema_directory_organizer(monkeypatch):
    if not os.path.isdir(SCHEMA_DIRECTORY):
        os.mkdir(SCHEMA_DIRECTORY)

    organizer = SchemaDirectoryOrganizer(SCHEMA_DIRECTORY)

    monkeypatch.setattr('topchef.models.FILE_MANAGER', organizer)
    monkeypatch.setattr(
        'topchef.config.Config.SCHEMA_DIRECTORY', SCHEMA_DIRECTORY
    )

    yield organizer

    shutil.rmtree(SCHEMA_DIRECTORY)


@pytest.yield_fixture
def service(schema_directory_organizer):

    test_service = models.Service(
        SERVICE_NAME, description=SERVICE_DESCRIPTION,
        job_registration_schema=SERVICE_SCHEMA,
        organizer=schema_directory_organizer
    )

    yield test_service


class TestService(object):

    def test_constructor(self, service):
        assert service.name == SERVICE_NAME
        assert isinstance(service.id, UUID)
        assert service.description == SERVICE_DESCRIPTION
        assert service.job_registration_schema == SERVICE_SCHEMA

    def test_constructor_no_schema(self, schema_directory_organizer):
        minimum_param_service = models.Service(
            SERVICE_NAME, organizer=schema_directory_organizer
        )

        assert minimum_param_service.name == SERVICE_NAME
        assert minimum_param_service.description
        assert minimum_param_service.job_registration_schema == {
            'type': 'object'
        }


@pytest.yield_fixture
def twin_services(schema_directory_organizer):
    services = (
        models.Service('Service1', organizer=schema_directory_organizer),
        models.Service('Service2', organizer=schema_directory_organizer)
    )

    yield services


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


@pytest.yield_fixture
def app_test_client(service):
    context=app.test_request_context()
    context.push()

    yield app.test_client()

    context.pop()


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
        "job_registration_schema": {"type": "object"},
    }

    def test_make_service_all_args(self, app_test_client):
        loader_result = models.Service.DetailedServiceSchema().load(
            self.data_to_load
        )

        assert isinstance(loader_result.data, models.Service)
        assert not loader_result.errors

VALID_JOB_SCHEMA = {'value': 1}


@pytest.fixture
def job(service):
    test_job = models.Job(service, VALID_JOB_SCHEMA,
                          file_manager=service.file_manager)

    return test_job


class TestJobConstructor(object):

    def test_constructor(self, job):
        assert job.status == "REGISTERED"
        assert isinstance(job.id, UUID)

    def test_constructor_bad_schema(self, service):
        with pytest.raises(jsonschema.ValidationError):
            models.Job(service, {'value': -1})
