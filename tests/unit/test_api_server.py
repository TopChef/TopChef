"""
Contains unit tests for :mod:`topchef.api_server`
"""
import json
import os
import pytest
from uuid import UUID
from topchef.api_server import app
from contextlib import contextmanager
from sqlalchemy import create_engine
from topchef.config import config
from topchef.database import METADATA
import topchef.api_server as server
from sqlalchemy.orm import sessionmaker

try:
    DATABASE_URI = os.environ['DATABASE_URI']
except KeyError:
    DATABASE_URI = 'sqlite://'

JOB_REGISTRATION_SCHEMA = {
    "name": "TestService",
    "description": "Some test data",
    "job_registration_schema": {
        "type": "object",
        "properties": {
            "value": {
                "type": "integer"
            }
        }
    }
}

VALID_JOB_SCHEMA = {'parameters': {'value': 1}}

@pytest.yield_fixture
def schema_directory():

    if not os.path.isdir(config.SCHEMA_DIRECTORY):
        os.mkdir(config.SCHEMA_DIRECTORY)

    yield

    if not os.listdir(config.SCHEMA_DIRECTORY):
        os.removedirs(config.SCHEMA_DIRECTORY)

@pytest.fixture()
def database(schema_directory):
    engine = create_engine(DATABASE_URI)

    config._engine = engine

    METADATA.create_all(bind=engine)
    server.SESSION_FACTORY = sessionmaker(bind=engine)

@contextmanager
def app_client(endpoint):
    app_client = app.test_client()
    request_context = app.test_request_context()

    request_context.push()

    yield app_client

    request_context.pop()


@pytest.mark.parametrize('endpoint', ['/', '/services', '/jobs'])
def test_get_request(database, endpoint):
    with app_client(endpoint) as client:
        response = client.get(
            endpoint, headers={'Content-Type': 'application/json'}
        )

    assert response.status_code == 200


def test_post_service(database):
    endpoint = '/services'
    with app_client(endpoint) as client:
        response = client.post(
            endpoint, headers={'Content-Type': 'application/json'},
            data=json.dumps(JOB_REGISTRATION_SCHEMA)
        )

    assert response.status_code == 201

@pytest.fixture
def posted_service(database):
    endpoint = '/services'

    with app_client(endpoint) as client:
        response = client.post(
            endpoint, headers={'Content-Type': 'application/json'},
            data=json.dumps(JOB_REGISTRATION_SCHEMA)
        )

        assert response.status_code == 201

        data = json.loads(response.data.decode('utf-8'))

        service_id = UUID(data['data']['service_details']['id'])

    return service_id

class TestService(object):

    def test_service_data_good_code(self, posted_service):
        endpoint = '/services/%s' % str(posted_service)

        with app_client(endpoint) as client:
            response = client.get(
                endpoint, headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 200

    def test_service_bad_id(self, posted_service):
        service_id = 'foo'
        assert service_id != posted_service

        endpoint = '/services/%s' % service_id

        with app_client(endpoint) as client:
            response = client.get(
                endpoint, headers={'Content-Type': 'application/json'}
            )
        
        assert response.status_code == 404

class TestPatchService(object):

    def test_service_patch(self, posted_service):
        endpoint = '/services/%s' % str(posted_service)

        with app_client(endpoint) as client:
            response = client.patch(endpoint)

        assert response.status_code == 200


    def test_service_404(self, posted_service):
        service_id = 'foo'
        assert service_id != str(posted_service)

        endpoint = '/services/%s' % service_id

        with app_client(endpoint) as client:
            response = client.get(
                endpoint, headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 404

@pytest.fixture
def posted_job(database, posted_service):
    endpoint = '/services/%s/jobs' % str(posted_service)

    with app_client(endpoint) as client:
        response = client.post(
            endpoint, headers={'Content-Type': 'application/json'},
            data=json.dumps(VALID_JOB_SCHEMA)
        )

        assert response.status_code == 201

        data = json.loads(response.data.decode('utf-8'))
        
        job_id = UUID(data['data']['job_details']['id'])

    return job_id
        
class TestGetServiceJobs(object):
    def test_get_jobs(self, posted_service, posted_job):
        endpoint = 'services/%s/jobs' % str(posted_service)

        with app_client(endpoint) as client:
            response = client.get(
                endpoint, headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 200

    def test_get_job(self, posted_service, posted_job):
        endpoint = 'jobs/%s' % (str(posted_job))

        with app_client(endpoint) as client:
            response = client.get(
                endpoint, headers={'Content-Type': 'application/json'}
            )
        
        assert response.status_code == 200

    def test_get_job_404(self, posted_service, posted_job):
        job_id = 'foo'
        assert job_id != str(posted_job)

        endpoint = 'jobs/%s' % (job_id)

        with app_client(endpoint) as client:
            response = client.get(
                endpoint, headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 404

