"""
Contains unit tests for :mod:`topchef.api`
"""
import unittest
import abc
from topchef.wsgi_app import TestingWSGIAPPFactory


class TestAPI(unittest.TestCase, metaclass=abc.ABCMeta):
    """
    Base class for testing the flask application, with a flask app request
    context
    """
    def setUp(self) -> None:
        """
        Prepare a test app and push its context to Flask
        """
        self.testing_app = TestingWSGIAPPFactory().app
        self._app_context = self.testing_app.test_request_context()
        self._app_context.push()

    def tearDown(self):
        """
        Removes the flask context used to test the application
        """
        self._app_context.pop()
