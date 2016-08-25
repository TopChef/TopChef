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
    
    time.sleep(3)

    assert not server.is_alive()

@pytest.fixture
def json_schema():
    schema = {
        'type': 'object',
        "$schema": "http://json-schema.org/draft-04/schema#",
        'properties': {
            'number': {
                'type': 'integer',
                'minimum': 0,
                'maximum': 2
            },
            'string': {
                'type': 'string'
            },
            'boolean': {
                'type': 'boolean'
            }
        }
    }

    return schema

@pytest.fixture
def valid_json():
    json_dict = {
        'number': 1,
        'string': 'string',
        'boolean': True
    }
    return json_dict

def test_is_server_up(flask_app):
    response = requests.get(
        flask_app , headers={'Content-Type':'application/json'}
    )
    assert response.status_code == 200

def test_json_loopback(flask_app, valid_json):
    url = '%s/echo' % flask_app
    response = requests.post(
        url, headers={'Content-Type': 'application/json'},
        data=json.dumps(valid_json)
    )

    assert response.status_code == 200

    response_from_server = response.json()

    assert response_from_server['data'] == valid_json

class TestJSONSchemaValidator(object):
    endpoint = '/validator'

    def test_validator_200(self, flask_app, json_schema, valid_json):
        url = '%s%s' % (flask_app, self.endpoint)

        data_to_post = {'object': valid_json, 'schema': json_schema}

        response = requests.post(
            url, headers={'Content-Type': 'application/json'},
            data=json.dumps(data_to_post)
        )

        assert response.status_code == 200

    def test_validator_400(self, flask_app, json_schema):
        invalid_json = {'number': 1, 'string': 2, 'boolean': True}

        url = '%s%s' % (flask_app, self.endpoint)

        data_to_post = {'object': invalid_json, 'schema': json_schema}

        response = requests.post(
            url, headers={'Content-Type': 'application/json'},
            data=json.dumps(data_to_post)
        )

        assert response.status_code == 400

        assert response.json()['errors']
