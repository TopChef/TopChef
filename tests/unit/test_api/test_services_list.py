"""
Contains unit tests for the services list
"""
import json
from tests.unit.test_api import TestAPI
import unittest.mock as mock
from sqlalchemy.orm import Session
from topchef.api import ServicesList


class TestServicesList(TestAPI):
    """
    Base class for unit tests of the services list
    """
    def setUp(self) -> None:
        """

        Create a fake service list endpoint
        """
        TestAPI.setUp(self)
        self.session = mock.MagicMock(spec=Session)
        self.service_list = ServicesList(self.session)


class TestGet(TestServicesList):
    """
    Contains unit tests for the ``get`` method
    """
    def setUp(self) -> None:
        """

        Establish an expected status code for the response
        """
        TestServicesList.setUp(self)
        self.expected_response_code = 200

    def test_200_status_code(self) -> None:
        """

        Tests that the method returns the 200 status code
        """
        response = self.service_list.get()
        self.assertEqual(self.expected_response_code, response.status_code)

    def test_data(self) -> None:
        """

        Tests that the response contains a ``data`` field
        """
        result_dict = json.loads(self.service_list.get().data.decode('utf-8'))
        self.assertIn('data', result_dict.keys())

    def test_meta(self) -> None:
        """

        Tests that the response contains a ``meta`` field that contains the
        schemas required to interpret the endpoint
        """
