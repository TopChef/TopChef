"""
Contains acceptance tests for the TopChef API
"""
import json
import pytest
import requests
import multiprocessing
import os
from topchef.api_server import app
import time

TESTING_HOST = 'localhost'
TESTING_PORT = 32164

@pytest.yield_fixture(scope='module')
def flask_app():
    """
    Start the server process on a high port, and in a separate process
    """
    server = multiprocessing.Process(
        target=app.run,
        kwargs={'host': TESTING_HOST, 'port': TESTING_PORT, 'debug': True}
    )
    
    server.start()

    time.sleep(3) # Give the server some time to start

    assert server.is_alive()

    base_url = 'http://%s:%s' % (TESTING_HOST, TESTING_PORT)

    yield base_url
    
    server.terminate()

@pytest.fixture
def valid_json():
    json_dict = {
        'number': 1,
        'string': 'string',
        'boolean': True
    }
    return json.dumps(json_dict)

def test_is_server_up(flask_app):
    response = requests.get(
        flask_app , headers={'Content-Type':'application/json'}
    )
    assert response.status_code == 200

def test_json_loopback(flask_app, valid_json):
    url = '%s/echo' % flask_app
    response = requests.post(
        url, headers={'Content-Type': 'application/json'},
        data=valid_json
    )

    assert response.status_code == 200

    response_from_server = response.json()

    assert response_from_server['data'] == json.loads(valid_json)

