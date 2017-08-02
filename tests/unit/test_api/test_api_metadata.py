"""
Contains unit tests for :mod:`topchef.api.api_metadata`
"""
import unittest
from topchef.api.api_metadata import APIMetadata
from topchef.wsgi_app import TestingWSGIAPPFactory


class TestAPIMetadata(unittest.TestCase):
    """
    Base class for testing the module
    """
    def setUp(self):
        self.testing_app = TestingWSGIAPPFactory().app
        self.endpoint = APIMetadata()

        self._app_context = self.testing_app.test_request_context()
        self._app_context.push()

    def tearDown(self):
        self._app_context.pop()

    def test_get(self):
        response = self.endpoint.get()
        self.assertEqual(response.status_code, 200)
