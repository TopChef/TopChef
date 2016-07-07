import pytest
import os
from topchef.api_server import app
from contextlib import contextmanager
from sqlalchemy import create_engine
from topchef.config import config
from tempfile import mkstemp
from topchef.database import METADATA


@pytest.fixture(scope='module')
def database():

    engine = create_engine('sqlite://')
    config._engine = engine

    METADATA.create_all(bind=engine)


@contextmanager
def app_client(endpoint):
    app_client = app.test_client()
    request_context = app.test_request_context()

    request_context.push()

    yield app_client

    request_context.pop()


@pytest.mark.parametrize('endpoint', ['/', '/services'])
def test_getter(database, endpoint):
    with app_client(endpoint) as client:
        response = client.get(
            endpoint, headers={'Content-Type': 'application/json'}
        )

    assert response.status_code == 200