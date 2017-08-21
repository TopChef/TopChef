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
from topchef.models.errors import RequestNotJSONError
from hypothesis import given, assume
from hypothesis.strategies import composite, text, dictionaries
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


@composite
def _valid_post_requests(
        draw,
        names: str=text(),
        descriptions: str=text(),
        job_registration_schemas: dict=dictionaries(text(), text()),
        job_result_schemas: dict=dictionaries(text(), text())
) -> dict:
    return {
        'name': draw(names),
        'description': draw(descriptions),
        'job_registration_schema': draw(job_registration_schemas),
        'job_result_schema': draw(job_result_schemas)
    }


class TestPost(TestServicesList):
    """
    Contains unit tests for the post method
    """

    @given(_valid_post_requests())
    def test_valid_post(self, request_body: dict):
        request = mock.MagicMock(spec=Request)
        request.get_json = mock.MagicMock(return_value=request_body)
        endpoint = ServicesList(
            self.session, request
        )
        response = endpoint.post()
        self.assertEqual(response.status_code, 201)
        self.assertIn('Location', response.headers)

    @given(dictionaries(text(), text()))
    def test_invalid_post(self, request_body: dict) -> None:
        assume("name" not in request_body.keys())
        assume("description" not in request_body.keys())
        assume("job_registration_schema" not in request_body.keys())
        assume("job_result_schema" not in request_body.keys())

        request = mock.MagicMock(spec=Request)
        request.get_json = mock.MagicMock(return_value=request_body)
        endpoint = ServicesList(
            self.session, request
        )

        with self.assertRaises(endpoint.Abort):
            endpoint.post()

        self.assertTrue(endpoint.errors)

    def test_post_request_not_json(self) -> None:
        """

        """
        self.request.get_json = mock.MagicMock(return_value=None)
        endpoint = ServicesList(
            self.session, self.request
        )
        with self.assertRaises(RequestNotJSONError):
            endpoint.post()
