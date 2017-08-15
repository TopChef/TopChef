"""
Contains unit tests for the validator endpoint
"""
import unittest
import unittest.mock as mock
from sqlalchemy.orm import Session
from flask import Request, Flask
from topchef.api.validator import JSONSchemaValidator


class TestValidator(unittest.TestCase):
    """
    Base class for testing the validator
    """
    schema = {
        '$schema': "http://json-schema.org/draft-04/schema#",
        'title': 'Validator Schema',
        'description':
            "A Schema that a random number between 1 and 10 satisfies",
        'type': 'object',
        'properties': {
            'value': {
                'type': 'integer',
                'minimum': 1,
                'maximum': 10
            }
        }
    }

    valid_instance = {'value': 1}
    invalid_instance = {'value': 11}

    def setUp(self) -> None:
        self.session = mock.MagicMock(spec=Session)
        self.request = mock.MagicMock(spec=Request)
        app = Flask(__name__)
        app.add_url_rule(
            '/', view_func=JSONSchemaValidator.as_view(
                JSONSchemaValidator.__name__
            )
        )
        self.context = app.test_request_context()
        self.context.push()

    def tearDown(self) -> None:
        self.context.pop()


class TestGet(TestValidator):
    def test_get(self):
        endpoint = JSONSchemaValidator(self.session, self.request)
        response = endpoint.get()
        self.assertEqual(200, response.status_code)


class TestPost(TestValidator):
    def test_post_valid_instance(self):
        self.request.get_json = mock.MagicMock(return_value={
            'schema': self.schema, 'object': self.valid_instance
        })
        endpoint = JSONSchemaValidator(self.session, self.request)
        response = endpoint.post()

        self.assertEqual(200, response.status_code)

    def test_post_invalid_instance_valid_request(self):
        self.request.get_json = mock.MagicMock(
            return_value={
                'schema': self.schema, 'object': self.invalid_instance
            }
        )
        endpoint = JSONSchemaValidator(self.session, self.request)
        with self.assertRaises(endpoint.Abort):
            endpoint.post()
        self.assertTrue(endpoint.errors)

    def test_post_invalid_request(self):
        self.request.get_json = mock.MagicMock(
            return_value={
                'schema': self.schema, 'instance': self.valid_instance
            }
        )
        endpoint = JSONSchemaValidator(self.session, self.request)
        with self.assertRaises(endpoint.Abort):
            endpoint.post()
        self.assertTrue(endpoint.errors)
