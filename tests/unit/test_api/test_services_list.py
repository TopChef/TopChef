"""
Contains unit tests for the services list
"""
import json
from topchef.models import ServiceList, Service
from tests.unit.test_api import TestAPI
import unittest.mock as mock
from sqlalchemy.orm import Session
from topchef.api import ServicesList
from hypothesis import given
from tests.unit.service_generator import services


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
        self.service_list = mock.MagicMock(spec=ServiceList)
        self.service_list_constructor = mock.MagicMock(
            spec=type, return_value=self.service_list
        )


class TestServiceGenerator(TestAPI):
    @given(services())
    def test_description(self, service: Service) -> None:
        self.assertIsInstance(service.description, str)


class TestGet(TestServicesList):
    """
    Contains unit tests for the ``get`` method
    """
    def setUp(self) -> None:
        """

        Establish an expected status code for the response
        """
        TestServicesList.setUp(self)
        self.service = mock.MagicMock(spec=Service)
        self.services = [self.service],
        self.service_list.__iter__ = mock.MagicMock(
            return_value=self.services.__iter__()
        )
        self.expected_response_code = 200

    def test_200_status_code(self) -> None:
        """

        Tests that the method returns the 200 status code
        """
        response = self.endpoint.get()
        self.assertEqual(self.expected_response_code, response.status_code)
        self.assertEqual(mock.call(self.session),
                         self.service_list_constructor.call_args)

    def test_data(self) -> None:
        """

        Tests that the response contains a ``data`` field
        """
        result_dict = json.loads(self.endpoint.get().data.decode('utf-8'))
        self.assertIn('data', result_dict.keys())

    def test_meta(self) -> None:
        """

        Tests that the response contains a ``meta`` field that contains the
        schemas required to interpret the endpoint
        """