"""
Contains test fixtures for the TopChef Client
"""
import pytest

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
    return {'number': 1, 'string': 'test', 'boolean': True}

@pytest.fixture
def invalid_json():
    return {'number': 3, 'string': 'test', 'boolean': True}

