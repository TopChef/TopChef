"""
Contains unit tests for the ``/jobs`` endpoint
"""
import unittest
import unittest.mock as mock
from flask import Request, Flask
from sqlalchemy.orm import Session
from topchef.api import JobsList


class TestJobList(unittest.TestCase):
    """
    Base class for unit testing the ``/jobs`` endpoint
    """
    def setUp(self) -> None:
        """
        Create a mock Flask request a mock DB session, and have the endpoint
        handle these fake requests
        """
        self.request = mock.MagicMock(spec=Request)
        self.session = mock.MagicMock(spec=Session)
        self.endpoint = JobsList(self.session, self.request)

        self._app = Flask(__name__)
        self._app.add_url_rule('/', view_func=JobsList.as_view(
            JobsList.__name__
        ))
        self._context = self._app.test_request_context()
        self._context.push()

    def tearDown(self) -> None:
        """
        Pop the testing context
        """
        self._context.pop()


class TestGet(TestJobList):
    """
    Contains unit tests for the ``GET`` request handler at this endpoint
    """
    def test_get(self) -> None:
        """
        Tests that the endpoint returns the ``200`` status code
        """
        response = self.endpoint.get()
        self.assertEqual(response.status_code, 200)
