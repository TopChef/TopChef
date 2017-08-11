"""
Contains unit tests for the services list
"""
import json
from topchef.models import ServiceList
from topchef.serializers import ServiceOverview as ServiceSerializer
from flask import Request
from tests.unit.test_api import TestAPI
import unittest.mock as mock
from sqlalchemy.orm import Session
from topchef.api import ServicesList
from hypothesis import given
from tests.unit.model_generators.service_list import service_lists


class TestServicesList(TestAPI):
    """
    Base class for unit tests of the services list
    """
    def setUp(self) -> None:
        """

        Create a fake service list endpoint
        """
        TestAPI.setUp(self)
        self.session = mock.MagicMock(spec=Session)  # type: Session
        self.request = mock.MagicMock(spec=Request)  # type: Request


class TestGet(TestServicesList):
    """
    Contains unit tests for the ``get`` method
    """
    def setUp(self):
        TestServicesList.setUp(self)
        self.expected_response_code = 200

    @given(service_lists())
    def test_200_status_code(self, service_list: ServiceList) -> None:
        """

        Tests that the method returns the 200 status code
        """
        endpoint = ServicesList(
            self.session, self.request, service_list
        )
        response = endpoint.get()
        self.assertEqual(self.expected_response_code, response.status_code)
        self.assert_data_equal(
            json.loads(response.data.decode('utf-8')), service_list
        )

    def assert_data_equal(self, data: dict, service_list: ServiceList) -> None:
        """

        :param data: The data to check
        :param service_list: The list of services to check
        """
        serializer = ServiceSerializer()
        serializer_data, errors = serializer.dump(service_list, many=True)
        self.assertFalse(errors)
        self.assertEqual(
            data['data'],
            serializer_data
        )
