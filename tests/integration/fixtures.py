"""
Contains test fixtures for integration tests
"""
import os
import pytest
from sqlalchemy.orm import Session
from topchef.config import config
from topchef.api_server import app
from topchef import models
from multiprocessing import Process

SERVICE_NAME = 'Integration Testing Service'
SERVICE_DESCRIPTION = 'A service made from the ```service``` test fixture ' \
                      'needed for integration testing'
SERVICE_SCHEMA = {
    'type': 'object',
    'properties': {
        'value': {
            'type': 'integer',
            'minimum': 0
        }
    }
}

SERVER_HOST = 'localhost'
SERVER_PORT = 32141


@pytest.yield_fixture
def database():
    engine = config.database_engine

    if not os.path.isdir(config.SCHEMA_DIRECTORY):
        os.mkdir(config.SCHEMA_DIRECTORY)

    yield Session(bind=engine, expire_on_commit=False)


@pytest.yield_fixture
def api_server(database):
    """
    Create the resources to run the server
    :return:
    """
    server_process = Process(target=lambda: app.run(
            port=SERVER_PORT, host=SERVER_HOST
        )
    )
    server_process.start()

    yield

    server_process.terminate()


@pytest.yield_fixture
def service(api_server):
    testing_service = models.Service(
        SERVICE_NAME, SERVICE_DESCRIPTION, SERVICE_SCHEMA
    )

    yield testing_service


@pytest.yield_fixture
def service_in_database(service, database):
    database.add(service)

    try:
        database.commit()
        yield service
    except:
        database.rollback()
        raise

    database.remove(service)
    database.commit()
    database.expire()
