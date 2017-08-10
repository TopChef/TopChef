"""
Contains unit tests for the ``/services/<service_id>`` endpoint
"""
import json
import unittest
import unittest.mock as mock
from uuid import UUID
from topchef.models import Service, ServiceList
from topchef.api import ServiceDetail
from topchef.models.exceptions import NotUUIDError, ServiceWithUUIDNotFound
from sqlalchemy.orm import Session
from flask import Flask, Request
from hypothesis import given, assume
from hypothesis.strategies import text, uuids
from topchef.serializers import ServiceDetail as ServiceSerializer
from tests.unit.model_generators.service_list import service_lists


class TestServiceDetail(unittest.TestCase):
    """
    Base class for unit testing the API
    """
    def setUp(self) -> None:
        """
        Set up some mock model classes and create an endpoint
        """
        self.session = mock.MagicMock(spec=Session)
        self.request = mock.MagicMock(spec=Request)

        self._app = Flask(__name__)
        self._app.add_url_rule(
            '/', view_func=ServiceDetail.as_view(
                ServiceDetail.__name__, self.session
            )
        )

        self._context = self._app.test_request_context()

        self._context.push()

    def tearDown(self):
        """

        Pop the test request context
        """
        self._context.pop()


class TestGet(TestServiceDetail):
    """
    Contains unit tests for the ``get`` method
    """
    def setUp(self):
        TestServiceDetail.setUp(self)
        self.service = mock.MagicMock(spec=Service)
        self.endpoint = ServiceDetail(self.session)

    @given(text())
    def test_get_not_uuid(self, bad_id: str) -> None:
        """
        Tests that if a string is passed in, that a ``NotUUIDError`` is raised

        :param bad_id: A string that cannot be converted to a UUID
        """
        with self.assertRaises(NotUUIDError) as assertion:
            self.endpoint.get(bad_id)

        self.assertEqual(
            404, assertion.exception.status_code
        )

    @given(uuids(), service_lists())
    def test_get_service_not_found(
            self,
            service_id: UUID,
            service_list: ServiceList
    ) -> None:
        """
        Tests that a ``ServiceWithUUIDNotFound`` is thrown if a service with
        this ID is not found

        :param service_id: The ID for which a service does not exist
        :param service_list: The list of services to be made
        """
        assume(service_id not in set(service.id for service in service_list))
        endpoint = ServiceDetail(self.session, self.request, service_list)
        with self.assertRaises(ServiceWithUUIDNotFound) as assertion:
            endpoint.get(str(service_id))

        self.assertEqual(
            404, assertion.exception.status_code
        )

    @given(service_lists())
    def test_get_service_happy_path(
            self, service_list: ServiceList
    ) -> None:
        """

        Tests that a valid service gives a ``200`` response from the detail
        endpoint

        :param service_list: A randomly-generated list of services
        """
        assume(len(service_list) > 0)
        service = self._get_first_service_from_list(service_list)
        endpoint = ServiceDetail(self.session, self.request, service_list)

        response = endpoint.get(str(service.id))
        self.assertEqual(
            200, response.status_code
        )
        self.assert_data_equal(
            json.loads(response.data.decode('utf-8')),
            service
        )

    def assert_data_equal(self, data: dict, service: Service) -> None:
        self.assertEqual(
            data['data'], self._get_dict_for_service(service)
        )

    @staticmethod
    def _get_first_service_from_list(service_list: ServiceList) -> Service:
        return next(service for service in service_list)

    @staticmethod
    def _get_dict_for_service(service: Service) -> dict:
        serializer = ServiceSerializer()
        return serializer.dump(service).data
