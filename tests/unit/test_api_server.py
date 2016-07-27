import json
import os
import pytest
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


@pytest.mark.parametrize('endpoint', ['/', '/services'])
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
            data=json.dumps({
                "name": "TestService",
                "description": "Some test data",
                "schema": {
                    "type": "object",
                    "properties": {
                        "value": {
                            "type": "integer"
                        }
                    }
                }
            })
        )

    assert response.status_code == 201
